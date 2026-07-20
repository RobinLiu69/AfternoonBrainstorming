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

import subprocess
import sys
from pathlib import Path
from typing import Optional

import pygame

from shared.setting import WHITE, RED, FOLDER_PATH
from core.game_screen import GameScreen, draw_text
from core.replay_source import ReplaySource
from screens.widgets import make_back_button


VISIBLE_ROWS: int = 10
CTRL_OR_CMD: int = pygame.KMOD_CTRL | pygame.KMOD_META


def main(game_screen: GameScreen) -> Optional[Path]:
    battle_records_dir = f"{FOLDER_PATH}/battle_records"
    replays: list[Path] = ReplaySource.list_available_replays(battle_records_dir)

    if not replays:
        return _show_empty_and_wait(game_screen)

    selected: int = 0
    scroll_top: int = 0
    renaming: bool = False
    rename_text: str = ""
    delete_armed: bool = False
    clock = pygame.time.Clock()
    running: bool = True
    chosen: Optional[Path] = None
    back_button = make_back_button(game_screen, text="back", corner="top_left")

    while running:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if renaming:
                    if event.key == pygame.K_RETURN:
                        new_path = _commit_rename(replays[selected], rename_text)
                        if new_path is not None:
                            replays[selected] = new_path
                        renaming = False
                        pygame.key.set_repeat()
                    elif event.key == pygame.K_ESCAPE:
                        renaming = False
                        pygame.key.set_repeat()
                    elif event.key == pygame.K_BACKSPACE:
                        rename_text = rename_text[:-1]
                    elif event.mod & CTRL_OR_CMD:
                        if event.key == pygame.K_c:
                            _clipboard_put(rename_text)
                        elif event.key == pygame.K_v:
                            rename_text += _clipboard_get()
                    elif event.unicode and event.unicode.isprintable():
                        rename_text += event.unicode
                elif event.key == pygame.K_ESCAPE:
                    if delete_armed:
                        delete_armed = False
                    else:
                        running = False
                elif event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                    delete_armed = False
                elif event.key == pygame.K_DOWN:
                    selected = min(len(replays) - 1, selected + 1)
                    delete_armed = False
                elif event.key == pygame.K_RETURN:
                    chosen = replays[selected]
                    running = False
                elif event.key == pygame.K_r:
                    renaming = True
                    rename_text = replays[selected].stem
                    delete_armed = False
                    pygame.key.set_repeat(400, 40)
                elif event.key == pygame.K_d:
                    if delete_armed:
                        _delete_replay(replays[selected])
                        del replays[selected]
                        delete_armed = False
                        if not replays:
                            return _show_empty_and_wait(game_screen)
                        selected = min(selected, len(replays) - 1)
                        scroll_top = max(0, min(scroll_top, len(replays) - VISIBLE_ROWS))
                    else:
                        delete_armed = True
            elif renaming:
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.touch(*event.pos):
                    running = False
                    break
                delete_armed = False
                clicked_idx = _row_at(event.pos[1], scroll_top, game_screen)
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

        _draw(game_screen, replays, selected, scroll_top, renaming, rename_text,
              delete_armed)
        back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    pygame.key.set_repeat()
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


def _clipboard_get() -> str:
    try:
        if sys.platform == "darwin":
            text = subprocess.run(["pbpaste"], capture_output=True,
                                  text=True, timeout=2).stdout
        else:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            data = pygame.scrap.get(pygame.SCRAP_TEXT)
            text = data.decode("utf-8", "ignore") if data else ""
        return "".join(c for c in text if c.isprintable())
    except Exception:
        return ""


def _clipboard_put(text: str) -> None:
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, timeout=2)
        else:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
    except Exception:
        pass


def _commit_rename(path: Path, new_name: str) -> Optional[Path]:
    new_name = "".join(c for c in new_name.strip() if c not in '\\/:*?"<>|')
    if not new_name or new_name == path.stem:
        return None
    new_path = path.with_name(new_name + path.suffix)
    if new_path.exists():
        return None

    log_path = path.with_suffix(".log")
    new_log_path = new_path.with_suffix(".log")
    if log_path.exists() and new_log_path.exists():
        return None

    path.rename(new_path)
    if log_path.exists():
        log_path.rename(new_log_path)
    return new_path


def _delete_replay(path: Path) -> None:
    log_path = path.with_suffix(".log")
    path.unlink(missing_ok=True)
    if log_path.exists():
        log_path.unlink()


def _draw(game_screen: GameScreen, replays: list[Path],
          selected: int, scroll_top: int,
          renaming: bool, rename_text: str,
          delete_armed: bool) -> None:
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
        if is_selected and renaming:
            cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else " "
            label = f"{prefix}{rename_text}{cursor}"
        else:
            label = f"{prefix}{path.stem}"
        color = RED if (is_selected and delete_armed) else WHITE
        y = list_top + (i - scroll_top) * row_h
        draw_text(label, game_screen.mid_text_font, color,
                  cx - game_screen.block_size * 2.5, y, game_screen.surface)

    footer_y = game_screen.display_height - game_screen.block_size * 0.5
    draw_text("UP/DOWN select    ENTER confirm    R rename    D delete    ESC back",
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