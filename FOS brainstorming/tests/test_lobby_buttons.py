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

import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from core.game_screen import GameScreen
from core.lobby_state import LobbyState
from screens.lobby import lobby


class _Recorder:
    mode = "lan_server"

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def dispatch(self, action):
        self.sent.append((action.player, action.action_type))
        return None


@pytest.fixture(scope="module")
def game_screen():
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


def _buttons(game_screen, state: LobbyState, role: str):
    row_offsets, _header = lobby._layout("lan_server")
    buttons = lobby._make_buttons(game_screen, row_offsets)
    lobby._refresh_button_labels(buttons, state, role, "lan_server")
    return buttons


def _click(buttons, name, state, role, dispatcher):
    button = buttons[name]
    lobby._click_dispatch(buttons, button.x + button.width / 2,
                          button.y + button.height / 2, state, role, dispatcher)


def _overlaps(a, b) -> bool:
    return (a.x < b.x + b.width and b.x < a.x + a.width
            and a.y < b.y + b.height and b.y < a.y + a.height)


class TestTheHostHasAReachableWatchButton:
    def test_the_host_sees_a_watch_label(self, game_screen) -> None:
        buttons = _buttons(game_screen, LobbyState(), "host")

        assert buttons["host_watch"].text
        assert not buttons["host_watch"].text.startswith("(")

    def test_the_watch_button_does_not_sit_on_top_of_start_match(self, game_screen) -> None:
        buttons = _buttons(game_screen, LobbyState(), "host")

        assert not _overlaps(buttons["host_watch"], buttons["start_match"])
        assert not _overlaps(buttons["host_watch"], buttons["switch_role"])

    def test_clicking_it_asks_to_step_out_of_the_seat(self, game_screen) -> None:
        state = LobbyState()
        buttons = _buttons(game_screen, state, "host")
        dispatcher = _Recorder()

        _click(buttons, "host_watch", state, "host", dispatcher)

        assert dispatcher.sent == [("host", "switch_to_spectator")]

    def test_clicking_it_again_asks_for_the_seat_back(self, game_screen) -> None:
        state = LobbyState(host_playing=False)
        buttons = _buttons(game_screen, state, "host")
        dispatcher = _Recorder()

        assert buttons["host_watch"].text == "take player1"
        _click(buttons, "host_watch", state, "host", dispatcher)

        assert dispatcher.sent == [("host", "switch_to_player")]

    def test_a_taken_seat_reads_as_disabled_and_does_nothing(self, game_screen) -> None:
        state = LobbyState(host_playing=False)
        state.host_seat_connected = True
        buttons = _buttons(game_screen, state, "host")
        dispatcher = _Recorder()

        assert buttons["host_watch"].text.startswith("(")
        _click(buttons, "host_watch", state, "host", dispatcher)

        assert dispatcher.sent == []

    def test_local_play_has_no_watch_button(self, game_screen) -> None:
        state = LobbyState()
        row_offsets, _header = lobby._layout("local")
        buttons = lobby._make_buttons(game_screen, row_offsets)
        lobby._refresh_button_labels(buttons, state, "host", "local")

        assert buttons["host_watch"].text == ""

    def test_a_client_still_gets_its_own_switch_button(self, game_screen) -> None:
        state = LobbyState()
        buttons = _buttons(game_screen, state, "player2")
        dispatcher = _Recorder()

        assert buttons["switch_role"].text == "switch to spectator"
        assert buttons["host_watch"].text == ""
        _click(buttons, "switch_role", state, "player2", dispatcher)

        assert dispatcher.sent == [("player2", "switch_to_spectator")]

    def test_a_spectator_can_claim_the_free_host_seat(self, game_screen) -> None:
        state = LobbyState(host_playing=False)
        state.peer_connected = True
        buttons = _buttons(game_screen, state, "spectator")
        dispatcher = _Recorder()

        assert buttons["switch_role"].text == "take player1 seat"
        _click(buttons, "switch_role", state, "spectator", dispatcher)

        assert dispatcher.sent == [("spectator", "switch_to_player")]
