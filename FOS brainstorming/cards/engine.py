# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

"""Effect resolution: collect, suppress, order, run.

Everything that used to be a scattered ``if not card.nullify`` guard is the
single :meth:`EffectEngine.is_suppressed` check here, and everything that used
to depend on board list order now has an explicit, total ordering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable, Sequence

from cards.effects import Effect, EffectKind, Suppression
from cards.stats import Modifier
from cards.statuses import NULLIFIED

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.runtime import Card


def _board_order(game_state: "GameState") -> dict[str, int]:
    """Position of each card in the canonical board sweep.

    That sweep is player one's board, then player two's, then neutrals — the
    order the old system broadcast events in, because it simply iterated
    ``get_all_cards()``. It is arbitrary (a card played later by player one
    still reacts before one played earlier by player two) but it is what the
    game is balanced around, and it round-trips through serialisation intact,
    so it is kept as the tie-break rather than replaced with creation order.
    """
    return {card.instance_id: index for index, card in enumerate(game_state.get_all_cards())}


def _sort_key(pair: tuple["Card", Effect], board_order: dict[str, int]) -> tuple[int, int, int]:
    """Total order for effect resolution: priority, then board position, then
    declaration order within the card."""
    card, effect = pair
    position = board_order.get(card.instance_id, len(board_order) + card.seq)
    return (int(effect.priority), position, effect.order)


class EffectEngine:
    """Owns effect lookup and suppression for one game."""

    def __init__(self) -> None:
        self._resolving_auras = False

    # -- suppression ----------------------------------------------------

    def suppressions(self, game_state: "GameState") -> list[Suppression]:
        """Every suppression currently in force.

        Resolved in two passes to avoid a cycle: a card that is silenced cannot
        contribute suppressions of its own. Two passes is enough for this game
        (nothing suppresses a suppressor of a suppressor) and, unlike a fixpoint
        loop, always terminates with a predictable answer.
        """
        found: list[Suppression] = []

        # Pass 1: silenced cards suppress all of their own effects.
        for card in game_state.get_all_cards():
            if NULLIFIED in card.statuses:
                found.append(Suppression(target_iid=card.instance_id, source_iid=card.instance_id))

        silenced = {s.target_iid for s in found}

        # Pass 2: suppressing auras belonging to cards that are not themselves silenced.
        for card in game_state.get_all_cards():
            if card.instance_id in silenced:
                continue
            for effect in card.definition.effects:
                if effect.kind is not EffectKind.STATIC or not effect.suppressing:
                    continue
                for produced in effect.fn(card, game_state) or ():
                    if isinstance(produced, Suppression):
                        found.append(produced)

        return found

    def is_suppressed(self, card: "Card", effect: Effect, game_state: "GameState") -> bool:
        if NULLIFIED in card.statuses:
            return True
        for suppression in self.suppressions(game_state):
            if suppression.target_iid == card.instance_id and suppression.covers(effect):
                return True
        return False

    # -- static effects -------------------------------------------------

    def aura_modifiers(self, card: "Card", game_state: "GameState") -> list[Modifier]:
        """Modifiers this card's own static effects grant to itself.

        Re-entrancy guard: an aura that reads a derived stat would otherwise
        recurse forever, so during resolution derived reads fall back to
        base + permanent counters.
        """
        if self._resolving_auras:
            return []

        effects = [e for e in card.definition.effects if e.kind is EffectKind.STATIC and not e.suppressing]
        if not effects:
            return []

        self._resolving_auras = True
        try:
            if NULLIFIED in card.statuses:
                return []
            suppressed = {
                s for s in self.suppressions(game_state)
                if s.target_iid == card.instance_id
            }
            produced: list[Modifier] = []
            for effect in sorted(effects, key=lambda e: (int(e.priority), e.order)):
                if any(s.covers(effect) for s in suppressed):
                    continue
                for item in effect.fn(card, game_state) or ():
                    if isinstance(item, Modifier):
                        produced.append(item)
            return produced
        finally:
            self._resolving_auras = False

    # -- dispatch -------------------------------------------------------

    def _live_effects(
        self,
        game_state: "GameState",
        event: str,
        sources: Iterable["Card"],
        kind: EffectKind,
    ) -> list[tuple["Card", Effect]]:
        suppressions = self.suppressions(game_state)
        by_target: dict[str, list[Suppression]] = {}
        for suppression in suppressions:
            by_target.setdefault(suppression.target_iid, []).append(suppression)

        collected: list[tuple["Card", Effect]] = []
        for card in sources:
            blocked = by_target.get(card.instance_id, ())
            for effect in card.definition.effects:
                if effect.kind is not kind or effect.event != event:
                    continue
                if any(s.covers(effect) for s in blocked):
                    continue
                collected.append((card, effect))

        board_order = _board_order(game_state)
        collected.sort(key=lambda pair: _sort_key(pair, board_order))
        return collected

    def dispatch(
        self,
        game_state: "GameState",
        event: str,
        sources: Sequence["Card"],
        make_context: Callable[["Card"], object],
    ) -> int:
        """Run every live triggered effect for ``event``. Returns how many ran."""
        ran = 0
        for card, effect in self._live_effects(game_state, event, sources, EffectKind.TRIGGERED):
            context = make_context(card)
            if not effect.applies(card, context):
                continue
            effect.fn(card, context)
            ran += 1
        return ran

    def replace(
        self,
        game_state: "GameState",
        event: str,
        payload: object,
        sources: Sequence["Card"],
    ) -> None:
        """Run replacement effects in priority order, mutating ``payload``."""
        for card, effect in self._live_effects(game_state, event, sources, EffectKind.REPLACEMENT):
            if getattr(payload, "cancelled", False):
                return
            if not effect.applies(card, payload):
                continue
            effect.fn(card, payload)
