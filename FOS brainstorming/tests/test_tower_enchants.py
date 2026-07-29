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

"""Enchantments as they behave inside a battle."""

import pytest

from cards.factory import CardFactory
from tower import card_pool, enchant_runtime

from tests.helpers import do_attack, make_game_state, place_card


@pytest.fixture(autouse=True)
def installed():
    enchant_runtime.install()
    yield
    enchant_runtime.uninstall()


class _Sink:
    def __init__(self):
        self.dying_cards: list = []


def play(game_state, code: str, x: int = 1, y: int = 1, owner: str = "player1"):
    player = game_state.get_player(owner)
    player.hand.append(code)
    player.play_card(x, y, len(player.hand) - 1, game_state)
    return player.on_board[-1]


def test_berserk_trades_health_for_damage():
    game_state = make_game_state()
    reference = CardFactory.create("LFW", "display", 0, 0)
    unit = play(game_state, "LFW*rage")
    assert unit.damage == reference.damage + 2
    assert unit.max_health == reference.health - 2


def test_radiant_scores_one_extra():
    game_state = make_game_state()
    unit = play(game_state, "ADCW*radiant")
    unit.numbness = False
    unit.settle(game_state)
    assert game_state.score == -2


def test_radiant_scores_nothing_while_numb():
    game_state = make_game_state()
    unit = play(game_state, "ADCW*radiant")
    assert unit.numbness is True
    unit.settle(game_state)
    assert game_state.score == 0


def test_plated_shaves_a_point_off_every_hit():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*plated")
    before = unit.health
    game_state.judge.deal(3, unit, game_state)
    assert unit.health == before - 2


def test_steady_shrugs_off_numbness_on_deploy_and_later():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*steady")
    assert unit.numbness is False

    unit.numbness = True
    enchant_runtime.enforce(game_state, "player1")
    assert unit.numbness is False


def test_rusted_cannot_hold_a_shield():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*rust")
    unit.armor = 5
    enchant_runtime.enforce(game_state, "player1")
    assert unit.armor == 0


def test_bleeding_costs_a_point_of_health_each_turn():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*bleed")
    before = unit.health
    enchant_runtime.turn_start(game_state, "player1")
    assert unit.health == before - 1


def test_artisan_mend_heals_but_never_past_full():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*art_mend")
    unit.health -= 3
    wounded = unit.health
    enchant_runtime.turn_start(game_state, "player1")
    assert unit.health == wounded + 1

    unit.health = unit.max_health
    enchant_runtime.turn_start(game_state, "player1")
    assert unit.health == unit.max_health


def test_burning_hands_the_enemy_two_points_once_per_card():
    game_state = make_game_state()
    play(game_state, "ADCW*burn", 1, 1)
    assert game_state.score == 2

    play(game_state, "ADCW*burn", 2, 1)
    assert game_state.score == 2


def test_burning_on_the_enemy_side_scores_for_the_player():
    game_state = make_game_state()
    play(game_state, "ADCW*burn", 1, 1, owner="player2")
    assert game_state.score == -2


def test_mana_hands_out_an_orb_and_draws_at_the_threshold():
    game_state = make_game_state()
    play(game_state, "ADCW*mana", 1, 1)
    assert game_state.players_token["player1"] == 1

    game_state.players_token["player1"] = game_state.tokens_to_draw_a_card - 1
    play(game_state, "ADCW*mana", 2, 1)
    assert game_state.players_token["player1"] == 0
    assert game_state.card_to_draw["player1"] == 1


def test_ghostly_units_leave_no_body_behind():
    game_state = make_game_state()
    unit = play(game_state, "ASSW*ghost")
    unit.health = 0
    game_state.player1.recycle_cards(game_state, _Sink())
    assert game_state.player1.discard_pile == []


def test_ghostly_spells_are_spent_not_discarded():
    game_state = make_game_state()
    game_state.player1.hand = ["HEAL*ghost"]
    game_state.player1.play_card(0, 0, 0, game_state)
    assert game_state.number_of_heals["player1"] == 1
    assert game_state.player1.discard_pile == []


def test_ghostly_cards_vanish_at_end_of_turn():
    game_state = make_game_state()
    game_state.player1.hand = ["HEAL*ghost", "HEAL", "MOVEO"]
    game_state.player1.turn_end(game_state)
    assert game_state.player1.hand == ["HEAL"]


def test_plain_spells_still_reach_the_discard_pile():
    game_state = make_game_state()
    game_state.player1.hand = ["HEAL"]
    game_state.player1.play_card(0, 0, 0, game_state)
    assert game_state.player1.discard_pile == ["HEAL"]


def test_flying_sword_reaches_out_when_nothing_is_in_range():
    game_state = make_game_state()
    attacker = play(game_state, "TANKW*sword", 0, 0)
    attacker.numbness = False
    far = place_card(game_state, "TANKW", "player2", 3, 2)
    before = far.health

    assert attacker.attack(game_state) is True
    assert far.health < before


def test_flying_sword_leaves_a_normal_attack_alone():
    game_state = make_game_state()
    attacker = play(game_state, "TANKW*sword", 1, 1)
    attacker.numbness = False
    near = place_card(game_state, "TANKW", "player2", 1, 2)
    far = place_card(game_state, "TANKW", "player2", 3, 0)
    near_before, far_before = near.health, far.health

    assert attacker.attack(game_state) is True
    assert near.health < near_before
    assert far.health == far_before


def test_dispersed_changes_faction_but_keeps_the_body():
    game_state = make_game_state()
    reference = CardFactory.create("TANKW", "display", 0, 0)
    unit = play(game_state, "TANKW*disperse")

    assert card_pool.job_of(unit.job_and_color) == "TANK"
    assert card_pool.color_tag_of(unit.job_and_color) != "W"
    assert unit.max_health == reference.health
    assert unit.damage == reference.damage
    assert unit.tower_code == "TANKW*disperse"


def test_dispersed_card_returns_to_the_deck_unchanged():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*disperse")
    unit.health = 0
    game_state.player1.recycle_cards(game_state, _Sink())
    assert game_state.player1.discard_pile == ["TANKW*disperse"]


def test_enchantments_stack_with_each_other():
    game_state = make_game_state()
    reference = CardFactory.create("LFW", "display", 0, 0)
    unit = play(game_state, "LFW*sharp.fort.radiant")
    assert unit.damage == reference.damage + 1
    assert unit.max_health == reference.health + 2

    unit.numbness = False
    unit.settle(game_state)
    assert game_state.score == -2


def test_uninstalled_runtime_leaves_cards_plain():
    enchant_runtime.uninstall()
    game_state = make_game_state()
    reference = CardFactory.create("LFW", "display", 0, 0)
    unit = play(game_state, "LFW*rage")
    assert unit.damage == reference.damage
    assert getattr(unit, "tower_enchants", None) is None


def test_min_damage_floor_only_lifts_the_configured_side():
    game_state = make_game_state()
    game_state.tower_min_damage = {"player1": 2}
    attacker = place_card(game_state, "TANKW", "player1", 1, 1)
    target = place_card(game_state, "TANKW", "player2", 1, 2)
    before = target.health

    do_attack(attacker, game_state)
    assert before - target.health == 2


def test_overheal_multiplier_doubles_the_shield():
    game_state = make_game_state()
    unit = place_card(game_state, "TANKW", "player1", 1, 1)
    unit.health = unit.max_health - 1
    game_state.tower_overheal_mult = {"player1": 2}
    unit.heal(5, game_state)
    assert unit.armor == 4
