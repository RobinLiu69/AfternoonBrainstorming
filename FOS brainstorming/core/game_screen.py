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

import os
import json
from typing import Sequence, TextIO, Optional, cast

import pygame

from core.setting import FOLDER_PATH


with open(f"{FOLDER_PATH}/setting/setting.json", "r", encoding="utf-8") as file:
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
        self.display_width: int = pygame.display.get_desktop_sizes()[0][0]
        self.display_height: int = pygame.display.get_desktop_sizes()[0][1]
        if self.display_width == 2880 and self.display_height == 1800:
            self.display_width = 1744
            self.display_height = 981
        print(self.display_width, self.display_height)
        self.surface, self.block_size = self.fitting_screen()
        print(self.display_width, self.display_height)
        self.thickness = self.display_width // 400
        self.font_init()
        self.playback: TextIO | None = None

    def fitting_screen(self) -> tuple[pygame.surface.Surface, float]:
        if self.display_width/self.display_height == 1.6:
            surface = pygame.display.set_mode((self.display_width, self.display_height))
            block_size = (self.display_width/8) / 1.2
        else:
            maxvalue = [0, 0]
            for H in range(self.display_height, 0, -1):
                for W in range(self.display_width, 0, -1):
                    if W/H == 1.6:
                        maxvalue = [W, H]
                        break
                if maxvalue != [0, 0]:
                    break
            self.display_width = maxvalue[0]
            self.display_height = maxvalue[1]
            surface = pygame.display.set_mode((self.display_width, self.display_height))
            block_size = (self.display_width/8) / 1.2
        return surface, block_size

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