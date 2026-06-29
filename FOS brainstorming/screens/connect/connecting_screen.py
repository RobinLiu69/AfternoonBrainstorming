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
from core.game_screen import GameScreen, draw_text
from core.network_layer import LANClient, VersionMismatchError


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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                canceled["flag"] = True
                return ("canceled", None)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                canceled["flag"] = True
                return ("canceled", None)

        status = result["status"]
        if status != "pending":
            return (status, result["error"])

        game_screen.render()

        cx = game_screen.display_width / 2
        cy = game_screen.display_height / 2
        bs = game_screen.block_size

        dots = "." * (1 + (pygame.time.get_ticks() // 400) % 3)
        base = "Connecting"
        anchor_x = cx - game_screen.big_text_font.size(base + "...")[0] / 2
        draw_text(base + dots, game_screen.big_text_font, WHITE,
                  anchor_x, cy - bs * 0.8, game_screen.surface)

        host_w = game_screen.mid_text_font.size(host_ip)[0]
        draw_text(host_ip, game_screen.mid_text_font, WHITE,
                  cx - host_w / 2, cy + bs * 0.1, game_screen.surface)

        draw_text("[Esc] cancel", game_screen.text_font, WHITE,
                  cx - bs * 0.7, cy + bs * 1.1, game_screen.surface)

        pygame.display.update()
        clock.tick(60)
