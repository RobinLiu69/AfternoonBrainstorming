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

"""Neutral props and the magic cards.

None of these have abilities; they exist so the board and the hand have
something to render and to occupy space.
"""

from __future__ import annotations

from cards.defs import neutral


@neutral("CUBE", job="CUBE", pattern="")
class Cube:
    """A neutral crate. Blocks a square, never scores."""


@neutral("CUBES", job="CUBES", pattern="")
class Cubes:
    """Hand/display face of the crate-placing magic card."""


@neutral("JUDGE", job="JUDGE", health=1, damage=0, pattern="", movable=False)
class Judge:
    """Not a card in any deck: the origin for damage the game itself deals."""


@neutral("MOVE", job="MOVE", health=-1, damage=-1, pattern="", movable=False)
class Move:
    """Magic card: grants one movement."""


@neutral("HEAL", job="HEAL", health=-1, damage=-1, pattern="", movable=False)
class Heal:
    """Magic card: restores health, overflow becoming armour."""
