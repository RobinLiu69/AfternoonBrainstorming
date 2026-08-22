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

"""Read-only look at the deck, the bench and the relics.

Reachable from the map at any time, so the player never has to remember what
they are carrying.  Hovering a card shows its enchantment; [F] adds the full
card hint and spells out every relic.
"""

import pygame

from shared import card_code
from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.card_hint import HintBox
from core.setting_config import load_setting
from utils.controls import key_pressed

from tower import card_picker, card_pool, run_state, ui_common


def main(game_screen: GameScreen, run: dict) -> None:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    hint_box = HintBox(width=int(bs * 3), height=int(bs))
    hint_on = load_setting("hint_on")
    back = ui_common.back_button(game_screen, "back")

    columns = 3
    col_w = bs * 2.3
    grid_x = cx - bs * 3.9
    grid_y = cy - bs * 1.5
    row_h = bs * 0.34

    entries = [("deck", i, code) for i, code in enumerate(run["deck"])]
    entries += [("bench", i, code) for i, code in enumerate(run["bench"])]

    def rect_for(slot: int) -> pygame.Rect:
        col, row = slot % columns, slot // columns
        return pygame.Rect(int(grid_x + col * col_w), int(grid_y + row * row_h),
                           int(col_w - bs * 0.1), int(row_h - bs * 0.04))

    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        hovered = ""
        for slot, (_zone, _index, code) in enumerate(entries):
            if rect_for(slot).collidepoint(mouse_x, mouse_y):
                hovered = code

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key in (pygame.K_ESCAPE, pygame.K_d):
                    running = False
                if key == pygame.K_f:
                    hint_on = not hint_on
            if event.type == pygame.MOUSEBUTTONDOWN and back.touch(mouse_x, mouse_y):
                running = False
            if event.type == pygame.QUIT:
                raise QuitGame

        ui_common.draw_run_bar(game_screen, run)

        draw_text("Your warband", game_screen.title_text_font, WHITE,
                  grid_x, cy - bs * 2.5, game_screen.surface)
        draw_text(f"deck {len(run['deck'])}/{run_state.deck_limit(run)}"
                  f"    bench {len(run['bench'])}/{run_state.bench_limit(run)}"
                  f"    [F] details",
                  game_screen.mid_text_font, ui_common.GOLD,
                  grid_x, cy - bs * 1.95, game_screen.surface)

        for slot, (zone, _index, code) in enumerate(entries):
            rect = rect_for(slot)
            color = (card_picker.BENCH_COLOR if zone == "bench"
                     else card_picker.ENCHANT_COLOR if card_code.is_enchanted(code)
                     else WHITE)
            label = card_pool.display_name(code)
            if zone == "bench":
                label = f"[bench] {label}"
            ui_common.draw_auto(game_screen, label, "text_font", color, rect.x, rect.y)
            if code == hovered:
                pygame.draw.rect(game_screen.surface, ui_common.HILITE, rect,
                                 ui_common.box_width(game_screen))


        if hovered:
            y = cy + bs * 1.9
            for line in ui_common.wrap_all(card_pool.enchant_lines(hovered),
                                           ui_common.PANEL_WRAP):
                ui_common.draw_auto(game_screen, line, "mid_text_font",
                                    card_picker.ENCHANT_COLOR, grid_x, y)
                y += bs * 0.32

        back.update(game_screen)
        hint_box.turn_on = hint_on
        if hint_on and hovered:
            hint_box.update(mouse_x, mouse_y, hovered, game_screen)

        ui_common.draw_relic_strip(game_screen, run, detailed=hint_on)
        pygame.display.update()
        clock.tick(60)

