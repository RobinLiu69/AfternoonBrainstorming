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

from core.lobby_state import LobbyState
from core.lobby_dispatcher import LobbyDispatcher
from core.draft_state import DraftState
from core.draft_dispatcher import DraftDispatcher
from core.match_prelude import log_match_prelude
from screens.lobby.lobby_action import LobbyAction
from screens.draft.draft_action import DraftAction
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
    assert _set_name(dispatcher, "host", "a" * 13).success is False
    assert _set_name(dispatcher, "host", "Rob_1n").success is True

    assert _set_name(dispatcher, "host", "").success is True
    assert state.player_names == {}


def test_names_survive_wire_roundtrip():
    state = LobbyState()
    state.player_names = {"host": "Robin", "peer": "Angus"}
    received = LobbyState()
    received.apply_dict(state.to_dict_for("spectator"))
    assert received.player_names == {"host": "Robin", "peer": "Angus"}


def test_draft_pick_history_records_mutations():
    draft_state = DraftState()
    draft_state.init_ban_deck()
    dispatcher = DraftDispatcher(draft_state, mode="local")

    dispatcher.dispatch(DraftAction("player1", "add_card", "TANKG"), draft_state)
    dispatcher.dispatch(DraftAction("player1", "add_card", "APG"), draft_state)
    dispatcher.dispatch(DraftAction("player1", "remove_card", "TANKG"), draft_state)
    dispatcher.dispatch(DraftAction("player1", "remove_last_card"), draft_state)
    dispatcher.dispatch(DraftAction("player1", "add_card", "HFG"), draft_state)

    assert draft_state.pick_history == [
        ("player1", "add", "TANKG"),
        ("player1", "add", "APG"),
        ("player1", "remove", "TANKG"),
        ("player1", "remove", "APG"),
        ("player1", "add", "HFG"),
    ]


def test_pick_history_stays_out_of_wire():
    draft_state = DraftState()
    draft_state.pick_history.append(("player1", "add", "TANKG"))
    assert "pick_history" not in draft_state.to_dict_for("player2")


def test_log_match_prelude_writes_names_bans_and_picks():
    lobby_state = LobbyState()
    lobby_state.player_names = {"host": "Robin", "peer": "Angus"}
    lobby_state.bans = {"TANKG": "peer", "HEAL": "host"}

    draft_state = DraftState()
    draft_state.pick_history = [("player1", "add", "APG")]

    logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
    entries = []
    logger.subscribe(entries.append)
    log_match_prelude(logger, draft_state, lobby_state)

    messages = [e.message for e in entries]
    assert "players player1=Robin player2=Angus" in messages
    assert "ban TANKG by Angus" in messages
    assert "ban HEAL by Robin" in messages
    assert "draft player1 add APG" in messages

    bans = [e for e in entries if e.data.get("ban_card")]
    assert {(e.data["ban_card"], e.data["banned_by"]) for e in bans} == {
        ("TANKG", "peer"), ("HEAL", "host"),
    }
