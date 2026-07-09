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

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from utils.controls import key_pressed


TEMP_COLOR: tuple[int, int, int] = (255, 170, 60)


def main(game_screen: GameScreen, run: dict, title: str) -> Optional[tuple[str, int]]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    entries: list[tuple[str, int, str]] = []
    for i, code in enumerate(run["deck"]):
        entries.append(("deck", i, code))
    for i, code in enumerate(run["temp_deck"]):
        entries.append(("temp", i, code))

    columns = 4
    btn_w, btn_h = bs * 1.6, bs * 0.45
    grid_w = columns * (btn_w + bs * 0.15) - bs * 0.15
    start_x = cx - grid_w / 2
    start_y = cy - bs * 1.9

    buttons: list[tuple[Button, str, int]] = []
    for idx, (source, i, code) in enumerate(entries):
        col = idx % columns
        row = idx // columns
        label = code if source == "deck" else f"{code} *"
        color = WHITE if source == "deck" else TEMP_COLOR
        btn = Button(btn_w, btn_h, start_x + col * (btn_w + bs * 0.15), start_y + row * (btn_h + bs * 0.1),
                     position="Left", padding=bs * 0.15,
                     box_width=box_width, font=game_screen.text_font,
                     text=label, text_color=color, box_color=color)
        buttons.append((btn, source, i))

    cancel_button = Button(bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
                           box_width=box_width, font=game_screen.big_text_font, text="cancel")

    selected: Optional[tuple[str, int]] = None
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
                if cancel_button.touch(mouse_x, mouse_y):
                    running = False
                for btn, source, i in buttons:
                    if btn.touch(mouse_x, mouse_y):
                        selected = (source, i)
                        running = False
            if event.type == pygame.QUIT:
                running = False

        draw_text(title, game_screen.big_big_text_font, WHITE,
                  cx - bs * 2.0, cy - bs * 2.7, game_screen.surface)
        draw_text("* = temporary card", game_screen.text_font, TEMP_COLOR,
                  cx + bs * 1.2, cy - bs * 2.5, game_screen.surface)

        for btn, _source, _i in buttons:
            btn.update(game_screen)
        cancel_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return selected
