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