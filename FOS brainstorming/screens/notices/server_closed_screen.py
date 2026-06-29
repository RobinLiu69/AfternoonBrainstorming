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

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text


def main(game_screen: GameScreen) -> None:
    clock = pygame.time.Clock()
    pygame.event.clear()

    while True:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        cx = game_screen.display_width / 2
        cy = game_screen.display_height / 2
        bs = game_screen.block_size

        lines = [
            ("Server Closed", game_screen.big_text_font, -bs * 1.2),
            ("the host left or closed the server", game_screen.mid_text_font, -bs * 0.1),
            ("(not a connection problem on your side)", game_screen.text_font, bs * 0.5),
            ("Press any key to go back", game_screen.text_font, bs * 1.3),
        ]
        for text, font, dy in lines:
            w = font.size(text)[0]
            draw_text(text, font, WHITE, cx - w / 2, cy + dy, game_screen.surface)

        pygame.display.update()
        clock.tick(60)
