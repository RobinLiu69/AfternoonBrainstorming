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

"""White — the baseline colour. Plain stats, almost no abilities."""

from __future__ import annotations

from cards.defs import color
from cards.effects import aura, on
from cards.events import Event
from cards.stats import SCORE, Modifier, Op

white = color("White", "W")


@white("ADC")
class Adc:
    """Large cross."""


@white("AP")
class Ap:
    """Nearest single target; the hit numbs."""

    @on(Event.ON_HIT)
    def numb_target(card, ctx):
        ctx.numb(ctx.target)


@white("TANK")
class Tank:
    """Small cross."""


@white("HF")
class Hf:
    """Nine squares."""


@white("LF")
class Lf:
    """Small cross."""


@white("ASS")
class Ass:
    """Diagonal cross."""


@white("APT")
class Apt:
    """Shields itself and its nearest ally for its own attack value."""

    @on(Event.ON_HIT)
    def shield_line(card, ctx):
        for ally in ctx.nearest_ally():
            ctx.buff(ally, armor=card.damage)
        ctx.buff(card, armor=card.damage)


@white("SP")
class Sp:
    """Scores an extra point every turn it survives un-numbed."""

    @aura()
    def bonus_point(card, game_state):
        yield Modifier.aura(
            SCORE, card.definition.settings.get("extra_score", 1), card=card
        )
