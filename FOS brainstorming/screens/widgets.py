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

from typing import Literal

from core.game_screen import GameScreen
from core.UI import Button

Corner = Literal["top_left", "top_right", "bottom_left", "bottom_right"]


def make_back_button(game_screen: GameScreen, text: str = "back",
                     corner: Corner = "top_left") -> Button:
    bs = game_screen.block_size
    w, h = bs * 1.5, bs * 0.5
    box_width = max(1, int(bs / 30))
    margin = bs * 0.3

    if corner == "top_left":
        x, y = margin, bs * 0.25
    elif corner == "top_right":
        x, y = game_screen.display_width - w - margin, bs * 0.25
    elif corner == "bottom_left":
        x, y = margin, game_screen.display_height - h - bs * 0.25
    else:
        x, y = game_screen.display_width - w - margin, game_screen.display_height - h - bs * 0.25

    return Button(w, h, x, y, box_width=box_width,
                  font=game_screen.mid_text_font, text=text)
