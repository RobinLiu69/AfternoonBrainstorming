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