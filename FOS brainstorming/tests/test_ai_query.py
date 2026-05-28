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

from campaign import ai_query
from cards.card_white import Adc, Tank, Ass
from tests.helpers import make_game_state, place_card


def test_empty_positions_lists_unoccupied_cells():
    gs = make_game_state()
    place_card(gs, Tank, "player1", 0, 0)
    place_card(gs, Adc, "player2", 3, 3)

    empties = ai_query.empty_positions(gs)
    assert (0, 0) not in empties
    assert (3, 3) not in empties
    assert (1, 1) in empties
    assert len(empties) == 4 * 4 - 2


def test_position_safety_corner_edge_center():
    gs = make_game_state()
    assert ai_query.position_safety(gs, 0, 0) == 3.0
    assert ai_query.position_safety(gs, 3, 3) == 3.0
    assert ai_query.position_safety(gs, 1, 0) == 2.0
    assert ai_query.position_safety(gs, 0, 2) == 2.0
    assert ai_query.position_safety(gs, 1, 1) == 1.0
    assert ai_query.position_safety(gs, 2, 2) == 1.0


def test_is_corner_and_is_edge():
    gs = make_game_state()
    assert ai_query.is_corner(gs, 0, 0)
    assert ai_query.is_corner(gs, 3, 3)
    assert not ai_query.is_corner(gs, 0, 1)
    assert ai_query.is_edge(gs, 0, 1)
    assert ai_query.is_edge(gs, 2, 3)
    assert not ai_query.is_edge(gs, 0, 0)
    assert not ai_query.is_edge(gs, 1, 1)


def test_enemy_and_friendly_cards():
    gs = make_game_state()
    a = place_card(gs, Adc, "player1", 0, 0)
    b = place_card(gs, Tank, "player2", 3, 3)

    assert ai_query.enemy_cards(gs, "player1") == [b]
    assert ai_query.enemy_cards(gs, "player2") == [a]
    assert ai_query.friendly_cards(gs, "player1") == [a]
    assert ai_query.friendly_cards(gs, "player2") == [b]


def test_attack_targets_small_cross():
    gs = make_game_state()
    tank = place_card(gs, Tank, "player1", 1, 1)
    above = place_card(gs, Adc, "player2", 1, 0)
    below = place_card(gs, Adc, "player2", 1, 2)
    diagonal = place_card(gs, Adc, "player2", 2, 2)

    hits = ai_query.attack_targets_at(gs, tank)
    assert above in hits
    assert below in hits
    assert diagonal not in hits


def test_attack_targets_large_cross_for_adc():
    gs = make_game_state()
    adc = place_card(gs, Adc, "player1", 1, 1)
    far_row = place_card(gs, Tank, "player2", 3, 1)
    far_col = place_card(gs, Tank, "player2", 1, 3)
    off_axis = place_card(gs, Tank, "player2", 2, 2)

    hits = ai_query.attack_targets_at(gs, adc)
    assert far_row in hits
    assert far_col in hits
    assert off_axis not in hits


def test_attack_targets_empty_when_no_enemies_in_range():
    gs = make_game_state()
    tank = place_card(gs, Tank, "player1", 0, 0)
    place_card(gs, Adc, "player2", 3, 3)

    hits = ai_query.attack_targets_at(gs, tank)
    assert hits == []


def test_nearest_enemy_distance():
    gs = make_game_state()
    place_card(gs, Adc, "player2", 0, 0)
    place_card(gs, Adc, "player2", 3, 3)

    assert ai_query.nearest_enemy_distance(gs, "player1", 1, 0) == 1
    assert ai_query.nearest_enemy_distance(gs, "player1", 2, 2) == 2


def test_attack_targets_does_not_consume_rng():
    """Mirror of card.detection() must not advance gs.rng — the engine call still needs it."""
    gs = make_game_state(rng_seed=42)
    sp = place_card(gs, "SPW", "player1", 0, 0)
    place_card(gs, Adc, "player2", 3, 3)
    place_card(gs, Adc, "player2", 2, 3)

    state_before = gs.rng.getstate()
    ai_query.attack_targets_at(gs, sp)
    assert gs.rng.getstate() == state_before


def test_cells_threatening_card_finds_corner_adc_kill_spot():
    gs = make_game_state()
    adc = place_card(gs, Adc, "player2", 3, 0)  # ATK ranges adc.health=5
    threats = ai_query.cells_threatening_card(gs, adc)
    assert threats == [(2, 1)]


def test_cells_threatening_card_returns_empty_for_high_hp_target():
    gs = make_game_state()
    tank = place_card(gs, Tank, "player2", 3, 0)  # 15 HP — ASS can't one-shot
    threats = ai_query.cells_threatening_card(gs, tank)
    assert threats == []


def test_cells_threatening_card_skips_occupied_spots():
    gs = make_game_state()
    adc = place_card(gs, Adc, "player2", 3, 0)
    place_card(gs, Ass, "player2", 2, 1)  # we already block the only kill spot
    threats = ai_query.cells_threatening_card(gs, adc)
    assert threats == []


def test_incoming_damage_zero_when_opponent_has_no_attacks():
    gs = make_game_state()
    enemy = place_card(gs, Adc, "player1", 1, 1)
    enemy.numbness = False
    gs.number_of_attacks["player1"] = 0
    assert ai_query.incoming_damage_at_position(gs, "player2", 0, 1) == 0


def test_incoming_damage_counts_non_numb_attackers_in_range():
    gs = make_game_state()
    enemy = place_card(gs, Adc, "player1", 1, 1)
    enemy.numbness = False
    gs.number_of_attacks["player1"] = 2
    # ADC has large_cross — row 1 and col 1 are in range
    assert ai_query.incoming_damage_at_position(gs, "player2", 0, 1) == enemy.damage


def test_incoming_damage_caps_by_opponent_attack_count():
    """Even with 3 enemies in range, opponent can only fire `number_of_attacks` of them."""
    gs = make_game_state()
    for x in range(3):
        e = place_card(gs, Adc, "player1", x, 0)
        e.numbness = False
    gs.number_of_attacks["player1"] = 1
    incoming = ai_query.incoming_damage_at_position(gs, "player2", 0, 1)
    assert incoming == 4  # only the top-damage enemy fires


def test_incoming_damage_ignores_numb_enemies():
    gs = make_game_state()
    e = place_card(gs, Adc, "player1", 1, 1)
    e.numbness = True
    gs.number_of_attacks["player1"] = 2
    assert ai_query.incoming_damage_at_position(gs, "player2", 0, 1) == 0
