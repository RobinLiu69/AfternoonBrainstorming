import pygame
from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.game_state import WHITE

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

    # def display(self, game_screen: GameScreen, config: BoardConfig) -> None:
    #     board_pixel_width = config.width * game_screen.block_size
    #     board_pixel_height = (config.height+0.5) * game_screen.block_size
        
    #     start_x = (game_screen.display_width - board_pixel_width) / 2
    #     start_y = (game_screen.display_height - board_pixel_height) / 2
        
    #     x = start_x + self.board_x * game_screen.block_size
    #     y = start_y + self.board_y * game_screen.block_size
        
    #     pygame.draw.rect(
    #         game_screen.surface,
    #         self.color,
    #         (x, y, self.width, self.height),
    #         game_screen.thickness
    #     )
    
    def display(self, game_screen: GameScreen) -> None:
        pygame.draw.rect(game_screen.surface, self.color, (((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0),
                    (game_screen.display_height/2)-(game_screen.block_size*1.675)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0), self.width, self.height), game_screen.thickness)

    def update(self, game_screen: GameScreen, config: BoardConfig) -> None:
        # self.display(game_screen, config)
        self.display(game_screen)