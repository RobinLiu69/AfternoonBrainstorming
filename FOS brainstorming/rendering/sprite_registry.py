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

import os
from typing import Optional

import pygame


class SpriteRegistry:
    _instance: Optional["SpriteRegistry"] = None
    
    def __init__(self, base_path: str, block_size: float):
        self._cache: dict[str, pygame.Surface] = {}
        self._base_path = base_path
        self._block_size = int(block_size)
    
    @classmethod
    def get_instance(cls) -> "SpriteRegistry":
        if cls._instance is None:
            raise RuntimeError("SpriteRegistry hasn't been initialized")
        return cls._instance
    
    @classmethod
    def initialize(cls, base_path: str, block_size: float) -> "SpriteRegistry":
        cls._instance = cls(base_path, block_size)
        return cls._instance
    
    def get(self, job_and_color: str) -> Optional[pygame.Surface]:
        if job_and_color in self._cache:
            return self._cache[job_and_color]
        
        path = os.path.join(self._base_path, f"{job_and_color}.png")
        if os.path.exists(path):
            raw = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.scale(raw, (self._block_size, self._block_size))
            self._cache[job_and_color] = scaled
            return scaled
        
        return None
    
    def preload(self, job_and_color_list: list[str]) -> None:
        for name in job_and_color_list:
            self.get(name)