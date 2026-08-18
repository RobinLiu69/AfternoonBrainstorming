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
from core.game_screen import GameScreen, cell_origin
from core.lobby_dispatcher import LobbyDispatcher
from core.lobby_state import BANNABLE_MAGIC_CARDS, LobbyState, is_bannable_card
from rendering.card_renderer import CardRenderer, draw_lock
from screens.lobby.lobby_action import LobbyAction


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


def _ink_in_name_strip(game_screen: GameScreen, board_x: int, board_y: int) -> int:
    bs = game_screen.block_size
    x, y = cell_origin(game_screen, board_x, board_y)
    seen = 0
    for dy in range(int(bs * 0.78), int(bs * 0.95)):
        for dx in range(int(bs * 0.08), int(bs * 0.9)):
            if game_screen.surface.get_at((int(x + dx), int(y + dy)))[:3] != (0, 0, 0):
                seen += 1
    return seen


class TestMagicCardsCanBeBanned:
    def test_every_magic_card_passes_the_bannable_gate(self) -> None:
        for name in BANNABLE_MAGIC_CARDS:
            assert is_bannable_card(name) is True

    def test_the_dispatcher_accepts_and_releases_them(self) -> None:
        state = LobbyState()
        state.in_ban_draft = True
        dispatcher = LobbyDispatcher(state, mode="local")

        for name in sorted(BANNABLE_MAGIC_CARDS):
            assert dispatcher.dispatch(
                LobbyAction("host", "ban_card", str_value=name)).success is True
        assert set(state.bans) == set(BANNABLE_MAGIC_CARDS)

        assert dispatcher.dispatch(
            LobbyAction("host", "unban_card", str_value="HEAL")).success is True
        assert "HEAL" not in state.bans


class TestALockedCardStaysIdentifiable:
    def test_a_locked_magic_card_still_shows_its_name(self, game_screen) -> None:
        renderer = CardRenderer(game_screen)
        game_screen.surface.fill((0, 0, 0))
        card = CardFactory.create("CUBES", "display", 0, 0)
        for data in card.get_render_data():
            renderer.render(data)
        draw_lock(game_screen, "CUBES", 0, 0)

        assert _ink_in_name_strip(game_screen, 0, 0) > 0

    def test_an_unlocked_magic_card_is_not_labelled_twice(self, game_screen) -> None:
        renderer = CardRenderer(game_screen)
        game_screen.surface.fill((0, 0, 0))
        card = CardFactory.create("MOVE", "display", 1, 0)
        for data in card.get_render_data():
            renderer.render(data)

        assert _ink_in_name_strip(game_screen, 1, 0) == 0

    def test_a_locked_unit_card_keeps_the_name_it_already_had(self, game_screen) -> None:
        renderer = CardRenderer(game_screen)
        game_screen.surface.fill((0, 0, 0))
        card = CardFactory.create("TANKW", "display", 2, 0)
        for data in card.get_render_data():
            renderer.render(data)
        before = _ink_in_name_strip(game_screen, 2, 0)
        draw_lock(game_screen, "TANKW", 2, 0)

        assert before > 0
        assert _ink_in_name_strip(game_screen, 2, 0) == before
