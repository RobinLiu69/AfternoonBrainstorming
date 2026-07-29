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

"""Pick one card out of the deck and bench.  Returns ``(zone, index)``."""

from typing import Callable, Optional

import pygame

from shared import card_code
from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from core.card_hint import HintBox
from core.setting_config import load_setting
from utils.controls import key_pressed

from tower import card_pool, ui_common

BENCH_COLOR: tuple[int, int, int] = (255, 170, 60)
ENCHANT_COLOR: tuple[int, int, int] = (170, 230, 255)


def _entry_color(zone: str, code: str) -> tuple[int, int, int]:
    if card_code.is_enchanted(code):
        return ENCHANT_COLOR
    return BENCH_COLOR if zone == "bench" else WHITE


def main(game_screen: GameScreen, run: dict, title: str,
         subtitle: str = "", cancellable: bool = True,
         allowed: Optional[Callable[[str, int, str], bool]] = None,
         ) -> Optional[tuple[str, int]]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width = ui_common.box_width(game_screen)

    hint_box = HintBox(width=int(bs * 3), height=int(bs))
    hint_on = load_setting("hint_on")

    entries: list[tuple[str, int, str]] = []
    entries += [("deck", i, code) for i, code in enumerate(run["deck"])]
    entries += [("bench", i, code) for i, code in enumerate(run["bench"])]

    # a Limit Break deck needs more columns, or the grid runs off the bottom
    columns = 4 if len(entries) <= 16 else 6
    btn_w = min(bs * 2.0, bs * 9.0 / columns - bs * 0.15)
    btn_h = bs * 0.45
    grid_w = columns * (btn_w + bs * 0.15) - bs * 0.15
    start_x = cx - grid_w / 2
    start_y = cy - bs * 1.7

    buttons: list[tuple[Button, str, int, str, bool]] = []
    for slot, (zone, index, code) in enumerate(entries):
        col, row = slot % columns, slot // columns
        usable = allowed is None or allowed(zone, index, code)
        color = _entry_color(zone, code) if usable else ui_common.DIM
        label = card_pool.display_name(code)
        if zone == "bench":
            label = f"[bench] {label}"
        btn = Button(btn_w, btn_h,
                     start_x + col * (btn_w + bs * 0.15),
                     start_y + row * (btn_h + bs * 0.12),
                     position="Left", padding=bs * 0.12, box_width=box_width,
                     font=game_screen.small_text_font,
                     text=label, text_color=color, box_color=color)
        buttons.append((btn, zone, index, code, usable))

    cancel = ui_common.back_button(game_screen, "cancel") if cancellable else None

    selected: Optional[tuple[str, int]] = None
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        hovered_code = ""
        for btn, _zone, _index, code, usable in buttons:
            if usable and btn.touch(mouse_x, mouse_y):
                hovered_code = code

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key == pygame.K_ESCAPE:
                    running = False
                if key == pygame.K_f:
                    hint_on = not hint_on
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cancel is not None and cancel.touch(mouse_x, mouse_y):
                    running = False
                else:
                    for btn, zone, index, _code, usable in buttons:
                        if usable and btn.touch(mouse_x, mouse_y):
                            selected = (zone, index)
                            running = False
                            break
            if event.type == pygame.QUIT:
                raise QuitGame

        ui_common.draw_run_bar(game_screen, run)
        draw_text(title, game_screen.big_big_text_font, WHITE,
                  cx - bs * 3.4, cy - bs * 2.6, game_screen.surface)
        if subtitle:
            draw_text(subtitle, game_screen.text_font, ui_common.GOLD,
                      cx - bs * 3.4, cy - bs * 2.1, game_screen.surface)

        for btn, _zone, _index, _code, _usable in buttons:
            btn.update(game_screen)
        if cancel is not None:
            cancel.update(game_screen)

        if hovered_code:
            lines = card_pool.enchant_lines(hovered_code)[:3]
            y = cy + bs * 1.25
            for line in lines:
                draw_text(line, game_screen.text_font, ENCHANT_COLOR,
                          cx - bs * 3.4, y, game_screen.surface)
                y += bs * 0.3

        hint_box.turn_on = hint_on
        if hint_on and hovered_code:
            hint_box.update(mouse_x, mouse_y, card_code.plain_code(hovered_code), game_screen)

        pygame.display.update()
        clock.tick(60)

    return selected
