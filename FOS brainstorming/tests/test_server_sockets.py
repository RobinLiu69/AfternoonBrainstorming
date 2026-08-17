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

import socket
import threading
import time

import pytest

from core.network.messages import _recv_msg, _send_msg
from core.network.server import LANServer
from shared.setting import VERSION


def wait_until(condition, timeout: float = 5.0, interval: float = 0.02):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = condition()
        if result:
            return result
        time.sleep(interval)
    raise AssertionError("condition not met within timeout")


@pytest.fixture
def server():
    lan = LANServer(VERSION, host="127.0.0.1", port=0)
    lan.set_scene("lobby")
    lan.start()
    lan.port = lan._server_sock.getsockname()[1]
    yield lan
    lan.stop()


def _hello(server: LANServer, intent: str = "play") -> tuple[socket.socket, dict]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    sock.connect(("127.0.0.1", server.port))
    _send_msg(sock, {"type": "hello", "intent": intent, "version": VERSION, "room": ""})
    return sock, _recv_msg(sock)


class TestOneClientCannotStallTheOthers:
    def test_each_connection_gets_its_own_write_lock(self, server) -> None:
        first, welcome_one = _hello(server)
        second, welcome_two = _hello(server, intent="watch")
        assert welcome_one["type"] == "welcome"
        assert welcome_two["type"] == "welcome"
        wait_until(lambda: server.roster.count() == 2)

        conns = [conn for conn, _role in server.roster.members()]
        locks = {id(server._write_lock_for(conn)) for conn in conns}

        assert len(locks) == 2
        first.close()
        second.close()

    def test_a_dropped_connection_takes_its_lock_with_it(self, server) -> None:
        sock, _welcome = _hello(server)
        wait_until(lambda: server.roster.count() == 1)
        conn = server.roster.members()[0][0]
        server._write_lock_for(conn)
        assert conn in server._write_locks

        sock.close()

        wait_until(lambda: server.roster.count() == 0)
        assert conn not in server._write_locks
        assert conn not in server._last_seen

    def test_a_silent_connection_does_not_block_the_next_one(self, server) -> None:
        mute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mute.connect(("127.0.0.1", server.port))

        started = time.monotonic()
        sock, welcome = _hello(server)
        elapsed = time.monotonic() - started

        assert welcome["type"] == "welcome"
        assert elapsed < 2.0
        mute.close()
        sock.close()


class TestABadActionDoesNotKillTheReceiveLoop:
    def test_the_loop_survives_a_raising_handler(self, server) -> None:
        seen: list[dict] = []

        def explode(envelope, conn):
            seen.append(envelope)
            raise RuntimeError("handler blew up")

        server.on_action = explode
        sock, _welcome = _hello(server)
        wait_until(lambda: server.roster.count() == 1)

        _send_msg(sock, {"type": "action", "seq": 1, "action_type": "toggle_hint"})
        assert _recv_msg(sock) == {"type": "ack", "seq": 1}

        _send_msg(sock, {"type": "action", "seq": 2, "action_type": "toggle_hint"})
        assert _recv_msg(sock) == {"type": "ack", "seq": 2}

        assert len(seen) == 2
        assert server.roster.count() == 1
        sock.close()


class TestTheSocketsAreTuned:
    def test_accepted_connections_disable_nagle(self, server) -> None:
        sock, _welcome = _hello(server)
        wait_until(lambda: server.roster.count() == 1)
        conn = server.roster.members()[0][0]

        assert conn.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY) == 1
        assert conn.gettimeout() is not None
        sock.close()
