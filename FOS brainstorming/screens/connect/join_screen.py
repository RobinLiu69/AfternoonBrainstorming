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
from core.game_screen import GameScreen, draw_text, QuitGame
from core.setting_config import load_setting, save_setting
from rendering import style
from screens.widgets import make_back_button

IP_PATTERN = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def main(game_screen: GameScreen, default: str = "",
         default_room: str = "") -> tuple[str, str]:
    pygame.key.set_repeat(400, 40)
    try:
        return _input_loop(game_screen, default or load_setting("last_join_ip"),
                           default_room)
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


GRAY = (140, 140, 140)
DIM_GRAY = (90, 90, 90)
ERROR_RED = (255, 120, 120)


def _field_rects(game_screen: GameScreen) -> dict[str, pygame.Rect]:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    width = bs * 4.2
    height = bs * 0.6
    return {
        "ip": pygame.Rect(cx - width / 2, cy - bs * 0.60, width, height),
        "room": pygame.Rect(cx - width / 2, cy + bs * 0.80, width, height),
    }


def _draw_field(game_screen: GameScreen, rect: pygame.Rect, label: str,
                value: str, placeholder: str, is_active: bool, caret: str) -> None:
    bs = game_screen.block_size
    draw_text(label, game_screen.text_font,
              style.INK if is_active else style.INK_MUTED,
              rect.x, rect.y - bs * 0.35, game_screen.surface)

    field = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    field.fill(style.CONTROL_FILL if is_active else style.PANEL_FILL)
    pygame.draw.rect(field, style.TOOLTIP_EDGE if is_active else style.PANEL_EDGE,
                     field.get_rect(), style.edge_width(game_screen))
    game_screen.surface.blit(field, rect.topleft)

    inset = rect.x + bs * 0.15

    def middle(font: pygame.font.Font) -> float:
        return rect.y + (rect.height - font.get_linesize()) / 2

    value_font = game_screen.big_text_font
    hint_font = game_screen.mid_text_font

    if value:
        draw_text(value + (caret if is_active else ""), value_font, style.INK,
                  inset, middle(value_font), game_screen.surface)
    elif is_active:
        draw_text(caret, value_font, style.INK,
                  inset, middle(value_font), game_screen.surface)
        draw_text(placeholder, hint_font, style.INK_DISABLED,
                  inset + bs * 0.25, middle(hint_font), game_screen.surface)
    else:
        draw_text(placeholder, hint_font, style.INK_DISABLED,
                  inset, middle(hint_font), game_screen.surface)


def render(game_screen: GameScreen, fields: dict[str, str], active: str,
           error: str, caret: str, back_button) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    rects = _field_rects(game_screen)
    pad = bs * style.PANEL_PAD

    panel_top = cy - bs * 1.55
    panel_bottom = rects["room"].bottom + pad
    style.section(game_screen, "SERVER", rects["ip"].x - pad, panel_top,
                  rects["ip"].width + pad * 2, panel_bottom - panel_top)

    style.title(game_screen, "JOIN GAME", cy - bs * 2.6)

    _draw_field(game_screen, rects["ip"], "Host IP", fields["ip"],
                "empty = this computer (127.0.0.1)", active == "ip", caret)
    _draw_field(game_screen, rects["room"], "Room number", fields["room"],
                "empty = create a new room", active == "room", caret)

    if error:
        draw_text(error, game_screen.text_font, ERROR_RED,
                  rects["room"].x, panel_bottom + bs * 0.18, game_screen.surface)

    style.muted_text(game_screen,
                     "[Enter] connect    [Tab] switch field    [Esc] cancel    [Ctrl+V] paste",
                     rects["room"].x, panel_bottom + bs * 0.50, game_screen.text_font)

    back_button.update(game_screen)


def _input_loop(game_screen: GameScreen, default: str = "",
                default_room: str = "") -> tuple[str, str]:
    fields = {"ip": default, "room": default_room}
    active = "ip"
    error = ""
    clock = pygame.time.Clock()
    blink = 0
    rects = _field_rects(game_screen)
    back_button = make_back_button(game_screen, text="back", corner="top_left")

    while True:
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.touch(*event.pos):
                    return "", ""
                for name, rect in rects.items():
                    if rect.collidepoint(event.pos):
                        active = name
                        error = ""

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "", ""
                if event.key == pygame.K_RETURN:
                    ip = fields["ip"] or "127.0.0.1"
                    if IP_PATTERN.match(ip):
                        save_setting("last_join_ip", fields["ip"])
                        return ip, fields["room"]
                    if "." not in fields["ip"] and not fields["room"]:
                        error = "that looks like a room number - it goes in the second field (Tab)"
                    else:
                        error = "not a valid IP (e.g. 192.168.1.10)"
                    continue
                error = ""
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

        render(game_screen, fields, active, error, caret, back_button)

        pygame.display.update()
        clock.tick(60)
