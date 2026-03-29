# core/board_config.py
from dataclasses import dataclass
from typing import Tuple

@dataclass
class BoardConfig:
    width: int = 4
    height: int = 4
    
    @property
    def total_cells(self) -> int:
        return self.width * self.height
    
    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)
    
    def get_symmetric_pos(self, x: int, y: int) -> Tuple[int, int]:
        return (self.width - 1 - x, self.height - 1 - y)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_all_positions(self) -> list[Tuple[int, int]]:
        return [(x, y) for y in range(self.height) for x in range(self.width)]
    
    def get_center_position(self) -> Tuple[float, float]:
        return ((self.width - 1) / 2, (self.height - 1) / 2)
    
    def get_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        return abs(x2 - x1) + abs(y2 - y1)
    
    def __str__(self) -> str:
        return f"Board({self.width}x{self.height})"