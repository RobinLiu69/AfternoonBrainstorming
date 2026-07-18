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

from core.lobby_state import LobbyState, TIME_CONTROL_OPTIONS, DEFAULT_TIME_CONTROL
from core.lobby_dispatcher import LobbyDispatcher
from core.battling_dispatcher import BattlingDispatcher
from core.game_action import GameAction
from screens.lobby.lobby_action import LobbyAction

from tests.helpers import make_game_state


def test_time_control_presets():
    state = LobbyState()
    assert state.time_control == DEFAULT_TIME_CONTROL
    assert state.countdown_seconds() == 600
    assert state.increment_seconds() == 0

    state.time_control = "5+5"
    assert state.countdown_seconds() == 300
    assert state.increment_seconds() == 5

    state.time_control = "15+10"
    assert state.countdown_seconds() == 900
    assert state.increment_seconds() == 10

    state.time_control = "nonsense"
    assert state.countdown_seconds() == 600
    assert state.increment_seconds() == 0


def test_time_control_survives_wire_roundtrip():
    state = LobbyState()
    state.time_control = "10+10"
    received = LobbyState()
    received.apply_dict(state.to_dict_for("player2"))
    assert received.time_control == "10+10"
    assert received.countdown_seconds() == 600
    assert received.increment_seconds() == 10


def test_set_time_control_action():
    state = LobbyState()
    dispatcher = LobbyDispatcher(state, mode="lan_server")

    result = dispatcher.dispatch(LobbyAction("host", "set_time_control", str_value="5+5"))
    assert result.success is True
    assert state.time_control == "5+5"

    result = dispatcher.dispatch(LobbyAction("host", "set_time_control", str_value="3min"))
    assert result.success is False
    assert state.time_control == "5+5"

    result = dispatcher.dispatch(LobbyAction("player2", "set_time_control", str_value="20min"))
    assert result.success is False
    assert state.time_control == "5+5"


def _make_countdown_game(increment: int):
    game_state = make_game_state()
    game_state.timer_mode = "countdown"
    game_state.turn_increment_seconds = increment
    game_state.player1.elapsed_time = 300
    game_state.player2.elapsed_time = 300
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")
    return game_state, dispatcher


def test_end_turn_adds_increment_to_ending_player():
    game_state, dispatcher = _make_countdown_game(increment=5)

    result = dispatcher.dispatch(GameAction("player1", "end_turn"), game_state)
    assert result.success is True
    assert game_state.player1.elapsed_time == 305
    assert game_state.player1.time_display == "05:05"
    assert game_state.player2.elapsed_time == 300

    result = dispatcher.dispatch(GameAction("player2", "end_turn"), game_state)
    assert result.success is True
    assert game_state.player2.elapsed_time == 305
    assert game_state.player1.elapsed_time == 305


def test_no_increment_without_time_bonus():
    game_state, dispatcher = _make_countdown_game(increment=0)
    dispatcher.dispatch(GameAction("player1", "end_turn"), game_state)
    assert game_state.player1.elapsed_time == 300


def test_no_increment_in_timer_mode():
    game_state, dispatcher = _make_countdown_game(increment=10)
    game_state.timer_mode = "timer"
    dispatcher.dispatch(GameAction("player1", "end_turn"), game_state)
    assert game_state.player1.elapsed_time == 300


def test_time_display_synced_over_wire():
    game_state = make_game_state()
    game_state.player1.elapsed_time = 425
    game_state.player1._refresh_time_display()
    data = game_state.player1.to_dict()
    assert data["time_display"] == "07:05"

    receiver = make_game_state()
    receiver.player1.apply_dict(data, {}, {}, None)
    assert receiver.player1.time_display == "07:05"
    assert receiver.player1.elapsed_time == 425


def test_draft_cannot_override_lobby_timer():
    from core.draft_state import DraftState
    from core.draft_dispatcher import DraftDispatcher
    from screens.draft.draft_action import DraftAction

    for mode in ("lan_server", "local"):
        draft_state = DraftState()
        draft_state.timer_mode = "countdown"
        dispatcher = DraftDispatcher(draft_state, mode=mode)

        action = DraftAction.from_json('{"player": "player1", "action_type": "toggle_timer"}')
        result = dispatcher.dispatch(action, draft_state)
        assert result.success is False
        assert draft_state.timer_mode == "countdown"

        action = DraftAction.from_json('{"player": "player1", "action_type": "toggle_file_save"}')
        result = dispatcher.dispatch(action, draft_state)
        assert result.success is False
        assert draft_state.file_auto_delete is False


def test_countdown_time_synced_over_wire():
    game_state = make_game_state()
    game_state.countdown_time = 300
    data = game_state.to_dict()
    assert data["countdown_time"] == 300

    labels = list(TIME_CONTROL_OPTIONS)
    assert labels == ["5min", "10min", "15min", "20min", "5+5", "10+10", "15+10"]
