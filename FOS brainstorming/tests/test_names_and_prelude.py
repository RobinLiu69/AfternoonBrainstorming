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

from core.lobby_state import LobbyState, MAX_NAME_LENGTH
from core.lobby_dispatcher import LobbyDispatcher
from core.draft_state import DraftState
from core.match_prelude import (log_match_prelude, resolve_ban_draft, log_ban_draft,
                                judge_bans_of, log_judge_bans)
from screens.lobby.lobby_action import LobbyAction
from utils.logger import GameLogger


def _dispatcher():
    state = LobbyState()
    return state, LobbyDispatcher(state, mode="lan_server")


def _set_name(dispatcher, player, name):
    return dispatcher.dispatch(LobbyAction(player, "set_name", str_value=name))


def test_set_name_maps_host_and_peer():
    state, dispatcher = _dispatcher()
    assert _set_name(dispatcher, "host", "Robin").success is True
    assert _set_name(dispatcher, "player2", "Angus").success is True
    assert state.player_names == {"host": "Robin", "peer": "Angus"}
    assert state.display_name("host") == "Robin"

    assert _set_name(dispatcher, "spectator", "Nobody").success is True
    assert "Nobody" not in state.player_names.values()

    assert _set_name(dispatcher, "player1", "WrongSeat").success is True
    assert "WrongSeat" not in state.player_names.values()


def test_set_name_validation():
    state, dispatcher = _dispatcher()
    assert _set_name(dispatcher, "host", "bad name").success is False
    assert _set_name(dispatcher, "host", "中文").success is False
    assert _set_name(dispatcher, "host", "a" * (MAX_NAME_LENGTH + 1)).success is False
    assert _set_name(dispatcher, "host", "a" * MAX_NAME_LENGTH).success is True
    assert _set_name(dispatcher, "host", "Rob_1n").success is True

    assert _set_name(dispatcher, "host", "").success is True
    assert state.player_names == {}


def test_names_survive_wire_roundtrip():
    state = LobbyState()
    state.player_names = {"host": "Robin", "peer": "Angus"}
    received = LobbyState()
    received.apply_dict(state.to_dict_for("spectator"))
    assert received.player_names == {"host": "Robin", "peer": "Angus"}


def test_seat_names_maps_identities_to_seats():
    state = LobbyState()
    state.host_seat = "player2"
    state.player_names = {"host": "Robin", "peer": "Angus"}
    assert state.seat_names() == {"player2": "Robin", "player1": "Angus"}


def test_draft_names_and_editor_label_survive_wire():
    draft_state = DraftState()
    draft_state.player_names = {"player1": "Robin", "player2": "Angus"}
    draft_state.phase = "p2_pick12"
    assert draft_state.current_editor_label() == "Angus"

    received = DraftState()
    received.apply_dict(draft_state.to_dict_for("player1"))
    assert received.player_names == {"player1": "Robin", "player2": "Angus"}
    assert received.current_editor_label() == "Angus"


def test_draft_editor_label_falls_back_without_names():
    draft_state = DraftState()
    draft_state.phase = "p1_first6"
    assert draft_state.current_editor_label() == "P1"


def test_prelude_writes_names_and_bans_to_jsonl(tmp_path):
    # competitions transmit only the jsonl, so the non-secret header (names + bans)
    # must be present; decks/seed are secret and get appended at game over instead.
    log_file = tmp_path / "match.log"
    logger = GameLogger(log_file=log_file, enable_console=False)

    lobby_state = LobbyState()
    lobby_state.player_names = {"host": "Robin", "peer": "Angus"}
    lobby_state.bans = {"TANKG": "host"}

    log_match_prelude(logger, lobby_state)
    logger.close()

    jsonl_text = (tmp_path / "match.jsonl").read_text(encoding="utf-8")

    assert "players player1=Robin player2=Angus" in jsonl_text
    assert "ban TANKG by Robin" in jsonl_text
    assert "draft player1 add" not in jsonl_text  # no per-pick churn
    assert "player1 deck" not in jsonl_text        # secret: written at game over


def test_log_match_prelude_writes_names_and_bans():
    lobby_state = LobbyState()
    lobby_state.player_names = {"host": "Robin", "peer": "Angus"}
    lobby_state.bans = {"TANKG": "peer", "HEAL": "host"}

    logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
    entries = []
    logger.subscribe(entries.append)
    log_match_prelude(logger, lobby_state)

    messages = [e.message for e in entries]
    assert "players player1=Robin player2=Angus" in messages
    assert "ban TANKG by Angus" in messages
    assert "ban HEAL by Robin" in messages
    assert all("draft " not in m for m in messages)
    assert all("deck" not in m for m in messages)

    bans = [e for e in entries if e.data.get("ban_card")]
    assert {(e.data["ban_card"], e.data["banned_by"]) for e in bans} == {
        ("TANKG", "peer"), ("HEAL", "host"),
    }


def test_resolve_ban_draft_uses_names_then_seat_fallback():
    state = LobbyState()
    state.host_seat = "player2"
    state.player_names = {"host": "Robin"}
    state.bans = {"TANKG": "host", "HEAL": "peer"}

    assert resolve_ban_draft(state) == {"TANKG": "Robin", "HEAL": "player1"}
    assert resolve_ban_draft(None) == {}


def test_ban_draft_carries_on_game_state_and_logs_at_game_over(tmp_path):
    from tests.helpers import make_game_state

    game_state = make_game_state()
    assert game_state.ban_draft == {}

    state = LobbyState()
    state.player_names = {"host": "Robin"}
    state.bans = {"TANKG": "host", "HFW": "host", "SPB": "peer"}
    game_state.ban_draft = resolve_ban_draft(state)

    logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
    entries = []
    logger.subscribe(entries.append)
    log_ban_draft(logger, game_state.ban_draft)

    assert len(entries) == 2
    messages = [e.message for e in entries]
    assert "ban TANKG-HFW by Robin" in messages
    assert "ban SPB by player2" in messages
    assert {(tuple(e.data["ban_cards"]), e.data["banned_by_name"]) for e in entries} == {
        (("TANKG", "HFW"), "Robin"), (("SPB",), "player2"),
    }


def test_judge_bans_exclude_player_picks_and_log_one_line():
    ban_deck = ["ADCR", "APR", "TANKG", "SPB"]
    ban_draft = {"TANKG": "Robin", "SPB": "player2"}
    judge = judge_bans_of(ban_deck, ban_draft)
    assert judge == ["ADCR", "APR"]

    logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
    entries = []
    logger.subscribe(entries.append)
    log_judge_bans(logger, judge)
    log_judge_bans(logger, [])

    assert len(entries) == 1
    assert entries[0].message == "ban ADCR-APR by judge"
    assert entries[0].data["banned_by_name"] == "judge"
    assert entries[0].data["ban_cards"] == ["ADCR", "APR"]
