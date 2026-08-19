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

import threading
from typing import Optional

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.network_layer import LANClient, VersionMismatchError
from rendering import style
from screens.widgets import make_back_button


def main(game_screen: GameScreen, client: LANClient, host_ip: str,
         intent: str = "play") -> tuple[str, Optional[Exception]]:
    result: dict = {"status": "pending", "error": None}
    canceled = {"flag": False}

    def worker() -> None:
        try:
            client.connect(intent=intent)
            if canceled["flag"]:
                client.disconnect()
                return
            result["status"] = "connected"
        except VersionMismatchError as e:
            result["error"] = e
            result["status"] = "version_mismatch"
        except (ConnectionRefusedError, RuntimeError, ConnectionError, OSError) as e:
            result["error"] = e
            result["status"] = "failed"

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    clock = pygame.time.Clock()
    pygame.event.clear()
    cancel_button = make_back_button(game_screen, text="cancel", corner="top_left")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                canceled["flag"] = True
                return ("canceled", None)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if cancel_button.touch(*event.pos):
                    canceled["flag"] = True
                    return ("canceled", None)

        status = result["status"]
        if status != "pending":
            return (status, result["error"])

        game_screen.render()
        render(game_screen, host_ip,
               1 + (pygame.time.get_ticks() // 400) % 3, cancel_button)

        pygame.display.update()
        clock.tick(60)


def render(game_screen: GameScreen, host_ip: str, dot_count: int,
           cancel_button) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    pad = bs * style.PANEL_PAD

    host_w = game_screen.big_text_font.size(host_ip)[0]
    hint = "[Esc] cancel"
    hint_w = game_screen.text_font.size(hint)[0]

    width = max(max(host_w, hint_w) + pad * 6, bs * style.MODAL_MIN_W)
    height = bs * (style.HEADER_HEIGHT + 0.88) + pad
    x, y = cx - width / 2, cy - height / 2

    style.section(game_screen, "CONNECTING" + "." * dot_count, x, y, width, height)

    draw_text(host_ip, game_screen.big_text_font, style.INK,
              cx - host_w / 2, y + bs * style.HEADER_HEIGHT + pad * 0.9,
              game_screen.surface)
    style.muted_text(game_screen, hint, cx - hint_w / 2,
                     y + height - pad - game_screen.text_font.get_linesize(),
                     game_screen.text_font)

    cancel_button.update(game_screen)
