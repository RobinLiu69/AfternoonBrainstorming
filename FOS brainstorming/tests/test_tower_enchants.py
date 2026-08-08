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


def test_an_enchanted_cyan_card_can_still_be_upgraded():
    from core.battling_dispatcher import BattlingDispatcher
    from core.game_action import GameAction

    game_state = make_game_state()
    game_state.player1.hand = ["APC*mana", "APC"]
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")

    for index in (0, 1):
        dispatcher.dispatch(GameAction(player="player1", action_type="toggle_upgrade",
                                       hand_index=index), game_state)
    assert game_state.player1.hand == ["APC*mana (+)", "APC (+)"]

    dispatcher.dispatch(GameAction(player="player1", action_type="toggle_upgrade",
                                   hand_index=0), game_state)
    assert game_state.player1.hand[0] == "APC*mana"


def test_an_enchanted_cyan_card_deploys_upgraded():
    game_state = make_game_state()
    game_state.players_coin["player1"] = 50
    plain = CardFactory.create("APC", "display", 0, 0)

    game_state.player1.hand = ["APC*fort (+)"]
    game_state.player1.play_card(1, 1, 0, game_state)

    unit = game_state.player1.on_board[-1]
    assert unit.job_and_color == "APC"
    assert getattr(unit, "upgrade", False) is True
    assert unit.max_health > plain.health + 2 - 1
    assert unit.tower_code == "APC*fort (+)"


def test_non_cyan_cards_never_gain_an_upgrade_marker():
    from core.battling_dispatcher import BattlingDispatcher
    from core.game_action import GameAction

    game_state = make_game_state()
    game_state.player1.hand = ["TANKW*sharp", "HEAL"]
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")
    for index in (0, 1):
        dispatcher.dispatch(GameAction(player="player1", action_type="toggle_upgrade",
                                       hand_index=index), game_state)
    assert game_state.player1.hand == ["TANKW*sharp", "HEAL"]


def test_the_hint_box_describes_enchantments():
    from shared import card_code
    from tower import language
    from tower.content import ENCHANTS

    language.use(language.ENGLISH)
    try:
        lines = card_code.describe_enchants("TANKW*sharp")
        assert len(lines) == 1
        assert ENCHANTS["sharp"]["label"] in lines[0]
        assert ENCHANTS["sharp"]["text"] in lines[0]

        assert card_code.describe_enchants("TANKW") == []
        assert len(card_code.describe_enchants("TANKW*sharp.fort")) == 2
    finally:
        language.use(None)


def test_the_hint_box_describes_enchantments_in_chinese_too():
    from shared import card_code
    from tower import language
    from tower.content_zh import ENCHANTS_ZH

    language.use(language.CHINESE)
    try:
        lines = card_code.describe_enchants("TANKW*sharp")
        assert ENCHANTS_ZH["sharp"][0] in lines[0]
        assert ENCHANTS_ZH["sharp"][1] in lines[0]
    finally:
        language.use(None)


def test_no_enchant_descriptions_once_the_runtime_is_gone():
    from shared import card_code
    enchant_runtime.uninstall()
    assert card_code.describe_enchants("TANKW*sharp") == []


def test_the_hint_box_finds_stats_for_an_enchanted_card():
    from core.card_hint import get_stat_prefix
    assert get_stat_prefix("TANKW*sharp") == get_stat_prefix("TANKW")
    assert get_stat_prefix("TANKW*sharp") != ""
    assert get_stat_prefix("APC*mana (+)") == get_stat_prefix("APC (+)")


def test_the_ai_still_recognises_an_enchanted_unit_card():
    from campaign import ai_query
    assert ai_query.is_playable_unit_card("TANKW*sharp") is True
    assert ai_query.is_playable_unit_card("HEAL*ghost") is False
    assert ai_query.is_playable_unit_card("MOVEO") is False


def test_vigor_heals_at_the_end_of_your_turn():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*vigor")
    unit.health -= 3
    wounded = unit.health

    enchant_runtime.turn_start(game_state, "player1")
    assert unit.health == wounded

    enchant_runtime.turn_end(game_state, "player1")
    assert unit.health == wounded + 1


def test_gigantism_doubles_the_body_and_takes_the_attack_away():
    game_state = make_game_state()
    reference = CardFactory.create("TANKW", "display", 0, 0)
    unit = play(game_state, "TANKW*gigantism")

    assert unit.max_health == reference.health * 2
    assert unit.damage == reference.damage * 2
    assert unit.attack_types == ""
    unit.numbness = False
    assert unit.attack(game_state) is False


def test_brown_sp_clears_the_giant_drawback():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*gigantism")
    enchant_runtime.clear_giant_drawback(unit)

    assert unit.attack_types == CardFactory.create("TANKW", "display", 0, 0).attack_types
    enchant_runtime.enforce(game_state, "player1")
    assert unit.attack_types != ""


def test_flight_reaches_across_the_whole_board():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*flight", 0, 0)
    unit.moving = True

    assert unit.move(3, 2, game_state) is True
    assert (unit.board_x, unit.board_y) == (3, 2)
    assert game_state.board_dict[0, 0].occupy is False
    assert game_state.board_dict[3, 2].occupy is True


def test_flight_still_refuses_an_occupied_square():
    game_state = make_game_state()
    unit = play(game_state, "TANKW*flight", 0, 0)
    place_card(game_state, "TANKW", "player2", 3, 2)
    unit.moving = True
    assert unit.move(3, 2, game_state) is False


def test_a_plain_unit_cannot_fly():
    game_state = make_game_state()
    unit = play(game_state, "TANKW", 0, 0)
    unit.moving = True
    assert unit.move(3, 2, game_state) is False


def test_carver_engraves_a_totem_on_every_hit():
    game_state = make_game_state()
    attacker = play(game_state, "TANKW*carver", 1, 1)
    place_card(game_state, "TANKW", "player2", 1, 2)
    attacker.numbness = False

    attacker.attack(game_state)
    assert game_state.players_totem["player1"] == 1


def test_echo_doubles_damage_and_cost_when_attacks_are_banked():
    game_state = make_game_state()
    attacker = play(game_state, "TANKW*echo", 1, 1)
    target = place_card(game_state, "TANKW", "player2", 1, 2)
    attacker.numbness = False
    base = CardFactory.create("TANKW", "display", 0, 0).damage

    game_state.number_of_attacks["player1"] = 1
    assert attacker.attack_cost(game_state) == 1
    before = target.health
    attacker.attack(game_state)
    assert before - target.health == base

    game_state.number_of_attacks["player1"] = 3
    assert attacker.attack_cost(game_state) == 2
    before = target.health
    attacker.attack(game_state)
    assert before - target.health == base * 2


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
