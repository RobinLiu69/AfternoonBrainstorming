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

"""A titled message with a continue button."""

from typing import Optional, Sequence

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from utils.controls import key_pressed
from core.UI import Button

from tower import ui_common


def render(game_screen: GameScreen, title: str, lines: Sequence[str],
           run: Optional[dict], color: Sequence[int], button, hint_on: bool) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    if run is not None:
        ui_common.draw_run_bar(game_screen, run)

    ui_common.draw_auto(game_screen, title, "title_text_font", color,
                        cx - bs * 2.6, cy - bs * 1.6)
    y = cy - bs * 0.7
    for line in lines:
        ui_common.draw_auto(game_screen, line, "big_text_font", WHITE,
                            cx - bs * 2.6, y)
        y += bs * 0.45

    button.update(game_screen)
    if run is not None:
        ui_common.draw_relic_strip(game_screen, run, detailed=hint_on)


def main(game_screen: GameScreen, title: str, lines: Sequence[str],
         run: Optional[dict] = None, color: Sequence[int] = WHITE,
         button_text: str = "continue") -> None:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    button = Button(bs * 2.2, bs * 0.6, cx - bs * 1.1, cy + bs * 1.6,
                    box_width=ui_common.box_width(game_screen),
                    font=game_screen.big_text_font, text=button_text)
    clock = pygame.time.Clock()
    hint_on = False

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key == pygame.K_f:
                    hint_on = not hint_on
                elif key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN and button.touch(mouse_x, mouse_y):
                running = False
            if event.type == pygame.QUIT:
                raise QuitGame

        render(game_screen, title, lines, run, color, button, hint_on)
        pygame.display.update()
        clock.tick(60)
