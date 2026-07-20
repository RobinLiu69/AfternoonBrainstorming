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

from core.draft_state import DraftState
from tests.helpers import make_game_state


def _sample_state():
    gs = make_game_state()
    gs.player1.deck = ["ADCG", "APG", "TANKG"]
    gs.player1.draw_pile = ["APG", "TANKG"]
    gs.player2.deck = ["ASSG", "SPG"]
    gs.player2.draw_pile = ["SPG"]
    return gs


def test_battle_state_hides_opponent_deck_and_draw_pile():
    gs = _sample_state()
    data = gs.to_dict_for("player1")
    assert data["player1"]["deck"] == gs.player1.deck
    assert data["player1"]["draw_pile"] == gs.player1.draw_pile
    assert data["player2"]["deck"] == ["?", "?"]
    assert data["player2"]["draw_pile"] == ["?"]

    data = gs.to_dict_for("player2")
    assert data["player2"]["deck"] == gs.player2.deck
    assert data["player1"]["deck"] == ["?", "?", "?"]
    assert data["player1"]["draw_pile"] == ["?", "?"]


def test_battle_state_hides_both_players_from_plain_spectator():
    gs = _sample_state()
    data = gs.to_dict_for("spectator")
    assert data["player1"]["deck"] == ["?", "?", "?"]
    assert data["player1"]["draw_pile"] == ["?", "?"]
    assert data["player2"]["deck"] == ["?", "?"]
    assert data["player2"]["draw_pile"] == ["?"]


def test_battle_state_reveals_everything_to_god():
    gs = _sample_state()
    data = gs.to_dict_for("god")
    assert data["player1"]["deck"] == gs.player1.deck
    assert data["player1"]["draw_pile"] == gs.player1.draw_pile
    assert data["player2"]["deck"] == gs.player2.deck
    assert data["player2"]["draw_pile"] == gs.player2.draw_pile


def test_battle_state_never_ships_rng_seed():
    gs = _sample_state()
    for viewer in ("player1", "player2", "spectator", "god"):
        assert "rng_seed" not in gs.to_dict_for(viewer)


def test_draft_state_hides_picks_beyond_first_six():
    ds = DraftState()
    ds.player1_deck = ["A", "B", "C", "D", "E", "F", "G", "H"]
    ds.player2_deck = ["Q", "R", "S", "T", "U", "V", "W"]

    data = ds.to_dict_for("player2")
    assert data["player1_deck"] == ["A", "B", "C", "D", "E", "F", "?", "?"]
    assert data["player2_deck"] == ds.player2_deck

    data = ds.to_dict_for("spectator")
    assert data["player1_deck"] == ["A", "B", "C", "D", "E", "F", "?", "?"]
    assert data["player2_deck"] == ["Q", "R", "S", "T", "U", "V", "?"]

    data = ds.to_dict_for("god")
    assert data["player1_deck"] == ds.player1_deck
    assert data["player2_deck"] == ds.player2_deck
