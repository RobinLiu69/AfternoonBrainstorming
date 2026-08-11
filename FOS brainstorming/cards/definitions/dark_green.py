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

"""DarkGreen — totems.

Cards pay health to engrave totems, and the whole colour scales off the total.
Each SP on the board doubles every engraving, which is why the multiplier is
computed at engrave time rather than being baked into each card.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import aura, on
from cards.events import Event, Resource
from cards.stats import DAMAGE, Modifier
from shared.combat_event import CombatEvent
from shared.setting import CARD_SETTING

dark_green = color("DarkGreen", "DKG")

_SP_SETTINGS = CARD_SETTING["DarkGreen"]["SP"]


def engrave(ctx, times: int) -> None:
    """Add totems, doubled once per friendly SP in play."""
    if times <= 0:
        return
    multiplier = _SP_SETTINGS["engraved_totem_coefficient"] ** ctx.count(
        lambda c: c.job_and_color == "SPDKG" and not c.nullify and c.owner == ctx.owner
    )
    ctx.gain(Resource.TOTEM, times * multiplier)


def _totem_scaling(divisor_key: str):
    """A static effect scaling attack with the owner's totem count."""

    def scale(card, game_state):
        divisor = card.definition.settings.get(divisor_key, 1)
        if divisor:
            yield Modifier.aura(
                DAMAGE, game_state.players_totem.get(card.owner, 0) // divisor, card=card
            )

    return scale


@dark_green("ADC")
class Adc:
    """Attack scales with a quarter of the totems."""

    scale = aura()(_totem_scaling("damage_divisor"))


@dark_green("AP")
class Ap:
    """Numbs and engraves deeply."""

    @on(Event.ON_HIT)
    def numb_and_engrave(card, ctx):
        ctx.numb(ctx.target)
        engrave(ctx, ctx.settings("engraved_totem"))


@dark_green("TANK")
class Tank:
    """Engraves whenever it is struck."""

    @on(Event.AFTER_DAMAGE_TAKEN)
    def engrave_on_hit(card, ctx):
        engrave(ctx, ctx.settings("engraved_totem"))


@dark_green("HF")
class Hf:
    """Bleeds every turn, and fights hardest when nearly dead."""

    @on(Event.ON_HIT)
    def drain(card, ctx):
        ctx.heal(card, 1)

    @aura()
    def cornered(card, game_state):
        if card.health <= 4:
            yield Modifier.aura(DAMAGE, card.definition.settings.get("damage_bonus", 0), card=card)

    @on(Event.TURN_START)
    def bleed(card, ctx):
        ctx.chip(card, ctx.settings("turn_start_health_loss"))
        engrave(ctx, ctx.settings("engraved_totem"))


@dark_green("LF")
class Lf:
    """Detonates on arrival for a share of the totems."""

    @on(Event.DEPLOYED)
    def detonate(card, ctx):
        share = ctx.gs.players_totem.get(card.owner, 0) // 4
        ctx.strike(ctx.targets("small_cross"), share)

    @on(Event.TURN_START)
    def bleed(card, ctx):
        ctx.chip(card, ctx.settings("turn_start_health_loss"))

    @on(Event.ON_HIT)
    def engrave_on_hit(card, ctx):
        engrave(ctx, ctx.settings("engraved_totem"))


@dark_green("ASS")
class Ass:
    """Trades its own life for a deep engraving on every kill."""

    scale = aura()(_totem_scaling("damage_divisor"))

    @on(Event.ON_KILL)
    def immolate(card, ctx):
        card.health = 0
        ctx.gs.pending_combat_events.append(CombatEvent(
            kind="hurt", board_x=card.board_x, board_y=card.board_y, post_health=0,
        ))
        engrave(ctx, ctx.settings("engraved_totem"))


@dark_green("APT")
class Apt:
    """Turns totems into damage, damage into armour, and armour into totems."""

    @aura()
    def scale(card, game_state):
        yield Modifier.aura(DAMAGE, game_state.players_totem.get(card.owner, 0) // 2, card=card)

    @on(Event.ON_HIT)
    def engrave_from_plating(card, ctx):
        engrave(ctx, card.armor // 2)

    @on(Event.AFTER_DAMAGE_DEALT)
    def plate_from_damage(card, ctx):
        ctx.add_armor(card, ctx.amount // 2)


@dark_green("SP")
class Sp:
    """Doubles every engraving while in play. Read by engrave() above."""
