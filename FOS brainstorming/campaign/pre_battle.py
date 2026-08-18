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
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from rendering import style
from utils.controls import key_pressed

from campaign.ai_decks import (
    STAGE_AI_DECKS, STAGE_PLAYER_DECKS, STAGE_LABELS, STAGE_DIFFICULTY,
)
from campaign.boss_config import STAGE_BUFF_TEXT


def _render(game_screen: GameScreen, label: str, difficulty: str,
            ai_deck: list[str], player_deck: list[str], buff_text: str) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    pad = bs * style.PANEL_PAD

    single = not buff_text
    left_x = cx - bs * (PANEL_W / 2) if single else cx - bs * 3.75
    title_w = game_screen.title_text_font.size(label)[0]
    draw_text(label, game_screen.title_text_font, style.INK,
              cx - title_w / 2, cy - bs * 3.0, game_screen.surface)
    note = f"difficulty: {difficulty}"
    note_w = game_screen.mid_text_font.size(note)[0]
    style.muted_text(game_screen, note, cx - note_w / 2, cy - bs * 2.3,
                     game_screen.mid_text_font)

    top = cy - bs * 1.75
    used = _draw_deck("AI DECK", ai_deck, left_x, top, game_screen)
    _draw_deck("YOUR DECK", player_deck, left_x, top + used + bs * 0.3, game_screen)

    if buff_text:
        lines = buff_text.splitlines()
        right_x = cx + bs * 0.15
        height = bs * style.HEADER_HEIGHT + pad + bs * 0.45 * len(lines) + pad * 0.6
        style.section(game_screen, "SPECIAL RULES", right_x, top, bs * PANEL_W, height)
        line_y = top + bs * style.HEADER_HEIGHT + pad
        for line in lines:
            draw_text(line, game_screen.mid_text_font, style.INK,
                      right_x + pad, line_y, game_screen.surface)
            line_y += bs * 0.45


def main(game_screen: GameScreen, stage: str) -> Optional[str]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    start_button = Button(
        bs * 1.5, bs * 0.6, cx - bs * 0.75, cy + bs * 2,
        box_width=box_width, font=game_screen.big_big_text_font, text="start",
    )
    back_button = Button(
        bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
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
                raise QuitGame
        _render(game_screen, label, difficulty, ai_deck, player_deck, buff_text)

        start_button.update(game_screen)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return result


PANEL_W = 3.6
DECK_ROWS = 6


def _deck_lines(deck: list[str]) -> list[str]:
    return [" ".join(deck[i:i + DECK_ROWS]) for i in range(0, len(deck), DECK_ROWS)]


def _draw_deck(title: str, deck: list[str], x: float, y: float,
               game_screen: GameScreen) -> float:
    bs = game_screen.block_size
    pad = bs * style.PANEL_PAD
    lines = _deck_lines(deck)
    height = bs * style.HEADER_HEIGHT + pad + bs * 0.36 * len(lines) + pad * 0.6

    style.section(game_screen, title, x, y, bs * PANEL_W, height,
                  right=f"{len(deck)} cards")
    line_y = y + bs * style.HEADER_HEIGHT + pad
    for line in lines:
        draw_text(line, game_screen.mid_text_font, style.INK,
                  x + pad, line_y, game_screen.surface)
        line_y += bs * 0.36
    return height
