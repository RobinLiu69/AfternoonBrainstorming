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

import core.network.token_store as token_store
from core.network.token_store import load_token, save_token
from core.network_layer import LANServer


class _FakeConn:
    def shutdown(self, *args) -> None:
        pass

    def close(self) -> None:
        pass


def test_token_store_roundtrip():
    assert load_token("10.0.0.1", 5555, "") == ""
    save_token("10.0.0.1", 5555, "", "abc")
    assert load_token("10.0.0.1", 5555, "") == "abc"

    save_token("10.0.0.1", 5555, "1234", "room-token")
    assert load_token("10.0.0.1", 5555, "1234") == "room-token"
    assert load_token("10.0.0.1", 5555, "") == "abc"

    save_token("10.0.0.1", 5555, "", "def")
    assert load_token("10.0.0.1", 5555, "") == "def"

    save_token("10.0.0.1", 5555, "", "")
    assert load_token("10.0.0.1", 5555, "") == ""
    assert load_token("10.0.0.1", 5555, "1234") == "room-token"


def test_second_instance_is_not_primary(monkeypatch):
    import socket

    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    port = blocker.getsockname()[1]

    monkeypatch.setattr(token_store, "_primary", None)
    monkeypatch.setattr(token_store, "_lock_sock", None)
    monkeypatch.setattr(token_store, "INSTANCE_LOCK_PORT", port)
    try:
        assert token_store.is_primary_instance() is False
        assert token_store.is_primary_instance() is False
    finally:
        blocker.close()


def test_first_instance_is_primary(monkeypatch):
    import socket

    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()

    monkeypatch.setattr(token_store, "_primary", None)
    monkeypatch.setattr(token_store, "_lock_sock", None)
    monkeypatch.setattr(token_store, "INSTANCE_LOCK_PORT", port)
    try:
        assert token_store.is_primary_instance() is True
    finally:
        if token_store._lock_sock is not None:
            token_store._lock_sock.close()


def test_token_store_survives_corrupt_file():
    token_store.TOKEN_FILE.write_text("not json", encoding="utf-8")
    assert load_token("10.0.0.1", 5555, "") == ""
    save_token("10.0.0.1", 5555, "", "abc")
    assert load_token("10.0.0.1", 5555, "") == "abc"


def test_lan_seat_granted_only_in_lobby():
    server = LANServer("test")
    server.set_scene("lobby")
    role, token = server._decide_role("play", None)
    assert role == "player2"
    assert token

    server.set_scene("battling")
    role, token = server._decide_role("play", None)
    assert role == "spectator"
    assert token == ""

    server.god_view = True
    role, token = server._decide_role("play", None)
    assert role == "god"
    assert token == ""


def test_lan_token_reclaims_seat_mid_battle():
    server = LANServer("test")
    server.set_scene("lobby")
    seat, token = server._decide_role("play", None)
    stale = _FakeConn()
    server._clients.append((stale, seat))

    server.set_scene("battling")
    role, reissued = server._decide_role("play", token)
    assert role == seat
    assert reissued == token
    assert all(c is not stale for c, _r in server._clients)

    role, token = server._decide_role("play", "wrong-token")
    assert role == "spectator"
    assert token == ""
