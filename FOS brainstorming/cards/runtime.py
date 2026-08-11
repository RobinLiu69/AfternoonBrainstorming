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

"""The card on the board.

One concrete class, never subclassed. Everything that used to be expressed by
overriding a method is now an :class:`~cards.effects.Effect` on the card's
:class:`~cards.defs.CardDef`, which is what makes abilities inspectable and
switchable at runtime.

Stats are derived rather than stored, so the only mutable combat state here is
current health, armour and a set of named statuses. Per-card bespoke state goes
in ``vars``, which serialises generically — no card ever needs its own
``to_dict``.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterable, Iterator

from cards import targeting
from cards.defs import CardDef
from cards.events import Event
from cards.stats import (
    ATTACK_COST, DAMAGE, MAX_HEALTH, SCORE, Layer, Modifier, ModifierBox, Op, fold,
)
from cards.statuses import NULLIFIED, clears_on_turn_end, is_highlight
from shared.combat_event import CombatEvent
from shared.setting import JOB_DICTIONARY
from shared.stat_type import StatType

if TYPE_CHECKING:
    from core.game_state import GameState


_instance_counter: int = 0
_instance_counter_lock = threading.Lock()


def _next_instance_id() -> tuple[str, int]:
    global _instance_counter
    with _instance_counter_lock:
        _instance_counter += 1
        return f"c{_instance_counter}", _instance_counter


def reset_instance_counter() -> None:
    global _instance_counter
    with _instance_counter_lock:
        _instance_counter = 0


@dataclass
class CardRenderData:
    instance_id: str
    job_and_color: str
    job: str
    color: tuple[int, int, int]
    board_x: int
    board_y: int
    health: int
    max_health: int
    damage: int
    original_damage: int
    armor: int
    extra_damage: int
    numbness: bool
    moving: bool
    mouse_selected: bool
    anger: bool
    been_targeted: bool
    owner: str
    shape_type: str
    shape_points: tuple
    nullify: bool

    use_sprite: bool = True
    sprite_key: str = ""
    sprite_alpha: int = 255
    render_shape: bool = True
    show_stats: bool = True


_SHAPES: dict[str, tuple[tuple[float, float], ...]] = {
    "ADC": ((0.5, 0.3), (0.25, 0.7), (0.75, 0.7)),
    "AP": ((0.5, 0.5),),
    "HF": ((0.4, 0.4), (0.6, 0.4), (0.75, 0.65), (0.25, 0.65)),
    "LF": ((0.5, 0.3), (0.36, 0.42), (0.4775, 0.55), (0.36, 0.68),
           (0.5, 0.8), (0.64, 0.68), (0.5225, 0.55), (0.64, 0.42)),
    "ASS": ((0.5, 0.4), (0.2, 0.65), (0.5, 0.5), (0.8, 0.65)),
    "APT": ((0.4, 0.3), (0.25, 0.5), (0.4, 0.7), (0.6, 0.7), (0.75, 0.5), (0.6, 0.3)),
    "SP": ((0.375, 0.3), (0.25, 0.45), (0.5, 0.75), (0.75, 0.45), (0.625, 0.3)),
    "TANK": ((0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25)),
    "CUBE": ((0.45, 0.45), (0.45, 0.55), (0.55, 0.55), (0.55, 0.45)),
    "LUCKYBLOCK": ((0.4, 0.4), (0.4, 0.6), (0.6, 0.6), (0.6, 0.4)),
    "MOVE": ((-10, -10), (-10, -10)),
    "HEAL": ((-10, -10), (-10, -10)),
}


class Card:
    """A single copy of a card, in play."""

    def __init__(
        self,
        definition: CardDef,
        *,
        owner: str,
        board_x: int,
        board_y: int,
        variant: str = "",
        **extra: Any,
    ) -> None:
        self.definition = definition
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y

        self.vars: dict[str, Any] = dict(extra)
        if variant:
            self.vars["variant"] = variant

        base_health, _ = definition.stats_for(self.variant)
        self.health: int = base_health
        self.display_health: int = base_health
        self.armor: int = 0

        self.modifiers = ModifierBox()
        self.statuses: set[str] = set()
        self.hit_cards: list["Card"] = []

        self.numbness: bool = definition.starts_numb and owner != "display"
        self.moving: bool = False
        self.mouse_selected: bool = False
        self.been_targeted: bool = False
        self.pending_death: bool = False

        self.instance_id, self.seq = _next_instance_id()
        self._gs: "GameState | None" = None
        self._bonus_snapshot: int | None = None

    # -- identity -------------------------------------------------------

    @property
    def variant(self) -> str:
        # ``upgrade=True`` is how Player.play_card and the tests ask for Cyan's
        # upgraded printing; it names the variant of the same definition.
        if self.vars.get("upgrade"):
            return "upgrade"
        return self.vars.get("variant", "")

    @property
    def job_and_color(self) -> str:
        return self.definition.name

    @property
    def job(self) -> str:
        return self.definition.job

    @property
    def color_name(self) -> str:
        return self.definition.color_name

    @property
    def color(self) -> tuple[int, int, int]:
        r, g, b = JOB_DICTIONARY["RGB_colors"][self.definition.color_name]
        return (r, g, b)

    @property
    def text_color(self) -> tuple[int, int, int]:
        return self.color

    def get_uid(self) -> str:
        return f"{self.owner}_{self.job_and_color}"

    def get_position(self) -> tuple[int, int]:
        return self.board_x, self.board_y

    def is_same_location(self, other: "Card") -> bool:
        return self.board_x == other.board_x and self.board_y == other.board_y

    def bind(self, game_state: "GameState") -> None:
        """Attach the game a card is playing in, so its auras can resolve."""
        self._gs = game_state

    def __repr__(self) -> str:
        return f"<{self.job_and_color} {self.owner} ({self.board_x},{self.board_y}) hp={self.health}>"

    # -- derived stats --------------------------------------------------

    @property
    def _base_health(self) -> int:
        return self.definition.stats_for(self.variant)[0]

    @property
    def _base_damage(self) -> int:
        return self.definition.stats_for(self.variant)[1]

    def _counters(self) -> list[Modifier]:
        """Permanent modifiers earned by resolving abilities."""
        return [m for m in self.modifiers.items if m.layer is Layer.COUNTER]

    def _transient(self) -> list[Modifier]:
        """Everything that is not a permanent counter: static effects of this
        card, plus stored modifiers that were granted for a limited time."""
        stored = [m for m in self.modifiers.items if m.layer is not Layer.COUNTER]
        if self._gs is None:
            return stored
        return stored + self._gs.effects.aura_modifiers(self, self._gs)

    def _all_modifiers(self) -> list[Modifier]:
        return self._counters() + self._transient()

    @property
    def damage(self) -> int:
        """Printed attack plus permanent counters. Temporary and aura bonuses
        are reported separately as ``extra_damage`` so the UI keeps showing the
        two apart, exactly as it did before."""
        return max(0, fold(self._base_damage, self._counters(), DAMAGE))

    @property
    def live_extra_damage(self) -> int:
        """Aura and temporary attack bonuses, recomputed from current state."""
        extras = self._transient()
        if not extras:
            return 0
        base = self.damage
        return max(0, fold(base, extras, DAMAGE) - base)

    @property
    def extra_damage(self) -> int:
        """Attack bonus as of the last upkeep pass.

        Deliberately a snapshot rather than a live read. The old system stored
        this in a field that ``on_update`` refreshed once per frame, so it held
        steady for the whole of a player action: DarkGreen HF keeps its
        low-health bonus across every target of one attack even though hitting
        the first target heals it back over the threshold. Reading it live
        instead would silently rebalance several cards, so the staleness is
        preserved — but it now lives here, once, instead of in six different
        ``on_update`` overrides.

        Use ``live_extra_damage`` when the current value is what you want.
        """
        if self._bonus_snapshot is None:
            return self.live_extra_damage
        return self._bonus_snapshot

    def refresh_bonus(self) -> None:
        """Take the per-frame attack-bonus snapshot. Called by GameState.update."""
        self._bonus_snapshot = self.live_extra_damage

    @property
    def attack_power(self) -> int:
        return self.damage + self.extra_damage

    @property
    def original_damage(self) -> int:
        return self._base_damage

    @property
    def max_health(self) -> int:
        return max(1, fold(self._base_health, self._all_modifiers(), MAX_HEALTH))

    @property
    def attack_types(self) -> str:
        return self.vars.get("pattern", self.definition.pattern)

    @property
    def anger(self) -> bool:
        """Kept for the renderer: true when any highlighted status is active."""
        return any(is_highlight(name) for name in self.statuses)

    @property
    def nullify(self) -> bool:
        return NULLIFIED in self.statuses

    @property
    def movable(self) -> bool:
        return self.vars.get("movable", self.definition.movable)

    @property
    def attack_uses(self) -> int:
        return max(1, fold(1, self._all_modifiers(), ATTACK_COST))

    def attack_cost(self, game_state: "GameState") -> int:
        return self.attack_uses

    def score_value(self) -> int:
        """Points this card is worth right now. A pure query — the turn-end
        cleanup that used to be tangled into the same method is separate."""
        if not self.definition.scores or self.numbness:
            return 0
        return max(0, fold(1, self._all_modifiers(), SCORE))

    def add_permanent(
        self,
        stat: str,
        amount: float,
        *,
        tags: Iterable[str] = ("scenario",),
    ) -> None:
        """Attach a permanent modifier from outside the ability system.

        For scenario scaling — campaign bosses, endless-mode mutators — which
        buff cards without being an ability of any card.
        """
        self.modifiers.add(Modifier(
            stat=stat, op=Op.ADD, value=amount,
            layer=Layer.COUNTER, tags=frozenset(tags),
        ))

    # -- health ---------------------------------------------------------

    def heal(self, value: int, game_state: "GameState") -> bool:
        if self.health + value <= self.max_health:
            self.health += value
        else:
            overflow = self.health + value - self.max_health
            self.armor += overflow // 2
            self.health = self.max_health
        self.display_health = self.health
        game_state.game_logger.log_heal(
            self.get_uid(), self.get_position(), value, self.health, self.armor
        )
        return True

    def check_lethal(self, game_state: "GameState", killer: "Card | None" = None) -> bool:
        """Whether this card actually dies. Idempotent: it only reads statuses,
        so recycle_cards may ask repeatedly."""
        from cards.actions import LethalEvent
        if self.nullify:
            return True
        event = LethalEvent(card=self, killer=killer)
        game_state.effects.replace(game_state, Event.LETHAL, event, [self])
        return not event.prevented

    def can_be_killed(self, game_state: "GameState") -> bool:
        return self.check_lethal(game_state)

    # -- lifecycle ------------------------------------------------------

    def deploy(self, game_state: "GameState") -> None:
        from cards.actions import Context
        self.bind(game_state)
        game_state.effects.dispatch(
            game_state, Event.DEPLOYED, [self],
            lambda card: Context(game_state, card),
        )

    def update(self, game_state: "GameState") -> None:
        """Per-frame hook.

        Derived stats no longer need a recomputation pass — they are folded on
        read — so this only refreshes the game reference and, for the few cards
        that ask for it, dispatches upkeep.
        """
        self.bind(game_state)
        self.refresh_bonus()
        for companion in self.companions:
            companion.bind(game_state)
        if self.definition.handles(Event.TICK):
            from cards.actions import Context
            game_state.effects.dispatch(
                game_state, Event.TICK, [self],
                lambda card: Context(game_state, card),
            )

    def refresh(self, game_state: "GameState") -> None:
        from cards.actions import TurnContext
        self.moving = False
        game_state.effects.dispatch(
            game_state, Event.TURN_START, [self],
            lambda card: TurnContext(game_state, card, seat=card.owner),
        )

    def settle(self, game_state: "GameState") -> None:
        from cards.actions import TurnContext
        self.moving = False

        points = self.score_value()
        game_state.game_statistics.increment(StatType.SCORED, self.get_uid(), points)
        if self.owner == "player1":
            game_state.score -= points
        elif self.owner == "player2":
            game_state.score += points

        game_state.effects.dispatch(
            game_state, Event.TURN_END, [self],
            lambda card: TurnContext(game_state, card, seat=card.owner),
        )

        self.numbness = False
        for name in [s for s in self.statuses if clears_on_turn_end(s)]:
            self.statuses.discard(name)

    def on_death(self, game_state: "GameState") -> bool:
        from cards.actions import Context
        game_state.effects.dispatch(
            game_state, Event.ON_DEATH, [self],
            lambda card: Context(game_state, card),
        )
        return False

    # -- movement -------------------------------------------------------

    def move(self, board_x: int, board_y: int, game_state: "GameState") -> bool:
        from cards.actions import MoveContext
        if not self.movable:
            return False
        if not game_state.board_config.is_valid_position(board_x, board_y):
            return False
        if game_state.board_dict[board_x, board_y].occupy:
            return False

        dx, dy = abs(self.board_x - board_x), abs(self.board_y - board_y)
        adjacent = (dx, dy) in ((0, 1), (1, 0), (1, 1))
        if not (adjacent and self.moving):
            return False

        origin = self.get_position()
        game_state.game_logger.log_card_moved(
            self.owner, self.job_and_color, origin, (board_x, board_y)
        )
        game_state.game_statistics.increment(StatType.MOVE, self.get_uid(), 1)

        game_state.board_dict[self.board_x, self.board_y].occupy = False
        self.board_x, self.board_y = board_x, board_y
        game_state.board_dict[board_x, board_y].occupy = True
        self.moving = False

        game_state.pending_combat_events.append(CombatEvent(
            kind="move", board_x=board_x, board_y=board_y,
            target_x=origin[0], target_y=origin[1],
        ))

        def context(card: "Card") -> MoveContext:
            return MoveContext(
                game_state, card, card=self, origin=origin, destination=(board_x, board_y),
            )

        game_state.effects.dispatch(game_state, Event.MOVED, [self], context)
        game_state.effects.dispatch(
            game_state, Event.CARD_MOVED, game_state.get_all_cards(), context
        )
        return True

    # -- combat ---------------------------------------------------------

    def attack(self, game_state: "GameState") -> bool:
        """A player-initiated attack. Abilities that grant extra attacks go
        through ctx.attack_with, which does not re-enter this method."""
        from cards.actions import AttackContext, perform_attack

        declaration = AttackContext(game_state, self)
        game_state.effects.replace(game_state, Event.ATTACK_DECLARED, declaration, [self])
        if declaration.cancelled:
            return False

        outcome = AttackContext(
            game_state, self, landed=perform_attack(game_state, self, self.attack_types)
        )
        game_state.effects.dispatch(
            game_state,
            Event.ATTACKED if outcome.landed else Event.ATTACK_MISSED,
            [self],
            lambda card: outcome,
        )

        self.hit_cards.clear()
        return outcome.landed

    def damage_calculate(
        self,
        value: int,
        attacker: "Card",
        game_state: "GameState",
        ability: bool = True,
        anim_delay: float = 0.0,
    ) -> bool:
        """Kept for callers outside the card system (Judge, endless events)."""
        from cards.actions import resolve_damage
        return resolve_damage(
            game_state, attacker, self, value,
            allow_abilities=ability, anim_delay=anim_delay,
        )

    def detection(
        self,
        attack_types: str,
        target_card_list: Iterable["Card"],
        game_state: "GameState",
    ) -> Iterator["Card"]:
        return targeting.find_targets(
            attack_types, self.get_position(), target_card_list, game_state
        )

    def attack_areas(
        self,
        board_x: int,
        board_y: int,
        attack_types: str | None,
        game_state: "GameState",
    ) -> Iterator[tuple[int, int]]:
        if not attack_types:
            return iter(())
        return targeting.pattern_cells(attack_types, (board_x, board_y), self.owner, game_state)

    def attack_area_display(self, game_state: "GameState") -> Iterable[tuple[int, int]]:
        yield from self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state)
        for companion in self.companions:
            yield from companion.attack_areas(
                companion.board_x, companion.board_y, companion.attack_types, game_state
            )

    def attack_order_actors(self, game_state: "GameState") -> Iterable[tuple["Card", list["Card"]]]:
        enemies = [c for c in game_state.get_side_cards(self.owner, True) if c.health > 0]
        yield (self, enemies)
        if self.companions:
            targetable = [c for c in enemies if c.job_and_color != "SHADOW"]
            for companion in self.companions:
                yield (companion, targetable)

    # -- companions (Fuchsia shadows) -----------------------------------

    @property
    def companions(self) -> list["Card"]:
        """Linked sub-entities that render and attack with this card but are not
        themselves on the board."""
        return self.vars.get("companions", [])

    # -- rendering ------------------------------------------------------

    def shape_points(self) -> tuple:
        return _SHAPES.get(self.job, ((0, 0), (0, 0)))

    def get_render_data(self) -> list[CardRenderData]:
        entries = [CardRenderData(
            instance_id=self.instance_id,
            job_and_color=self.job_and_color,
            job=self.job,
            color=self.color,
            board_x=self.board_x,
            board_y=self.board_y,
            health=self.display_health,
            max_health=self.max_health,
            damage=self.damage,
            original_damage=self.original_damage,
            armor=self.armor,
            extra_damage=self.extra_damage,
            numbness=self.numbness,
            moving=self.moving,
            mouse_selected=self.mouse_selected,
            anger=self.anger,
            been_targeted=self.been_targeted,
            owner=self.owner,
            shape_type="circle" if self.job == "AP" else "polygon",
            shape_points=self.shape_points(),
            nullify=self.nullify,
            use_sprite=False,
            sprite_key=self.job_and_color,
            sprite_alpha=255,
            render_shape=self.job != "CUBES",
        )]
        for companion in self.companions:
            entries += companion.get_render_data()
        return entries

    # -- serialisation --------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "seq": self.seq,
            "owner": self.owner,
            "job_and_color": self.job_and_color,
            "health": self.health,
            "display_health": self.display_health,
            "armor": self.armor,
            "board_x": self.board_x,
            "board_y": self.board_y,
            "numbness": self.numbness,
            "moving": self.moving,
            "mouse_selected": self.mouse_selected,
            "been_targeted": self.been_targeted,
            "pending_death": self.pending_death,
            "statuses": sorted(self.statuses),
            "modifiers": self.modifiers.to_list(),
            "vars": self._vars_to_dict(),
        }

    def _vars_to_dict(self) -> dict:
        out: dict[str, Any] = {}
        for key, value in self.vars.items():
            if key == "companions":
                out[key] = [c.to_dict() for c in value]
            elif key.startswith("_"):
                continue  # transient scratch state
            else:
                out[key] = value
        return out

    def apply_dict(self, data: dict) -> None:
        from cards.factory import CardFactory
        self.owner = data["owner"]
        self.health = data["health"]
        self.display_health = data.get("display_health", data["health"])
        self.armor = data["armor"]
        self.board_x = data["board_x"]
        self.board_y = data["board_y"]
        self.numbness = data["numbness"]
        self.moving = data["moving"]
        self.mouse_selected = data["mouse_selected"]
        self.been_targeted = data["been_targeted"]
        self.pending_death = data["pending_death"]
        self.statuses = set(data.get("statuses", ()))
        self.modifiers = ModifierBox.from_list(data.get("modifiers", []))

        incoming = dict(data.get("vars", {}))
        companions = incoming.pop("companions", None)
        self.vars = incoming
        if companions is not None:
            rebuilt = []
            for blob in companions:
                companion = CardFactory.from_dict(blob)
                # The link back to the parent is transient, so it is re-established
                # here rather than serialised as a dangling id.
                companion.vars["_parent"] = self
                rebuilt.append(companion)
            self.vars["companions"] = rebuilt

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        from cards.defs import CARD_DEFS
        definition = CARD_DEFS[data["job_and_color"]]
        card = cls(
            definition,
            owner=data["owner"],
            board_x=data["board_x"],
            board_y=data["board_y"],
        )
        card.instance_id = data["instance_id"]
        card.seq = data.get("seq", card.seq)
        card.apply_dict(data)
        return card
