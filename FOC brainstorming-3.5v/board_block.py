from dataclasses import dataclass, field
import os, json, pygame
import random
from typing import Sequence, Any, cast

from game_screen import GameScreen, WHITE


def initialize_board(length: int, game_screen: GameScreen) -> dict[str, "Board"]:
    return dict(zip(((str(i%4)+"-"+str(i//4)) for i in range(length)), (Board(width=int(game_screen.block_size), height=int(game_screen.block_size), occupy=False, color=WHITE, board_x=i % 4, board_y=i // 4) for i in range(length))))

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
        self.board_position = self.board_x + (self.board_y * 4)
        

    def display(self, game_screen: GameScreen) -> None:
        pygame.draw.rect(game_screen.surface, self.color, (((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0),
                    (game_screen.display_height/2)-(game_screen.block_size*1.675)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0), self.width, self.height), game_screen.thickness)
    
    def update(self, game_screen: GameScreen) -> None:
        self.display(game_screen)