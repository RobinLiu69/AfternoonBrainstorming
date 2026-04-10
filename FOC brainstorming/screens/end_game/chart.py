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

from dataclasses import dataclass, field
import os

import pygame

from core.setting import FOLDER_PATH
from core.game_screen import GameScreen


@dataclass(kw_only=True)
class Chart:
    file_path: str
    x: int
    y: int
    width: int
    height: int
    visible: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        full_path = FOLDER_PATH + "/imgs/" + self.file_path
        self.image: pygame.surface.Surface | None = None
        if os.path.exists(full_path):
            self.image = pygame.transform.scale(
                pygame.image.load(full_path).convert_alpha(),
                (self.width, self.height),
            )

    def display(self, game_screen: GameScreen) -> None:
        if self.visible and self.image:
            game_screen.surface.blit(self.image, (self.x, self.y))