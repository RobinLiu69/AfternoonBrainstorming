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

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from core.lobby_dispatcher import LobbyDispatcher
from core.lobby_state import LobbyState
from screens.lobby.ban_draft import ban_actor, ban_controls, owns_ban_draft
from screens.lobby.lobby_action import LobbyAction


def _watching() -> LobbyState:
    state = LobbyState(host_playing=False)
    state.host_seat_connected = True
    state.peer_connected = True
    state.in_ban_draft = True
    return state


def _playing() -> LobbyState:
    state = LobbyState()
    state.peer_connected = True
    state.in_ban_draft = True
    return state


class TestWhoBansWhenTheHostWatches:
    def test_the_seated_clients_each_get_their_own_side(self) -> None:
        state = _watching()

        assert ban_controls(state, "lan_server", state.host_seat) == ("host", state.host_seat)
        assert ban_controls(state, "lan_server", state.peer_seat()) == ("peer", state.peer_seat())

    def test_the_watching_host_cannot_ban(self) -> None:
        state = _watching()

        assert ban_controls(state, "lan_server", "host") == (None, "")

    def test_a_playing_host_still_bans_as_the_host(self) -> None:
        state = _playing()

        assert ban_controls(state, "lan_server", "host") == ("host", state.host_seat)

    def test_a_playing_host_seat_name_is_not_a_second_banner(self) -> None:
        state = _playing()

        assert ban_controls(state, "lan_server", state.host_seat) == ("host", state.host_seat)

    def test_local_play_drives_both_sides(self) -> None:
        assert ban_controls(_playing(), "local", "host") == ("both", "")


class TestWhichSlotABanIsClaimedUnder:
    def test_a_watched_host_side_is_claimed_by_its_seat(self) -> None:
        state = _watching()

        assert ban_actor(state, "host") == state.host_seat
        assert ban_actor(state, "peer") == state.peer_seat()

    def test_a_playing_host_claims_the_host_slot(self) -> None:
        state = _playing()

        assert ban_actor(state, "host") == "host"
        assert ban_actor(state, "peer") == state.peer_seat()


class TestWhoControlsTheBanDraft:
    def test_the_watching_host_still_owns_the_room(self) -> None:
        state = _watching()
        controls, _seat = ban_controls(state, "lan_server", "host")

        assert owns_ban_draft("host", controls) is True

    def test_a_seated_client_never_owns_the_room(self) -> None:
        state = _watching()
        for seat in (state.host_seat, state.peer_seat()):
            controls, _seat = ban_controls(state, "lan_server", seat)
            assert owns_ban_draft(seat, controls) is False

    def test_a_spectator_owns_nothing(self) -> None:
        state = _watching()
        controls, _seat = ban_controls(state, "lan_server", "spectator")

        assert owns_ban_draft("spectator", controls) is False


class TestTheDispatcherAgrees:
    def test_both_seated_clients_land_on_different_sides(self) -> None:
        state = _watching()
        dispatcher = LobbyDispatcher(state, mode="lan_server")

        for banner, card in (("host", "TANKG"), ("peer", "APG")):
            action = LobbyAction(ban_actor(state, banner), "ban_card", str_value=card)
            assert dispatcher.dispatch(action).success is True

        assert state.bans == {"TANKG": "host", "APG": "peer"}

    def test_a_watching_host_cannot_ban_by_hand(self) -> None:
        state = _watching()
        dispatcher = LobbyDispatcher(state, mode="lan_server")

        result = dispatcher.dispatch(LobbyAction("host", "ban_card", str_value="TANKG"))

        assert result.success is False
        assert state.bans == {}

    def test_a_watching_host_cannot_overwrite_the_seat_holders_name(self) -> None:
        state = _watching()
        dispatcher = LobbyDispatcher(state, mode="lan_server")
        dispatcher.dispatch(LobbyAction(state.host_seat, "set_name", str_value="Alice"))

        dispatcher.dispatch(LobbyAction("host", "set_name", str_value="Ghost"))

        assert state.display_name("host") == "Alice"

    def test_a_playing_host_still_names_and_bans_as_host(self) -> None:
        state = _playing()
        dispatcher = LobbyDispatcher(state, mode="lan_server")

        dispatcher.dispatch(LobbyAction("host", "set_name", str_value="Robin"))
        assert dispatcher.dispatch(
            LobbyAction("host", "ban_card", str_value="TANKG")).success is True

        assert state.display_name("host") == "Robin"
        assert state.bans == {"TANKG": "host"}
