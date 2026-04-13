# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.setting import WHITE


if TYPE_CHECKING:
    from core.game_screen import GameScreen
    from core.board_config import BoardConfig


def initialize_board(game_screen: GameScreen, config: BoardConfig) -> dict[tuple[int, int], "Board"]:
    board_dict = {}
    
    for y in range(config.height):
        for x in range(config.width):
            board = Board(
                width=int(game_screen.block_size),
                height=int(game_screen.block_size),
                occupy=False,
                color=WHITE,
                board_x=x,
                board_y=y
            )
            board_dict[x, y] = board
    
    return board_dict


@dataclass(kw_only=True)
class Board:
    name: str = "Board"
    width: int
    height: int
    occupy: bool
    color: tuple[int, int, int]
    board_x: int
    board_y: int
    thickness: int = 2

    def __post_init__(self) -> None:
        self.size = self.width
        
    def get_position_index(self, board_width: int) -> int:
        return self.board_x + (self.board_y * board_width)

    def to_dict(self) -> dict:
        return {
            "board_x": self.board_x,
            "board_y": self.board_y,
            "occupy":  self.occupy,
        }
 
    def apply_dict(self, data: dict) -> None:
        self.occupy = data["occupy"]