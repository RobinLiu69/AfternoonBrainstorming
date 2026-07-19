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
import struct
import time

import pytest

from shared.setting import VERSION
from core.network.client import LANClient
from cards.factory import CardFactory
from server.room_server import RoomServer

CardFactory.register_all()

TEST_DECK = ["ADCW", "ADCW", "TANKW", "TANKW", "APW", "APW",
             "HFW", "HFW", "LFW", "LFW", "ASSW", "ASSW"]


def wait_until(condition, timeout: float = 8.0, interval: float = 0.02):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = condition()
        if result:
            return result
        time.sleep(interval)
    raise AssertionError("condition not met within timeout")


class StateCollector:
    def __init__(self, client: LANClient):
        self.states: list[dict] = []
        client.on_state_update = self.states.append

    @property
    def last(self):
        return self.states[-1] if self.states else None


@pytest.fixture
def room_server():
    server = RoomServer(VERSION, host="127.0.0.1", port=0)
    server.start()
    clients: list[LANClient] = []

    def make_client(room: str = "") -> LANClient:
        client = LANClient(VERSION, "127.0.0.1", port=server.port, room=room)
        clients.append(client)
        return client

    yield server, make_client

    for client in clients:
        client.disconnect()
    server.stop()


def _send_lobby(client: LANClient, action_type: str, player: str = "host", **extra):
    client.send_action({"action_type": action_type, "player": player, **extra})


def _send_draft(client: LANClient, action_type: str, player: str, card_name: str = ""):
    client.send_action({"action_type": action_type, "player": player,
                        "card_name": card_name})


def _send_battle(client: LANClient, action_type: str, player: str, **extra):
    client.send_action({"action_type": action_type, "player": player, **extra})


def _draft_full_deck(owner_client, joiner_client, owner_seat="player1"):
    joiner_seat = "player2" if owner_seat == "player1" else "player1"
    p1_client = owner_client if owner_seat == "player1" else joiner_client
    p2_client = joiner_client if owner_seat == "player1" else owner_client
    p1_collector = StateCollector(p1_client)

    for card in TEST_DECK[:6]:
        _send_draft(p1_client, "add_card", "player1", card)
    _send_draft(p1_client, "advance_phase", "player1")
    wait_until(lambda: p1_collector.last is not None
               and p1_collector.last.get("phase") == "p2_pick12")

    for card in TEST_DECK:
        _send_draft(p2_client, "add_card", "player2", card)
    _send_draft(p2_client, "advance_phase", "player2")
    wait_until(lambda: p1_collector.last.get("phase") == "p1_last6")

    for card in TEST_DECK[6:]:
        _send_draft(p1_client, "add_card", "player1", card)
    _send_draft(p1_client, "advance_phase", "player1")


def test_create_room_assigns_code_and_host_role(room_server):
    server, make_client = room_server
    creator = make_client()
    role, state = creator.connect()

    assert role == "host"
    assert creator.scene == "lobby"
    assert creator.room.isdigit() and len(creator.room) == 4
    assert state["room_code"] == creator.room
    assert state["your_role"] == "host"
    assert server.room_count() == 1


def test_join_room_as_player_and_spectator(room_server):
    server, make_client = room_server
    creator = make_client()
    creator.connect()

    joiner = make_client(room=creator.room)
    role, state = joiner.connect()
    assert role == "player2"
    assert state["peer_connected"] is True

    spectator = make_client(room=creator.room)
    role, state = spectator.connect()
    assert role == "spectator"
    assert state["spectator_count"] == 1


def test_join_unknown_room_rejected(room_server):
    _server, make_client = room_server
    client = make_client(room="0000")
    with pytest.raises(ConnectionError, match="room_not_found"):
        client.connect()


def test_rooms_are_isolated(room_server):
    server, make_client = room_server
    creator_a = make_client()
    creator_a.connect()
    creator_b = make_client()
    creator_b.connect()

    assert creator_a.room != creator_b.room
    assert server.room_count() == 2

    joiner_b = make_client(room=creator_b.room)
    role, state = joiner_b.connect()
    assert role == "player2"

    collector_a = StateCollector(creator_a)
    time.sleep(0.3)
    assert all(not s.get("peer_connected") for s in collector_a.states)


def test_non_owner_cannot_use_host_actions(room_server):
    _server, make_client = room_server
    creator = make_client()
    creator.connect()
    joiner = make_client(room=creator.room)
    joiner.connect()

    creator_collector = StateCollector(creator)
    _send_lobby(joiner, "set_setting", player="host", setting="god_view", bool_value=True)
    _send_lobby(joiner, "start_match", player="host")
    time.sleep(0.5)

    assert creator.pending_scene is None
    assert all(not s.get("god_view") for s in creator_collector.states)


def test_full_match_flow(room_server):
    server, make_client = room_server
    creator = make_client()
    creator.connect()
    joiner = make_client(room=creator.room)
    joiner.connect()

    _send_lobby(creator, "set_setting", setting="file_auto_delete", bool_value=True)
    _send_lobby(creator, "set_setting", setting="timer_mode", str_value="countdown")
    _send_lobby(creator, "set_setting", setting="time_control", str_value="5+5")
    _send_lobby(creator, "start_match")
    wait_until(lambda: creator.pending_scene == "draft")
    wait_until(lambda: joiner.pending_scene == "draft")

    assert creator.role == "player1"
    assert joiner.role == "player2"
    creator.consume_pending_scene()
    joiner.consume_pending_scene()

    _draft_full_deck(creator, joiner)

    wait_until(lambda: creator.pending_scene == "battling")
    wait_until(lambda: joiner.pending_scene == "battling")
    _scene, battle_state = creator.consume_pending_scene()
    joiner.consume_pending_scene()

    assert battle_state["turn_number"] == 0
    assert len(battle_state["player1"]["hand"]) > 0
    assert battle_state["player1"]["deck"] == TEST_DECK
    assert battle_state["player2"]["deck"] == ["?"] * 12
    assert "rng_seed" not in battle_state
    assert battle_state["player2"]["draw_pile"] == ["?"] * len(battle_state["player2"]["draw_pile"])
    assert battle_state["timer_mode"] == "countdown"
    assert battle_state["countdown_time"] == 300
    assert battle_state["player1"]["elapsed_time"] == 300

    creator_collector = StateCollector(creator)
    _send_battle(creator, "end_turn", "player1")
    wait_until(lambda: creator_collector.last is not None
               and creator_collector.last.get("turn_number") == 1)
    assert 303 <= creator_collector.last["player1"]["elapsed_time"] <= 305

    _send_battle(joiner, "end_turn", "player2")
    wait_until(lambda: creator_collector.last.get("turn_number") == 2)

    _send_battle(joiner, "end_turn", "player2")
    time.sleep(0.3)
    assert creator_collector.last.get("turn_number") == 2


def test_player_reconnect_during_draft(room_server):
    _server, make_client = room_server
    creator = make_client()
    creator.connect()
    joiner = make_client(room=creator.room)
    joiner.connect()

    _send_lobby(creator, "start_match")
    wait_until(lambda: creator.pending_scene == "draft")
    creator.consume_pending_scene()

    creator_collector = StateCollector(creator)
    joiner.disconnect()
    wait_until(lambda: creator_collector.last is not None
               and creator_collector.last.get("paused") is True)

    assert joiner.try_reconnect() is True
    assert joiner.role == "player2"
    wait_until(lambda: creator_collector.last.get("paused") is False)


def test_impersonated_actions_are_dropped(room_server):
    _server, make_client = room_server
    creator = make_client()
    creator.connect()
    joiner = make_client(room=creator.room)
    joiner.connect()
    spectator = make_client(room=creator.room)
    spectator.connect()

    _send_lobby(creator, "start_match")
    wait_until(lambda: creator.pending_scene == "draft")
    creator.consume_pending_scene()

    creator_collector = StateCollector(creator)
    _send_draft(spectator, "add_card", "player1", "ADCW")
    _send_draft(joiner, "add_card", "player1", "ADCW")
    time.sleep(0.5)
    assert all(not s.get("player1_deck") for s in creator_collector.states)

    _send_draft(creator, "add_card", "player1", "ADCW")
    wait_until(lambda: creator_collector.last is not None
               and creator_collector.last.get("player1_deck") == ["ADCW"])


def test_oversized_message_does_not_kill_server(room_server):
    server, make_client = room_server
    raw = socket.create_connection(("127.0.0.1", server.port), timeout=5)
    raw.sendall(struct.pack(">I", 0x7FFFFFFF) + b"junk")
    raw.close()
    time.sleep(0.3)

    creator = make_client()
    role, _state = creator.connect()
    assert role == "host"


def test_switch_to_player_receives_reconnect_token(room_server):
    _server, make_client = room_server
    creator = make_client()
    creator.connect()
    spectator = make_client(room=creator.room)
    role, _state = spectator.connect(intent="spectate")
    assert role == "spectator"

    spectator.send_action({"action_type": "switch_to_player", "player": "spectator"})
    wait_until(lambda: spectator.token)

    spectator.disconnect()
    wait_until(lambda: spectator.try_reconnect() is True, interval=0.3)
    assert spectator.role == "player2"


def test_deck_hidden_from_log_until_game_over(room_server):
    server, make_client = room_server
    creator = make_client()
    creator.connect()
    joiner = make_client(room=creator.room)
    joiner.connect()
    room = server._rooms[creator.room]

    _send_lobby(creator, "start_match")
    wait_until(lambda: creator.pending_scene == "draft")
    creator.consume_pending_scene()
    joiner.consume_pending_scene()

    _draft_full_deck(creator, joiner)
    wait_until(lambda: creator.pending_scene == "battling")

    wait_until(lambda: room.game_state is not None)
    log_path = room.game_state.game_logger.log_file
    jsonl_path = room.game_state.game_logger._jsonl_path
    assert log_path is not None and log_path.exists()

    mid_battle_log = log_path.read_text(encoding="utf-8")
    assert "player1 deck" not in mid_battle_log
    assert "rng_seed" not in mid_battle_log

    room.battle_dispatcher.pending_winner = "player1"
    wait_until(lambda: room.closed)

    final_log = log_path.read_text(encoding="utf-8")
    assert f"player1 deck {'-'.join(TEST_DECK)}" in final_log
    assert f"player2 deck {'-'.join(TEST_DECK)}" in final_log
    assert "rng_seed" in final_log

    creator.disconnect()
    joiner.disconnect()
    time.sleep(0.3)
    for path in (log_path, jsonl_path):
        if path is not None and path.exists():
            path.unlink()


def test_spectator_can_join_mid_battle(room_server):
    _server, make_client = room_server
    creator = make_client()
    creator.connect()
    joiner = make_client(room=creator.room)
    joiner.connect()

    _send_lobby(creator, "set_setting", setting="file_auto_delete", bool_value=True)
    _send_lobby(creator, "start_match")
    wait_until(lambda: creator.pending_scene == "draft")
    creator.consume_pending_scene()
    joiner.consume_pending_scene()

    _draft_full_deck(creator, joiner)
    wait_until(lambda: creator.pending_scene == "battling")

    spectator = make_client(room=creator.room)
    role, state = spectator.connect()
    assert role == "spectator"
    assert spectator.scene == "battling"
    assert state["player1"]["deck"] == ["?"] * 12
    assert state["player2"]["deck"] == ["?"] * 12
