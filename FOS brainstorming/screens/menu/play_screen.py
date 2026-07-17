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

import socket
from typing import Optional

import pygame

from shared.setting import WHITE, VERSION
from core.game_screen import GameScreen, draw_text
from core.game_state import GameState
from core.draft_state import DraftState
from core.lobby_state import LobbyState
from core.network_layer import LANClient, LANServer, VersionMismatchError
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral
from core.UI import Button

from screens.connect import join_screen, connecting_screen
from screens.lobby import lobby
from screens.notices import version_mismatch_screen, connection_failed_screen
from screens.draft import draft
from screens.battling import battling
from screens.battling.finalize import finalize_battle

from utils.controls import key_pressed
from utils.logger import GameLogger


DEFAULT_PORT = 5555


def _choose_mode(game_screen: GameScreen) -> str:
    running = True
    box_width: int = int(game_screen.block_size/30)

    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    main_w, main_h = bs * 1.5, bs * 0.75
    main_x = cx - main_w

    host_button = Button(main_w*2, main_h, main_x, cy - bs * 1.4,
                        box_width=box_width, font=game_screen.big_big_text_font, text="host")
    join_button = Button(main_w*2, main_h, main_x, cy - bs * 0.5,
                        box_width=box_width, font=game_screen.big_big_text_font, text="join")
    local_button = Button(main_w*2, main_h, main_x, cy + bs,
                        box_width=box_width, font=game_screen.big_big_text_font, text="local")

    state = "quit"

    clock = pygame.time.Clock()

    while running:
        game_screen.render()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if local_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "local"
                if host_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "host"
                if join_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "join"

            if event.type == pygame.QUIT:
                running = False

        draw_text("Afternoon Brainstorming", game_screen.title_text_font, WHITE,
                cx - bs * 2.3, cy - bs * 2.4, game_screen.surface)
        draw_text("by Five O'clock Shadow Studio", game_screen.mid_text_font, WHITE,
                cx + bs * 1.2, cy - bs * 1.9, game_screen.surface)

        local_button.update(game_screen)
        host_button.update(game_screen)
        join_button.update(game_screen)

        draw_text(f"version: {VERSION}", game_screen.mid_text_font, WHITE,
                game_screen.display_width - bs * 2,
                cy + bs * 2.5, game_screen.surface)

        pygame.display.update()
        clock.tick(60)
    return state


def _connect_failure_reason(error: Exception) -> str:
    if isinstance(error, socket.gaierror):
        return "Invalid host IP"
    if isinstance(error, TimeoutError):
        return "Connection timed out (host unreachable?)"
    if isinstance(error, ConnectionRefusedError):
        return "Connection refused (no game hosted there?)"
    message = str(error)
    if "room_not_found" in message:
        return "Room not found (wrong room number?)"
    if "room_full" in message:
        return "Room is full"
    if "server_full" in message:
        return "Server is full (no free rooms)"
    return "Could not reach the host"


def _build_game_state_from_draft(draft_state: DraftState) -> GameState:
    player1 = Player(name="player1", deck=draft_state.player1_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=draft_state.player2_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    keep_files = not draft_state.file_auto_delete
    logger = GameLogger(enable_file=keep_files, enable_console=True, enable_jsonl=keep_files)
    game_state = GameState(player1, player2, neutral, BoardConfig(), game_logger=logger)
    game_state.timer_mode = draft_state.timer_mode
    game_state.file_auto_delete = draft_state.file_auto_delete

    game_state.game_logger.info(f"timer mode {game_state.timer_mode}")
    game_state.game_logger.info(f"version {VERSION}", version=VERSION)
    return game_state


def _build_game_state_for_client() -> GameState:
    player1 = Player(name="player1", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    silent_logger = GameLogger(enable_file=False, enable_console=True, enable_jsonl=False)

    return GameState(player1, player2, neutral, BoardConfig(), game_logger=silent_logger)


def _apply_time_control(game_state: GameState, lobby_state: LobbyState) -> None:
    game_state.countdown_time = lobby_state.countdown_seconds()
    game_state.turn_increment_seconds = lobby_state.increment_seconds()
    effective_tc = (lobby_state.time_control
                    if game_state.timer_mode == "countdown" else "unlimited")
    game_state.game_logger.info(
        f"time control {effective_tc}",
        countdown_seconds=game_state.countdown_time,
        increment_seconds=game_state.turn_increment_seconds)


def _run_local(game_screen: GameScreen) -> None:
    lobby_state = LobbyState()
    lobby_exit = lobby.main(game_screen, mode="local", lobby_state=lobby_state)
    if lobby_exit.kind != "start_match":
        return

    exit_reason = draft.main(game_screen, mode="local",
                             timer_mode=lobby_state.timer_mode,
                             file_auto_delete=lobby_state.file_auto_delete)
    if exit_reason.kind != "finished" or exit_reason.draft_state is None:
        return

    game_state = _build_game_state_from_draft(exit_reason.draft_state)
    _apply_time_control(game_state, lobby_state)

    winner = battling.main(game_state, game_screen, mode="local")
    if winner not in ("None", ""):
        finalize_battle(game_state, game_screen, winner)


def _run_host(game_screen: GameScreen) -> None:
    lobby_state = LobbyState()
    server = LANServer(VERSION, port=DEFAULT_PORT,
                       god_view=lobby_state.god_view,
                       host_seat=lobby_state.host_seat)
    try:
        lobby_exit = lobby.main(game_screen, mode="lan_server",
                                server=server, lobby_state=lobby_state)
        if lobby_exit.kind != "start_match":
            return

        exit_reason = draft.main(
            game_screen, mode="lan_server", server=server,
            host_seat=lobby_state.host_seat,
            reconnect_timeout=lobby_state.reconnect_timeout,
            timer_mode=lobby_state.timer_mode,
            file_auto_delete=lobby_state.file_auto_delete,
        )
        if exit_reason.kind == "peer_lost":
            print("[play_screen] draft cancelled: opponent did not reconnect in time")
            return
        if exit_reason.kind != "finished" or exit_reason.draft_state is None:
            return

        game_state = _build_game_state_from_draft(exit_reason.draft_state)
        _apply_time_control(game_state, lobby_state)

        winner = battling.main(
            game_state, game_screen,
            mode="lan_server", server=server,
            host_seat=lobby_state.host_seat,
            reconnect_timeout=lobby_state.reconnect_timeout,
        )
        if winner not in ("None", ""):
            finalize_battle(game_state, game_screen, winner, server)
    finally:
        server.stop()


def _run_client_battle(game_screen: GameScreen, client: LANClient,
                       initial_state_dict: Optional[dict]) -> None:
    game_state = _build_game_state_for_client()
    winner = battling.main(game_state, game_screen,
                           mode="lan_client", client=client,
                           initial_state_dict=initial_state_dict)
    if winner not in ("None", ""):
        finalize_battle(game_state, game_screen, winner)


def _run_join(game_screen: GameScreen) -> None:
    host_ip, room_code = join_screen.main(game_screen)
    if not host_ip:
        return

    client = LANClient(VERSION, host_ip, port=DEFAULT_PORT, room=room_code)
    try:
        status, error = connecting_screen.main(game_screen, client, host_ip)
        if status == "canceled":
            return
        if status == "version_mismatch" and isinstance(error, VersionMismatchError):
            version_mismatch_screen.main(game_screen, error.server_version, error.client_version)
            return
        if status == "failed" and error is not None:
            print(f"[play_screen] Failed to join {host_ip}: {error}")
            connection_failed_screen.main(game_screen, host_ip, _connect_failure_reason(error))
            return

        if client.scene == "lobby":
            lobby_state = LobbyState()
            lobby_state.apply_dict(client.initial_state)
            lobby_exit = lobby.main(game_screen, mode="lan_client",
                                    client=client, lobby_state=lobby_state)
            if lobby_exit.kind != "start_match":
                return
            client.scene = "draft"

        if client.scene == "battling":
            _run_client_battle(game_screen, client, client.initial_state)
            return

        exit_reason = draft.main(game_screen, mode="lan_client", client=client)
        if exit_reason.kind == "scene_handoff":
            _run_client_battle(game_screen, client, exit_reason.next_scene_state)
    finally:
        client.disconnect()


def main(game_screen: GameScreen) -> None:
    while True:
        match _choose_mode(game_screen):
            case "host":
                _run_host(game_screen)
            case "join":
                _run_join(game_screen)
            case "local":
                _run_local(game_screen)
            case _:
                return
