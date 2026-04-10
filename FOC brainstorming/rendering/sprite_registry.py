# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright 2024-2026 Robin Liu / FOC Studio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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