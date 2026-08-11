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

"""Card definitions, one module per colour.

Importing this package registers every card into cards.defs.CARD_DEFS.
"""

from __future__ import annotations


_LOADED = False


def load_all() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    from cards.definitions import (  # noqa: F401
        neutral, white, red, purple, brown, blue,
        orange, dark_green, green, cyan, fuchsia,
    )
