# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright 2024-2026 Robin Liu / FOC Studio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------

# screens/join_screen.py
import pygame

from core.setting import WHITE
from core.game_screen import GameScreen, draw_text


def main(game_screen: GameScreen, default: str = "") -> str:
    text = default
    clock = pygame.time.Clock()
    blink = 0

    while True:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ""
                if event.key == pygame.K_RETURN:
                    if text:
                        return text
                    continue
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                    continue

                ch = event.unicode
                if ch and (ch.isdigit() or ch == ".") and len(text) < 21:
                    text += ch

        caret = "_" if (blink // 30) % 2 == 0 else " "
        blink += 1

        cx = game_screen.display_width / 2
        cy = game_screen.display_height / 2

        draw_text("Enter host IP",
                  game_screen.big_text_font, WHITE,
                  cx - game_screen.block_size * 1.2,
                  cy - game_screen.block_size * 1.2,
                  game_screen.surface)

        draw_text(text + caret,
                  game_screen.big_text_font, WHITE,
                  cx - game_screen.block_size * 1.8,
                  cy - game_screen.block_size * 0.1,
                  game_screen.surface)

        draw_text("[Enter] connect    [Esc] cancel",
                  game_screen.text_font, WHITE,
                  cx - game_screen.block_size * 1.6,
                  cy + game_screen.block_size * 1.0,
                  game_screen.surface)
        
        pygame.display.update()
        clock.tick(60)