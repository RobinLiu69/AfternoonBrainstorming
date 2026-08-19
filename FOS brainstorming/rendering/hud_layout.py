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

import pygame

from core.game_screen import GameScreen
from rendering import style

PANEL_MARGIN = 0.14
PANEL_WIDTH = 2.52
PANEL_TOP = 0.55
PANEL_BOTTOM = 0.18
PAD = 0.12
STAT_LINES = 3
FOOTER_LINES = 2
ROW_HEIGHT = 0.34
GLYPH = 0.26


def panel_rect(game_screen: GameScreen, seat: str) -> pygame.Rect:
    bs = game_screen.block_size
    width = bs * PANEL_WIDTH
    x = (bs * PANEL_MARGIN if seat == "player1"
         else game_screen.display_width - bs * PANEL_MARGIN - width)
    top = bs * PANEL_TOP
    height = game_screen.display_height - top - bs * PANEL_BOTTOM
    return pygame.Rect(int(x), int(top), int(width), int(height))


def content_left(game_screen: GameScreen, seat: str) -> float:
    return panel_rect(game_screen, seat).x + game_screen.block_size * PAD


def content_width(game_screen: GameScreen, seat: str) -> float:
    return panel_rect(game_screen, seat).width - game_screen.block_size * PAD * 2


def stats_top(game_screen: GameScreen, seat: str) -> float:
    bs = game_screen.block_size
    return panel_rect(game_screen, seat).y + bs * style.HEADER_HEIGHT + bs * PAD * 0.8


def hand_label_top(game_screen: GameScreen, seat: str) -> float:
    line = game_screen.text_font.get_linesize()
    return stats_top(game_screen, seat) + line * STAT_LINES + game_screen.block_size * PAD


def footer_top(game_screen: GameScreen, seat: str) -> float:
    line = game_screen.text_font.get_linesize()
    return (panel_rect(game_screen, seat).bottom - game_screen.block_size * PAD
            - line * FOOTER_LINES)


def hand_area(game_screen: GameScreen, seat: str) -> pygame.Rect:
    top = hand_label_top(game_screen, seat) + game_screen.mid_text_font.get_linesize()
    bottom = footer_top(game_screen, seat) - game_screen.block_size * PAD * 0.6
    return pygame.Rect(int(content_left(game_screen, seat)), int(top),
                       int(content_width(game_screen, seat)), int(max(0, bottom - top)))


def row_height(game_screen: GameScreen) -> float:
    return game_screen.block_size * ROW_HEIGHT


def visible_rows(game_screen: GameScreen, seat: str) -> int:
    return max(0, int(hand_area(game_screen, seat).height // row_height(game_screen)))


def row_rect(game_screen: GameScreen, seat: str, index: int) -> pygame.Rect:
    area = hand_area(game_screen, seat)
    height = row_height(game_screen)
    return pygame.Rect(area.x, int(area.y + height * index), area.width, int(height))


def shown_rows(game_screen: GameScreen, seat: str, count: int) -> int:
    limit = visible_rows(game_screen, seat)
    return count if count <= limit else max(0, limit - 1)


def index_at(game_screen: GameScreen, seat: str, mouse_x: float, mouse_y: float,
             count: int) -> int:
    area = hand_area(game_screen, seat)
    if not area.collidepoint(mouse_x, mouse_y):
        return -1
    index = int((mouse_y - area.y) // row_height(game_screen))
    return index if 0 <= index < shown_rows(game_screen, seat, count) else -1
