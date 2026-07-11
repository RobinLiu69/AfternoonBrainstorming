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

from campaign.ai_decks import STAGE_ORDER, STAGE_LABELS
from campaign import campaign_save

from collections import deque


LOCKED_COLOR: tuple[int, int, int] = (90, 90, 90)
CLEARED_COLOR: tuple[int, int, int] = (255, 215, 0)


def main(game_screen: GameScreen) -> Optional[str]:
    running = True
    box_width: int = int(game_screen.block_size / 30)
    
    target = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
              pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, 
              pygame.K_b, pygame.K_a]
    
    buffer = deque(maxlen=len(target))

    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    state = campaign_save.load()
    unlocked = set(state.get("unlocked", []))
    cleared = set(state.get("cleared", []))

    main_w, main_h = bs * 3.5, bs * 0.6
    main_x = cx - main_w / 2
    text_x = bs * 0.25
    text_y = bs * 0.15

    buttons: list[tuple[Button, str, bool]] = []
    start_y = cy - bs * 1.8
    for i, stage in enumerate(STAGE_ORDER):
        label = STAGE_LABELS.get(stage, stage)
        if stage in cleared:
            label = f"{label}  *"
        if stage not in unlocked:
            label = f"[LOCKED]  {STAGE_LABELS.get(stage, stage)}"
        color = WHITE
        if stage not in unlocked:
            color = LOCKED_COLOR
        elif stage in cleared:
            color = CLEARED_COLOR
        btn = Button(
            main_w, main_h, main_x, start_y + i * (main_h + bs * 0.15),
            text_x, text_y,
            box_width=box_width, font=game_screen.big_text_font,
            text=label, text_color=color, box_color=color,
        )
        buttons.append((btn, stage, stage in unlocked))

    back_button = Button(
        bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
        bs * 0.55, bs * 0.2,
        box_width=box_width, font=game_screen.big_text_font, text="back",
    )

    selected: Optional[str] = None
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                buffer.append(event.key)
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE:
                    running = False
                if list(buffer) == target:
                    for i, stage in enumerate(STAGE_ORDER):
                        campaign_save.mark_cleared(stage)
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.touch(mouse_x, mouse_y):
                    running = False
                for btn, stage, is_unlocked in buttons:
                    if btn.touch(mouse_x, mouse_y) and is_unlocked:
                        selected = stage
                        running = False
            if event.type == pygame.QUIT:
                running = False

        draw_text("Campaign", game_screen.title_text_font, WHITE,
                  cx - bs * 0.875, cy - bs * 2.7, game_screen.surface)
        draw_text("* = cleared", game_screen.text_font, CLEARED_COLOR,
                  cx - bs * 0.3, cy - bs * 2.1, game_screen.surface)

        for btn, _stage, _u in buttons:
            btn.update(game_screen)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return selected