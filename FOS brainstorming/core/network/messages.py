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

import json
import socket
import struct
from typing import Optional


def _recv_exactly(sock: socket.socket, n: int) -> Optional[bytes]:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _send_msg(sock: socket.socket, payload: dict) -> None:
    data = json.dumps(payload).encode()
    sock.sendall(struct.pack(">I", len(data)) + data)


def _recv_msg(sock: socket.socket) -> Optional[dict]:
    raw_len = _recv_exactly(sock, 4)
    if raw_len is None:
        return None
    length = struct.unpack(">I", raw_len)[0]
    raw_data = _recv_exactly(sock, length)
    if raw_data is None:
        return None
    return json.loads(raw_data.decode())

