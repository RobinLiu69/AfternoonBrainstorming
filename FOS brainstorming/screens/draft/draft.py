# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOC Studio
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

from core.draft_state import DraftState
from core.draft_dispatcher import DraftDispatcher
from core.match_settings import MatchSettings
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.game_screen import GameScreen, draw_text
from core.network_layer import LANClient, LANServer
from core.scene_exit import DraftExitReason
from screens.draft.draft_action import collect_draft_actions
from screens.draft.exhibit_registry import ExhibitRegistry
from screens.notices import server_closed_screen
from rendering.draft_renderer import DraftRenderer
from shared.setting import WHITE
from core.setting_config import load_setting


def _render_quit_confirm(gs: GameScreen) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    overlay = pygame.Surface((gs.display_width, gs.display_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    gs.surface.blit(overlay, (0, 0))
    lines = [
        "Shut down server and leave?",
        "all players will be disconnected",
        "[Y] yes        [N] no",
    ]
    offsets = (-bs * 0.7, -bs * 0.05, bs * 0.7)
    for line, dy in zip(lines, offsets):
        w = gs.mid_text_font.size(line)[0]
        draw_text(line, gs.mid_text_font, WHITE, cx - w / 2, cy + dy, gs.surface)


def _to_board_x(mouse_x: int, game_screen: GameScreen) -> Optional[int]:
    left = game_screen.display_width / 2 - game_screen.block_size * 2
    right = game_screen.display_width / 2 + game_screen.block_size * 2
    if left < mouse_x < right:
        return int((mouse_x - left) / game_screen.block_size)
    return None


def _to_board_y(mouse_y: int, game_screen: GameScreen) -> Optional[int]:
    top = game_screen.display_height / 2 - game_screen.block_size * 1.65
    bottom = game_screen.display_height / 2 + game_screen.block_size * 1.35
    if top < mouse_y < bottom:
        return int((mouse_y - top) / game_screen.block_size)
    return None


def _turn_page(page: int, direction: int, total: int) -> int:
    return (page + direction) % total


def main(game_screen: GameScreen, mode: str = "local",
         server: Optional[LANServer] = None, client: Optional[LANClient] = None,
         draft_state: Optional[DraftState] = None,
         host_seat: str = "player1",
         reconnect_timeout: float = 60.0,
         settings: Optional[MatchSettings] = None) -> DraftExitReason:
    registry = ExhibitRegistry(game_screen)
    if draft_state is None:
        draft_state = DraftState()
    draft_state.board_config = BoardConfig(4, 3)
    draft_state.board_dict = initialize_board(game_screen, draft_state.board_config)
    draft_state.settings = settings.copy() if settings is not None else MatchSettings()

    dispatcher = DraftDispatcher(draft_state, mode=mode,
                                 reconnect_timeout=reconnect_timeout,
                                 host_seat=host_seat)

    match mode:
        case "lan_server":
            assert server is not None, "lan_server mode requires a LANServer"
            dispatcher.attach_server(server)
            if not server.is_running:
                server.start()
            draft_state.local_player = host_seat
            server.broadcast_scene_for("draft", draft_state.to_dict_for)

        case "lan_client":
            assert client is not None, "lan_client mode requires a LANClient"
            dispatcher.attach_client(client)
            if not client.is_connected:
                role, initial_state = client.connect()
            else:
                role = client.role
                initial_state = client.pending_scene_state or client.initial_state

            if initial_state:
                draft_state.apply_dict(initial_state)
            if client.pending_scene == "draft":
                client.pending_scene = None
                client.pending_scene_state = None
            draft_state.local_player = role or "player2"

        case _:
            draft_state.local_player = "player1"

    renderer = DraftRenderer(game_screen, registry)

    page = 0
    index = 0
    hint_on = load_setting("hint_on")
    last_phase = draft_state.phase
    clock = pygame.time.Clock()

    last_reconnect_attempt = 0.0
    disconnect_since: float | None = None
    confirming_quit = False

    while True:
        if mode == "local":
            draft_state.local_player = draft_state.current_editor()

        if mode == "lan_client" and client is not None:
            handoff = client.consume_pending_scene()
            if handoff is not None:
                _scene, next_state = handoff
                return DraftExitReason(
                    kind="scene_handoff",
                    next_scene_state=next_state,
                )
            if client.is_disconnected:
                if client.role not in ("player1", "player2"):
                    server_closed_screen.main(game_screen)
                    return DraftExitReason(kind="quit")
                import time as _time
                now = _time.monotonic()
                if disconnect_since is None:
                    disconnect_since = now
                if now - last_reconnect_attempt > 2.0:
                    last_reconnect_attempt = now
                    if client.try_reconnect():
                        print("[draft] reconnect succeeded")
                        disconnect_since = None
                        if client.scene == "battling":
                            print("[draft] host moved on to battle, handing off")
                            return DraftExitReason(
                                kind="scene_handoff",
                                next_scene_state=client.initial_state,
                            )
                        if client.scene != "draft":
                            print(f"[draft] host is no longer drafting (scene={client.scene!r}), leaving")
                            server_closed_screen.main(game_screen)
                            return DraftExitReason(kind="quit")
                        if client.initial_state:
                            draft_state.apply_dict(client.initial_state)
                if disconnect_since is not None and (
                    client.reconnect_refused or now - disconnect_since > reconnect_timeout
                ):
                    print("[draft] host gone; leaving draft")
                    server_closed_screen.main(game_screen)
                    return DraftExitReason(kind="quit")
            else:
                disconnect_since = None

        if mode == "lan_server" and server is not None:
            server.pulse()
            if getattr(dispatcher, "peer_lost", False):
                return DraftExitReason(kind="peer_lost")

        if draft_state.phase != last_phase:
            page = 0
            index = 0
            last_phase = draft_state.phase

        if draft_state.phase == "done" and mode != "lan_client":
            return DraftExitReason(kind="finished", draft_state=draft_state)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = _to_board_x(mouse_x, game_screen)
        mouse_board_y = _to_board_y(mouse_y, game_screen)

        if mode == "lan_server" and server is not None:
            draft_state.net_spectator_count = server.count_spectators()
            draft_state.net_latencies = dispatcher.latencies
        elif mode == "lan_client" and client is not None:
            draft_state.net_spectator_count = client.net_spectator_count
            draft_state.net_latencies = client.net_latencies

        if confirming_quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return DraftExitReason(kind="quit")
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_y, pygame.K_RETURN):
                        return DraftExitReason(kind="quit")
                    if event.key in (pygame.K_n, pygame.K_ESCAPE):
                        confirming_quit = False
            renderer.render_frame(page, index, mouse_board_x, mouse_board_y, draft_state, hint_on, multiplayer=True)
            _render_quit_confirm(game_screen)
            pygame.display.update()
            clock.tick(60)
            continue

        actions = collect_draft_actions(
            draft_state.local_player, page, index, registry,
            mouse_board_x, mouse_board_y,
        )

        for action in actions:
            if action.action_type == "quit":
                if mode == "lan_server":
                    confirming_quit = True
                    break
                return DraftExitReason(kind="quit")

            if action.action_type == "toggle_hint":
                hint_on = not hint_on
                continue

            if action.action_type == "page_next":
                page = _turn_page(page, 1, registry.page_count())
                index = registry.index_count(page) - 1
                continue

            if action.action_type == "page_prev":
                page = _turn_page(page, -1, registry.page_count())
                index = registry.index_count(page) - 1
                continue
            
            if action.action_type == "change_index":
                index = action.data
                continue
            
            if action.action_type == "index_next":
                index = ((index + 1) + len(registry.get_page_colors(page))) % len(registry.get_page_colors(page))

            if action.action_type == "index_prev":
                index = ((index - 1) + len(registry.get_page_colors(page))) % len(registry.get_page_colors(page))

            dispatcher.dispatch(action, draft_state)

        renderer.render_frame(page, index, mouse_board_x, mouse_board_y, draft_state, hint_on,
                              multiplayer=mode in ("lan_server", "lan_client"))
        pygame.display.update()
        clock.tick(60)