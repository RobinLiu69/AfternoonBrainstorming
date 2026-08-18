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
from core.card_hint import HintBox
from core.game_screen import GameScreen
from core.lobby_state import LobbyState
from screens.draft.exhibit_registry import ExhibitRegistry
from screens.lobby.ban_draft import _SpectatorBoardCache, _render_hint, hovered_name


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


@pytest.fixture(scope="module")
def registry(game_screen):
    return ExhibitRegistry(game_screen)


def _banned() -> LobbyState:
    state = LobbyState()
    state.in_ban_draft = True
    state.bans = {"TANKG": "host", "APG": "peer"}
    return state


class TestWhatTheMouseIsOver:
    def test_a_card_in_the_pool_reports_its_name(self, registry) -> None:
        names = {hovered_name(registry, [], "host", 0, 0, x, y)
                 for x in range(4) for y in range(3)}

        assert "TANKW" in names

    def test_an_empty_cell_reports_nothing(self, registry) -> None:
        assert hovered_name(registry, [], "host", 0, 0, 3, 2) == ""

    def test_the_mouse_outside_the_board_reports_nothing(self, registry) -> None:
        assert hovered_name(registry, [], "host", 0, 0, None, 1) == ""
        assert hovered_name(registry, [], "host", 0, 0, 1, None) == ""

    def test_a_watcher_reads_the_banned_board_instead_of_the_pool(self) -> None:
        cards = _SpectatorBoardCache().get(_banned())

        assert hovered_name(None, cards, None, 0, 0, 0, 0) == "TANKG"
        assert hovered_name(None, cards, None, 0, 0, 0, 1) == "APG"

    def test_a_watcher_over_an_empty_slot_reports_nothing(self) -> None:
        cards = _SpectatorBoardCache().get(_banned())

        assert hovered_name(None, cards, None, 0, 0, 3, 1) == ""


class TestTheHintOnlyDrawsWhenAsked:
    def _box(self, game_screen) -> HintBox:
        bs = game_screen.block_size
        return HintBox(width=int(bs * 3), height=int(bs))

    def _ink(self, game_screen) -> int:
        surface = game_screen.surface
        return sum(1 for x in range(0, surface.get_width(), 4)
                   for y in range(0, surface.get_height(), 4)
                   if surface.get_at((x, y))[:3] != (0, 0, 0))

    def test_it_draws_for_a_hovered_card(self, game_screen) -> None:
        game_screen.surface.fill((0, 0, 0))
        _render_hint(game_screen, self._box(game_screen), True, "TANKW", 300, 200)

        assert self._ink(game_screen) > 0

    def test_it_stays_hidden_when_toggled_off(self, game_screen) -> None:
        game_screen.surface.fill((0, 0, 0))
        _render_hint(game_screen, self._box(game_screen), False, "TANKW", 300, 200)

        assert self._ink(game_screen) == 0

    def test_it_stays_hidden_over_an_empty_cell(self, game_screen) -> None:
        game_screen.surface.fill((0, 0, 0))
        _render_hint(game_screen, self._box(game_screen), True, "", 300, 200)

        assert self._ink(game_screen) == 0
