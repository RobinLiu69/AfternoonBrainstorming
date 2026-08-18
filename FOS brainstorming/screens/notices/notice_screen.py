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

import pygame

from core.game_screen import GameScreen, draw_text, QuitGame
from rendering import style
from shared.setting import WHITE

FOOTER = "Press any key to go back"
LINE_STEP = 0.34
MIN_WIDTH = 5.0


def render(game_screen: GameScreen, title: str, lines: tuple[str, ...]) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    pad = bs * style.PANEL_PAD

    body = [line for line in lines if line]
    widths = [game_screen.mid_text_font.size(line)[0] for line in body]
    widths.append(game_screen.mid_text_font.size(title)[0] + bs * 0.4)
    widths.append(game_screen.text_font.size(FOOTER)[0])
    width = max(max(widths) + pad * 2, bs * MIN_WIDTH)

    header = bs * style.HEADER_HEIGHT
    height = header + pad + bs * LINE_STEP * len(body) + bs * 0.45 + pad
    x = cx - width / 2
    y = cy - height / 2

    style.section(game_screen, title, x, y, width, height)

    text_y = y + header + pad
    for line in body:
        draw_text(line, game_screen.mid_text_font, WHITE,
                  x + pad, text_y, game_screen.surface)
        text_y += bs * LINE_STEP

    footer_w = game_screen.text_font.size(FOOTER)[0]
    style.muted_text(game_screen, FOOTER, x + width / 2 - footer_w / 2,
                     y + height - pad - game_screen.text_font.get_linesize(),
                     game_screen.text_font)


def main(game_screen: GameScreen, title: str, *lines: str) -> None:
    clock = pygame.time.Clock()
    pygame.event.clear()

    while True:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        render(game_screen, title, lines)

        pygame.display.update()
        clock.tick(60)
