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

from shared.setting import WHITE, CYAN
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from utils.controls import key_pressed


GOLD: tuple[int, int, int] = (255, 215, 0)


def main(game_screen: GameScreen, state: dict) -> Optional[str]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    run = state.get("run")
    btn_w, btn_h = bs * 3.0, bs * 0.6
    btn_x = cx - btn_w / 2

    buttons: list[tuple[str, Button]] = []
    y = cy - bs * 1.2
    if run:
        label = f"continue  (floor {run['floor']})"
        buttons.append(("continue", Button(btn_w, btn_h, btn_x, y,
                                           bs * 0.25, bs * 0.15,
                                           box_width=box_width, font=game_screen.big_text_font,
                                           text=label, text_color=CYAN, box_color=CYAN)))
        y += btn_h + bs * 0.2
    new_label = "new climb" if not run else "new climb  (abandon current)"
    buttons.append(("new", Button(btn_w, btn_h, btn_x, y,
                                  bs * 0.25, bs * 0.15,
                                  box_width=box_width, font=game_screen.big_text_font,
                                  text=new_label)))

    back_button = Button(bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
                         bs * 0.55, bs * 0.2,
                         box_width=box_width, font=game_screen.big_text_font, text="back")

    selected: Optional[str] = None
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
                if back_button.touch(mouse_x, mouse_y):
                    running = False
                for name, btn in buttons:
                    if btn.touch(mouse_x, mouse_y):
                        selected = name
                        running = False
            if event.type == pygame.QUIT:
                running = False

        draw_text("Endless Tower", game_screen.title_text_font, WHITE,
                  cx - bs * 1.6, cy - bs * 2.7, game_screen.surface)
        best = state.get("best_floor", 0)
        runs = state.get("runs_played", 0)
        draw_text(f"best: {best} floors cleared    climbs: {runs}",
                  game_screen.big_text_font, GOLD,
                  cx - bs * 1.6, cy - bs * 1.9, game_screen.surface)

        for _name, btn in buttons:
            btn.update(game_screen)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return selected
