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
import threading
from typing import Optional

from core.network.messages import _recv_msg, _send_msg
from server.room import Room


class RoomServer:
    def __init__(self, version: str, host: str = "0.0.0.0", port: int = 5555,
                 max_rooms: int = 50, room_client_cap: int = 16):
        self.version = version
        self.host = host
        self.port = port
        self.max_rooms = max_rooms
        self.room_client_cap = room_client_cap

        self._rooms: dict[str, Room] = {}
        self._lock = threading.Lock()
        self._server_sock: Optional[socket.socket] = None
        self._running = False
        self._accept_thread: Optional[threading.Thread] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def room_count(self) -> int:
        with self._lock:
            return len(self._rooms)

    def start(self) -> None:
        if self._running:
            return
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(32)
        self.port = self._server_sock.getsockname()[1]
        self._running = True
        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()
        print(f"[RoomServer] Listening on {self.host}:{self.port} (version {self.version})")

    def _accept_loop(self) -> None:
        if not self._server_sock:
            return
        while self._running:
            try:
                conn, addr = self._server_sock.accept()
            except OSError:
                break
            threading.Thread(target=self._handle_new_connection,
                             args=(conn, addr), daemon=True).start()

    def _reject(self, conn: socket.socket, addr, reason: str, **extra) -> None:
        try:
            _send_msg(conn, {"type": "rejected", "reason": reason, **extra})
        except OSError:
            pass
        try:
            conn.close()
        except OSError:
            pass
        print(f"[RoomServer] Rejected {addr}: {reason}")

    def _handle_new_connection(self, conn: socket.socket, addr) -> None:
        try:
            conn.settimeout(5.0)
            hello = _recv_msg(conn)
            conn.settimeout(None)
        except (OSError, ValueError):
            try:
                conn.close()
            except OSError:
                pass
            return

        if hello is None or hello.get("type") != "hello":
            print(f"[RoomServer] Bad hello from {addr}: {hello!r}")
            try:
                conn.close()
            except OSError:
                pass
            return

        client_version = hello.get("version", "")
        if client_version != self.version:
            self._reject(conn, addr, "version_mismatch",
                         server_version=self.version,
                         client_version=client_version)
            return

        room_code = str(hello.get("room", "") or "")
        if room_code == "":
            self._create_room_for(conn, addr, hello)
        else:
            self._join_room(conn, addr, hello, room_code)

    def _new_room_code(self) -> str:
        for _ in range(200):
            code = str(secrets.randbelow(9000) + 1000)
            if code not in self._rooms:
                return code
        raise RuntimeError("could not allocate a room code")

    def _create_room_for(self, conn: socket.socket, addr, hello: dict) -> None:
        with self._lock:
            if not self._running or len(self._rooms) >= self.max_rooms:
                room = None
            else:
                code = self._new_room_code()
                room = Room(code, version=self.version, on_close=self._on_room_close)
                self._rooms[code] = room
        if room is None:
            self._reject(conn, addr, "server_full")
            return
        print(f"[RoomServer] {addr} created room {room.code}")
        room.adopt_connection(conn, addr, hello, creator=True)

    def _join_room(self, conn: socket.socket, addr, hello: dict, room_code: str) -> None:
        with self._lock:
            room = self._rooms.get(room_code)
        if room is None or room.closed:
            self._reject(conn, addr, "room_not_found")
            return
        if room.channel.client_count() >= self.room_client_cap:
            self._reject(conn, addr, "room_full")
            return
        print(f"[RoomServer] {addr} joining room {room_code}")
        room.adopt_connection(conn, addr, hello)

    def _on_room_close(self, room: Room) -> None:
        with self._lock:
            existing = self._rooms.get(room.code)
            if existing is room:
                del self._rooms[room.code]

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False

        if self._server_sock:
            try:
                self._server_sock.close()
            except OSError:
                pass
            self._server_sock = None

        with self._lock:
            rooms = list(self._rooms.values())
        for room in rooms:
            room.close()

        if self._accept_thread is not None:
            self._accept_thread.join(timeout=2.0)
            self._accept_thread = None
        print("[RoomServer] stopped")
