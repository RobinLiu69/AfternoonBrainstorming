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


def main(game_screen: GameScreen, host_ip: str, reason: str) -> None:
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

        draw_text("Connection Failed",
                  game_screen.big_text_font, WHITE,
                  cx - bs * 2.6, cy - bs * 1.4, game_screen.surface)

        draw_text(f"Host :  {host_ip}",
                  game_screen.mid_text_font, WHITE,
                  cx - bs * 2.0, cy - bs * 0.4, game_screen.surface)

        draw_text(reason,
                  game_screen.mid_text_font, WHITE,
                  cx - bs * 2.0, cy + bs * 0.2, game_screen.surface)

        draw_text("Press any key to go back",
                  game_screen.text_font, WHITE,
                  cx - bs * 1.3, cy + bs * 1.2, game_screen.surface)

        pygame.display.update()
        clock.tick(60)
