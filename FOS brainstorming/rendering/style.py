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
SCRIM_FILL = (0, 0, 0, 205)
TOOLTIP_FILL = (8, 8, 8, 255)
TOOLTIP_EDGE = (255, 255, 255, 210)
DIVIDER = (255, 255, 255, 55)

PANEL_PAD = 0.18
HEADER_HEIGHT = 0.30
CORNER_RATIO = 30


def edge_width(gs: GameScreen) -> int:
    return max(1, int(gs.block_size / 45))


def corner_radius(gs: GameScreen) -> int:
    return max(1, int(gs.block_size / CORNER_RATIO)) * 2


def panel(gs: GameScreen, x: float, y: float, width: float, height: float) -> None:
    surface = pygame.Surface((max(1, int(width)), max(1, int(height))), pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.rect(surface, PANEL_FILL, rect, 0, border_radius=corner_radius(gs))
    pygame.draw.rect(surface, PANEL_EDGE, rect, edge_width(gs), border_radius=corner_radius(gs))
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


def modal(gs: GameScreen, x: float, y: float, width: float, height: float) -> None:
    surface = pygame.Surface((max(1, int(width)), max(1, int(height))), pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.rect(surface, TOOLTIP_FILL, rect, 0, border_radius=corner_radius(gs))
    pygame.draw.rect(surface, TOOLTIP_EDGE, rect, edge_width(gs), border_radius=corner_radius(gs))
    gs.surface.blit(surface, (int(x), int(y)))


def muted_text(gs: GameScreen, text: str, x: float, y: float,
               font: pygame.font.Font | None = None) -> None:
    draw_text(text, font or gs.mid_text_font, INK_DISABLED, x, y, gs.surface)


def centred(gs: GameScreen, text: str, y: float,
            font: pygame.font.Font | None = None,
            colour: tuple[int, int, int] = INK) -> None:
    font = font or gs.title_text_font
    draw_text(text, font, colour, gs.display_width / 2 - font.size(text)[0] / 2,
              y, gs.surface)


def title(gs: GameScreen, text: str, y: float | None = None) -> None:
    centred(gs, text, gs.block_size * 0.25 if y is None else y, gs.title_text_font)


IDENTITY_LABELS: dict[str, str] = {
    "player1": "You: P1",
    "player2": "You: P2",
    "spectator": "Spectator",
    "god": "God View",
    "host": "You: host",
}


def identity_label(gs: GameScreen, role: str) -> None:
    draw_text(IDENTITY_LABELS.get(role, role), gs.text_font, INK,
              gs.block_size * 0.2, gs.block_size * 0.2, gs.surface)


def spectator_count(gs: GameScreen, count: int) -> None:
    if not count or count <= 0:
        return
    text = f"spectators: {count}"
    width = gs.text_font.size(text)[0]
    draw_text(text, gs.text_font, INK,
              gs.display_width - width - gs.block_size * 0.3,
              gs.block_size * 0.2, gs.surface)


def awaiting_server(gs: GameScreen, waiting: bool) -> None:
    if not waiting:
        return
    text = "waiting for host..."
    width = gs.text_font.size(text)[0]
    draw_text(text, gs.text_font, INK,
              gs.display_width / 2 - width / 2, gs.block_size * 0.2, gs.surface)


def pause_overlay(gs: GameScreen, reason: str, seconds_remaining: float,
                  note: str) -> None:
    scrim(gs)
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2

    if seconds_remaining == float("inf"):
        window_line = "reconnect window: unlimited"
        note_line = "(waiting for opponent)"
    else:
        window_line = f"reconnect window: {max(0, int(seconds_remaining))}s"
        note_line = note

    lines = [reason or "opponent disconnected", window_line, note_line]
    widths = [gs.big_text_font.size(line)[0] for line in lines]
    pad = bs * PANEL_PAD
    width = max(widths) + pad * 2
    height = bs * 0.5 * len(lines) + pad * 2
    x, y = cx - width / 2, cy - height / 2
    modal(gs, x, y, width, height)

    for i, line in enumerate(lines):
        colour = INK if i == 0 else INK_MUTED
        draw_text(line, gs.big_text_font, colour,
                  cx - widths[i] / 2, y + pad + bs * 0.5 * i, gs.surface)
