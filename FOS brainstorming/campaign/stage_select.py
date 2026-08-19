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
from rendering import style
from core.UI import Button
from utils.controls import key_pressed

from campaign.ai_decks import STAGE_ORDER, STAGE_LABELS
from campaign import campaign_save
from screens.widgets import make_back_button

from collections import deque


LOCKED_COLOR: tuple[int, int, int] = style.INK_DISABLED
CLEARED_COLOR: tuple[int, int, int] = style.INK_MUTED


def stage_label(stage: str, unlocked: set[str], cleared: set[str]) -> tuple[str, tuple[int, int, int]]:
    label = STAGE_LABELS.get(stage, stage)
    if stage not in unlocked:
        return f"[LOCKED]  {label}", LOCKED_COLOR
    if stage in cleared:
        return f"{label}  *", CLEARED_COLOR
    return f"{label}  <", WHITE


def make_buttons(game_screen: GameScreen, unlocked: set[str],
                 cleared: set[str]) -> list[tuple[Button, str, bool]]:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    main_w, main_h = bs * 3.5, bs * 0.6
    start_y = cy - bs * 1.8
    box_width = int(bs / 30)

    buttons: list[tuple[Button, str, bool]] = []
    for i, stage in enumerate(STAGE_ORDER):
        label, colour = stage_label(stage, unlocked, cleared)
        buttons.append((
            Button(main_w, main_h, cx - main_w / 2,
                   start_y + i * (main_h + bs * 0.15),
                   position="Left", padding=bs * 0.25, box_width=box_width,
                   font=game_screen.big_text_font, text=label,
                   text_color=colour, box_color=colour),
            stage, stage in unlocked))
    return buttons


def render(game_screen: GameScreen, buttons: list[tuple[Button, str, bool]],
           back_button: Button) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    style.title(game_screen, "Campaign", cy - bs * 2.7)
    style.muted_text(game_screen, "*  cleared          <  next up",
                     cx - bs * 1.05, cy - bs * 2.15, game_screen.text_font)
    for button, _stage, _unlocked in buttons:
        button.update(game_screen)
    back_button.update(game_screen)


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

    buttons = make_buttons(game_screen, unlocked, cleared)
    back_button = make_back_button(game_screen, text="back", corner="top_left")

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
                raise QuitGame
        render(game_screen, buttons, back_button)

        pygame.display.update()
        clock.tick(60)

    return selected