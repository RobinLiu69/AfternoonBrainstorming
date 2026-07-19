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

from cards.factory import CardFactory
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.draft_state import DraftState
from core.game_screen import GameScreen
from core.lobby_state import LobbyState
from core.match_settings import MatchSettings
from rendering.draft_renderer import DraftRenderer
from screens.draft.exhibit_registry import ExhibitRegistry
from screens.lobby import lobby


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


def _tournament_settings() -> MatchSettings:
    return MatchSettings(timer_mode="countdown", time_control="5+5",
                         ruleset="tournament", file_auto_delete=True)


def test_draft_frame_renders_with_match_settings(game_screen):
    registry = ExhibitRegistry(game_screen)
    renderer = DraftRenderer(game_screen, registry)

    draft_state = DraftState()
    draft_state.settings = _tournament_settings()
    draft_state.init_ban_deck()
    draft_state.board_config = BoardConfig(4, 3)
    draft_state.board_dict = initialize_board(game_screen, draft_state.board_config)
    draft_state.local_player = "player1"
    draft_state.player1_deck = ["ADCW"]

    banned_spots = [(page, row)
                    for page in range(registry.page_count())
                    for row in range(4)
                    if any(draft_state.is_banned(card.job_and_color)
                           for card in registry.get_page(page, row))]
    assert banned_spots

    renderer.render_frame(0, 0, None, None, draft_state, hint_on=False, multiplayer=True)
    page, row = banned_spots[0]
    renderer.render_frame(page, row, None, None, draft_state, hint_on=False, multiplayer=True)

    draft_state.paused = True
    draft_state.pause_seconds_remaining = 30.0
    renderer.render_frame(page, row, None, None, draft_state, hint_on=False, multiplayer=True)


@pytest.mark.parametrize("mode", ["local", "lan_server"])
def test_lobby_widgets_render_for_host(game_screen, mode):
    state = LobbyState()
    state.settings = _tournament_settings()

    row_offsets, advanced_header_offset = lobby._layout(mode)
    buttons = lobby._make_buttons(game_screen, row_offsets)
    lobby._refresh_button_labels(buttons, state, "host", mode)

    assert buttons["ruleset"].text == "ruleset: tournament"
    assert buttons["time"].text == "time: 5+5"

    game_screen.render()
    lobby._render_title(game_screen)
    if advanced_header_offset is not None:
        lobby._render_advanced_header(game_screen, advanced_header_offset)
    for name, button in buttons.items():
        if name != "switch_role":
            button.update(game_screen)


def test_lobby_labels_render_for_client(game_screen):
    state = LobbyState()
    state.settings = _tournament_settings()
    state.local_role = "player2"

    row_offsets, _advanced = lobby._layout("lan_client")
    game_screen.render()
    lobby._render_settings_labels(game_screen, state, row_offsets)
    lobby._render_roster(game_screen, state, "player2")
