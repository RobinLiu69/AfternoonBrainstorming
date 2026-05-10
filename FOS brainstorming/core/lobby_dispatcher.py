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

import time
from dataclasses import dataclass

from core.lobby_state import LobbyState, RECONNECT_TIMEOUT_OPTIONS
from core.network_layer import LANServer, LANClient
from screens.lobby_action import LobbyAction


@dataclass
class LobbyResult:
    success: bool
    message: str = ""


class LobbyDispatcher:
    def __init__(self, lobby_state: LobbyState, mode: str = "local"):
        self.mode = mode
        self._network = None
        self._state = lobby_state
        self.start_signal: bool = False
        self.peer_left: bool = False
        self._last_ping_time: float = 0.0

    def attach_server(self, server: "LANServer") -> None:
        self._network = server
        server.set_scene("lobby")
        server.host_seat = self._state.host_seat
        server.god_view = self._state.god_view
        server.on_action = self._on_remote_action
        server.on_client_connect = self._on_client_connect
        server.on_peer_disconnect = self._on_peer_disconnect
        server.on_peer_reconnect = self._on_peer_reconnect
        server.on_client_dropped = self._on_client_dropped
        server.on_pong = self._on_pong

    def attach_client(self, client: "LANClient") -> None:
        self._network = client
        client.on_state_update = self._state.apply_dict

    def _on_client_connect(self, role: str) -> dict:
        if role in ("player1", "player2"):
            self._state.peer_connected = True
        else:
            self._state.spectator_count += 1
        welcome_state = self._state.to_dict_for(role)
        self._broadcast()
        return welcome_state

    def _on_peer_disconnect(self) -> None:
        self._state.peer_connected = False
        self._broadcast()

    def _on_peer_reconnect(self) -> None:
        self._state.peer_connected = True
        self._broadcast()

    def _on_client_dropped(self, role: str) -> None:
        if role in ("spectator", "god") and self._state.spectator_count > 0:
            self._state.spectator_count -= 1
            self._broadcast()

    def _refresh_roster(self) -> None:
        if not isinstance(self._network, LANServer):
            return
        peer_seat = self._state.peer_seat()
        with self._network._lock:
            roles = [r for _c, r in self._network._clients]
        self._state.peer_connected = peer_seat in roles
        self._state.spectator_count = sum(1 for r in roles if r in ("spectator", "god"))

    def dispatch(self, action: LobbyAction) -> LobbyResult:
        match self.mode:
            case "lan_server":
                result = self._execute(action)
                if result.success:
                    self._broadcast()
                return result
            case "lan_client":
                self._send_to_server(action)
                return LobbyResult(True, message="pending")
        return LobbyResult(False, message=f"unknown mode: {self.mode}")

    def _on_remote_action(self, envelope: dict, sender_conn=None) -> None:
        payload = {k: v for k, v in envelope.items() if k != "type"}
        try:
            action = LobbyAction(**payload)
        except TypeError as e:
            print(f"[LobbyDispatcher] Bad remote action: {e}")
            return
        result = self._execute(action, sender_conn=sender_conn)
        if result.success:
            self._broadcast()

    def _send_to_server(self, action: LobbyAction) -> None:
        if not isinstance(self._network, LANClient):
            return
        self._network.send_action({
            "action_type": action.action_type,
            "player": action.player,
            "bool_value": action.bool_value,
            "str_value": action.str_value,
            "float_value": action.float_value,
        })

    def _execute(self, action: LobbyAction, sender_conn=None) -> LobbyResult:
        host_only = ("set_god_view", "set_timer_mode", "set_file_auto_delete",
                     "set_reconnect_timeout", "swap_seats", "start_match")
        if action.action_type in host_only and action.player != "host":
            return LobbyResult(False, message="host only")

        match action.action_type:
            case "set_god_view":
                if action.bool_value is None:
                    return LobbyResult(False)
                self._state.god_view = action.bool_value
                if isinstance(self._network, LANServer):
                    self._network.god_view = action.bool_value
                return LobbyResult(True)

            case "set_timer_mode":
                if action.str_value not in ("timer", "countdown"):
                    return LobbyResult(False)
                self._state.timer_mode = action.str_value
                return LobbyResult(True)

            case "set_file_auto_delete":
                if action.bool_value is None:
                    return LobbyResult(False)
                self._state.file_auto_delete = action.bool_value
                return LobbyResult(True)

            case "set_reconnect_timeout":
                if action.float_value is None or action.float_value not in RECONNECT_TIMEOUT_OPTIONS:
                    return LobbyResult(False)
                self._state.reconnect_timeout = action.float_value
                return LobbyResult(True)

            case "swap_seats":
                new_seat = "player2" if self._state.host_seat == "player1" else "player1"
                self._state.host_seat = new_seat
                if isinstance(self._network, LANServer):
                    self._network.update_host_seat(new_seat)
                return LobbyResult(True)

            case "switch_to_spectator":
                if not isinstance(self._network, LANServer):
                    return LobbyResult(False, message="server only")
                conn = sender_conn if sender_conn is not None else self._find_conn_by_role(action.player)
                if conn is None:
                    return LobbyResult(False, message="no such connection")
                if action.player not in ("player1", "player2"):
                    return LobbyResult(False, message="not a player slot")
                new_role = "god" if self._network.god_view else "spectator"
                self._network.reassign_role(conn, new_role)
                self._network._peer_token = None
                self._refresh_roster()
                return LobbyResult(True)

            case "switch_to_player":
                if not isinstance(self._network, LANServer):
                    return LobbyResult(False, message="server only")
                if self._state.peer_connected:
                    return LobbyResult(False, message="seat occupied")
                conn = sender_conn if sender_conn is not None else self._find_conn_by_role(action.player)
                if conn is None:
                    return LobbyResult(False, message="no such connection")
                import secrets
                new_token = secrets.token_urlsafe(16)
                self._network._peer_token = new_token
                peer_seat = self._network.peer_seat()
                self._network.reassign_role(conn, peer_seat)
                self._refresh_roster()
                return LobbyResult(True)

            case "start_match":
                if not self._state.peer_connected:
                    return LobbyResult(False, message="no peer")
                self.start_signal = True
                return LobbyResult(True)

            case "quit":
                return LobbyResult(True)

        return LobbyResult(False, message=f"unknown action: {action.action_type}")

    def _find_conn_by_role(self, role: str):
        if not isinstance(self._network, LANServer):
            return None
        with self._network._lock:
            for c, r in self._network._clients:
                if r == role:
                    return c
        return None

    def _on_pong(self, role: str, rtt_ms: float) -> None:
        self._state.latencies[role] = round(rtt_ms, 1)
        self._broadcast()

    def tick(self) -> None:
        if not isinstance(self._network, LANServer):
            return
        now = time.monotonic()
        if now - self._last_ping_time >= 2.0:
            self._last_ping_time = now
            self._network.broadcast_ping()
            self._network.check_heartbeat(timeout=10.0)

    def _broadcast(self) -> None:
        if not isinstance(self._network, LANServer):
            return
        self._network.broadcast_state_for(self._state.to_dict_for)
