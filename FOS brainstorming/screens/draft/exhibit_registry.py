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

from typing import Optional

from shared.setting import JOB_DICTIONARY, CARD_SETTING
from cards.base import Card
from cards.factory import CardFactory
from core.game_screen import GameScreen

import pygame


_JOB_ORDER = ["ADC", "AP", "TANK", "HF", "LF", "ASS", "APT", "SP"]
_POSITIONS  = [(0,0),(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1)]
_MAGIC_DEFS = [("CUBES", 0, 2), ("HEAL", 1, 2), ("MOVE", 2, 2)]


class ExhibitRegistry:
    def __init__(self, game_screen: GameScreen) -> None:
        self.game_screen = game_screen
        self._pages     = self._build_pages()
        self._magic_row = self._build_magic()
        self.switch_rects = self._create_switch_rects()

    def _build_pages(self) -> list[list[list[Card]]]:
        pages: list[list[list[Card]]] = []
        for page_array in JOB_DICTIONARY["colors_array"]:
            page: list[list[Card]] = []
            for color_tag, color_name in page_array.items():
                color: list[Card] = []
                available = CARD_SETTING.get(color_name, {}).keys()
                for job, pos in zip(_JOB_ORDER, _POSITIONS):
                    key = job + color_tag
                    if job not in available:
                        continue
                    if key not in CardFactory._registry:
                        continue
                    try:
                        color.append(CardFactory.create(key, "display", *pos))
                    except ValueError:
                        pass
                if color:
                    page.append(color)
            if page:
                pages.append(page)
        return pages

    def _build_magic(self) -> list[Card]:
        result = []
        for name, x, y in _MAGIC_DEFS:
            try:
                result.append(CardFactory.create(name, "display", x, y))
            except ValueError:
                pass
        return result

    def page_count(self) -> int:
        return len(self._pages)
    
    def index_count(self, page: int) -> int:
        return len(self._pages[page]) if page < len(self._pages) else 0

    def get_page(self, page: int, index: int) -> list[Card]:
        return self._pages[page][index] if page < len(self._pages) and index < len(self._pages[page]) else []

    def get_page_colors(self, page: int) -> list[tuple[int, int, int]]:
        colors: list[tuple[int, int, int]] = []
        for color_name in JOB_DICTIONARY["colors_array"][page].values():
            r, g, b = JOB_DICTIONARY["RGB_colors"][color_name]
            colors.append((r, g, b))
        return colors
                
    def get_magic_row(self) -> list[Card]:
        return self._magic_row

    def card_name_at(self, page: int, index: int, board_x: Optional[int], board_y: Optional[int]) -> str:
        if board_x is None or board_y is None:
            return "None"
        for card in self.get_page(page, index):
            if card.board_x == board_x and card.board_y == board_y:
                return card.job_and_color
        for card in self._magic_row:
            if card.board_x == board_x and card.board_y == board_y:
                return card.job_and_color
        return "None"
    
    def _create_switch_rects(self):
        RECT_NUM = 10
        
        TOP_LEFT = (self.game_screen.display_width / 2 - self.game_screen.block_size * 1.95, self.game_screen.display_height / 2 - self.game_screen.block_size * 1.9)
        WIDTH = self.game_screen.block_size / 8
        HEIGHT = self.game_screen.block_size / 8
        
        GAP = self.game_screen.block_size / 5
        
        switch_rects_pos = []
        
        for i in range(RECT_NUM):
            switch_rects_pos.append(pygame.Rect(TOP_LEFT[0] + i * GAP, TOP_LEFT[1], WIDTH, HEIGHT))
        
        return switch_rects_pos