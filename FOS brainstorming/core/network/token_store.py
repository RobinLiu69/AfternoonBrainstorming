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
from pathlib import Path
from typing import Optional

from shared.setting import FOLDER_PATH

TOKEN_FILE = Path(FOLDER_PATH) / "net_tokens.json"

INSTANCE_LOCK_PORT = 47821

_primary: Optional[bool] = None
_lock_sock: Optional[socket.socket] = None


def is_primary_instance() -> bool:
    global _primary, _lock_sock
    if _primary is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", INSTANCE_LOCK_PORT))
            sock.listen(1)
            _lock_sock = sock
            _primary = True
        except OSError:
            sock.close()
            _primary = False
            print("[token_store] another game instance is running; "
                  "token persistence disabled for this instance")
    return _primary


def _key(host: str, port: int, room: str) -> str:
    return f"{host}:{port}/{room}"


def _load_all() -> dict:
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_token(host: str, port: int, room: str) -> str:
    value = _load_all().get(_key(host, port, room), "")
    return value if isinstance(value, str) else ""


def save_token(host: str, port: int, room: str, token: str) -> None:
    data = _load_all()
    key = _key(host, port, room)
    if token:
        data[key] = token
    elif key in data:
        del data[key]
    else:
        return
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError as e:
        print(f"[token_store] failed to persist token: {e}")
