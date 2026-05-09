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

from dataclasses import dataclass
from typing import Optional

import pygame

from core.lobby_state import LobbyState, RECONNECT_TIMEOUT_OPTIONS
from core.lobby_dispatcher import LobbyDispatcher
from core.network_layer import LANServer, LANClient
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from screens.lobby_action import LobbyAction
from shared.setting import WHITE


@dataclass
class LobbyExit:
    kind: str  # "start_match" | "quit" | "peer_lost"
    state: Optional[LobbyState] = None


def _is_host(role: str) -> bool:
    return role == "host"


def _is_player(role: str) -> bool:
    return role in ("player1", "player2")


def _is_spectator(role: str) -> bool:
    return role in ("spectator", "god")


def _make_buttons(gs: GameScreen) -> dict[str, Button]:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    box_width = max(1, int(bs / 30))

    btn_w = bs * 3.0
    btn_h = bs * 0.45
    btn_x = cx - btn_w / 2

    def mk(y_offset: float, text: str) -> Button:
        return Button(btn_w, btn_h, btn_x, cy + bs * y_offset,
                      bs * 0.15, bs * 0.10,
                      box_width=box_width, font=gs.mid_text_font, text=text)

    return {
        "god_view":          mk(-1.05, "god view: off"),
        "timer_mode":        mk(-0.55, "timer mode: timer"),
        "file_auto_delete":  mk(-0.05, "auto-delete log: no"),
        "reconnect_timeout": mk(0.45, "reconnect timeout: 60s"),
        "swap_seats":        mk(0.95, "host plays: player1"),
        "switch_role":       mk(1.45, "switch role"),
        "start_match":       mk(2.05, "START MATCH"),
    }


def _refresh_button_labels(buttons: dict[str, Button], state: LobbyState, role: str) -> None:
    buttons["god_view"].text          = f"god view: {'on' if state.god_view else 'off'}"
    buttons["timer_mode"].text        = f"timer mode: {state.timer_mode}"
    buttons["file_auto_delete"].text  = f"auto-delete log: {'yes' if state.file_auto_delete else 'no'}"
    buttons["reconnect_timeout"].text = f"reconnect timeout: {int(state.reconnect_timeout)}s"
    buttons["swap_seats"].text        = f"host plays: {state.host_seat}"

    if _is_host(role):
        buttons["switch_role"].text = "(spectators can switch role themselves)"
    elif role == state.peer_seat():
        buttons["switch_role"].text = "switch to spectator"
    elif _is_spectator(role):
        if state.peer_connected:
            buttons["switch_role"].text = "(player slot occupied)"
        else:
            buttons["switch_role"].text = f"take {state.peer_seat()} seat"
    else:
        buttons["switch_role"].text = ""


def _render_roster(gs: GameScreen, state: LobbyState, role: str) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2

    draw_text("LOBBY", gs.title_text_font, WHITE,
              cx - bs * 0.7, cy - bs * 2.5, gs.surface)

    host_seat = state.host_seat
    peer_seat = state.peer_seat()
    peer_status = "connected" if state.peer_connected else "waiting..."

    you_marker = lambda this_role: "  <-- you" if role == this_role else ""

    lines = [
        f"{host_seat}: host{you_marker('host')}",
        f"{peer_seat}: {peer_status}{you_marker(peer_seat)}",
        f"spectators: {state.spectator_count}{you_marker('spectator') or you_marker('god')}",
    ]
    for i, line in enumerate(lines):
        draw_text(line, gs.text_font, WHITE,
                  cx - bs * 3.0, cy - bs * (2.4 - i * 0.35), gs.surface)

    if state.god_view:
        draw_text("(spectators see all decks)", gs.mid_text_font, WHITE,
                  cx - bs * 3.0, cy - bs * 1.4, gs.surface)


def _render_help(gs: GameScreen, role: str) -> None:
    bs = gs.block_size
    cy = gs.display_height / 2
    cx = gs.display_width / 2
    if _is_host(role):
        msg = "click to toggle / cycle  |  ESC: leave & shut down server"
    else:
        msg = "host controls settings  |  ESC: leave"
    draw_text(msg, gs.mid_text_font, WHITE,
              cx - bs * 3.0, cy + bs * 2.7, gs.surface)


def _click_dispatch(buttons: dict[str, Button], mouse_x: float, mouse_y: float,
                    state: LobbyState, role: str, dispatcher: LobbyDispatcher) -> None:
    if _is_host(role):
        if buttons["god_view"].touch(mouse_x, mouse_y):
            dispatcher.dispatch(LobbyAction("host", "set_god_view", bool_value=not state.god_view))
            return
        if buttons["timer_mode"].touch(mouse_x, mouse_y):
            new_mode = "countdown" if state.timer_mode == "timer" else "timer"
            dispatcher.dispatch(LobbyAction("host", "set_timer_mode", str_value=new_mode))
            return
        if buttons["file_auto_delete"].touch(mouse_x, mouse_y):
            dispatcher.dispatch(LobbyAction("host", "set_file_auto_delete", bool_value=not state.file_auto_delete))
            return
        if buttons["reconnect_timeout"].touch(mouse_x, mouse_y):
            try:
                idx = RECONNECT_TIMEOUT_OPTIONS.index(state.reconnect_timeout)
            except ValueError:
                idx = 1
            new_t = RECONNECT_TIMEOUT_OPTIONS[(idx + 1) % len(RECONNECT_TIMEOUT_OPTIONS)]
            dispatcher.dispatch(LobbyAction("host", "set_reconnect_timeout", float_value=new_t))
            return
        if buttons["swap_seats"].touch(mouse_x, mouse_y):
            dispatcher.dispatch(LobbyAction("host", "swap_seats"))
            return
        if buttons["start_match"].touch(mouse_x, mouse_y):
            dispatcher.dispatch(LobbyAction("host", "start_match"))
            return
    else:
        if buttons["switch_role"].touch(mouse_x, mouse_y):
            if role == state.peer_seat():
                dispatcher.dispatch(LobbyAction(role, "switch_to_spectator"))
            elif _is_spectator(role) and not state.peer_connected:
                dispatcher.dispatch(LobbyAction(role, "switch_to_player"))


def main(game_screen: GameScreen, mode: str,
         server: Optional[LANServer] = None,
         client: Optional[LANClient] = None,
         lobby_state: Optional[LobbyState] = None) -> LobbyExit:

    state = lobby_state if lobby_state is not None else LobbyState()
    dispatcher = LobbyDispatcher(state, mode=mode)

    if mode == "lan_server":
        assert server is not None
        dispatcher.attach_server(server)
        if not server.is_running:
            server.start()
        state.local_role = "host"

    elif mode == "lan_client":
        assert client is not None
        dispatcher.attach_client(client)
        if not client.is_connected:
            role, initial_state = client.connect()
        else:
            role, initial_state = client.role, client.initial_state
        if initial_state:
            state.apply_dict(initial_state)
        state.local_role = role or ""

    buttons = _make_buttons(game_screen)
    clock = pygame.time.Clock()

    while True:
        if mode == "lan_client" and client is not None:
            if client.pending_scene is not None:
                return LobbyExit(kind="start_match", state=state)
            if state.local_role:
                client.role = state.local_role

        if mode == "lan_server" and dispatcher.start_signal:
            return LobbyExit(kind="start_match", state=state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return LobbyExit(kind="quit")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return LobbyExit(kind="quit")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                _click_dispatch(buttons, mx, my, state, state.local_role, dispatcher)

        game_screen.render()
        _render_roster(game_screen, state, state.local_role)
        _refresh_button_labels(buttons, state, state.local_role)

        if _is_host(state.local_role):
            for key in ("god_view", "timer_mode", "file_auto_delete", "reconnect_timeout", "swap_seats", "start_match"):
                buttons[key].update(game_screen)
        else:
            buttons["god_view"].update(game_screen)
            buttons["timer_mode"].update(game_screen)
            buttons["file_auto_delete"].update(game_screen)
            buttons["reconnect_timeout"].update(game_screen)
            buttons["swap_seats"].update(game_screen)
            if buttons["switch_role"].text:
                buttons["switch_role"].update(game_screen)

        _render_help(game_screen, state.local_role)
        pygame.display.update()
        clock.tick(60)
