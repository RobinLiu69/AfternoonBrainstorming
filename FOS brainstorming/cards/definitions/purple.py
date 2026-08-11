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

"""Purple — disruption.

Only AP, TANK, HF and ASS exist; the other four purple cards were never
implemented and are deliberately not registered, matching the old module.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import on
from cards.events import Event, Resource

purple = color("Purple", "P")


@purple("AP")
class Ap:
    """Silences the nearest enemy on arrival and on every hit."""

    @on(Event.DEPLOYED)
    def silence_on_arrival(card, ctx):
        for target in ctx.targets("nearest", ctx.enemies(include_neutral=False)):
            ctx.silence(target)

    @on(Event.ON_HIT)
    def silence_target(card, ctx):
        ctx.numb(ctx.target)
        ctx.silence(ctx.target)


@purple("TANK")
class Tank:
    """Punishes enemy movement. Numbness does not stop this."""

    @on(Event.CARD_MOVED, when=lambda card, ctx: ctx.card.owner != card.owner)
    def punish(card, ctx):
        ctx.deal_damage(ctx.card, ctx.settings("move_strike_damage"))


@purple("HF")
class Hf:
    """Converts crowding into extra attacks at the start of its turn."""

    @on(Event.TURN_START)
    def crowd_bonus(card, ctx):
        if not card.attack_types:
            return
        # Neutral props do not count towards the crowd.
        in_range = ctx.targets(card.attack_types, ctx.enemies(include_neutral=False))
        ctx.gain(Resource.ATTACKS, len(in_range) // 3)


@purple("ASS")
class Ass:
    """Draws cards for however far behind on board it is."""

    @on(Event.ON_KILL)
    def catch_up(card, ctx):
        deficit = (
            len(ctx.gs.get_player_cards(ctx.victim.owner))
            - len(ctx.allies(living=False))
            - ctx.settings("unit_gap")
        )
        draws = min(deficit, ctx.settings("maximum_card_draw_from_killed"))
        if draws > 0:
            ctx.draw(draws)
