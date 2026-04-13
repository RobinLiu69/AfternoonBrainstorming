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

from dataclasses import dataclass


@dataclass
class BoardConfig:
    width: int = 4
    height: int = 4
    
    @property
    def total_cells(self) -> int:
        return self.width * self.height
    
    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)
    
    def get_symmetric_pos(self, x: int, y: int) -> tuple[int, int]:
        return (self.width - 1 - x, self.height - 1 - y)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_all_positions(self) -> list[tuple[int, int]]:
        return [(x, y) for y in range(self.height) for x in range(self.width)]
    
    def get_center_position(self) -> tuple[float, float]:
        return ((self.width - 1) / 2, (self.height - 1) / 2)
    
    def get_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        return abs(x2 - x1) + abs(y2 - y1)
    
    def __str__(self) -> str:
        return f"Board({self.width}x{self.height})"
    
    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> BoardConfig:
        return cls(width=data["width"], height=data["height"])