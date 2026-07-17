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
from core.UI import Button
from utils.controls import key_pressed

from endless.content import RELICS


GOLD: tuple[int, int, int] = (255, 215, 0)


def main(game_screen: GameScreen, run: dict, state: dict, floors_cleared: int, new_best: bool) -> None:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    continue_button = Button(bs * 1.5, bs * 0.6, cx - bs * 0.75, cy + bs * 2.2,
                             box_width=box_width, font=game_screen.big_text_font, text="continue")

    relic_names = ", ".join(RELICS[r]["label"] for r in run.get("relics", []) if r in RELICS)
    deck_size = len(run.get("deck", [])) + len(run.get("temp_deck", []))
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if key_pressed(keys) in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.touch(mouse_x, mouse_y):
                    running = False
            if event.type == pygame.QUIT:
                running = False

        draw_text("The tower claims you...", game_screen.title_text_font, (255, 80, 80),
                  cx - bs * 2.3, cy - bs * 2.8, game_screen.surface)
        draw_text(f"fell on floor {run['floor']}", game_screen.big_big_text_font, WHITE,
                  cx - bs * 1.5, cy - bs * 1.6, game_screen.surface)
        draw_text(f"floors cleared: {floors_cleared}", game_screen.big_text_font, WHITE,
                  cx - bs * 1.5, cy - bs * 0.9, game_screen.surface)
        if new_best:
            draw_text("NEW BEST!", game_screen.big_big_text_font, GOLD,
                      cx - bs * 1.5, cy - bs * 0.3, game_screen.surface)
        else:
            draw_text(f"best: {state.get('best_floor', 0)}", game_screen.big_text_font, GOLD,
                      cx - bs * 1.5, cy - bs * 0.3, game_screen.surface)
        draw_text(f"final deck: {deck_size} cards    coins: {run.get('coins', 0)}",
                  game_screen.mid_text_font, WHITE,
                  cx - bs * 1.5, cy + bs * 0.5, game_screen.surface)
        if relic_names:
            draw_text(f"relics: {relic_names}", game_screen.mid_text_font, WHITE,
                      cx - bs * 1.5, cy + bs * 0.95, game_screen.surface)

        continue_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)
