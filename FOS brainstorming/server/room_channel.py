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
        self._forced_role: Optional[tuple[str, str]] = None
        super().__init__(version, host="", port=0, god_view=god_view,
                         host_seat=host_seat,
                         heartbeat_interval=heartbeat_interval,
                         heartbeat_timeout=heartbeat_timeout)
        self.room_code = room_code

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
            self._write_locks.clear()
            self._evicted.clear()
        for conn in conns:
            self._force_close(conn)

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

    def _decide_role(self, intent: str, token: Optional[str]) -> tuple[str, str]:
        with self._lock:
            forced = self._forced_role
            if forced is not None:
                chosen_role, issued_token = forced
                self._forced_role = None
                self._role_tokens[chosen_role] = issued_token
        if forced is not None:
            return chosen_role, issued_token
        return super()._decide_role(intent, token)
