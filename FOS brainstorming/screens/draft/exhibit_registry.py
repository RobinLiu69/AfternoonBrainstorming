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

from typing import Optional

from core.setting import JOB_DICTIONARY, CARD_SETTING
from cards.base import Card
from cards.factory import CardFactory


_JOB_ORDER = ["ADC", "AP", "TANK", "HF", "LF", "ASS", "APT", "SP"]
_POSITIONS  = [(0,0),(1,0),(2,0),(3,0),(0,1),(1,1),(2,1),(3,1)]
_MAGIC_DEFS = [("CUBES", 0, 2), ("HEAL", 1, 2), ("MOVE", 2, 2)]


class ExhibitRegistry:
    def __init__(self) -> None:
        self._pages     = self._build_pages()
        self._magic_row = self._build_magic()

    def _build_pages(self) -> list[list[Card]]:
        pages = []
        for color_tag, color_name in JOB_DICTIONARY["colors_dict"].items():
            available = CARD_SETTING.get(color_name, {}).keys()
            page: list[Card] = []
            for job, pos in zip(_JOB_ORDER, _POSITIONS):
                key = job + color_tag
                if job not in available:
                    continue
                if key not in CardFactory._registry:
                    continue
                try:
                    page.append(CardFactory.create(key, "display", *pos))
                except ValueError:
                    pass
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

    def get_page(self, page: int) -> list[Card]:
        return self._pages[page] if page < len(self._pages) else []

    def get_magic_row(self) -> list[Card]:
        return self._magic_row

    def card_name_at(self, page: int, board_x: Optional[int], board_y: Optional[int]) -> str:
        if board_x is None or board_y is None:
            return "None"
        for card in self.get_page(page):
            if card.board_x == board_x and card.board_y == board_y:
                return card.job_and_color
        for card in self._magic_row:
            if card.board_x == board_x and card.board_y == board_y:
                return card.job_and_color
        return "None"