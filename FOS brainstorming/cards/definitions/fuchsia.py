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

"""Fuchsia — shadows.

A shadow is a companion *entity*, not an ability: it has a position, it renders,
it threatens squares. It is deliberately not on either player's board, so it
cannot be targeted or scored — it only ever acts as a second origin for its
parent's attacks.

Modelling it as an entity (rather than as state smeared across the parent, as
the old FuchsiaCard base class did) is why this file has no serialisation code:
companions round-trip through the generic ``vars`` mechanism.
"""

from __future__ import annotations

from cards import targeting
from cards.defs import CARD_DEFS, color, neutral
from cards.effects import Priority, aura, on, replaces
from cards.events import Event

fuchsia = color("Fuchsia", "F")

SHADOW = "SHADOW"


@neutral(SHADOW, job=SHADOW, color_name="Fuchsia", health=1, damage=0,
         pattern="", starts_numb=False)
class Shadow:
    """A silent double. All of its behaviour is driven by its parent."""


def spawn_shadow(ctx, parent, x: int, y: int, *, pattern: str | None = None, movable: bool = True):
    shadow = CARD_DEFS[SHADOW](parent.owner, x, y)
    shadow.vars["pattern"] = parent.attack_types if pattern is None else pattern
    shadow.vars["movable"] = movable
    shadow.vars["_parent"] = parent
    shadow.bind(ctx.gs)
    parent.vars.setdefault("companions", []).append(shadow)
    return shadow


def mirror_of(ctx, card) -> tuple[int, int]:
    return ctx.gs.board_config.get_symmetric_pos(card.board_x, card.board_y)


def cast_shadow(ctx, card, **kwargs):
    """The usual opening: a double appears at the mirrored square."""
    if card.owner == "display":
        return None
    x, y = mirror_of(ctx, card)
    return spawn_shadow(ctx, card, x, y, **kwargs)


def shadows_strike(ctx, card, *, opponents_only: bool = False) -> bool:
    """Each shadow attacks from its own square, using its parent's strength."""
    landed = False
    for shadow in list(card.companions):
        pool = (ctx.gs.get_opponent_cards(card.owner) if opponents_only
                else ctx.gs.get_side_cards(card.owner, True))
        living = [c for c in pool if c.health > 0]
        targets = list(targeting.find_targets(
            shadow.attack_types, shadow.get_position(), living, ctx.gs
        ))
        if targets and ctx.attack_now(card, pattern=shadow.attack_types, targets=targets):
            landed = True
    return landed


def salvage_with_shadows(card, ctx) -> None:
    """The body could reach nothing, but a shadow still might.

    Note these helpers are called from per-class handlers rather than being a
    single decorated function shared between definitions: decorating one
    function object once per class would accumulate an effect per class on that
    object, and the last definition would then run it several times.
    """
    if card.numbness:
        return
    if shadows_strike(ctx, card):
        ctx.salvage()


def _numb_the_shadowed(card, ctx) -> None:
    for shadow in card.companions:
        for enemy in ctx.enemies():
            if shadow.is_same_location(enemy):
                ctx.numb(enemy)


def _shadows_track(card, ctx) -> None:
    for shadow in card.companions:
        if shadow.movable:
            shadow.board_x, shadow.board_y = ctx.gs.board_config.get_symmetric_pos(
                card.board_x, card.board_y
            )


@fuchsia("ADC")
class Adc:
    """Body and shadow strike together."""

    @on(Event.DEPLOYED)
    def open(card, ctx):
        cast_shadow(ctx, card)

    @on(Event.MOVED)
    def track(card, ctx):
        _shadows_track(card, ctx)

    @on(Event.ATTACKED)
    def follow_up(card, ctx):
        shadows_strike(ctx, card)

    @on(Event.ATTACK_MISSED)
    def salvage(card, ctx):
        salvage_with_shadows(card, ctx)


@fuchsia("AP")
class Ap:
    """Anything standing in its shadow is numbed."""

    @on(Event.DEPLOYED)
    def open(card, ctx):
        cast_shadow(ctx, card)
        _numb_the_shadowed(card, ctx)

    @on(Event.MOVED)
    def track(card, ctx):
        _shadows_track(card, ctx)

    @on(Event.TURN_START)
    def numb_the_shadowed(card, ctx):
        _numb_the_shadowed(card, ctx)

    @on(Event.ON_HIT)
    def numb_target(card, ctx):
        ctx.numb(ctx.target)


@fuchsia("TANK")
class Tank:
    """Its shadow denies a square outright."""

    @on(Event.DEPLOYED)
    def open(card, ctx):
        cast_shadow(ctx, card)

    @on(Event.MOVED)
    def track(card, ctx):
        _shadows_track(card, ctx)

    @on(Event.TICK)
    def hold_the_square(card, ctx):
        for shadow in card.companions:
            ctx.gs.board_dict[shadow.board_x, shadow.board_y].occupy = True

    @on(Event.ON_DEATH)
    def release_the_square(card, ctx):
        _free_shadow_squares(card, ctx)


@fuchsia("HF")
class Hf:
    """Body and shadow strike together across nine squares."""

    @on(Event.DEPLOYED)
    def open(card, ctx):
        cast_shadow(ctx, card)

    @on(Event.MOVED)
    def track(card, ctx):
        _shadows_track(card, ctx)

    @on(Event.ATTACKED)
    def follow_up(card, ctx):
        shadows_strike(ctx, card)

    @on(Event.ATTACK_MISSED)
    def salvage(card, ctx):
        salvage_with_shadows(card, ctx)


@fuchsia("LF")
class Lf:
    """Whatever both body and shadow reach is struck a third time."""

    @on(Event.DEPLOYED)
    def open(card, ctx):
        cast_shadow(ctx, card, pattern="nearest")

    @on(Event.MOVED)
    def track(card, ctx):
        _shadows_track(card, ctx)

    @on(Event.ATTACKED)
    def converge(card, ctx):
        from shared.setting import ANIM_LUNGE_STEP
        struck_by_body = {c.instance_id for c in card.hit_cards}
        already_hit = len(card.hit_cards)

        shadows_strike(ctx, card, opponents_only=True)

        for target in card.hit_cards[already_hit:]:
            if target.instance_id in struck_by_body and target.health > 0:
                delay = ctx.gs.attack_anim_cursor + ANIM_LUNGE_STEP * 0.55
                ctx.deal_damage(target, card.damage, anim_delay=delay)
                ctx.gs.attack_anim_cursor += ANIM_LUNGE_STEP


@fuchsia("ASS")
class Ass:
    """Leaves a motionless double standing where it kills."""

    @on(Event.ON_KILL)
    def leave_a_double(card, ctx):
        spawn_shadow(ctx, card, ctx.victim.board_x, ctx.victim.board_y, movable=False)

    @on(Event.ON_DEATH)
    def release_squares(card, ctx):
        _free_shadow_squares(card, ctx)

    @on(Event.ATTACKED)
    def follow_up(card, ctx):
        shadows_strike(ctx, card)

    @on(Event.ATTACK_MISSED)
    def salvage(card, ctx):
        salvage_with_shadows(card, ctx)


@fuchsia("APT")
class Apt:
    """Allies standing in its shadow take half damage; it keeps the rest as armour."""

    @on(Event.DEPLOYED)
    def open(card, ctx):
        cast_shadow(ctx, card)

    @on(Event.MOVED)
    def track(card, ctx):
        _shadows_track(card, ctx)

    @replaces(Event.DAMAGE_MODIFY, priority=Priority.NORMAL, when=lambda card, event: (
        card.health > 0
        and event.victim is not card
        and event.victim.owner == card.owner
        and any(s.is_same_location(event.victim) for s in card.companions)
    ))
    def absorb_half(card, event):
        import math
        taken = math.floor(event.amount * 0.5)
        card.armor += taken
        event.amount = math.ceil(event.amount * 0.5)


@fuchsia("SP")
class Sp:
    """Grants the farthest friendly fuchsia card a second, fixed shadow."""

    @on(Event.DEPLOYED)
    def gift_a_double(card, ctx):
        kin = [
            c for c in ctx.allies()
            if c.color_name == "Fuchsia" and c.job_and_color != "SPF"
        ]
        if not kin:
            return
        x, y = mirror_of(ctx, card)
        for target in ctx.targets("farthest", kin):
            spawn_shadow(ctx, target, x, y, movable=False)


def _free_shadow_squares(card, ctx) -> None:
    """Release squares held by this card's shadows, unless something else stands there."""
    for shadow in card.companions:
        occupied_by_other = any(
            c.health > 0 and c.get_position() == shadow.get_position()
            for c in ctx.gs.get_all_cards() if c is not card
        )
        if not occupied_by_other:
            ctx.gs.board_dict[shadow.board_x, shadow.board_y].occupy = False
