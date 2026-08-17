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

import time

from core.lobby_state import LobbyState
from core.match_settings import MatchSettings, TIME_CONTROL_OPTIONS, DEFAULT_TIME_CONTROL
from core.lobby_dispatcher import LobbyDispatcher
from core.battling_dispatcher import BattlingDispatcher
from core.game_action import GameAction
from screens.lobby.lobby_action import set_setting

from tests.helpers import make_game_state


def test_time_control_presets():
    settings = MatchSettings()
    assert settings.time_control == DEFAULT_TIME_CONTROL
    assert settings.countdown_seconds() == 600
    assert settings.increment_seconds() == 0

    settings.time_control = "5+5"
    assert settings.countdown_seconds() == 300
    assert settings.increment_seconds() == 5

    settings.time_control = "15+10"
    assert settings.countdown_seconds() == 900
    assert settings.increment_seconds() == 10

    settings.time_control = "nonsense"
    assert settings.countdown_seconds() == 600
    assert settings.increment_seconds() == 0


def test_time_control_survives_wire_roundtrip():
    state = LobbyState()
    state.settings.time_control = "10+10"
    received = LobbyState()
    received.apply_dict(state.to_dict_for("player2"))
    assert received.settings.time_control == "10+10"
    assert received.settings.countdown_seconds() == 600
    assert received.settings.increment_seconds() == 10


def test_set_time_control_action():
    state = LobbyState()
    dispatcher = LobbyDispatcher(state, mode="lan_server")

    result = dispatcher.dispatch(set_setting("time_control", "5+5"))
    assert result.success is True
    assert state.settings.time_control == "5+5"

    result = dispatcher.dispatch(set_setting("time_control", "3min"))
    assert result.success is False
    assert state.settings.time_control == "5+5"

    result = dispatcher.dispatch(set_setting("time_control", "20min", player="player2"))
    assert result.success is False
    assert state.settings.time_control == "5+5"


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
        draft_state.settings.timer_mode = "countdown"
        dispatcher = DraftDispatcher(draft_state, mode=mode)

        action = DraftAction.from_json('{"player": "player1", "action_type": "toggle_timer"}')
        result = dispatcher.dispatch(action, draft_state)
        assert result.success is False
        assert draft_state.settings.timer_mode == "countdown"

        action = DraftAction.from_json('{"player": "player1", "action_type": "toggle_file_save"}')
        result = dispatcher.dispatch(action, draft_state)
        assert result.success is False
        assert draft_state.settings.file_auto_delete is False


def test_countdown_time_synced_over_wire():
    game_state = make_game_state()
    game_state.countdown_time = 300
    data = game_state.to_dict()
    assert data["countdown_time"] == 300

    for preset in ("5min", "10min", "15min", "20min", "5+5", "10+10", "15+10"):
        assert preset in TIME_CONTROL_OPTIONS


def test_flag_in_increment_mode_grants_one_increment_and_ends_turn():
    for increment in (5, 10):
        game_state, dispatcher = _make_countdown_game(increment=increment)
        game_state.player1.elapsed_time = 0
        game_state.player1.time_out = True

        winner = dispatcher.resolve_flag(game_state)

        assert winner is None
        assert game_state.player1.elapsed_time == increment
        assert game_state.player1.time_out is False
        assert game_state.turn_number == 1


def test_flag_in_pure_countdown_is_a_loss():
    game_state, dispatcher = _make_countdown_game(increment=0)
    game_state.player1.elapsed_time = 0
    game_state.player1.time_out = True

    winner = dispatcher.resolve_flag(game_state)

    assert winner == "player2"
    assert game_state.turn_number == 0


def test_resolve_flag_noop_when_nobody_flagged():
    game_state, dispatcher = _make_countdown_game(increment=5)
    assert dispatcher.resolve_flag(game_state) is None
    assert game_state.turn_number == 0


def test_timeout_flag_is_self_correcting():
    import time
    game_state = make_game_state()

    game_state.player1.elapsed_time = 0
    game_state.player1.start_time = time.time()
    game_state.player1._update_timer_logic("countdown")
    assert game_state.player1.time_out is True

    game_state.player1.elapsed_time = 10
    game_state.player1.start_time = time.time()
    game_state.player1._update_timer_logic("countdown")
    assert game_state.player1.time_out is False


def _tick_a_second(player) -> None:
    import time as _time
    player.start_time = _time.time() - 2
    player._update_timer_logic("countdown")


def test_countdown_tracks_how_long_each_side_has_spent():
    gs = make_game_state()
    gs.timer_mode = "countdown"
    gs.countdown_time = 300
    player = gs.player1
    player.timer_start(gs)

    assert player.time_used_display == "00:00"

    for _ in range(7):
        _tick_a_second(player)

    assert player.elapsed_time == 293
    assert player.time_used == 7
    assert player.time_used_display == "00:07"


def test_a_turn_increment_refunds_the_clock_without_refunding_the_spend():
    gs = make_game_state()
    gs.timer_mode = "countdown"
    gs.countdown_time = 300
    gs.turn_increment_seconds = 5
    player = gs.player1
    player.timer_start(gs)
    for _ in range(7):
        _tick_a_second(player)

    player.elapsed_time += gs.turn_increment_seconds
    player._refresh_time_display()

    assert player.time_display == "04:58"
    assert player.time_used_display == "00:07"


def test_the_timer_mode_never_counts_a_spend():
    gs = make_game_state()
    gs.timer_mode = "timer"
    player = gs.player1
    player.timer_start(gs)
    player.start_time = time.time() - 2
    player._update_timer_logic("timer")

    assert player.elapsed_time == 1
    assert player.time_used == 0


def test_the_spend_survives_the_wire_and_old_payloads_do_not_crash():
    gs = make_game_state()
    gs.timer_mode = "countdown"
    gs.countdown_time = 300
    gs.player1.timer_start(gs)
    for _ in range(3):
        _tick_a_second(gs.player1)

    payload = gs.player1.to_dict()
    gs.player2.apply_dict(payload, {}, {}, None)
    assert gs.player2.time_used_display == "00:03"

    legacy = {key: value for key, value in payload.items() if key != "time_used"}
    gs.player2.apply_dict(legacy, {}, {}, None)
    assert gs.player2.time_used_display == "00:00"
