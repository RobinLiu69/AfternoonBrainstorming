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

from shared.setting import WHITE
from core.board_block import Board
from core.board_config import BoardConfig


class _DiscardList(list):
    def append(self, item) -> None:
        pass


class HeadlessRenderer:
    def __init__(self) -> None:
        self.dying_cards = _DiscardList()


def make_board_dict(config: BoardConfig) -> dict[tuple[int, int], Board]:
    return {
        (x, y): Board(width=100, height=100, occupy=False, color=WHITE,
                      board_x=x, board_y=y)
        for y in range(config.height)
        for x in range(config.width)
    }
