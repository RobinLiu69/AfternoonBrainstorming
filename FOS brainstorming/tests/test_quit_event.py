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

import pygame
import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from cards.factory import CardFactory
from core.game_screen import GameScreen, QuitGame
from screens.draft.draft_action import collect_draft_actions
from screens.battling.battling_action import collect_actions
from tests.helpers import make_game_state


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


def _queue_quit():
    pygame.event.clear()
    pygame.event.post(pygame.event.Event(pygame.QUIT))


def test_draft_collector_raises_quitgame(game_screen):
    _queue_quit()
    with pytest.raises(QuitGame):
        collect_draft_actions("player1", 0, 0, None, None, None)


def test_battle_collector_raises_quitgame(game_screen):
    _queue_quit()
    game_state = make_game_state()
    with pytest.raises(QuitGame):
        collect_actions("player1", [], game_state, game_screen)
