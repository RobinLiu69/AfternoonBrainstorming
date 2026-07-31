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

"""Relics that only mean something once a battle is running."""

import pytest

from shared import card_code
from cards.factory import CardFactory
from tower import enchant_runtime, run_state
from tower.battle_effects import SideRuntime, install_side_channels
from tower.content import RELICS
from tower.tower_ai import TowerAIController

from tests.helpers import make_game_state, place_card

FACTIONS = ["R", "B", "C", "BR"]
DUMMY_ENEMY = {"strategy": "white", "strategy_overrides": {}, "relics": [], "effects": {}}


@pytest.fixture(autouse=True)
def installed():
    enchant_runtime.install()
    yield
    enchant_runtime.uninstall()


def side_for(relic_ids, player_name: str = "player1") -> SideRuntime:
    return SideRuntime(run_state.effects_from_relics(relic_ids), player_name)


def started(side: SideRuntime, game_state) -> SideRuntime:
    side.on_battle_start(game_state)
    return side


def take_turn(side: SideRuntime, game_state, turn: int) -> None:
    game_state.turn_number = turn
    side.on_turn_start(game_state)


# --------------------------------------------------------------------------
# turn start
# --------------------------------------------------------------------------

def test_mana_spring_pours_an_orb_every_turn():
    game_state = make_game_state()
    side = started(side_for(["mana_spring"]), game_state)
    take_turn(side, game_state, 0)
    assert game_state.players_token["player1"] == 1


def test_treasure_chest_pays_two_coins_a_turn():
    game_state = make_game_state()
    side = started(side_for(["treasure_chest"]), game_state)
    take_turn(side, game_state, 0)
    take_turn(side, game_state, 2)
    assert game_state.players_coin["player1"] == 4


def test_mages_blood_trades_the_draw_for_orbs():
    game_state = make_game_state()
    side = started(side_for(["mages_blood"]), game_state)
    take_turn(side, game_state, 0)
    assert game_state.skip_turn_draw["player1"] is True
    # three orbs hit the threshold at once, so they convert into a draw
    assert game_state.card_to_draw["player1"] == 1


def test_battle_focus_refills_to_two_attacks_and_drops_leftovers():
    game_state = make_game_state()
    side = started(side_for(["battle_focus"]), game_state)
    game_state.number_of_attacks["player1"] = 7
    take_turn(side, game_state, 0)
    assert game_state.number_of_attacks["player1"] == 2


def test_pacifism_takes_the_attacks_and_gives_a_card():
    game_state = make_game_state()
    side = started(side_for(["pacifism"]), game_state)
    game_state.number_of_attacks["player1"] = 3
    take_turn(side, game_state, 0)
    assert game_state.number_of_attacks["player1"] == 0
    assert game_state.card_to_draw["player1"] == 1


def test_message_in_a_bottle_arrives_every_third_turn():
    game_state = make_game_state()
    side = started(side_for(["message_in_a_bottle"]), game_state)
    for turn in (0, 2):
        take_turn(side, game_state, turn)
    assert game_state.player1.hand == []

    take_turn(side, game_state, 4)
    assert len(game_state.player1.hand) == 1
    gift = game_state.player1.hand[0]
    assert card_code.has_enchant(gift, "ghost")
    assert card_code.plain_code(gift) in ("HEAL", "CUBES", "MOVE")


def test_a_turn_only_counts_once():
    game_state = make_game_state()
    side = started(side_for(["mana_spring"]), game_state)
    take_turn(side, game_state, 0)
    side.on_turn_start(game_state)
    assert game_state.players_token["player1"] == 1


# --------------------------------------------------------------------------
# reshuffles
# --------------------------------------------------------------------------

def test_cuckoo_clock_draws_when_the_deck_comes_back():
    game_state = make_game_state()
    side = started(side_for(["cuckoo_clock"]), game_state)
    side.maintain(game_state)
    assert game_state.card_to_draw["player1"] == 0

    game_state.player1.draw_pile = ["TANKW"] * 5
    side.maintain(game_state)
    assert game_state.card_to_draw["player1"] == 1


def test_pocket_watch_pays_an_attack_on_reshuffle():
    game_state = make_game_state()
    side = started(side_for(["pocket_watch"]), game_state)
    side.maintain(game_state)
    game_state.player1.draw_pile = ["TANKW"] * 5
    side.maintain(game_state)
    assert game_state.number_of_attacks["player1"] == 1


def test_drawing_down_the_pile_is_not_a_reshuffle():
    game_state = make_game_state()
    game_state.player1.draw_pile = ["TANKW"] * 5
    side = started(side_for(["cuckoo_clock"]), game_state)
    for _ in range(5):
        game_state.player1.draw_pile.pop()
        side.maintain(game_state)
    assert game_state.card_to_draw["player1"] == 0


# --------------------------------------------------------------------------
# spells and healing
# --------------------------------------------------------------------------

def test_dorans_ring_draws_off_the_first_spell_only():
    game_state = make_game_state()
    side = started(side_for(["dorans_ring"]), game_state)
    game_state.player1.hand = ["HEAL", "HEAL"]
    side.maintain(game_state)

    game_state.player1.play_card(0, 0, 0, game_state)
    side.maintain(game_state)
    assert game_state.card_to_draw["player1"] == 1

    game_state.player1.play_card(0, 0, 0, game_state)
    side.maintain(game_state)
    assert game_state.card_to_draw["player1"] == 1


def test_first_aid_kit_makes_heals_bigger():
    game_state = make_game_state()
    install_side_channels(game_state, {
        "player1": run_state.effects_from_relics(["first_aid_kit"]),
        "player2": {},
    })
    unit = place_card(game_state, "TANKW", "player1", 1, 1)
    unit.health = 1
    game_state.number_of_heals["player1"] = 1

    game_state.player1.heal_card(1, 1, game_state)
    assert unit.health == 9


def test_ring_of_healing_doubles_the_overheal_shield():
    game_state = make_game_state()
    install_side_channels(game_state, {
        "player1": run_state.effects_from_relics(["ring_of_healing"]),
        "player2": {},
    })
    unit = place_card(game_state, "TANKW", "player1", 1, 1)
    unit.health = unit.max_health - 1
    unit.heal(5, game_state)
    assert unit.armor == 4


def test_sewing_kit_lifts_weak_hits_to_two():
    game_state = make_game_state()
    install_side_channels(game_state, {
        "player1": run_state.effects_from_relics(["sewing_kit"]),
        "player2": {},
    })
    attacker = place_card(game_state, "TANKW", "player1", 1, 1)
    target = place_card(game_state, "TANKW", "player2", 1, 2)
    before = target.health

    attacker.numbness = False
    attacker.attack(game_state)
    assert before - target.health == 2


# --------------------------------------------------------------------------
# unit buffs
# --------------------------------------------------------------------------

def test_wax_furnace_only_sharpens_enchanted_units():
    game_state = make_game_state()
    side = started(side_for(["wax_furnace"]), game_state)
    reference = CardFactory.create("LFW", "display", 0, 0)

    game_state.player1.hand = ["LFW*fort", "LFW"]
    game_state.player1.play_card(1, 1, 0, game_state)
    game_state.player1.play_card(2, 1, 0, game_state)
    side.maintain(game_state)

    enchanted, plain = game_state.player1.on_board
    assert enchanted.damage == reference.damage + 1
    assert plain.damage == reference.damage


def test_amulets_and_emblems_land_on_their_own_job():
    game_state = make_game_state()
    side = started(side_for(["amulet_TANK", "emblem_ADC"]), game_state)
    tank_ref = CardFactory.create("TANKW", "display", 0, 0)
    adc_ref = CardFactory.create("ADCW", "display", 0, 0)

    game_state.player1.hand = ["TANKW", "ADCW"]
    game_state.player1.play_card(1, 1, 0, game_state)
    game_state.player1.play_card(2, 1, 0, game_state)
    side.maintain(game_state)

    tank, adc = game_state.player1.on_board
    assert tank.max_health == tank_ref.health + 1
    assert tank.damage == tank_ref.damage
    assert adc.damage == adc_ref.damage + 1
    assert adc.max_health == adc_ref.health


# --------------------------------------------------------------------------
# controller wiring
# --------------------------------------------------------------------------

def test_controller_installs_the_side_channels_for_both_sides():
    game_state = make_game_state()
    controller = TowerAIController(
        DUMMY_ENEMY,
        run_state.effects_from_relics(["sewing_kit"]),
        run_state.effects_from_relics(["first_aid_kit"]),
    )
    controller._maintain_units(game_state)

    assert game_state.tower_heal_bonus == {"player1": 2, "player2": 0}
    assert game_state.tower_min_damage == {"player1": 0, "player2": 2}


def test_controller_starts_each_side_once():
    game_state = make_game_state()
    controller = TowerAIController(
        DUMMY_ENEMY,
        run_state.effects_from_relics([]),
        run_state.effects_from_relics(["prepared_pack"]),
    )
    game_state.player1.deck = ["TANKW"] * 8
    game_state.player1.discard_pile = ["TANKW"] * 8
    controller._apply_initial(game_state)

    assert len(game_state.player1.hand) == 4
    assert controller.player.started is True
    assert controller.enemy.started is True


# --------------------------------------------------------------------------
# run level
# --------------------------------------------------------------------------

def test_ship_in_a_bottle_pays_out_per_pirate():
    run = run_state.new_run(FACTIONS, seed=1)
    run_state.add_relic(run, "ship_in_a_bottle")
    assert run_state.victory_bonus_gold(run) == 0

    run["deck"] = ["TANKC", "ADCC", "TANKW"]
    assert run_state.victory_bonus_gold(run) == 40


def test_blue_crystal_ball_stings_when_the_orbs_fire():
    game_state = make_game_state()
    side = started(side_for(["blue_crystal_ball"]), game_state)
    target = place_card(game_state, "TANKW", "player2", 1, 1)
    before = target.health

    game_state.players_token["player1"] = 2
    side.maintain(game_state)
    assert target.health == before

    game_state.players_token["player1"] = 0
    side.maintain(game_state)
    assert target.health == before - 1


def test_blasting_wand_leaves_targets_free_to_act():
    game_state = make_game_state()
    side = started(side_for(["blasting_wand"]), game_state)
    mage = place_card(game_state, "APW", "player1", 1, 1)
    target = place_card(game_state, "TANKW", "player2", 1, 2)
    side.maintain(game_state)
    target.numbness = False

    mage.numbness = False
    mage.attack(game_state)
    assert target.health < target.max_health
    assert target.numbness is False


def test_credit_card_lets_you_overspend_and_income_repays_it():
    run = run_state.new_run(FACTIONS, seed=2)
    run["gold"] = 50
    run_state.add_relic(run, "credit_card")

    assert run_state.affordable(run, 200) is True
    assert run_state.spend_gold(run, 200) is True
    assert run["gold"] == 0
    assert run["debt"] == 150

    assert run_state.spend_gold(run, 100) is False

    assert run_state.award_gold(run, 100) == 0
    assert run["debt"] == 50
    assert run["gold"] == 0

    assert run_state.award_gold(run, 100) == 50
    assert run["debt"] == 0
    assert run["gold"] == 50


def test_debt_grows_each_floor_until_it_is_paid():
    run = run_state.new_run(FACTIONS, seed=2)
    run_state.add_relic(run, "credit_card")
    run["debt"] = 100
    assert run_state.floor_upkeep(run)["debt"] == 10
    assert run["debt"] == 110


def test_without_a_credit_card_you_cannot_overspend():
    run = run_state.new_run(FACTIONS, seed=2)
    run["gold"] = 50
    assert run_state.spend_gold(run, 60) is False
    assert run["gold"] == 50
    assert run["debt"] == 0


def test_carving_knife_engraves_every_turn():
    game_state = make_game_state()
    side = started(side_for(["carving_knife"]), game_state)
    take_turn(side, game_state, 0)
    take_turn(side, game_state, 2)
    assert game_state.players_totem["player1"] == 2


def test_mob_pigeon_delivers_on_the_fourth_turn():
    game_state = make_game_state()
    side = started(side_for(["mob_pigeon"]), game_state)
    for turn in (0, 2, 4):
        take_turn(side, game_state, turn)
    assert game_state.player1.hand == []

    take_turn(side, game_state, 6)
    assert game_state.player1.hand == ["MOVE"]


def test_rabbits_foot_raises_starting_luck():
    game_state = make_game_state()
    started(side_for(["rabbits_foot"]), game_state)
    assert game_state.players_luck["player1"] == 65


def test_chipped_crown_starts_you_a_point_behind():
    game_state = make_game_state()
    started(side_for(["chipped_crown"]), game_state)
    assert game_state.score == 1

    other = make_game_state()
    started(side_for(["chipped_crown"], "player2"), other)
    assert other.score == -1


def test_strategists_fan_scores_while_your_board_is_empty():
    game_state = make_game_state()
    side = started(side_for(["strategists_fan"]), game_state)

    side.on_turn_end(game_state)
    assert game_state.score == -1

    place_card(game_state, "TANKW", "player1", 1, 1)
    side.on_turn_end(game_state)
    assert game_state.score == -1


def test_radiant_totem_pays_per_twenty():
    game_state = make_game_state()
    side = started(side_for(["radiant_totem"]), game_state)

    game_state.players_totem["player1"] = 19
    side.on_turn_end(game_state)
    assert game_state.score == 0

    game_state.players_totem["player1"] = 45
    side.on_turn_end(game_state)
    assert game_state.score == -2


def test_razor_hat_bleeds_an_enemy_whenever_anything_moves():
    game_state = make_game_state()
    side = started(side_for(["razor_hat"]), game_state)
    mover = place_card(game_state, "TANKW", "player1", 1, 1)
    target = place_card(game_state, "TANKW", "player2", 3, 0)
    side.maintain(game_state)
    before = target.health

    mover.moving = True
    mover.move(1, 2, game_state)
    side.maintain(game_state)
    assert target.health == before - 1

    side.maintain(game_state)
    assert target.health == before - 1


def test_oni_mask_pays_armor_for_growth():
    game_state = make_game_state()
    side = started(side_for(["oni_mask"]), game_state)
    unit = place_card(game_state, "TANKW", "player1", 1, 1)
    side.maintain(game_state)
    assert unit.armor == 0

    unit.damage += 1
    side.maintain(game_state)
    assert unit.armor == 0

    unit.damage += 1
    side.maintain(game_state)
    assert unit.armor == 1

    unit.damage += 2
    side.maintain(game_state)
    assert unit.armor == 2


def test_ninja_scroll_punishes_a_second_hit_on_the_same_target():
    game_state = make_game_state()
    side = started(side_for(["ninja_scroll"]), game_state)
    attacker = place_card(game_state, "TANKW", "player1", 1, 1)
    target = place_card(game_state, "TANKW", "player2", 1, 2)
    side.maintain(game_state)
    attacker.numbness = False
    base = attacker.damage

    before = target.health
    attacker.attack(game_state)
    assert before - target.health == base

    before = target.health
    attacker.hit_cards.append(target)
    attacker.attack(game_state)
    assert before - target.health == base + 2


def test_hidden_dagger_cuts_enemies_standing_on_shadows():
    from cards.card_fuchsia import Shadow

    game_state = make_game_state()
    side = started(side_for(["hidden_dagger"]), game_state)
    caster = place_card(game_state, "ADCF", "player1", 0, 1)
    shadow = Shadow("player1", 2, 1, caster, "", False)
    game_state.player1.on_board.append(shadow)
    on_shadow = place_card(game_state, "TANKW", "player2", 2, 1)
    elsewhere = place_card(game_state, "TANKW", "player2", 0, 0)
    hurt, safe = on_shadow.health, elsewhere.health

    side.on_turn_end(game_state)
    assert on_shadow.health == hurt - 1
    assert elsewhere.health == safe
    assert shadow.health > 0


def test_curse_ward_turns_curses_away():
    run = run_state.new_run(FACTIONS, seed=1)
    assert run_state.can_take_relic(run, "worn_pack") is True

    run_state.add_relic(run, "curse_ward")
    assert run_state.can_take_relic(run, "worn_pack") is False
    assert run_state.add_relic(run, "worn_pack") is False


def test_palanquin_widens_the_bench():
    run = run_state.new_run(FACTIONS, seed=1)
    before = run_state.bench_limit(run)
    run_state.add_relic(run, "palanquin")
    assert run_state.bench_limit(run) == before + 2


def test_every_relic_effect_key_is_known_to_the_merger():
    from tower.content import (
        ADDITIVE_EFFECTS, FLAG_EFFECTS, JOB_EFFECTS, MAX_EFFECTS,
        MIN_EFFECTS, MULTIPLIED_EFFECTS,
    )
    known = (ADDITIVE_EFFECTS | FLAG_EFFECTS | JOB_EFFECTS | MAX_EFFECTS
             | MIN_EFFECTS | MULTIPLIED_EFFECTS)
    for relic_id, relic in RELICS.items():
        for key in relic.get("effects", {}):
            assert key in known, f"{relic_id} has an unmergeable effect {key!r}"
