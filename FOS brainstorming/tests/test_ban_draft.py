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

from shared.setting import CARD_SETTING, JOB_DICTIONARY, JOB_ORDER
from core.lobby_state import LobbyState, MAX_BANS_PER_PLAYER, is_bannable_card
from core.lobby_dispatcher import LobbyDispatcher
from core.draft_state import DraftState, TOURNAMENT_BANS
from core.draft_dispatcher import DraftDispatcher
from screens.lobby.lobby_action import LobbyAction
from screens.draft.draft_action import DraftAction


def _dispatcher(state=None):
    state = state if state is not None else LobbyState()
    return state, LobbyDispatcher(state, mode="lan_server")


def _ban(dispatcher, player, card):
    return dispatcher.dispatch(LobbyAction(player, "ban_card", str_value=card))


def _tournament_allowed_card() -> str:
    for page in JOB_DICTIONARY["colors_array"]:
        tag, color_name = list(page.items())[-1]
        for job in JOB_ORDER:
            if job in CARD_SETTING.get(color_name, {}):
                return job + tag
    raise AssertionError("no tournament-allowed card found")


def test_is_bannable_card():
    assert is_bannable_card("TANKG")
    assert is_bannable_card("HFDKG")
    assert is_bannable_card("HEAL")
    assert is_bannable_card("CUBES")
    assert is_bannable_card("MOVE")
    assert not is_bannable_card("MOVEO")
    assert not is_bannable_card("CUBE")
    assert not is_bannable_card("LUCKYBLOCK")
    assert not is_bannable_card("XXXG")
    assert not is_bannable_card("")


def test_only_host_toggles_ban_draft():
    state, dispatcher = _dispatcher()
    assert dispatcher.dispatch(
        LobbyAction("player2", "set_ban_draft", bool_value=True)).success is False
    assert state.in_ban_draft is False

    assert dispatcher.dispatch(
        LobbyAction("host", "set_ban_draft", bool_value=True)).success is True
    assert state.in_ban_draft is True

    assert dispatcher.dispatch(
        LobbyAction("host", "set_ban_draft", bool_value=False)).success is True
    assert state.in_ban_draft is False


def test_ban_requires_ban_draft_and_player_identity():
    state, dispatcher = _dispatcher()
    assert _ban(dispatcher, "player2", "TANKG").success is False

    state.in_ban_draft = True
    assert _ban(dispatcher, "spectator", "TANKG").success is False
    assert _ban(dispatcher, "player1", "TANKG").success is False
    assert _ban(dispatcher, "player2", "MOVEO").success is False
    assert _ban(dispatcher, "player2", "TANKG").success is True
    assert _ban(dispatcher, "host", "HEAL").success is True
    assert state.bans == {"TANKG": "peer", "HEAL": "host"}


def test_bans_follow_person_across_seat_swap():
    state, dispatcher = _dispatcher()
    state.in_ban_draft = True
    assert _ban(dispatcher, "host", "TANKG").success is True
    assert _ban(dispatcher, "player2", "APG").success is True
    assert state.bans == {"TANKG": "host", "APG": "peer"}

    state.in_ban_draft = False
    assert dispatcher.dispatch(LobbyAction("host", "swap_seats")).success is True
    assert state.host_seat == "player2"
    state.in_ban_draft = True

    assert state.bans == {"TANKG": "host", "APG": "peer"}
    assert dispatcher.dispatch(
        LobbyAction("host", "unban_card", str_value="TANKG")).success is True
    assert dispatcher.dispatch(
        LobbyAction("player1", "unban_card", str_value="APG")).success is True
    assert state.bans == {}


def test_duplicate_ban_rejected():
    state, dispatcher = _dispatcher()
    state.in_ban_draft = True
    assert _ban(dispatcher, "player2", "TANKG").success is True
    assert _ban(dispatcher, "player2", "TANKG").success is False
    assert _ban(dispatcher, "host", "TANKG").success is False


def test_ban_limit_per_person():
    state, dispatcher = _dispatcher()
    state.in_ban_draft = True
    cards = ["TANKG", "APG", "ADCG", "HFG", "LFG"]
    for card in cards[:MAX_BANS_PER_PLAYER]:
        assert _ban(dispatcher, "player2", card).success is True
    assert _ban(dispatcher, "player2", cards[MAX_BANS_PER_PLAYER]).success is False
    assert _ban(dispatcher, "host", cards[MAX_BANS_PER_PLAYER]).success is True
    assert state.ban_count("peer") == MAX_BANS_PER_PLAYER
    assert state.ban_count("host") == 1


def test_unban_only_own_bans():
    state, dispatcher = _dispatcher()
    state.in_ban_draft = True
    _ban(dispatcher, "player2", "TANKG")

    assert dispatcher.dispatch(
        LobbyAction("host", "unban_card", str_value="TANKG")).success is False
    assert "TANKG" in state.bans

    assert dispatcher.dispatch(
        LobbyAction("player2", "unban_card", str_value="TANKG")).success is True
    assert state.bans == {}


def test_local_mode_can_ban_for_both_identities():
    state = LobbyState()
    state.in_ban_draft = True
    dispatcher = LobbyDispatcher(state, mode="local")

    assert dispatcher.dispatch(
        LobbyAction("host", "ban_card", str_value="TANKG")).success is True
    assert dispatcher.dispatch(
        LobbyAction("player2", "ban_card", str_value="APG")).success is True
    assert state.bans == {"TANKG": "host", "APG": "peer"}
    assert state.ban_count("host") == 1
    assert state.ban_count("peer") == 1

    assert dispatcher.dispatch(
        LobbyAction("player2", "unban_card", str_value="TANKG")).success is False
    assert dispatcher.dispatch(
        LobbyAction("host", "unban_card", str_value="TANKG")).success is True
    assert state.bans == {"APG": "peer"}


def test_tournament_locked_cards_not_bannable():
    state, dispatcher = _dispatcher()
    state.in_ban_draft = True
    state.settings.ruleset = "tournament"

    locked_card = next(iter(TOURNAMENT_BANS))
    assert _ban(dispatcher, "player2", locked_card).success is False

    allowed_card = _tournament_allowed_card()
    assert allowed_card not in TOURNAMENT_BANS
    assert _ban(dispatcher, "player2", allowed_card).success is True
    assert _ban(dispatcher, "host", "HEAL").success is True


def test_bans_survive_wire_roundtrip():
    state = LobbyState()
    state.in_ban_draft = True
    state.bans = {"TANKG": "host", "APG": "peer"}

    received = LobbyState()
    received.apply_dict(state.to_dict_for("spectator"))
    assert received.in_ban_draft is True
    assert received.bans == {"TANKG": "host", "APG": "peer"}
    assert list(received.bans) == ["TANKG", "APG"]


def test_lobby_bans_block_draft_picks():
    lobby_state = LobbyState()
    lobby_state.in_ban_draft = True
    _state, dispatcher = _dispatcher(lobby_state)
    _ban(dispatcher, "player2", "TANKG")
    _ban(dispatcher, "host", "HEAL")

    draft_state = DraftState()
    draft_state.init_ban_deck()
    draft_state.add_ban([c for c in lobby_state.bans if not draft_state.is_banned(c)])
    draft_dispatcher = DraftDispatcher(draft_state, mode="local")

    result = draft_dispatcher.dispatch(
        DraftAction("player1", "add_card", "TANKG"), draft_state)
    assert result.success is False
    assert draft_state.is_banned("TANKG")

    result = draft_dispatcher.dispatch(
        DraftAction("player1", "add_card", "HEAL"), draft_state)
    assert result.success is False

    result = draft_dispatcher.dispatch(
        DraftAction("player1", "add_card", "APG"), draft_state)
    assert result.success is True
