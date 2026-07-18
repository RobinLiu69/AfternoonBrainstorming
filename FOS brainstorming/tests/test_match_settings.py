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

from core.match_settings import MATCH_SETTING_NAMES, MatchSettings, RULESET_OPTIONS
from core.lobby_state import LobbyState, SETTING_OPTIONS
from core.lobby_dispatcher import LobbyDispatcher
from core.draft_state import DraftState
from screens.lobby.lobby_action import LobbyAction, set_setting

from tests.helpers import make_game_state


def test_every_match_setting_is_registered():
    assert MATCH_SETTING_NAMES <= set(SETTING_OPTIONS)


def test_set_setting_routes_to_match_settings_and_lobby_fields():
    state = LobbyState()
    dispatcher = LobbyDispatcher(state, mode="lan_server")

    result = dispatcher.dispatch(set_setting("ruleset", "tournament"))
    assert result.success is True
    assert state.settings.ruleset == "tournament"

    result = dispatcher.dispatch(set_setting("god_view", True))
    assert result.success is True
    assert state.god_view is True

    result = dispatcher.dispatch(set_setting("reconnect_timeout", 120.0))
    assert result.success is True
    assert state.reconnect_timeout == 120.0


def test_set_setting_rejects_bad_input():
    state = LobbyState()
    dispatcher = LobbyDispatcher(state, mode="lan_server")

    assert dispatcher.dispatch(set_setting("ruleset", "ranked")).success is False
    assert state.settings.ruleset == "free play"

    assert dispatcher.dispatch(set_setting("no_such_setting", "x")).success is False

    assert dispatcher.dispatch(set_setting("ruleset", "tournament", player="player2")).success is False
    assert state.settings.ruleset == "free play"

    empty = LobbyAction("host", "set_setting", setting="ruleset")
    assert dispatcher.dispatch(empty).success is False


def test_set_setting_canonicalizes_value_type():
    state = LobbyState()
    dispatcher = LobbyDispatcher(state, mode="lan_server")

    remote = LobbyAction("host", "set_setting", setting="file_auto_delete", float_value=1.0)
    assert dispatcher.dispatch(remote).success is True
    assert state.settings.file_auto_delete is True


def test_settings_survive_lobby_wire_roundtrip():
    state = LobbyState()
    state.settings.ruleset = "tournament"
    state.settings.timer_mode = "countdown"
    state.settings.time_control = "5+5"
    state.settings.file_auto_delete = True

    received = LobbyState()
    received.apply_dict(state.to_dict_for("player2"))
    assert received.settings == state.settings


def test_draft_state_syncs_settings_to_every_viewer():
    draft_state = DraftState()
    draft_state.settings = MatchSettings(timer_mode="countdown", time_control="5+5",
                                         ruleset="tournament", file_auto_delete=True)

    received = DraftState()
    received.apply_dict(draft_state.to_dict_for("player2"))
    assert received.settings == draft_state.settings

    for name in MATCH_SETTING_NAMES:
        assert name in draft_state.to_dict_for("spectator")


def test_apply_to_configures_game_state():
    settings = MatchSettings(timer_mode="countdown", time_control="5+5",
                             ruleset="tournament", file_auto_delete=True)
    game_state = make_game_state()
    settings.apply_to(game_state)

    assert game_state.timer_mode == "countdown"
    assert game_state.countdown_time == 300
    assert game_state.turn_increment_seconds == 5
    assert game_state.file_auto_delete is True


def test_copy_is_independent():
    original = MatchSettings()
    copied = original.copy()
    copied.ruleset = RULESET_OPTIONS[1]
    assert original.ruleset == RULESET_OPTIONS[0]
