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