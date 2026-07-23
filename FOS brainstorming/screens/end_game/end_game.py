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

from core.game_state import GameState
from core.game_screen import GameScreen
from core.network_layer import LANClient
from rendering.end_game_renderer import EndGameRenderer
from utils.controls import key_pressed


def _host_advanced(client: LANClient) -> bool:
    if client.is_disconnected:
        return True
    if client.pending_scene is not None and client.pending_scene != "lobby":
        return True
    state = client.latest_state
    return isinstance(state, dict) and bool(state.get("in_ban_draft"))


def main(winner: str, game_state: GameState, game_screen: GameScreen,
         client: Optional[LANClient] = None) -> None:
    renderer = EndGameRenderer(game_screen, game_state)

    display_state: str = "mid"
    running = True
    clock = pygame.time.Clock()

    prev_state_handler = None
    if client is not None:
        prev_state_handler = client.on_state_update
        client.on_state_update = None

    try:
        while running:
            if client is not None and _host_advanced(client):
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type != pygame.KEYDOWN:
                    continue

                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_TAB:
                        display_state = "mid" if display_state == "raw" else "raw"
                        renderer.set_display_state(display_state)
                    case pygame.K_SPACE:
                        display_state = {
                            "mid": "player1",
                            "player1": "player2",
                            "player2": "mid",
                        }.get(display_state, "mid")
                        renderer.set_display_state(display_state)
                    case pygame.K_1:
                        display_state = "mid" if display_state == "player1" else "player1"
                        renderer.set_display_state(display_state)
                    case pygame.K_2:
                        display_state = "mid" if display_state == "player2" else "player2"
                        renderer.set_display_state(display_state)

            renderer.render_frame(winner, display_state)
            pygame.display.update()
            clock.tick(60)
    finally:
        if client is not None:
            client.on_state_update = prev_state_handler