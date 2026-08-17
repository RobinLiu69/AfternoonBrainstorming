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

"""Pick the four factions that may show up during a climb."""

from typing import Optional

import pygame

from shared.setting import WHITE, JOB_DICTIONARY
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from utils.controls import key_pressed

from tower import ui_common
from tower.content import (
    FACTION_BLURBS, FACTION_NAMES, FACTION_PICK_COUNT, SELECTABLE_FACTIONS,
)


def _faction_color(tag: str) -> tuple[int, int, int]:
    r, g, b = JOB_DICTIONARY["RGB_colors"][FACTION_NAMES[tag]]
    return (r, g, b)


def main(game_screen: GameScreen) -> Optional[list[str]]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width = ui_common.box_width(game_screen)

    chosen: list[str] = []
    columns = 2
    btn_w, btn_h = bs * 3.2, bs * 0.55
    grid_w = columns * (btn_w + bs * 0.2) - bs * 0.2
    start_x = cx - grid_w / 2
    start_y = cy - bs * 1.6

    def rect_for(index: int) -> tuple[float, float]:
        col, row = index % columns, index // columns
        return start_x + col * (btn_w + bs * 0.2), start_y + row * (btn_h + bs * 0.15)

    def build() -> list[tuple[Button, str]]:
        out: list[tuple[Button, str]] = []
        for i, tag in enumerate(SELECTABLE_FACTIONS):
            x, y = rect_for(i)
            picked = tag in chosen
            color = _faction_color(tag) if picked else WHITE
            order = f"{chosen.index(tag) + 1}. " if picked else ""
            label = f"{order}{FACTION_NAMES[tag]}  -  {FACTION_BLURBS.get(tag, '')}"
            out.append((Button(btn_w, btn_h, x, y, position="Left", padding=bs * 0.15,
                               box_width=box_width, font=game_screen.text_font,
                               text=label, text_color=color, box_color=color), tag))
        return out

    buttons = build()
    confirm = Button(bs * 2.4, bs * 0.6, cx - bs * 1.2, cy + bs * 1.9,
                     box_width=box_width, font=game_screen.big_text_font, text="start climb")
    back = ui_common.back_button(game_screen, "cancel")

    result: Optional[list[str]] = None
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        ready = len(chosen) == FACTION_PICK_COUNT

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if key_pressed(pygame.key.get_pressed()) == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.touch(mouse_x, mouse_y):
                    running = False
                elif ready and confirm.touch(mouse_x, mouse_y):
                    result = list(chosen)
                    running = False
                else:
                    for btn, tag in buttons:
                        if btn.touch(mouse_x, mouse_y):
                            if tag in chosen:
                                chosen.remove(tag)
                            elif len(chosen) < FACTION_PICK_COUNT:
                                chosen.append(tag)
                            buttons = build()
                            break
            if event.type == pygame.QUIT:
                raise QuitGame

        draw_text("Choose your factions", game_screen.title_text_font, WHITE,
                  cx - bs * 2.6, cy - bs * 2.9, game_screen.surface)
        draw_text(f"White is always in. Pick {FACTION_PICK_COUNT} more - "
                  "cards, shops and enemies all come from them.",
                  game_screen.text_font, WHITE,
                  cx - bs * 3.4, cy - bs * 2.1, game_screen.surface)

        for btn, _tag in buttons:
            btn.update(game_screen)

        confirm.text_color = WHITE if ready else ui_common.DIM
        confirm.box_color = WHITE if ready else ui_common.DIM
        confirm.text = "start climb" if ready else f"{len(chosen)}/{FACTION_PICK_COUNT} chosen"
        confirm.update(game_screen)
        back.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return result
