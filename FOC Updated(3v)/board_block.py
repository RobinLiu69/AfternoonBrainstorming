import pygame
from dataclasses import dataclass, field
from typing import Sequence, Any, cast


@dataclass(kw_only=True)
class Board:
    name: str = "Board"
    x: int
    y: int
    width: int
    height: int
    card: bool
    color: tuple[int, int, int]
    board_x: int
    board_y: int
    thickness: int = 2

    def __post_init__(self) -> None:
        self.size = self.width
        self.board_position = self.board_x + (self.board_y * 4)

    def display(self, surface: pygame.surface.Surface) -> int:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 4)
        return 0