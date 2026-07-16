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

from core.lobby_state import LobbyState, RECONNECT_TIMEOUT_OPTIONS, TIME_CONTROL_OPTIONS
from core.lobby_dispatcher import LobbyDispatcher
from core.network_layer import LANServer, LANClient
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from screens.lobby.lobby_action import LobbyAction
from screens.notices import server_closed_screen
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


def _room_has_others(state: LobbyState) -> bool:
    return state.peer_connected or state.spectator_count > 0


MATCH_SETTING_OFFSETS = {"time": -1.40, "swap_seats": -0.95}
ADVANCED_HEADER_OFFSET = -0.25
ADVANCED_SETTING_OFFSETS = {"god_view": -0.02, "file_auto_delete": 0.43,
                            "reconnect_timeout": 0.88}


def _make_buttons(gs: GameScreen) -> dict[str, Button]:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    box_width = max(1, int(bs / 30))

    left_btn_w = bs * 2.8
    btn_h = bs * 0.43
    left_x = cx - bs * 3.3

    def left_btn(y_offset: float) -> Button:
        return Button(left_btn_w, btn_h, left_x, cy + bs * y_offset,
                      position="Left", padding=bs * 0.15,
                      box_width=box_width, font=gs.mid_text_font)

    switch_w = bs * 2.5
    switch_role = Button(switch_w, btn_h, cx - switch_w / 2, cy + bs * 1.70,
                         position="Left", padding=bs * 0.15,
                         box_width=box_width, font=gs.mid_text_font)

    start_w = bs * 3.2
    start_match = Button(start_w, bs * 0.55, cx - start_w / 2, cy + bs * 2.30,
                         position="Middle", padding=bs * 0.15,
                         box_width=box_width, font=gs.text_font, text="START MATCH")

    buttons = {name: left_btn(off) for name, off in
               (MATCH_SETTING_OFFSETS | ADVANCED_SETTING_OFFSETS).items()}
    buttons["switch_role"] = switch_role
    buttons["start_match"] = start_match
    return buttons


def _time_label(state: LobbyState) -> str:
    return "unlimited" if state.timer_mode == "timer" else state.time_control


def _cycle_time(state: LobbyState, dispatcher: LobbyDispatcher) -> None:
    options = ["unlimited"] + list(TIME_CONTROL_OPTIONS)
    try:
        idx = options.index(_time_label(state))
    except ValueError:
        idx = 0
    chosen = options[(idx + 1) % len(options)]
    if chosen == "unlimited":
        dispatcher.dispatch(LobbyAction("host", "set_timer_mode", str_value="timer"))
        return
    if state.timer_mode != "countdown":
        dispatcher.dispatch(LobbyAction("host", "set_timer_mode", str_value="countdown"))
    dispatcher.dispatch(LobbyAction("host", "set_time_control", str_value=chosen))


def _format_timeout(timeout: float) -> str:
    return "unlimited" if timeout == float("inf") else f"{int(timeout)}s"


def _setting_labels(state: LobbyState) -> dict[str, str]:
    return {
        "time": f"time: {_time_label(state)}",
        "swap_seats": f"host plays: {state.host_seat}",
        "god_view": f"god view: {'on' if state.god_view else 'off'}",
        "file_auto_delete": f"auto-delete log: {'yes' if state.file_auto_delete else 'no'}",
        "reconnect_timeout": f"reconnect timeout: {_format_timeout(state.reconnect_timeout)}",
    }


def _refresh_button_labels(buttons: dict[str, Button], state: LobbyState, role: str) -> None:
    for name, label in _setting_labels(state).items():
        buttons[name].text = label

    buttons["start_match"].text = "START MATCH" if state.peer_connected else "(waiting for player)"

    if _is_host(role):
        buttons["switch_role"].text = ""
    elif role == state.peer_seat():
        buttons["switch_role"].text = "switch to spectator"
    elif _is_spectator(role):
        if state.peer_connected:
            buttons["switch_role"].text = "(player slot occupied)"
        else:
            buttons["switch_role"].text = f"take {state.peer_seat()} seat"
    else:
        buttons["switch_role"].text = ""


def _render_settings_labels(gs: GameScreen, state: LobbyState) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    x = cx - bs * 3.15
    labels = _setting_labels(state)
    offsets = MATCH_SETTING_OFFSETS | ADVANCED_SETTING_OFFSETS
    for name, y_off in offsets.items():
        draw_text(labels[name], gs.mid_text_font, WHITE,
                  x, cy + bs * y_off + bs * 0.10, gs.surface)


def _render_advanced_header(gs: GameScreen) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    draw_text("advanced", gs.mid_text_font, WHITE,
              cx - bs * 3.3, cy + bs * ADVANCED_HEADER_OFFSET, gs.surface)


def _render_roster(gs: GameScreen, state: LobbyState, role: str) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    right_x = cx + bs * 0.3

    draw_text("LOBBY", gs.title_text_font, WHITE,
              cx - bs * 0.7, cy - bs * 2.8, gs.surface)

    draw_text("Settings", gs.text_font, WHITE,
              cx - bs * 3.3, cy - bs * 1.85, gs.surface)

    draw_text("Players", gs.text_font, WHITE,
              right_x, cy - bs * 1.85, gs.surface)

    host_seat = state.host_seat
    peer_seat = state.peer_seat()
    peer_status = "connected" if state.peer_connected else "waiting..."

    def lat_str(key: str) -> str:
        ms = state.latencies.get(key)
        return f" ({ms:.0f}ms)" if ms is not None else ""

    def you_marker(r: str) -> str:
        return "  <-- you" if role == r else ""

    spectator_you = you_marker("spectator") or you_marker("god")

    lines = [
        f"{host_seat}: host{you_marker('host')}",
        f"{peer_seat}: {peer_status}{lat_str(peer_seat)}{you_marker(peer_seat)}",
        f"spectators: {state.spectator_count}{spectator_you}",
    ]
    for i, line in enumerate(lines):
        draw_text(line, gs.text_font, WHITE,
                  right_x, cy - bs * (1.35 - i * 0.48), gs.surface)

    if state.god_view:
        draw_text("(spectators see all decks)", gs.mid_text_font, WHITE,
                  right_x, cy + bs * 0.20, gs.surface)


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


def _render_help(gs: GameScreen, role: str) -> None:
    bs = gs.block_size
    cy = gs.display_height / 2
    cx = gs.display_width / 2
    if _is_host(role):
        msg = "click to toggle / cycle  |  ESC: leave & shut down server"
    else:
        msg = "host controls settings  |  ESC: leave"
    draw_text(msg, gs.mid_text_font, WHITE,
              cx - bs * 3.3, cy + bs * 3.0, gs.surface)


def _click_dispatch(buttons: dict[str, Button], mouse_x: float, mouse_y: float,
                    state: LobbyState, role: str, dispatcher: LobbyDispatcher) -> None:
    if _is_host(role):
        if buttons["god_view"].touch(mouse_x, mouse_y):
            dispatcher.dispatch(LobbyAction("host", "set_god_view", bool_value=not state.god_view))
            return
        if buttons["time"].touch(mouse_x, mouse_y):
            _cycle_time(state, dispatcher)
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
    confirming_quit = False

    while True:
        if mode == "lan_client" and client is not None:
            if client.is_disconnected:
                server_closed_screen.main(game_screen)
                return LobbyExit(kind="quit")
            if client.pending_scene is not None:
                return LobbyExit(kind="start_match", state=state)
            if state.local_role:
                client.role = state.local_role

        if mode == "lan_server" and server is not None:
            server.pulse()

        if mode == "lan_server" and dispatcher.start_signal:
            return LobbyExit(kind="start_match", state=state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return LobbyExit(kind="quit")
            if event.type == pygame.KEYDOWN:
                if confirming_quit:
                    if event.key in (pygame.K_y, pygame.K_RETURN):
                        return LobbyExit(kind="quit")
                    if event.key in (pygame.K_n, pygame.K_ESCAPE):
                        confirming_quit = False
                    continue
                if event.key == pygame.K_ESCAPE:
                    if mode == "lan_server" and _room_has_others(state):
                        confirming_quit = True
                    else:
                        return LobbyExit(kind="quit")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not confirming_quit:
                mx, my = pygame.mouse.get_pos()
                _click_dispatch(buttons, mx, my, state, state.local_role, dispatcher)

        dispatcher.tick()

        game_screen.render()
        _render_roster(game_screen, state, state.local_role)
        _render_advanced_header(game_screen)
        _refresh_button_labels(buttons, state, state.local_role)

        if _is_host(state.local_role):
            for key in ("time", "swap_seats", "god_view", "file_auto_delete", "reconnect_timeout", "start_match"):
                buttons[key].update(game_screen)
        else:
            _render_settings_labels(game_screen, state)
            sw = buttons["switch_role"]
            if sw.text and not sw.text.startswith("("):
                sw.update(game_screen)
            elif sw.text:
                draw_text(sw.text, game_screen.mid_text_font, WHITE,
                          sw.x + game_screen.block_size * 0.15,
                          sw.y + game_screen.block_size * 0.10,
                          game_screen.surface)

        _render_help(game_screen, state.local_role)
        if confirming_quit:
            _render_quit_confirm(game_screen)
        pygame.display.update()
        clock.tick(60)
