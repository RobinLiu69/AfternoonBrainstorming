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
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from utils.controls import key_pressed

from tower import ui_common
from tower.content import FACTION_NAMES


def make_buttons(game_screen: GameScreen, state: dict) -> list[tuple[str, Button]]:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width = ui_common.box_width(game_screen)

    run = state.get("run")
    btn_w, btn_h = bs * 3.4, bs * 0.6
    btn_x = cx - btn_w / 2

    buttons: list[tuple[str, Button]] = []
    y = cy - bs * 0.8
    if run:
        buttons.append(("continue", Button(
            btn_w, btn_h, btn_x, y, box_width=box_width,
            font=game_screen.big_text_font, text_color=CYAN, box_color=CYAN,
            text=f"continue  (act {run['act']}, layer {run['layer']})")))
        y += btn_h + bs * 0.25
    buttons.append(("new", Button(
        btn_w, btn_h, btn_x, y, box_width=box_width, font=game_screen.big_text_font,
        text="new climb" if not run else "new climb  (abandon current)")))
    return buttons


def render(game_screen: GameScreen, state: dict,
           buttons: list[tuple[str, Button]], back: Button) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    run = state.get("run")

    draw_text("Tower", game_screen.title_text_font, WHITE,
              cx - bs * 0.9, cy - bs * 2.7, game_screen.surface)
    best_act = state.get("best_act", 0)
    best_layer = state.get("best_layer", 0)
    best = f"act {best_act} layer {best_layer}" if best_act else "none yet"
    draw_text(f"best: {best}    climbs: {state.get('runs_played', 0)}",
              game_screen.big_text_font, ui_common.GOLD,
              cx - bs * 1.9, cy - bs * 1.9, game_screen.surface)

    if run:
        names = ", ".join(FACTION_NAMES[t] for t in run.get("factions", []))
        draw_text(f"factions: White, {names}", game_screen.text_font, WHITE,
                  cx - bs * 1.9, cy - bs * 1.4, game_screen.surface)

    for _name, btn in buttons:
        btn.update(game_screen)
    back.update(game_screen)


def main(game_screen: GameScreen, state: dict) -> Optional[str]:
    running = True
    buttons = make_buttons(game_screen, state)

    back = ui_common.back_button(game_screen)
    selected: Optional[str] = None
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if key_pressed(pygame.key.get_pressed()) == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.touch(mouse_x, mouse_y):
                    running = False
                for name, btn in buttons:
                    if btn.touch(mouse_x, mouse_y):
                        selected = name
                        running = False
            if event.type == pygame.QUIT:
                raise QuitGame

        render(game_screen, state, buttons, back)

        pygame.display.update()
        clock.tick(60)

    return selected
