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

from endless.content import effect_lines, MUTATIONS


KIND_COLORS: dict[str, tuple[int, int, int]] = {
    "normal": WHITE,
    "elite": (255, 140, 0),
    "boss": (255, 60, 60),
    "mutation": (190, 90, 255),
}


def main(game_screen: GameScreen, spec: dict, ai_fx: dict, player_fx: dict) -> Optional[str]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    start_button = Button(bs * 1.5, bs * 0.6, cx - bs * 0.75, cy + bs * 2,
                          bs * 0.4, bs * 0.15,
                          box_width=box_width, font=game_screen.big_big_text_font, text="start")
    back_button = Button(bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
                         bs * 0.55, bs * 0.2,
                         box_width=box_width, font=game_screen.big_text_font, text="back")

    result: Optional[str] = None
    clock = pygame.time.Clock()

    kind_color = KIND_COLORS.get(spec["kind"], WHITE)
    ai_lines = effect_lines(ai_fx, "AI")
    player_lines = effect_lines(player_fx, "You")
    mutation_lines = []
    if spec.get("mutation_name"):
        mutation_lines.append(MUTATIONS[spec["mutation_name"]]["text"])

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE:
                    result = "back"
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.touch(mouse_x, mouse_y):
                    result = "start"
                    running = False
                if back_button.touch(mouse_x, mouse_y):
                    result = "back"
                    running = False
            if event.type == pygame.QUIT:
                running = False

        draw_text(spec["label"], game_screen.title_text_font, kind_color,
                  cx - bs * 2.5, cy - bs * 3.0, game_screen.surface)

        _draw_deck("AI deck:", spec["ai_deck"], cx - bs * 2.5, cy - bs * 1.9, game_screen)

        y = cy - bs * 0.3
        if mutation_lines:
            draw_text("mutation:", game_screen.big_text_font, KIND_COLORS["mutation"],
                      cx - bs * 2.5, y, game_screen.surface)
            for line in mutation_lines:
                y += bs * 0.45
                draw_text(line, game_screen.mid_text_font, KIND_COLORS["mutation"],
                          cx - bs * 2.5, y, game_screen.surface)
            y += bs * 0.6

        if ai_lines:
            draw_text("enemy buffs:", game_screen.big_text_font, (255, 100, 100),
                      cx + bs * 1.0, cy - bs * 1.9, game_screen.surface)
            for i, line in enumerate(ai_lines):
                draw_text(line, game_screen.mid_text_font, (255, 200, 200),
                          cx + bs * 1.0, cy - bs * 1.3 + i * bs * 0.45, game_screen.surface)

        if player_lines:
            draw_text("your buffs:", game_screen.big_text_font, (100, 255, 140),
                      cx + bs * 1.0, cy + bs * 0.2, game_screen.surface)
            for i, line in enumerate(player_lines):
                draw_text(line, game_screen.mid_text_font, (190, 255, 200),
                          cx + bs * 1.0, cy + bs * 0.8 + i * bs * 0.45, game_screen.surface)

        start_button.update(game_screen)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return result


def _draw_deck(title: str, deck: list[str], x: float, y: float, game_screen: GameScreen) -> None:
    draw_text(title, game_screen.big_text_font, WHITE, x, y, game_screen.surface)
    bs = game_screen.block_size
    line_y = y + bs * 0.5
    draw_text(" ".join(deck[:6]), game_screen.mid_text_font, WHITE, x, line_y, game_screen.surface)
    draw_text(" ".join(deck[6:]), game_screen.mid_text_font, WHITE, x, line_y + bs * 0.4, game_screen.surface)
