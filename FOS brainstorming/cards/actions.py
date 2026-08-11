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

"""What an ability is allowed to do, and the damage pipeline.

Effects never touch game state directly. They issue commands through the
:class:`Context` they are handed, which keeps every mutation in one auditable
place — logging, animation events and statistics are emitted here rather than
being re-implemented (and forgotten) in individual abilities.

The commands are deliberately shaped like queued actions even though they
currently execute inline, so introducing a real action queue later does not
touch a single card definition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Sequence

from cards import targeting
from cards.events import Event
from cards.stats import Layer, Modifier, Op
from cards.statuses import NULLIFIED
from shared.combat_event import CombatEvent
from shared.setting import ANIM_LUNGE_STEP
from shared.stat_type import StatType

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.runtime import Card


# --- pipeline payloads ---------------------------------------------------


@dataclass
class DamageEvent:
    """Mutable record passed through the damage replacement windows."""

    attacker: "Card"
    victim: "Card"
    amount: int
    cancelled: bool = False
    allow_abilities: bool = True
    anim_delay: float = 0.0

    def reduce_by(self, value: int) -> None:
        self.amount = max(0, self.amount - value)

    def increase_by(self, value: int) -> None:
        self.amount += value

    def cancel(self) -> None:
        self.cancelled = True


@dataclass
class DeployCost:
    """Payload for the deploy-cost window. Cancel to refuse the placement."""

    card: "Card"
    gs: "GameState"
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


@dataclass
class LethalEvent:
    """Fired when a card reaches zero health; ``prevented`` keeps it alive."""

    card: "Card"
    killer: "Card | None" = None
    prevented: bool = False

    def prevent(self) -> None:
        self.prevented = True


# --- contexts ------------------------------------------------------------


@dataclass
class Context:
    """The command surface handed to every triggered effect."""

    gs: "GameState"
    source: "Card"

    # -- queries --------------------------------------------------------

    @property
    def rng(self):
        return self.gs.rng

    @property
    def owner(self) -> str:
        return self.source.owner

    def settings(self, key: str, default: Any = None) -> Any:
        """Read a tuning value from card_setting.json for this card."""
        return self.source.definition.settings.get(key, default)

    def allies(self, *, living: bool = True) -> list["Card"]:
        cards = self.gs.get_player_cards(self.source.owner)
        return [c for c in cards if c.health > 0] if living else list(cards)

    def enemies(self, *, living: bool = True, include_neutral: bool = True) -> list["Card"]:
        cards = (self.gs.get_side_cards(self.source.owner, True) if include_neutral
                 else self.gs.get_opponent_cards(self.source.owner))
        return [c for c in cards if c.health > 0] if living else list(cards)

    def everyone(self) -> list["Card"]:
        return self.gs.get_all_cards()

    def targets(
        self,
        pattern: str,
        candidates: Iterable["Card"] | None = None,
        origin: tuple[int, int] | None = None,
    ) -> list["Card"]:
        """Resolve a targeting pattern from this card's position."""
        pool = self.enemies() if candidates is None else candidates
        return list(targeting.find_targets(
            pattern, origin or self.source.get_position(), pool, self.gs
        ))

    def nearest_ally(self, *, exclude_self: bool = True) -> list["Card"]:
        pool = [c for c in self.allies() if not exclude_self or c is not self.source]
        return self.targets("nearest", pool)

    def count(self, predicate) -> int:
        return self.gs.count_cards(predicate)

    # -- combat ---------------------------------------------------------

    def deal_damage(
        self,
        target: "Card",
        amount: int,
        *,
        allow_abilities: bool = True,
        attacker: "Card | None" = None,
        anim_delay: float = 0.0,
    ) -> bool:
        return resolve_damage(
            self.gs, attacker or self.source, target, amount,
            allow_abilities=allow_abilities, anim_delay=anim_delay,
        )

    def chip(self, target: "Card", amount: int) -> bool:
        """Damage dealt by the game itself rather than by an attacker, so it
        triggers no on-hit abilities."""
        return resolve_damage(self.gs, self.gs.judge, target, amount, allow_abilities=False)

    def cancel_queued_attacks(self) -> None:
        """Drop attacks queued by this resolution. Used by effects that fire a
        burst of damage and must not also set off a chain of follow-up attacks."""
        self.gs.pending_attacks.clear()

    def strike(self, targets: Iterable["Card"], amount: int, **kwargs) -> int:
        landed = 0
        for target in list(targets):
            if self.deal_damage(target, amount, **kwargs):
                landed += 1
        return landed

    def attack_with(
        self,
        card: "Card | None" = None,
        *,
        pattern: str | None = None,
        targets: Sequence["Card"] = (),
        ignore_numb: bool = False,
        allow_abilities: bool = True,
    ) -> None:
        """Queue an extra attack. Queued rather than recursive, so an ability
        that grants an attack cannot re-enter the attack it was fired from."""
        from shared.attack_request import AttackRequest
        self.gs.pending_attacks.append(AttackRequest(
            attacker=card or self.source,
            attack_types=pattern,
            custom_target_tuple=tuple(targets),
            ignore_numbness=ignore_numb,
            use_ability=allow_abilities,
        ))

    def attack_now(
        self,
        card: "Card | None" = None,
        *,
        pattern: str | None = None,
        targets: Sequence["Card"] = (),
        ignore_numb: bool = False,
        allow_abilities: bool = True,
    ) -> bool:
        actor = card or self.source
        return perform_attack(
            self.gs, actor,
            pattern if pattern is not None else actor.attack_types,
            targets=targets, ignore_numb=ignore_numb, allow_abilities=allow_abilities,
        )

    # -- stats and statuses ---------------------------------------------

    def grant(
        self,
        target: "Card",
        stat: str,
        amount: float,
        *,
        op: Op = Op.ADD,
        tags: Iterable[str] = ("buff",),
        permanent: bool = True,
    ) -> Modifier:
        """Attach a modifier. This is the only way to change a derived stat."""
        modifier = Modifier(
            stat=stat, op=op, value=amount,
            layer=Layer.COUNTER if permanent else Layer.AURA,
            tags=frozenset(tags),
            source_iid=self.source.instance_id,
            seq=self.gs.next_modifier_seq(),
        )
        target.modifiers.add(modifier)
        self.gs.effects.dispatch(
            self.gs, Event.MODIFIER_GRANTED,
            self.gs.get_both_player_cards(),
            lambda card: ModifierContext(self.gs, card, target=target, modifier=modifier),
        )
        return modifier

    def buff(
        self,
        target: "Card",
        *,
        damage: int = 0,
        armor: int = 0,
        max_health: int = 0,
        tags: Iterable[str] = ("buff",),
        permanent: bool = True,
    ) -> None:
        """Apply a buff as one act and announce it.

        Going through a single command means abilities that react to *being
        buffed* need one listener rather than every buffing card having to know
        about them.
        """
        from cards.stats import DAMAGE, MAX_HEALTH
        tags = frozenset(tags)
        if damage:
            self.grant(target, DAMAGE, damage, tags=tags, permanent=permanent)
        if max_health:
            self.grant(target, MAX_HEALTH, max_health, tags=tags, permanent=permanent)
        if armor:
            self.add_armor(target, armor)

        payload = BuffContext(
            self.gs, self.source, target=target,
            damage=damage, armor=armor, max_health=max_health, tags=tags,
        )
        self.gs.effects.dispatch(
            self.gs, Event.BUFF_APPLIED, self.gs.get_both_player_cards(),
            lambda card: payload,
        )

    def strip(self, target: "Card", *, tags: Iterable[str] = ("buff",), source_iid: str | None = None) -> None:
        """Remove modifiers by tag or origin — a precise silence, rather than
        resetting the card to its printed stats."""
        target.modifiers.remove_where(tags=tags, source_iid=source_iid)

    def add_armor(self, target: "Card", amount: int) -> None:
        target.armor = max(0, target.armor + amount)

    def heal(self, target: "Card", amount: int) -> bool:
        return target.heal(amount, self.gs)

    def set_status(self, target: "Card", status: str, on: bool = True) -> None:
        if on:
            target.statuses.add(status)
        else:
            target.statuses.discard(status)

    def has_status(self, target: "Card", status: str) -> bool:
        return status in target.statuses

    def numb(self, target: "Card", value: bool = True) -> None:
        target.numbness = value

    def silence(self, target: "Card") -> None:
        """Suppress every effect on a card and strip what its abilities gave it."""
        self.set_status(target, NULLIFIED, True)
        self.strip(target, tags=("buff",))
        target.armor = 0

    def arm_move(self, target: "Card | None" = None) -> None:
        (target or self.source).moving = True

    # -- economy --------------------------------------------------------

    def gain(self, resource: str, amount: int, *, seat: str | None = None) -> None:
        self.gs.gain_resource(resource, seat or self.source.owner, amount, source=self.source)

    def spend(self, resource: str, amount: int, *, seat: str | None = None) -> bool:
        return self.gs.spend_resource(resource, seat or self.source.owner, amount)

    def resource(self, resource: str, *, seat: str | None = None) -> int:
        return self.gs.resource(resource, seat or self.source.owner)

    def draw(self, count: int = 1, *, seat: str | None = None) -> None:
        self.gs.card_to_draw[seat or self.source.owner] += count

    def skip_next_draw(self, *, seat: str | None = None) -> None:
        self.gs.skip_turn_draw[seat or self.source.owner] = True

    def add_to_hand(self, card_name: str, *, seat: str | None = None) -> None:
        self.gs.get_player(seat or self.source.owner).hand.append(card_name)

    def add_score(self, amount: int, *, seat: str | None = None) -> None:
        """Positive means good for ``seat``; the sign convention on
        GameState.score is handled here so abilities never get it backwards."""
        who = seat or self.source.owner
        self.gs.score += -amount if who == "player1" else amount

    def spawn(self, card_name: str, x: int, y: int, *, owner: str = "neutral") -> bool:
        from cards.factory import spawn_card
        board = (self.gs.neutral.on_board if owner == "neutral"
                 else self.gs.get_player(owner).on_board)
        return spawn_card(x, y, card_name, owner, board, self.gs)

    def free_cells(self, *, exclude: Iterable[tuple[int, int]] = ()) -> list[tuple[int, int]]:
        skip = set(exclude)
        return [pos for pos, block in self.gs.board_dict.items()
                if not block.occupy and pos not in skip]

    # -- misc -----------------------------------------------------------

    def log(self, message: str, **fields) -> None:
        from utils.logger import LogCategory
        self.gs.game_logger.info(message, LogCategory.SPECIAL_ACTION, **fields)


@dataclass
class AttackContext(Context):
    """Payload for the attack action windows.

    Doubles as a replacement payload (``cancelled``) and a trigger context
    (``landed``), so an effect can veto an attack or rescue one that found no
    target.
    """

    landed: bool = False
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True

    def salvage(self) -> None:
        """Report that this attack did something after all."""
        self.landed = True


@dataclass
class HitContext(Context):
    target: "Card" = None  # type: ignore[assignment]


@dataclass
class DamageContext(Context):
    other: "Card" = None  # type: ignore[assignment]
    amount: int = 0


@dataclass
class KillContext(Context):
    victim: "Card" = None  # type: ignore[assignment]


@dataclass
class KilledContext(Context):
    killer: "Card" = None  # type: ignore[assignment]


@dataclass
class MoveContext(Context):
    card: "Card" = None  # type: ignore[assignment]
    origin: tuple[int, int] = (0, 0)
    destination: tuple[int, int] = (0, 0)


@dataclass
class ResourceContext(Context):
    # Named resource_name, not resource, so it does not shadow Context.resource().
    resource_name: str = ""
    seat: str = ""
    amount: int = 0
    granter: "Card | None" = None


@dataclass
class ModifierContext(Context):
    target: "Card" = None  # type: ignore[assignment]
    modifier: Modifier | None = None


@dataclass
class BuffContext(Context):
    target: "Card" = None  # type: ignore[assignment]
    damage: int = 0
    armor: int = 0
    max_health: int = 0
    tags: frozenset[str] = frozenset()


@dataclass
class TurnContext(Context):
    seat: str = ""


# --- the damage pipeline -------------------------------------------------


def resolve_damage(
    game_state: "GameState",
    attacker: "Card",
    victim: "Card",
    amount: int,
    *,
    allow_abilities: bool = True,
    anim_delay: float = 0.0,
) -> bool:
    """Apply one instance of damage. Returns whether it landed.

    The window order is fixed and documented here rather than being implied by
    the shape of a 60-line method:

    1. ``DAMAGE_PREVENTION`` — may cancel outright
    2. ``ON_HIT`` — the attacker's on-hit abilities
    3. ``DAMAGE_MODIFY`` — attacker bonuses, victim resistances, board effects
    4. apply to armour then health
    5. ``AFTER_DAMAGE_TAKEN`` / ``AFTER_DAMAGE_DEALT``
    6. ``LETHAL`` if the victim reached zero
    """
    if victim.health <= 0:
        return False

    attacker.hit_cards.append(victim)
    engine = game_state.effects
    everyone = game_state.get_all_cards()

    event = DamageEvent(
        attacker=attacker, victim=victim, amount=amount,
        allow_abilities=allow_abilities, anim_delay=anim_delay,
    )

    engine.replace(game_state, Event.DAMAGE_PREVENTION, event, everyone)
    if event.cancelled:
        return False

    if allow_abilities:
        ran = engine.dispatch(
            game_state, Event.ON_HIT, [attacker],
            lambda card: HitContext(game_state, card, target=victim),
        )
        if ran:
            game_state.game_statistics.increment(StatType.ABILITY, attacker.get_uid(), 1)

    # Aura-granted attack power. Suppressed sources contribute nothing, so a
    # silenced attacker loses its bonuses instead of keeping a stale integer.
    event.increase_by(attacker.extra_damage)
    engine.replace(game_state, Event.DAMAGE_MODIFY, event, everyone)

    value = max(0, min(event.amount, victim.armor + victim.health))
    absorbed = min(victim.armor, value)
    victim.armor -= absorbed
    victim.health -= value - absorbed

    game_state.game_statistics.add_damage_dealt(attacker.get_uid(), value)
    game_state.game_statistics.add_damage_taken(victim.get_uid(), value)
    game_state.game_logger.log_attack(
        attacker.get_uid(), attacker.get_position(),
        victim.get_uid(), victim.get_position(), value,
    )
    game_state.pending_combat_events.append(CombatEvent(
        kind="hurt", board_x=victim.board_x, board_y=victim.board_y,
        delay=event.anim_delay, post_health=victim.health,
    ))
    game_state.pending_combat_events.append(CombatEvent(
        kind="float", board_x=victim.board_x, board_y=victim.board_y,
        damage=value, delay=event.anim_delay,
    ))

    engine.dispatch(
        game_state, Event.AFTER_DAMAGE_TAKEN, [victim],
        lambda card: DamageContext(game_state, card, other=attacker, amount=value),
    )

    if victim.health <= 0:
        _resolve_lethal(game_state, victim, attacker, event.anim_delay)

    engine.dispatch(
        game_state, Event.AFTER_DAMAGE_DEALT, [attacker],
        lambda card: DamageContext(game_state, card, other=victim, amount=value),
    )
    return True


def _resolve_lethal(
    game_state: "GameState",
    victim: "Card",
    attacker: "Card",
    anim_delay: float,
) -> None:
    game_state.game_statistics.add_kill(attacker.get_uid())
    game_state.game_statistics.add_death(victim.get_uid())

    game_state.effects.dispatch(
        game_state, Event.ON_KILL, [attacker],
        lambda card: KillContext(game_state, card, victim=victim),
    )
    game_state.effects.dispatch(
        game_state, Event.ON_KILLED, [victim],
        lambda card: KilledContext(game_state, card, killer=attacker),
    )

    if not victim.check_lethal(game_state, attacker):
        return

    victim.pending_death = True
    game_state.pending_combat_events.append(CombatEvent(
        kind="death", board_x=victim.board_x, board_y=victim.board_y, delay=anim_delay,
    ))


# --- the attack pipeline -------------------------------------------------


def perform_attack(
    game_state: "GameState",
    attacker: "Card",
    pattern: str,
    *,
    targets: Sequence["Card"] = (),
    ignore_numb: bool = False,
    allow_abilities: bool = True,
) -> bool:
    """Resolve one attack, then drain anything abilities queued behind it.

    The drain replaces the old ``_attack_draining`` re-entrancy flag: queued
    attacks are a natural consequence of having a queue rather than a guard
    bolted onto recursion.
    """
    outermost = not game_state.attack_draining
    if outermost:
        game_state.attack_draining = True
    try:
        landed = _attack_once(
            game_state, attacker, pattern,
            targets=targets, ignore_numb=ignore_numb, allow_abilities=allow_abilities,
        )
        if outermost:
            while game_state.pending_attacks:
                request = game_state.pending_attacks.popleft()
                actor = request.attacker
                if actor.health <= 0:
                    continue
                queued_pattern = (request.attack_types if request.attack_types is not None
                                  else actor.attack_types)
                if not queued_pattern:
                    continue
                _attack_once(
                    game_state, actor, queued_pattern,
                    targets=request.custom_target_tuple,
                    ignore_numb=request.ignore_numbness,
                    allow_abilities=request.use_ability,
                )
                actor.hit_cards.clear()
        return landed
    finally:
        if outermost:
            game_state.attack_draining = False


def _attack_once(
    game_state: "GameState",
    attacker: "Card",
    pattern: str,
    *,
    targets: Sequence["Card"] = (),
    ignore_numb: bool = False,
    allow_abilities: bool = True,
) -> bool:
    if not ignore_numb and (attacker.numbness or not pattern):
        return False

    if targets:
        chosen: tuple["Card", ...] = tuple(targets)
    else:
        enemies = [c for c in game_state.get_side_cards(attacker.owner, True) if c.health > 0]
        chosen = tuple(targeting.find_targets(
            pattern, attacker.get_position(), enemies, game_state
        ))

    if not chosen:
        return False

    base_delay = game_state.attack_anim_cursor
    for index, target in enumerate(chosen):
        strike_delay = base_delay + index * ANIM_LUNGE_STEP
        game_state.pending_combat_events.append(CombatEvent(
            kind="attack",
            board_x=attacker.board_x, board_y=attacker.board_y,
            target_x=target.board_x, target_y=target.board_y,
            delay=strike_delay,
        ))
        game_state.game_logger.log_launch_attack(attacker.get_uid(), attacker.get_position())
        resolve_damage(
            game_state, attacker, target, attacker.damage,
            allow_abilities=allow_abilities,
            anim_delay=strike_delay + ANIM_LUNGE_STEP * 0.55,
        )
    game_state.attack_anim_cursor = base_delay + len(chosen) * ANIM_LUNGE_STEP
    return True
