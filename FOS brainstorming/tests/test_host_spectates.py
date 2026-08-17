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
import time

import pytest

from core.lobby_dispatcher import LobbyDispatcher
from core.lobby_state import LobbyState
from core.network.messages import _recv_msg, _send_msg
from core.network.server import LANServer
from screens.lobby.lobby_action import LobbyAction
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
def lobby():
    state = LobbyState()
    server = LANServer(VERSION, host="127.0.0.1", port=0)
    dispatcher = LobbyDispatcher(state, mode="lan_server")
    server.start()
    server.port = server._server_sock.getsockname()[1]
    dispatcher.attach_server(server)
    yield state, dispatcher, server
    server.stop()


def _join(server: LANServer, intent: str = "play", token: str = "") -> tuple:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    sock.connect(("127.0.0.1", server.port))
    hello = {"type": "hello", "intent": intent, "version": VERSION, "room": ""}
    if token:
        hello["token"] = token
    _send_msg(sock, hello)
    welcome = _recv_msg(sock)
    return sock, welcome["role"], welcome.get("token", "")


class TestTheSeatBookkeeping:
    def test_only_the_peer_seat_is_open_while_the_host_plays(self) -> None:
        state = LobbyState()

        assert state.open_seats() == ("player2",)
        assert state.seat_filled("player1") is True
        assert state.both_seats_filled() is False

    def test_both_seats_open_once_the_host_steps_out(self) -> None:
        state = LobbyState(host_playing=False)

        assert set(state.open_seats()) == {"player1", "player2"}
        assert state.seat_filled("player1") is False
        assert state.both_seats_filled() is False

        state.host_seat_connected = True
        state.peer_connected = True
        assert state.both_seats_filled() is True

    def test_a_seat_still_knows_which_identity_it_carries(self) -> None:
        state = LobbyState(host_seat="player2")

        assert state.seat_identity("player2") == "host"
        assert state.seat_identity("player1") == "peer"


class TestTheHostCanStepOutOfTheSeat:
    def test_switching_to_spectator_opens_the_host_seat(self, lobby) -> None:
        state, dispatcher, server = lobby

        assert dispatcher.dispatch(LobbyAction("host", "switch_to_spectator")).success

        assert state.host_playing is False
        assert server.roster.host_playing is False
        assert set(server.roster.open_seats()) == {"player1", "player2"}

    def test_the_host_can_take_the_seat_back(self, lobby) -> None:
        state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))

        assert dispatcher.dispatch(LobbyAction("host", "switch_to_player")).success

        assert state.host_playing is True
        assert server.roster.open_seats() == (state.peer_seat(),)

    def test_the_host_cannot_take_a_seat_someone_else_holds(self, lobby) -> None:
        state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))
        first, role, _token = _join(server)
        wait_until(lambda: server.roster.count() == 1)
        dispatcher._refresh_roster()

        result = dispatcher.dispatch(LobbyAction("host", "switch_to_player"))

        assert role in ("player1", "player2")
        if role == state.host_seat:
            assert result.success is False
            assert state.host_playing is False
        first.close()

    def test_a_vacated_host_seat_is_handed_to_the_next_player(self, lobby) -> None:
        state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))

        first, first_role, _t1 = _join(server)
        second, second_role, _t2 = _join(server)
        wait_until(lambda: server.roster.count() == 2)
        dispatcher._refresh_roster()

        assert {first_role, second_role} == {"player1", "player2"}
        assert state.both_seats_filled() is True
        first.close()
        second.close()

    def test_a_third_joiner_still_only_gets_to_watch(self, lobby) -> None:
        _state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))
        first, _r1, _t1 = _join(server)
        second, _r2, _t2 = _join(server)
        wait_until(lambda: server.roster.count() == 2)

        third, third_role, _t3 = _join(server)

        assert third_role == "spectator"
        for sock in (first, second, third):
            sock.close()

    def test_each_seat_keeps_its_own_reconnect_token(self, lobby) -> None:
        _state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))
        first, first_role, first_token = _join(server)
        second, second_role, second_token = _join(server)
        wait_until(lambda: server.roster.count() == 2)

        assert first_token and second_token and first_token != second_token
        first.close()
        wait_until(lambda: server.roster.count() == 1)

        back, back_role, _token = _join(server, token=first_token)

        assert back_role == first_role
        assert second_role != first_role
        second.close()
        back.close()


class TestTheMatchWaitsForBothSeats:
    def test_the_host_cannot_start_with_an_empty_seat(self, lobby) -> None:
        _state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))
        first, _role, _token = _join(server)
        wait_until(lambda: server.roster.count() == 1)
        dispatcher._refresh_roster()

        result = dispatcher.dispatch(LobbyAction("host", "start_match"))

        assert result.success is False
        assert dispatcher.start_signal is False
        first.close()

    def test_the_host_can_start_once_both_seats_are_taken(self, lobby) -> None:
        _state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))
        first, _r1, _t1 = _join(server)
        second, _r2, _t2 = _join(server)
        wait_until(lambda: server.roster.count() == 2)
        dispatcher._refresh_roster()

        assert dispatcher.dispatch(LobbyAction("host", "start_match")).success is True
        assert dispatcher.start_signal is True
        first.close()
        second.close()

    def test_a_seated_client_names_the_seat_it_holds(self, lobby) -> None:
        state, dispatcher, server = lobby
        dispatcher.dispatch(LobbyAction("host", "switch_to_spectator"))

        dispatcher.dispatch(LobbyAction(state.host_seat, "set_name", str_value="Alice"))
        dispatcher.dispatch(LobbyAction(state.peer_seat(), "set_name", str_value="Bob"))

        assert state.player_names == {"host": "Alice", "peer": "Bob"}
        assert state.seat_names() == {state.host_seat: "Alice", state.peer_seat(): "Bob"}
