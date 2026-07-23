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
import time
from typing import Optional

import pygame

from shared.setting import WHITE, VERSION
from core.game_screen import GameScreen, draw_text
from core.game_state import GameState
from core.draft_state import DraftState
from core.lobby_state import LobbyState
from core.match_prelude import (log_player_names, resolve_ban_draft, judge_bans_of,
                                log_ban_draft, log_judge_bans)
from core.network_layer import LANClient, LANServer, VersionMismatchError
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral
from core.UI import Button

from screens.connect import join_screen, connecting_screen
from screens.widgets import make_back_button
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
    back_button = make_back_button(game_screen, text="back", corner="top_left")

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
                if back_button.touch(mouse_x, mouse_y):
                    running = False
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
        back_button.update(game_screen)

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


def _build_game_state_from_draft(draft_state: DraftState,
                                 lobby_state: Optional[LobbyState] = None) -> GameState:
    player1 = Player(name="player1", deck=draft_state.player1_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=draft_state.player2_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    keep_files = not draft_state.settings.file_auto_delete
    logger = GameLogger(enable_file=keep_files, enable_console=True, enable_jsonl=keep_files)
    game_state = GameState(player1, player2, neutral, BoardConfig(), game_logger=logger)
    draft_state.settings.apply_to(game_state)
    game_state.game_logger.info(f"version {VERSION}", version=VERSION)
    log_player_names(logger, lobby_state)
    game_state.ban_draft = resolve_ban_draft(lobby_state)
    game_state.judge_bans = judge_bans_of(draft_state.ban_deck, game_state.ban_draft)
    log_ban_draft(logger, game_state.ban_draft)
    log_judge_bans(logger, game_state.judge_bans)
    logger.info(f"player1 deck {'-'.join(player1.deck)}")
    logger.info(f"player2 deck {'-'.join(player2.deck)}")
    logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)
    return game_state


def _build_game_state_for_client() -> GameState:
    player1 = Player(name="player1", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    silent_logger = GameLogger(enable_file=False, enable_console=True, enable_jsonl=False)

    return GameState(player1, player2, neutral, BoardConfig(), game_logger=silent_logger)


def _run_local(game_screen: GameScreen) -> None:
    lobby_state = LobbyState()
    lobby_exit = lobby.main(game_screen, mode="local", lobby_state=lobby_state)
    if lobby_exit.kind != "start_match":
        return

    exit_reason = draft.main(game_screen, mode="local",
                             settings=lobby_state.settings,
                             extra_bans=list(lobby_state.bans),
                             player_names=lobby_state.seat_names())
    if exit_reason.kind != "finished" or exit_reason.draft_state is None:
        return

    game_state = _build_game_state_from_draft(exit_reason.draft_state, lobby_state)

    winner = battling.main(game_state, game_screen, mode="local")
    if winner not in ("None", ""):
        finalize_battle(game_state, game_screen, winner)


def _run_host(game_screen: GameScreen) -> None:
    lobby_state = LobbyState()
    server = LANServer(VERSION, port=DEFAULT_PORT,
                       god_view=lobby_state.god_view,
                       host_seat=lobby_state.host_seat)
    try:
        while True:
            lobby_exit = lobby.main(game_screen, mode="lan_server",
                                    server=server, lobby_state=lobby_state)
            if lobby_exit.kind != "start_match":
                return

            exit_reason = draft.main(
                game_screen, mode="lan_server", server=server,
                host_seat=lobby_state.host_seat,
                reconnect_timeout=lobby_state.reconnect_timeout,
                settings=lobby_state.settings,
                extra_bans=list(lobby_state.bans),
                player_names=lobby_state.seat_names(),
            )
            if exit_reason.kind == "peer_lost":
                print("[play_screen] draft cancelled: opponent did not reconnect in time")
                server.broadcast_scene_for("lobby", lobby_state.to_dict_for)
                continue
            if exit_reason.kind == "quit":
                server.broadcast_scene_for("lobby", lobby_state.to_dict_for)
                continue
            if exit_reason.kind != "finished" or exit_reason.draft_state is None:
                return

            game_state = _build_game_state_from_draft(exit_reason.draft_state, lobby_state)

            winner = battling.main(
                game_state, game_screen,
                mode="lan_server", server=server,
                host_seat=lobby_state.host_seat,
                reconnect_timeout=lobby_state.reconnect_timeout,
            )
            if winner in ("None", ""):
                server.broadcast_scene_for("lobby", lobby_state.to_dict_for)
                continue
            server.broadcast_scene_for("lobby", lobby_state.to_dict_for)
            finalize_battle(game_state, game_screen, winner, server)
    finally:
        server.stop()


def _run_client_battle(game_screen: GameScreen, client: LANClient,
                       initial_state_dict: Optional[dict]) -> Optional[str]:
    game_state = _build_game_state_for_client()
    winner = battling.main(game_state, game_screen,
                           mode="lan_client", client=client,
                           initial_state_dict=initial_state_dict)
    handoff = None
    if winner in ("None", ""):
        handoff = client.consume_pending_scene()
    else:
        finalize_battle(game_state, game_screen, winner, client=client)
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            handoff = client.consume_pending_scene()
            if handoff is not None or client.is_disconnected:
                break
            time.sleep(0.05)

    if handoff is None:
        return None
    scene, state = handoff
    if scene == "lobby" and isinstance(client.latest_state, dict) \
            and client.latest_state.get("in_ban_draft"):
        state = client.latest_state
    client.scene = scene
    client.initial_state = state
    return scene


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

        while True:
            if client.scene == "lobby":
                lobby_state = LobbyState()
                lobby_state.apply_dict(client.initial_state)
                lobby_exit = lobby.main(game_screen, mode="lan_client",
                                        client=client, lobby_state=lobby_state)
                if lobby_exit.kind != "start_match":
                    return
                client.scene = "draft"

            if client.scene == "battling":
                next_scene = _run_client_battle(game_screen, client, client.initial_state)
            else:
                exit_reason = draft.main(game_screen, mode="lan_client", client=client)
                if exit_reason.kind != "scene_handoff":
                    return
                if exit_reason.next_scene == "lobby":
                    client.scene = "lobby"
                    client.initial_state = exit_reason.next_scene_state or {}
                    continue
                next_scene = _run_client_battle(game_screen, client, exit_reason.next_scene_state)

            if next_scene is None:
                return
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
