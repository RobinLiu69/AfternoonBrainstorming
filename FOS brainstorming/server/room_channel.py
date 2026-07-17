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

import secrets
import socket
from typing import Optional

from core.network.server import LANServer


class RoomChannel(LANServer):
    def __init__(self, version: str, room_code: str,
                 god_view: bool = False, host_seat: str = "player1",
                 heartbeat_interval: float = 1.0, heartbeat_timeout: float = 10.0):
        self._role_tokens: dict[str, str] = {}
        self._forced_role: Optional[tuple[str, str]] = None
        super().__init__(version, host="", port=0, god_view=god_view,
                         host_seat=host_seat,
                         heartbeat_interval=heartbeat_interval,
                         heartbeat_timeout=heartbeat_timeout)
        self.room_code = room_code

    @property
    def _peer_token(self) -> Optional[str]:
        return self._role_tokens.get(self.peer_seat())

    @_peer_token.setter
    def _peer_token(self, value: Optional[str]) -> None:
        if value is None:
            self._role_tokens.pop(self.peer_seat(), None)
        else:
            self._role_tokens[self.peer_seat()] = value

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        with self._lock:
            conns = [c for c, _r in self._clients]
            self._clients.clear()
            self._last_seen.clear()
        for conn in conns:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                conn.close()
            except OSError:
                pass

    def adopt_creator(self, conn: socket.socket, addr, hello: dict) -> None:
        self._forced_role = ("host", secrets.token_urlsafe(16))
        try:
            self.handle_connection(conn, addr, hello)
        finally:
            self._forced_role = None

    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def has_role(self, role: str) -> bool:
        with self._lock:
            return any(r == role for _c, r in self._clients)

    def move_token(self, old_role: str, new_role: str) -> None:
        with self._lock:
            if old_role in self._role_tokens:
                self._role_tokens[new_role] = self._role_tokens.pop(old_role)

    def update_host_seat(self, new_seat: str) -> None:
        if new_seat not in ("player1", "player2") or new_seat == self.host_seat:
            return
        old_peer = self.peer_seat()
        self.host_seat = new_seat
        new_peer = self.peer_seat()
        with self._lock:
            self._clients = [(c, new_peer if r == old_peer else r) for c, r in self._clients]
            if old_peer in self._role_tokens:
                self._role_tokens[new_peer] = self._role_tokens.pop(old_peer)

    def _decide_role(self, intent: str, token: Optional[str]) -> tuple[str, str]:
        evicted: list[socket.socket] = []
        with self._lock:
            if self._forced_role is not None:
                chosen_role, issued_token = self._forced_role
                self._forced_role = None
                self._role_tokens[chosen_role] = issued_token
            else:
                token_role = ""
                if token:
                    token_role = next(
                        (r for r, t in self._role_tokens.items() if t == token), "")
                if token_role:
                    chosen_role = token_role
                    issued_token = token  # type: ignore[assignment]
                    kept: list[tuple[socket.socket, str]] = []
                    for c, r in self._clients:
                        if r == token_role:
                            evicted.append(c)
                            self._evicted.add(c)
                            self._last_seen.pop(c, None)
                        else:
                            kept.append((c, r))
                    self._clients = kept
                elif (self.scene == "lobby" and intent == "play"
                      and not any(r == self.peer_seat() for _c, r in self._clients)):
                    chosen_role = self.peer_seat()
                    issued_token = secrets.token_urlsafe(16)
                    self._role_tokens[chosen_role] = issued_token
                else:
                    chosen_role = "god" if self.god_view else "spectator"
                    issued_token = ""

        for c in evicted:
            try:
                c.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                c.close()
            except OSError:
                pass

        return chosen_role, issued_token
