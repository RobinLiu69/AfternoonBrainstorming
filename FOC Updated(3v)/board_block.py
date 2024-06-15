import pygame
from dataclasses import dataclass, fields
from typing import Sequence, Any


@dataclass(kw_only=True)
class Board:
    name: str = "Board"
    x: int
    y: int
    width: int
    height: int
    card: bool
    size: int = width
    color: tuple[int, ...]
    BoardX: int
    BoardY: int
    Board: int = BoardX+(BoardY*4)
    thickness: int = 2

    def display(self, surface: pygame.surface.Surface) -> int:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 4)
        return 0