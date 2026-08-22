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

import unittest

from core.battling_dispatcher import (STALEMATE_TURNS, score_is_frozen,
                                      stalemate_winner)
from tests.helpers import make_game_state


class TestAFrozenScoreEndsTheMatch(unittest.TestCase):
    def _state_with_history(self, history):
        game_state = make_game_state()
        game_state.game_statistics.score_history = list(history)
        return game_state

    def test_a_short_match_is_never_called_a_stalemate(self):
        state = self._state_with_history([3] * (STALEMATE_TURNS - 1))
        self.assertFalse(score_is_frozen(state))

    def test_a_score_that_never_moves_is_a_stalemate(self):
        state = self._state_with_history([3] * STALEMATE_TURNS)
        self.assertTrue(score_is_frozen(state))

    def test_a_move_anywhere_in_the_window_clears_the_stalemate(self):
        state = self._state_with_history([1] + [3] * (STALEMATE_TURNS - 1))
        self.assertFalse(score_is_frozen(state))
        state = self._state_with_history([3] * (STALEMATE_TURNS - 1) + [4])
        self.assertFalse(score_is_frozen(state))

    def test_a_long_frozen_match_still_counts(self):
        state = self._state_with_history(list(range(50)) + [7] * STALEMATE_TURNS)
        self.assertTrue(score_is_frozen(state))


class TestTheLeaderWinsAStalemate(unittest.TestCase):
    def test_a_negative_score_means_player1_is_ahead(self):
        state = make_game_state()
        state.score = -4
        self.assertEqual(stalemate_winner(state), "player1")

    def test_a_positive_score_means_player2_is_ahead(self):
        state = make_game_state()
        state.score = 4
        self.assertEqual(stalemate_winner(state), "player2")

    def test_a_level_score_is_broken_by_units_on_board(self):
        state = make_game_state()
        state.score = 0
        state.player1.on_board = [_unit(3), _unit(3)]
        state.player2.on_board = [_unit(9)]
        self.assertEqual(stalemate_winner(state), "player1")

    def test_equal_boards_are_broken_by_total_health(self):
        state = make_game_state()
        state.score = 0
        state.player1.on_board = [_unit(2)]
        state.player2.on_board = [_unit(5)]
        self.assertEqual(stalemate_winner(state), "player2")

    def test_a_perfectly_level_match_is_a_draw(self):
        state = make_game_state()
        state.score = 0
        state.player1.on_board = [_unit(4)]
        state.player2.on_board = [_unit(4)]
        self.assertEqual(stalemate_winner(state), "draw")


class _Unit:
    def __init__(self, health):
        self.health = health


def _unit(health):
    return _Unit(health)


if __name__ == "__main__":
    unittest.main()
