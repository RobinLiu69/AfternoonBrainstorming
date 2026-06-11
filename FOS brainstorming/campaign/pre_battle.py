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

from campaign.ai_decks import (
    STAGE_AI_DECKS, STAGE_PLAYER_DECKS, STAGE_LABELS, STAGE_DIFFICULTY,
)
from campaign.boss_config import STAGE_BUFF_TEXT


def main(game_screen: GameScreen, stage: str) -> Optional[str]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    start_button = Button(
        bs * 1.5, bs * 0.6, cx - bs * 0.75, cy + bs * 2,
        bs * 0.4, bs * 0.15,
        box_width=box_width, font=game_screen.big_big_text_font, text="start",
    )
    back_button = Button(
        bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
        bs * 0.55, bs * 0.2,
        box_width=box_width, font=game_screen.big_text_font, text="back",
    )

    result: Optional[str] = None
    clock = pygame.time.Clock()

    ai_deck = STAGE_AI_DECKS[stage]
    player_deck = STAGE_PLAYER_DECKS[stage]
    label = STAGE_LABELS.get(stage, stage)
    difficulty = STAGE_DIFFICULTY.get(stage, "normal").upper()
    buff_text = STAGE_BUFF_TEXT.get(stage, "")

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

        draw_text(label, game_screen.title_text_font, WHITE,
                  cx - bs * 2.5, cy - bs * 3.0, game_screen.surface)
        draw_text(f"difficulty: {difficulty}", game_screen.big_text_font, WHITE,
                  cx - bs * 2.5, cy - bs * 1.9, game_screen.surface)

        _draw_deck("AI deck:", ai_deck, cx - bs * 2.5, cy - bs * 1.2, game_screen)
        _draw_deck("Your deck:", player_deck, cx - bs * 2.5, cy + bs * 0.6, game_screen)

        if buff_text:
            draw_text("special rules:", game_screen.big_text_font, (255, 100, 100),
                      cx + bs * 1.0, cy - bs * 1.9, game_screen.surface)
            for i, line in enumerate(buff_text.split("\n")):
                draw_text(line, game_screen.mid_text_font, (255, 200, 200),
                          cx + bs * 1.0, cy - bs * 1.3 + i * bs * 0.45, game_screen.surface)

        start_button.update(game_screen)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return result


def _draw_deck(title: str, deck: list[str], x: float, y: float, game_screen: GameScreen) -> None:
    draw_text(title, game_screen.big_text_font, WHITE, x, y, game_screen.surface)
    bs = game_screen.block_size
    line_y = y + bs * 0.5
    chunk = " ".join(deck[:6])
    chunk2 = " ".join(deck[6:])
    draw_text(chunk, game_screen.mid_text_font, WHITE, x, line_y, game_screen.surface)
    draw_text(chunk2, game_screen.mid_text_font, WHITE, x, line_y + bs * 0.4, game_screen.surface)
