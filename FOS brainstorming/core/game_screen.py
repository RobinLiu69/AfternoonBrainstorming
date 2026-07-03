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

from __future__ import annotations
import os
import json
from typing import Sequence, TextIO, Optional, cast

import pygame
from pygame._sdl2.video import Window

from shared.setting import FOLDER_PATH
from core.display_config import load_display_mode


with open(f"{FOLDER_PATH}/config/setting.json", "r", encoding="utf-8") as file:
    SETTING: dict[str, str] = json.loads(file.read())

BASIC_FONT = FOLDER_PATH+SETTING["basic_font"]
CHINESE_FONT = FOLDER_PATH+SETTING["chinese_font"]

KETYS_TO_DISPLAY = SETTING["keys_to_display"]
KEYS_TO_CHECK = SETTING["keys_to_check"]
PIE_TITLE_TEXTS = SETTING["pie_title_texts"]
BOARD_SIZE: tuple[int, int] = cast(tuple[int, int], tuple(map(int, SETTING["board_size"])))


def draw_text(text: str, font: pygame.font.Font, text_color: Sequence[int], x: float, y: float, surface: pygame.surface.Surface) -> None:
    rendered = font.render(text, True, text_color)
    
    w, h = rendered.get_size()
    transparent = pygame.Surface((w, h), pygame.SRCALPHA)
    transparent.fill((0, 0, 0, 0))
    transparent.blit(rendered, (0, 0))
    rendered.set_colorkey((0, 0, 0))
    transparent.blit(rendered, (0, 0))
    
    surface.blit(transparent, (x, y))


def to_board_x(mouse_x: int, game_screen: GameScreen) -> Optional[int]:
    return (int((mouse_x - (game_screen.display_width/2 - game_screen.block_size*2)) / game_screen.block_size)
        if mouse_x > game_screen.display_width/2 - game_screen.block_size*2 and
        mouse_x < game_screen.display_width/2 + game_screen.block_size*2 else None)


def to_board_y(mouse_y: int, game_screen: GameScreen) -> Optional[int]:
    return (int((mouse_y - (game_screen.display_height/2 - game_screen.block_size*1.65)) / game_screen.block_size)
        if mouse_y > game_screen.display_height/2 - game_screen.block_size*1.65 and
        mouse_y < game_screen.display_height/2 + game_screen.block_size*2.35 else None)


class GameScreen:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("AfternoonBrainstorming")
        self.set_window_icon()
        self.playback: TextIO | None = None
        self._sdl_window: Window | None = None
        self.display_mode: str = load_display_mode()
        self.apply_display_mode(self.display_mode)

    def set_window_icon(self) -> None:
        icon_path = f"{FOLDER_PATH}/assets/icon.png"
        if os.path.isfile(icon_path):
            try:
                pygame.display.set_icon(pygame.image.load(icon_path))
            except pygame.error:
                pass

    @staticmethod
    def fit_16_10(width: float, height: float) -> tuple[int, int]:
        if width / height > 1.6:
            fitted_height = int(height)
            fitted_width = int(fitted_height * 1.6)
        else:
            fitted_width = int(width)
            fitted_height = int(fitted_width / 1.6)
        return fitted_width, fitted_height

    def apply_display_mode(self, mode: str) -> None:
        self.display_mode = mode
        self._sdl_window = None

        pygame.display.quit()
        pygame.display.init()
        pygame.display.set_caption("AfternoonBrainstorming")
        self.set_window_icon()

        desktop_width, desktop_height = pygame.display.get_desktop_sizes()[0]
        if mode == "fullscreen":
            self.display_width, self.display_height = self.fit_16_10(desktop_width, desktop_height)
            self.surface = pygame.display.set_mode((self.display_width, self.display_height),
                                                   pygame.FULLSCREEN | pygame.SCALED)
        else:
            percent = int(mode)
            self.display_width, self.display_height = self.fit_16_10(desktop_width * percent / 100,
                                                                     desktop_height * percent / 100)
            flags = pygame.NOFRAME if percent >= 100 else 0
            self.surface = pygame.display.set_mode((self.display_width, self.display_height), flags)
            self._center_window(desktop_width, desktop_height)
        self.block_size: float = (self.display_width / 8) / 1.2
        self.thickness: int = self.display_width // 400
        self.font_init()

    def _center_window(self, desktop_width: int, desktop_height: int) -> None:
        x = max(0, (desktop_width - self.display_width) // 2)
        y = max(0, (desktop_height - self.display_height) // 2)
        try:
            pygame.display.set_window_position((x, y))
            return
        except AttributeError:
            pass

        if self._sdl_window is None:
            self._sdl_window = Window.from_display_module()
        self._sdl_window.position = (x, y)

    def font_init(self) -> None:
        self.text_font_size: int = int(self.display_width/1500*16.5)
        self.text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, self.text_font_size)
        self.mid_text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, int(self.text_font_size*1.25))
        self.title_text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, int(self.text_font_size*3))
        self.info_text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, int(self.text_font_size/1.1))
        self.big_text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, int(self.text_font_size/16.5*25))
        self.big_big_text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, int(self.text_font_size*2))
        self.small_text_font: pygame.font.Font = pygame.font.Font(BASIC_FONT, int(self.text_font_size/15*8.66))
        self.text_fontCHI: pygame.font.Font = pygame.font.Font(CHINESE_FONT, self.text_font_size)


    def render(self) -> None:
        self.surface.fill(pygame.Color((0, 0, 0)))