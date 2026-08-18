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

from core.game_screen import GameScreen, draw_text

INK = (255, 255, 255)
INK_MUTED = (150, 150, 150)
INK_DISABLED = (105, 105, 105)

PANEL_FILL = (255, 255, 255, 12)
PANEL_EDGE = (255, 255, 255, 70)
HEADER_FILL = (255, 255, 255, 32)
CONTROL_FILL = (255, 255, 255, 20)
SCRIM_FILL = (0, 0, 0, 170)
TOOLTIP_FILL = (10, 10, 10, 235)
TOOLTIP_EDGE = (255, 255, 255, 210)
DIVIDER = (255, 255, 255, 55)

PANEL_PAD = 0.18
HEADER_HEIGHT = 0.30
CORNER_RADIUS = 0


def edge_width(gs: GameScreen) -> int:
    return max(1, int(gs.block_size / 45))


def panel(gs: GameScreen, x: float, y: float, width: float, height: float) -> None:
    surface = pygame.Surface((max(1, int(width)), max(1, int(height))), pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.rect(surface, PANEL_FILL, rect, 0, border_radius=CORNER_RADIUS)
    pygame.draw.rect(surface, PANEL_EDGE, rect, edge_width(gs), border_radius=CORNER_RADIUS)
    gs.surface.blit(surface, (int(x), int(y)))


def header(gs: GameScreen, title: str, x: float, y: float, width: float,
           right: str = "") -> float:
    height = gs.block_size * HEADER_HEIGHT
    band = pygame.Surface((max(1, int(width)), max(1, int(height))), pygame.SRCALPHA)
    band.fill(HEADER_FILL)
    gs.surface.blit(band, (int(x), int(y)))
    inset = gs.block_size * PANEL_PAD * 0.6
    text_y = y + (height - gs.mid_text_font.get_linesize()) / 2
    draw_text(title, gs.mid_text_font, INK, x + inset, text_y, gs.surface)
    if right:
        right_w = gs.text_font.size(right)[0]
        draw_text(right, gs.text_font, INK_MUTED, x + width - right_w - inset,
                  y + (height - gs.text_font.get_linesize()) / 2, gs.surface)
    return height


def section(gs: GameScreen, title: str, x: float, y: float,
            width: float, height: float, right: str = "") -> float:
    panel(gs, x, y, width, height)
    return header(gs, title, x, y, width, right)


def scrim(gs: GameScreen) -> None:
    overlay = pygame.Surface((gs.display_width, gs.display_height), pygame.SRCALPHA)
    overlay.fill(SCRIM_FILL)
    gs.surface.blit(overlay, (0, 0))


def muted_text(gs: GameScreen, text: str, x: float, y: float,
               font: pygame.font.Font | None = None) -> None:
    draw_text(text, font or gs.mid_text_font, INK_DISABLED, x, y, gs.surface)
