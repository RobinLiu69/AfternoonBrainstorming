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

from shared.setting import WHITE, CYAN
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from core.setting_config import save_setting, load_setting
from utils.controls import key_pressed


OPTIONS: list[tuple[str, str]] = [
    ("60", "window 60%"),
    ("80", "window 80%"),
    ("100", "window 100%"),
    ("fullscreen", "fullscreen"),
]

TABS: list[tuple[str, str]] = [
    ("display", "display"),
    ("gameplay", "gameplay"),
]


def _build_tab_buttons(game_screen: GameScreen, active_tab: str) -> list[tuple[str, Button]]:
    bs = game_screen.block_size
    box_width = int(bs / 30)
    cx = game_screen.display_width / 2

    btn_w, btn_h = bs * 1.6, bs * 0.5
    total_w = btn_w * len(TABS) + bs * 0.3 * (len(TABS) - 1)
    start_x = cx - total_w / 2
    tab_y = game_screen.display_height / 2 - bs * 2.6

    tab_buttons: list[tuple[str, Button]] = []
    for index, (tab_id, label) in enumerate(TABS):
        color = CYAN if tab_id == active_tab else WHITE
        button = Button(btn_w, btn_h, start_x + index * (btn_w + bs * 0.3), tab_y,
                        box_color=color, box_width=box_width, text_color=color,
                        font=game_screen.big_text_font, text=label)
        tab_buttons.append((tab_id, button))
    return tab_buttons


def _build_display_buttons(game_screen: GameScreen) -> tuple[list[tuple[str, Button]], Button]:
    bs = game_screen.block_size
    box_width = int(bs / 30)
    cx = game_screen.display_width / 2

    btn_w, btn_h = bs * 2.6, bs * 0.7
    btn_x = cx - btn_w / 2
    top_y = game_screen.display_height / 2 - bs * 1.8

    option_buttons: list[tuple[str, Button]] = []
    for index, (mode, label) in enumerate(OPTIONS):
        color = CYAN if mode == game_screen.display_mode else WHITE
        button = Button(btn_w, btn_h, btn_x, top_y + index * bs * 0.9,
                        position="Left", padding=bs * 0.25,
                        box_color=color, box_width=box_width, text_color=color,
                        font=game_screen.big_big_text_font, text=label)
        option_buttons.append((mode, button))

    back_button = Button(btn_w, btn_h, btn_x, top_y + len(OPTIONS) * bs * 0.9 + bs * 0.35,
                         box_width=box_width, font=game_screen.big_big_text_font, text="back")
    return option_buttons, back_button


def _name_label(name: str, editing: bool, caret: str) -> str:
    if editing:
        return f"name : {name}{caret}"
    return f"name : {name if name else '-'}"


def _build_gameplay_buttons(game_screen: GameScreen, hint_on: bool,
                            player_name: str) -> tuple[Button, Button, Button]:
    bs = game_screen.block_size
    box_width = int(bs / 30)
    cx = game_screen.display_width / 2

    btn_w, btn_h = bs * 2.6, bs * 0.7
    btn_x = cx - btn_w / 2
    top_y = game_screen.display_height / 2 - bs * 1.8

    hint_button = Button(btn_w, btn_h, btn_x, top_y,
                         position="Left", padding=bs * 0.25,
                         box_width=box_width, font=game_screen.big_big_text_font,
                         text=f"Hint on : {hint_on}")

    name_button = Button(btn_w, btn_h, btn_x, top_y + bs * 0.9,
                         position="Left", padding=bs * 0.25,
                         box_width=box_width, font=game_screen.big_big_text_font,
                         text=_name_label(player_name, False, ""))

    back_button = Button(btn_w, btn_h, btn_x, top_y + bs * 1.8 + bs * 0.35,
                         box_width=box_width, font=game_screen.big_big_text_font, text="back")
    return hint_button, name_button, back_button


def main(game_screen: GameScreen) -> None:
    active_tab = "display"
    tab_buttons = _build_tab_buttons(game_screen, active_tab)
    option_buttons, display_back_button = _build_display_buttons(game_screen)

    hint_on = load_setting("hint_on")
    player_name = load_setting("player_name")
    hint_button, name_button, gameplay_back_button = \
        _build_gameplay_buttons(game_screen, hint_on, player_name)

    editing_name = False
    blink = 0
    running = True
    clock = pygame.time.Clock()

    def commit_name() -> None:
        nonlocal editing_name
        editing_name = False
        save_setting("player_name", player_name)

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if editing_name:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        commit_name()
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        ch = event.unicode
                        if ch and (ch.isascii() and (ch.isalnum() or ch == "_")) and len(player_name) < 12:
                            player_name += ch
                    continue
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if editing_name and not name_button.touch(mouse_x, mouse_y):
                    commit_name()
                for tab_id, button in tab_buttons:
                    if button.touch(mouse_x, mouse_y) and tab_id != active_tab:
                        active_tab = tab_id
                        tab_buttons = _build_tab_buttons(game_screen, active_tab)
                        break

                if active_tab == "display":
                    for mode, button in option_buttons:
                        if button.touch(mouse_x, mouse_y) and mode != game_screen.display_mode:
                            save_setting("display_mode", mode)
                            game_screen.apply_display_mode(mode)
                            tab_buttons = _build_tab_buttons(game_screen, active_tab)
                            option_buttons, display_back_button = _build_display_buttons(game_screen)
                            hint_button, name_button, gameplay_back_button = \
                                _build_gameplay_buttons(game_screen, hint_on, player_name)
                            break
                    if display_back_button.touch(mouse_x, mouse_y):
                        running = False
                elif active_tab == "gameplay":
                    if hint_button.touch(mouse_x, mouse_y):
                        hint_on = not hint_on
                        save_setting("hint_on", hint_on)
                        hint_button.text = f"Hint on : {hint_on}"
                    if name_button.touch(mouse_x, mouse_y):
                        editing_name = True
                    if gameplay_back_button.touch(mouse_x, mouse_y):
                        running = False
            if event.type == pygame.QUIT:
                running = False

        if not running and editing_name:
            commit_name()

        for _tab_id, button in tab_buttons:
            button.update(game_screen)

        if active_tab == "display":
            for _mode, button in option_buttons:
                button.update(game_screen)
            display_back_button.update(game_screen)
        elif active_tab == "gameplay":
            caret = "_" if (blink // 30) % 2 == 0 else " "
            blink += 1
            name_button.text = _name_label(player_name, editing_name, caret)
            hint_button.update(game_screen)
            name_button.update(game_screen)
            gameplay_back_button.update(game_screen)

        pygame.display.update()
        clock.tick(60)
