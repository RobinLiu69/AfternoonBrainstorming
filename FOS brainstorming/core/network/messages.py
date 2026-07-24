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
from typing import Callable, Optional


MAX_MESSAGE_BYTES = 16 * 1024 * 1024

ENVELOPE_KEYS: frozenset = frozenset({"type", "seq"})


def action_payload(envelope: dict) -> dict:
    return {k: v for k, v in envelope.items() if k not in ENVELOPE_KEYS}


def _recv_exactly(sock: socket.socket, n: int,
                  on_idle: Optional[Callable[[], bool]] = None) -> Optional[bytes]:
    buf = b""
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except TimeoutError:
            if on_idle is not None and on_idle():
                continue
            raise
        if not chunk:
            return None
        buf += chunk
    return buf


def _send_msg(sock: socket.socket, payload: dict) -> None:
    data = json.dumps(payload).encode()
    sock.sendall(struct.pack(">I", len(data)) + data)


def _recv_msg(sock: socket.socket,
              on_idle: Optional[Callable[[], bool]] = None) -> Optional[dict]:
    raw_len = _recv_exactly(sock, 4, on_idle)
    if raw_len is None:
        return None
    length = struct.unpack(">I", raw_len)[0]
    if length > MAX_MESSAGE_BYTES:
        raise ValueError(f"message too large: {length} bytes")
    raw_data = _recv_exactly(sock, length, on_idle)
    if raw_data is None:
        return None
    return json.loads(raw_data.decode())

