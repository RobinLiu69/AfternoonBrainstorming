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

"""Orange — movement.

Attacking unlocks a step, and stepping pays off again. The bonuses a step
grants are temporary modifiers tagged ``TEMPORARY`` and stripped when the turn
settles, rather than an integer that each card had to remember to zero.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import on
from cards.events import Event, Resource
from cards.statuses import RAMPAGE

orange = color("Orange", "O")

TEMPORARY = "temporary"

MOVE_CARD = "MOVEO"
"""A movement card that expires at end of turn; Player.turn_end discards it."""


def _moved_ally(card, ctx) -> bool:
    return ctx.card.owner == card.owner and ctx.card is not card


@orange("ADC")
class Adc:
    """Attacks, steps, and attacks again from the new square."""

    @on(Event.ATTACKED)
    def unlock_step(card, ctx):
        ctx.arm_move()

    @on(Event.MOVED)
    def follow_up(card, ctx):
        ctx.attack_now()


@orange("AP")
class Ap:
    """Numbs, and hands its owner a movement card each turn."""

    @on(Event.ON_HIT)
    def numb_target(card, ctx):
        ctx.numb(ctx.target)

    @on(Event.TURN_START)
    def issue_move(card, ctx):
        ctx.add_to_hand(MOVE_CARD)


@orange("TANK")
class Tank:
    """Being hit produces a movement card."""

    @on(Event.AFTER_DAMAGE_TAKEN)
    def issue_move(card, ctx):
        ctx.add_to_hand(MOVE_CARD)


@orange("HF")
class Hf:
    """Builds momentum by moving; the momentum lapses at end of turn."""

    @on(Event.ATTACKED)
    def unlock_step(card, ctx):
        ctx.arm_move()

    @on(Event.MOVED)
    def momentum(card, ctx):
        ctx.grant(
            card, "damage", ctx.settings("move_damage_gain"),
            tags=(TEMPORARY,), permanent=False,
        )
        ctx.set_status(card, RAMPAGE)

    @on(Event.TURN_END)
    def lose_momentum(card, ctx):
        ctx.strip(card, tags=(TEMPORARY,))


@orange("LF")
class Lf:
    """Strikes whatever it lands next to."""

    @on(Event.ATTACKED)
    def unlock_step(card, ctx):
        ctx.arm_move()

    @on(Event.MOVED)
    def cleave(card, ctx):
        others = [c for c in ctx.enemies(include_neutral=False) if c is not card]
        ctx.strike(ctx.targets("nearest", others), card.damage)


@orange("ASS")
class Ass:
    """A kill made after moving refunds the attack."""

    @on(Event.MOVED)
    def prime(card, ctx):
        ctx.set_status(card, RAMPAGE)

    @on(Event.ON_KILL)
    def refund(card, ctx):
        ctx.arm_move()
        if ctx.has_status(card, RAMPAGE):
            ctx.gain(Resource.ATTACKS, ctx.settings("attack_gain_per_kill"))
            ctx.set_status(card, RAMPAGE, False)


@orange("APT")
class Apt:
    """Plates the team as it moves, and forges its own plating into attack."""

    @on(Event.MOVED)
    def forge(card, ctx):
        ctx.add_armor(card, ctx.settings("move_armor_gain"))
        converted = card.armor // 2
        if converted > 0:
            ctx.buff(card, damage=converted)
            card.armor = card.armor % 2

    @on(Event.CARD_MOVED, when=_moved_ally)
    def plate_the_mover(card, ctx):
        gain = ctx.settings("move_armor_gain")
        ctx.add_armor(ctx.card, gain)
        ctx.add_armor(card, gain)


@orange("SP")
class Sp:
    """Snipes the far side of the board whenever a friendly card moves."""

    @on(Event.CARD_MOVED, when=lambda card, ctx: ctx.card.owner == card.owner)
    def snipe(card, ctx):
        ctx.strike(ctx.targets("farthest"), ctx.settings("move_strike_damage"))
