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

import re
import subprocess
import sys

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text


def main(game_screen: GameScreen, default: str = "",
         default_room: str = "") -> tuple[str, str]:
    pygame.key.set_repeat(400, 40)
    try:
        return _input_loop(game_screen, default, default_room)
    finally:
        pygame.key.set_repeat()


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


def _input_loop(game_screen: GameScreen, default: str = "",
                default_room: str = "") -> tuple[str, str]:
    fields = {"ip": default, "room": default_room}
    active = "ip"
    clock = pygame.time.Clock()
    blink = 0

    while True:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "", ""

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "", ""
                if event.key == pygame.K_RETURN:
                    if fields["ip"]:
                        return fields["ip"], fields["room"]
                    continue
                if event.key in (pygame.K_TAB, pygame.K_UP, pygame.K_DOWN):
                    active = "room" if active == "ip" else "ip"
                    continue
                if event.key == pygame.K_BACKSPACE:
                    fields[active] = fields[active][:-1]
                    continue
                if event.key == pygame.K_v and event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META):
                    pasted = _clipboard_get()
                    if active == "ip":
                        match = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", pasted)
                        if match:
                            fields["ip"] = match.group(0)
                        else:
                            cleaned = "".join(c for c in pasted if c.isdigit() or c == ".")
                            fields["ip"] = (fields["ip"] + cleaned)[:21]
                    else:
                        cleaned = "".join(c for c in pasted if c.isdigit())
                        fields["room"] = (fields["room"] + cleaned)[:6]
                    continue

                ch = event.unicode
                if active == "ip":
                    if ch and (ch.isdigit() or ch == ".") and len(fields["ip"]) < 21:
                        fields["ip"] += ch
                else:
                    if ch and ch.isdigit() and len(fields["room"]) < 6:
                        fields["room"] += ch

        caret = "_" if (blink // 30) % 2 == 0 else " "
        blink += 1

        cx = game_screen.display_width / 2
        cy = game_screen.display_height / 2
        bs = game_screen.block_size

        draw_text("Enter host IP",
                  game_screen.big_text_font, WHITE,
                  cx - bs * 1.2, cy - bs * 1.6, game_screen.surface)

        ip_caret = caret if active == "ip" else ""
        draw_text(fields["ip"] + ip_caret,
                  game_screen.big_text_font, WHITE,
                  cx - bs * 1.8, cy - bs * 0.8, game_screen.surface)

        draw_text("Room number (empty = create new room)",
                  game_screen.text_font, WHITE,
                  cx - bs * 1.8, cy + bs * 0.1, game_screen.surface)

        room_caret = caret if active == "room" else ""
        draw_text(fields["room"] + room_caret,
                  game_screen.big_text_font, WHITE,
                  cx - bs * 1.8, cy + bs * 0.5, game_screen.surface)

        draw_text("[Enter] connect    [Tab] switch field    [Esc] cancel    [Ctrl+V] paste",
                  game_screen.text_font, WHITE,
                  cx - bs * 2.4, cy + bs * 1.5, game_screen.surface)

        pygame.display.update()
        clock.tick(60)
