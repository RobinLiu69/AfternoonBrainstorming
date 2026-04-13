# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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

from __future__ import annotations
from pathlib import Path
from typing import Optional

import pygame

from core.setting import WHITE, FOLDER_PATH
from core.game_screen import GameScreen, draw_text
from core.replay_source import ReplaySource


VISIBLE_ROWS: int = 10


def main(game_screen: GameScreen) -> Optional[Path]:
    battle_records_dir = f"{FOLDER_PATH}/battle_records"
    replays: list[Path] = ReplaySource.list_available_replays(battle_records_dir)

    if not replays:
        return _show_empty_and_wait(game_screen)

    selected: int = 0
    scroll_top: int = 0
    clock = pygame.time.Clock()
    running: bool = True
    chosen: Optional[Path] = None

    while running:
        game_screen.render()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                elif event.key == pygame.K_DOWN:
                    selected = min(len(replays) - 1, selected + 1)
                elif event.key == pygame.K_RETURN:
                    chosen = replays[selected]
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_idx = _row_at(mouse_y, scroll_top, game_screen)
                if clicked_idx is not None and 0 <= clicked_idx < len(replays):
                    if clicked_idx == selected:
                        chosen = replays[selected]
                        running = False
                    else:
                        selected = clicked_idx
            elif event.type == pygame.MOUSEWHEEL:
                scroll_top = max(0, min(len(replays) - VISIBLE_ROWS, scroll_top - event.y))

        if selected < scroll_top:
            scroll_top = selected
        elif selected >= scroll_top + VISIBLE_ROWS:
            scroll_top = selected - VISIBLE_ROWS + 1

        _draw(game_screen, replays, selected, scroll_top)

        pygame.display.update()
        clock.tick(60)

    return chosen


def _row_at(mouse_y: int, scroll_top: int, game_screen: GameScreen) -> Optional[int]:
    list_top = game_screen.display_height / 2 - game_screen.block_size * 1.5
    row_h = game_screen.block_size * 0.35
    if mouse_y < list_top:
        return None
    offset = int((mouse_y - list_top) / row_h)
    if offset >= VISIBLE_ROWS:
        return None
    return scroll_top + offset


def _draw(game_screen: GameScreen, replays: list[Path],
          selected: int, scroll_top: int) -> None:
    cx = game_screen.display_width / 2
    top = game_screen.display_height / 2 - game_screen.block_size * 2.3

    draw_text("Select Replay", game_screen.big_big_text_font, WHITE,
              cx - game_screen.block_size * 1.5, top, game_screen.surface)

    list_top = game_screen.display_height / 2 - game_screen.block_size * 1.5
    row_h = game_screen.block_size * 0.35

    end = min(len(replays), scroll_top + VISIBLE_ROWS)
    for i in range(scroll_top, end):
        path = replays[i]
        is_selected = (i == selected)
        prefix = "> " if is_selected else "  "
        label = f"{prefix}{path.stem}"
        y = list_top + (i - scroll_top) * row_h
        draw_text(label, game_screen.mid_text_font, WHITE,
                  cx - game_screen.block_size * 2.5, y, game_screen.surface)

    footer_y = game_screen.display_height - game_screen.block_size * 0.5
    draw_text("UP/DOWN select    ENTER confirm    ESC back",
              game_screen.mid_text_font, WHITE,
              cx - game_screen.block_size * 2.5, footer_y, game_screen.surface)

    if len(replays) > VISIBLE_ROWS:
        indicator = f"{selected + 1} / {len(replays)}"
        draw_text(indicator, game_screen.mid_text_font, WHITE,
                  cx + game_screen.block_size * 2.5,
                  game_screen.display_height / 2 - game_screen.block_size * 1.5,
                  game_screen.surface)


def _show_empty_and_wait(game_screen: GameScreen) -> None:
    clock = pygame.time.Clock()
    running = True
    while running:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        cx = game_screen.display_width / 2
        cy = game_screen.display_height / 2
        draw_text("No replays found", game_screen.big_big_text_font, WHITE,
                  cx - game_screen.block_size * 1.8, cy - game_screen.block_size * 0.5,
                  game_screen.surface)
        draw_text("Play a local or host game first to record one.",
                  game_screen.mid_text_font, WHITE,
                  cx - game_screen.block_size * 1.5, cy + game_screen.block_size * 0.2,
                  game_screen.surface)
        draw_text("Press any key to exit.",
                  game_screen.mid_text_font, WHITE,
                  cx - game_screen.block_size * 0.9, cy + game_screen.block_size * 0.7,
                  game_screen.surface)

        pygame.display.update()
        clock.tick(60)

    return None