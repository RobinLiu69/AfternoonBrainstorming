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

from shared.setting import WHITE, CYAN
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from core.display_config import save_display_mode
from utils.controls import key_pressed


OPTIONS: list[tuple[str, str]] = [
    ("60", "window 60%"),
    ("80", "window 80%"),
    ("100", "window 100%"),
    ("fullscreen", "fullscreen"),
]


def _build_buttons(game_screen: GameScreen) -> tuple[list[tuple[str, Button]], Button]:
    bs = game_screen.block_size
    box_width = int(bs / 30)
    cx = game_screen.display_width / 2

    btn_w, btn_h = bs * 2.6, bs * 0.7
    btn_x = cx - btn_w / 2
    top_y = game_screen.display_height / 2 - bs * 1.8

    option_buttons: list[tuple[str, Button]] = []
    for index, (mode, label) in enumerate(OPTIONS):
        color = CYAN if mode == game_screen.display_mode else WHITE
        button = Button(btn_w, btn_h, btn_x, top_y + index * bs * 0.9,
                        bs * 0.25, bs * 0.18,
                        box_color=color, box_width=box_width, text_color=color,
                        font=game_screen.big_big_text_font, text=label)
        option_buttons.append((mode, button))

    back_button = Button(btn_w, btn_h, btn_x, top_y + len(OPTIONS) * bs * 0.9 + bs * 0.35,
                         bs * 1.0, bs * 0.18,
                         box_width=box_width, font=game_screen.big_big_text_font, text="back")
    return option_buttons, back_button


def main(game_screen: GameScreen) -> None:
    option_buttons, back_button = _build_buttons(game_screen)

    running = True
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for mode, button in option_buttons:
                    if button.touch(mouse_x, mouse_y) and mode != game_screen.display_mode:
                        save_display_mode(mode)
                        game_screen.apply_display_mode(mode)
                        option_buttons, back_button = _build_buttons(game_screen)
                        break
                if back_button.touch(mouse_x, mouse_y):
                    running = False
            if event.type == pygame.QUIT:
                running = False

        bs = game_screen.block_size
        cx = game_screen.display_width / 2
        title = "display settings"
        title_width = game_screen.title_text_font.size(title)[0]
        draw_text(title, game_screen.title_text_font, WHITE,
                  cx - title_width / 2, game_screen.display_height / 2 - bs * 2.7, game_screen.surface)

        for _mode, button in option_buttons:
            button.update(game_screen)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)
