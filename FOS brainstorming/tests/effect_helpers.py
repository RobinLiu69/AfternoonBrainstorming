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

"""Helpers for testing abilities.

Abilities are no longer methods, so a test drives them by firing the timing
window they listen to. These wrappers keep that to one readable line and make
the timing explicit at the call site.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cards import actions
from cards.events import Event
from cards.stats import DAMAGE, MAX_HEALTH, Layer, Modifier, Op
from cards.statuses import NULLIFIED

if TYPE_CHECKING:
    from cards.runtime import Card
    from core.game_state import GameState


def _ctx(kind, gs, card, **payload):
    return kind(gs, card, **payload)


def fire(gs: "GameState", subject: "Card", event: str, context_type=actions.Context, **payload) -> int:
    """Dispatch one timing window at one card. Returns how many effects ran.

    The subject is named ``subject`` rather than ``card`` because several
    payloads carry their own ``card`` field (the mover, in movement windows).
    """
    return gs.effects.dispatch(gs, event, [subject], lambda c: _ctx(context_type, gs, c, **payload))


def on_hit(gs: "GameState", card: "Card", target: "Card") -> int:
    """The old ``card.ability(target, gs)``."""
    return fire(gs, card, Event.ON_HIT, actions.HitContext, target=target)


def on_kill(gs: "GameState", card: "Card", victim: "Card") -> int:
    return fire(gs, card, Event.ON_KILL, actions.KillContext, victim=victim)


def on_killed(gs: "GameState", card: "Card", killer: "Card") -> int:
    return fire(gs, card, Event.ON_KILLED, actions.KilledContext, killer=killer)


def damage_taken(gs: "GameState", card: "Card", attacker: "Card", amount: int = 0) -> int:
    """The old ``card.on_attacked_by(attacker, value, gs)``."""
    return fire(gs, card, Event.AFTER_DAMAGE_TAKEN, actions.DamageContext,
                other=attacker, amount=amount)


def damage_dealt(gs: "GameState", card: "Card", victim: "Card", amount: int = 0) -> int:
    """The old ``card.after_damage_calculated(target, value, gs)``."""
    return fire(gs, card, Event.AFTER_DAMAGE_DEALT, actions.DamageContext,
                other=victim, amount=amount)


def moved(gs: "GameState", card: "Card", origin=(0, 0)) -> int:
    """The old ``card.after_movement(x, y, gs)``."""
    return fire(gs, card, Event.MOVED, actions.MoveContext,
                card=card, origin=origin, destination=card.get_position())


def card_moved(gs: "GameState", observer: "Card", mover: "Card", origin=(0, 0)) -> int:
    """The old ``card.on_card_moved(mover, gs)``."""
    return fire(gs, observer, Event.CARD_MOVED, actions.MoveContext,
                card=mover, origin=origin, destination=mover.get_position())


def deployed(gs: "GameState", card: "Card") -> int:
    return fire(gs, card, Event.DEPLOYED)


def attacked(gs: "GameState", card: "Card") -> int:
    return fire(gs, card, Event.ATTACKED, actions.AttackContext, landed=True)


def token_gained(gs: "GameState", card: "Card", resource: str, amount: int = 1) -> int:
    return fire(gs, card, Event.RESOURCE_GAINED, actions.ResourceContext,
                resource_name=resource, seat=card.owner, amount=amount)


def card_drawn(gs: "GameState", card: "Card") -> int:
    return fire(gs, card, Event.CARD_DRAWN)


# --- scenario setup -----------------------------------------------------


def set_damage(card: "Card", value: int) -> None:
    """Force a card's attack to a value, for scenario setup.

    Expressed as a modifier because attack is derived; there is no field to
    assign to any more.
    """
    card.modifiers.remove_where(tags=("test",))
    delta = value - card.damage
    if delta:
        card.modifiers.add(Modifier(
            stat=DAMAGE, op=Op.ADD, value=delta, layer=Layer.COUNTER,
            tags=frozenset({"test"}),
        ))


def set_max_health(card: "Card", value: int) -> None:
    delta = value - card.max_health
    if delta:
        card.modifiers.add(Modifier(
            stat=MAX_HEALTH, op=Op.ADD, value=delta, layer=Layer.COUNTER,
            tags=frozenset({"test"}),
        ))


def silence(card: "Card", on: bool = True) -> None:
    """The old ``card.nullify = True``."""
    if on:
        card.statuses.add(NULLIFIED)
    else:
        card.statuses.discard(NULLIFIED)


def set_bonus(card: "Card", value: int) -> None:
    """Force the per-frame attack-bonus snapshot, for scenario setup."""
    card._bonus_snapshot = value


def drawbacks_off(card: "Card", gs: "GameState") -> bool:
    """Whether this card's drawback-tagged effects are currently suppressed.

    Replaces Brown's old ``effects_off()`` flag: suppression is now a property
    of the board (a raging friendly SP), not a field on the card.
    """
    for effect in card.definition.effects:
        if "drawback" in effect.tags:
            return gs.effects.is_suppressed(card, effect, gs)
    return False


def rage_ally(gs: "GameState", card: "Card", on: bool = True):
    """Add or remove a raging friendly Brown SP, which is what switches a
    giant's drawbacks off."""
    from cards.defs import CARD_DEFS
    from cards.statuses import RAGING
    board = gs.get_player_cards(card.owner)
    existing = [c for c in board if c.job_and_color == "SPBR" and c is not card]
    if not on:
        for sp in existing:
            sp.statuses.discard(RAGING)
        return None
    if existing:
        existing[0].statuses.add(RAGING)
        return existing[0]
    free = [pos for pos, b in gs.board_dict.items() if not b.occupy]
    x, y = free[-1] if free else (3, 3)
    sp = CARD_DEFS["SPBR"](card.owner, x, y)
    sp.statuses.add(RAGING)
    sp.bind(gs)
    gs.board_dict[x, y].occupy = True
    board.append(sp)
    return sp
