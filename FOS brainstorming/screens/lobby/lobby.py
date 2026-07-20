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
from typing import Callable, Optional, Sequence, TypeVar

import pygame

from core.match_settings import RULESET_OPTIONS, TIME_CONTROL_OPTIONS
from core.lobby_state import LobbyState, RECONNECT_TIMEOUT_OPTIONS
from core.lobby_dispatcher import LobbyDispatcher
from core.network_layer import LANServer, LANClient
from core.game_screen import GameScreen, draw_text
from core.setting_config import load_setting
from core.UI import Button
from screens.lobby import ban_draft
from screens.lobby.lobby_action import LobbyAction, set_setting
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


T = TypeVar("T")


def _next_option(options: Sequence[T], current: T) -> T:
    items = list(options)
    try:
        idx = items.index(current)
    except ValueError:
        idx = -1
    return items[(idx + 1) % len(items)]


def _format_timeout(timeout: float) -> str:
    return "unlimited" if timeout == float("inf") else f"{int(timeout)}s"


def _cycle_time(state: LobbyState, dispatcher: LobbyDispatcher) -> None:
    options = ["unlimited"] + list(TIME_CONTROL_OPTIONS)
    chosen = _next_option(options, state.settings.time_label())
    if chosen == "unlimited":
        dispatcher.dispatch(set_setting("timer_mode", "timer"))
        return
    if state.settings.timer_mode != "countdown":
        dispatcher.dispatch(set_setting("timer_mode", "countdown"))
    dispatcher.dispatch(set_setting("time_control", chosen))


@dataclass(frozen=True)
class _SettingRow:
    label: Callable[[LobbyState], str]
    click: Callable[[LobbyState, LobbyDispatcher], object]


ROWS: dict[str, _SettingRow] = {
    "time": _SettingRow(
        label=lambda s: f"time: {s.settings.time_label()}",
        click=_cycle_time),
    "ruleset": _SettingRow(
        label=lambda s: f"ruleset: {s.settings.ruleset}",
        click=lambda s, d: d.dispatch(set_setting(
            "ruleset", _next_option(RULESET_OPTIONS, s.settings.ruleset)))),
    "swap_seats": _SettingRow(
        label=lambda s: f"host plays: {s.host_seat}",
        click=lambda s, d: d.dispatch(LobbyAction("host", "swap_seats"))),
    "ban_draft": _SettingRow(
        label=lambda s: f"ban draft ({len(s.bans)} banned)",
        click=lambda s, d: d.dispatch(LobbyAction("host", "set_ban_draft", bool_value=True))),
    "god_view": _SettingRow(
        label=lambda s: f"god view: {'on' if s.god_view else 'off'}",
        click=lambda s, d: d.dispatch(set_setting("god_view", not s.god_view))),
    "file_auto_delete": _SettingRow(
        label=lambda s: f"auto-delete log: {'yes' if s.settings.file_auto_delete else 'no'}",
        click=lambda s, d: d.dispatch(set_setting(
            "file_auto_delete", not s.settings.file_auto_delete))),
    "reconnect_timeout": _SettingRow(
        label=lambda s: f"reconnect timeout: {_format_timeout(s.reconnect_timeout)}",
        click=lambda s, d: d.dispatch(set_setting(
            "reconnect_timeout", _next_option(RECONNECT_TIMEOUT_OPTIONS, s.reconnect_timeout)))),
}

MATCH_ROWS = ("time", "ruleset", "swap_seats", "ban_draft")
ADVANCED_ROWS = ("god_view", "file_auto_delete", "reconnect_timeout")
LOCAL_ROWS = ("time", "ruleset", "file_auto_delete")

FIRST_ROW_OFFSET = -1.55
ROW_STEP = 0.45
ADVANCED_HEADER_GAP = 0.60
ADVANCED_HEADER_TO_ROW = 0.25


def _layout(mode: str) -> tuple[dict[str, float], Optional[float]]:
    offsets: dict[str, float] = {}
    y = FIRST_ROW_OFFSET
    for name in (LOCAL_ROWS if mode == "local" else MATCH_ROWS):
        offsets[name] = y
        y += ROW_STEP
    if mode == "local":
        return offsets, None

    header = y - ROW_STEP + ADVANCED_HEADER_GAP
    y = header + ADVANCED_HEADER_TO_ROW
    for name in ADVANCED_ROWS:
        offsets[name] = y
        y += ROW_STEP
    return offsets, header


def _make_buttons(gs: GameScreen, row_offsets: dict[str, float]) -> dict[str, Button]:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    box_width = max(1, int(bs / 30))

    left_btn_w = bs * 2.8
    btn_h = bs * 0.43
    left_x = cx - bs * 3.3

    buttons = {name: Button(left_btn_w, btn_h, left_x, cy + bs * y_offset,
                            position="Left", padding=bs * 0.15,
                            box_width=box_width, font=gs.mid_text_font)
               for name, y_offset in row_offsets.items()}

    switch_w = bs * 2.5
    buttons["switch_role"] = Button(switch_w, btn_h, cx - switch_w / 2, cy + bs * 1.70,
                                    position="Left", padding=bs * 0.15,
                                    box_width=box_width, font=gs.mid_text_font)

    start_w = bs * 3.2
    buttons["start_match"] = Button(start_w, bs * 0.55, cx - start_w / 2, cy + bs * 2.30,
                                    position="Middle", padding=bs * 0.15,
                                    box_width=box_width, font=gs.text_font, text="START MATCH")
    return buttons


def _refresh_button_labels(buttons: dict[str, Button], state: LobbyState, role: str, mode: str) -> None:
    for name, row in ROWS.items():
        if name in buttons:
            buttons[name].text = row.label(state)

    if mode == "local":
        buttons["start_match"].text = "START"
    else:
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


def _render_settings_labels(gs: GameScreen, state: LobbyState,
                            row_offsets: dict[str, float]) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    x = cx - bs * 3.15
    for name, y_offset in row_offsets.items():
        draw_text(ROWS[name].label(state), gs.mid_text_font, WHITE,
                  x, cy + bs * y_offset + bs * 0.10, gs.surface)


def _render_advanced_header(gs: GameScreen, y_offset: float) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    draw_text("advanced", gs.mid_text_font, WHITE,
              cx - bs * 3.3, cy + bs * y_offset, gs.surface)


def _render_title(gs: GameScreen) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2

    draw_text("LOBBY", gs.title_text_font, WHITE,
              cx - bs * 0.7, cy - bs * 2.8, gs.surface)

    draw_text("Settings", gs.text_font, WHITE,
              cx - bs * 3.3, cy - bs * 1.85, gs.surface)


def _render_roster(gs: GameScreen, state: LobbyState, role: str) -> None:
    bs = gs.block_size
    cx = gs.display_width / 2
    cy = gs.display_height / 2
    right_x = cx + bs * 0.3

    if state.room_code:
        draw_text(f"room: {state.room_code}", gs.text_font, WHITE,
                  right_x, cy - bs * 2.35, gs.surface)

    draw_text("Players", gs.text_font, WHITE,
              right_x, cy - bs * 1.85, gs.surface)

    host_seat = state.host_seat
    peer_seat = state.peer_seat()
    host_label = state.display_name("host") or "host"
    if state.peer_connected:
        peer_label = state.display_name("peer") or "connected"
    else:
        peer_label = "waiting..."

    def lat_str(key: str) -> str:
        ms = state.latencies.get(key)
        return f" ({ms:.0f}ms)" if ms is not None else ""

    def you_marker(r: str) -> str:
        return "  <-- you" if role == r else ""

    spectator_you = you_marker("spectator") or you_marker("god")

    lines = [
        f"{host_seat}: {host_label}{you_marker('host')}",
        f"{peer_seat}: {peer_label}{lat_str(peer_seat)}{you_marker(peer_seat)}",
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


def _render_help(gs: GameScreen, role: str, mode: str) -> None:
    bs = gs.block_size
    cy = gs.display_height / 2
    cx = gs.display_width / 2
    if mode == "local":
        msg = "click to toggle / cycle  |  ESC: back"
    elif _is_host(role):
        msg = "click to toggle / cycle  |  ESC: leave & shut down server"
    else:
        msg = "host controls settings  |  ESC: leave"
    draw_text(msg, gs.mid_text_font, WHITE,
              cx - bs * 3.3, cy + bs * 3.0, gs.surface)


def _click_dispatch(buttons: dict[str, Button], mouse_x: float, mouse_y: float,
                    state: LobbyState, role: str, dispatcher: LobbyDispatcher) -> None:
    def touched(name: str) -> bool:
        button = buttons.get(name)
        return button is not None and button.touch(mouse_x, mouse_y)

    if _is_host(role):
        for name, row in ROWS.items():
            if touched(name):
                row.click(state, dispatcher)
                return
        if touched("start_match"):
            dispatcher.dispatch(LobbyAction("host", "start_match"))
    else:
        if touched("switch_role"):
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

    if mode == "local":
        state.local_role = "host"

    elif mode == "lan_server":
        assert server is not None
        dispatcher.attach_server(server)
        if not server.is_running:
            server.start()
        state.local_role = "host"
        my_name = load_setting("player_name")
        if my_name:
            dispatcher.dispatch(LobbyAction("host", "set_name", str_value=my_name))

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

    row_offsets, advanced_header_offset = _layout(mode)
    buttons = _make_buttons(game_screen, row_offsets)
    clock = pygame.time.Clock()
    confirming_quit = False
    my_name = load_setting("player_name") if mode == "lan_client" else ""
    name_sent_as = ""

    while True:
        if mode == "lan_client" and client is not None:
            if client.is_disconnected:
                server_closed_screen.main(game_screen)
                return LobbyExit(kind="quit")
            if client.pending_scene is not None:
                return LobbyExit(kind="start_match", state=state)
            if state.local_role and client.pending_scene is None:
                client.role = state.local_role
            if my_name and state.local_role and state.local_role != name_sent_as:
                dispatcher.dispatch(LobbyAction(state.local_role, "set_name",
                                                str_value=my_name))
                name_sent_as = state.local_role

        if mode == "lan_server" and server is not None:
            server.pulse()

        if dispatcher.start_signal:
            return LobbyExit(kind="start_match", state=state)

        if mode != "local" and state.in_ban_draft:
            ban_exit = ban_draft.main(game_screen, state, dispatcher, mode,
                                      server=server, client=client)
            if ban_exit == "quit":
                return LobbyExit(kind="quit")
            if ban_exit == "disconnected":
                server_closed_screen.main(game_screen)
                return LobbyExit(kind="quit")
            continue

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
        _render_title(game_screen)
        if mode != "local":
            _render_roster(game_screen, state, state.local_role)
        if advanced_header_offset is not None:
            _render_advanced_header(game_screen, advanced_header_offset)
        _refresh_button_labels(buttons, state, state.local_role, mode)

        if _is_host(state.local_role):
            for name, button in buttons.items():
                if name != "switch_role":
                    button.update(game_screen)
        else:
            _render_settings_labels(game_screen, state, row_offsets)
            sw = buttons["switch_role"]
            if sw.text and not sw.text.startswith("("):
                sw.update(game_screen)
            elif sw.text:
                draw_text(sw.text, game_screen.mid_text_font, WHITE,
                          sw.x + game_screen.block_size * 0.15,
                          sw.y + game_screen.block_size * 0.10,
                          game_screen.surface)

        _render_help(game_screen, state.local_role, mode)
        if confirming_quit:
            _render_quit_confirm(game_screen)
        pygame.display.update()
        clock.tick(60)
