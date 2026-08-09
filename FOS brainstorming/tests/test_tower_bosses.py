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

"""Act bosses, and the two-phase fight against The Forgotten."""

import random

import pytest

from shared import card_code
from core.game_action import GameAction
from core.battling_dispatcher import BattlingDispatcher
from tower import card_pool, enchant_runtime, enemies, run_state, tower_map
from tower.content import SELECTABLE_FACTIONS
from tower.tower_ai import TowerAIController

from tests.helpers import make_game_state, place_card

FACTIONS = ["R", "B", "C", "BR"]


@pytest.fixture(autouse=True)
def installed():
    enchant_runtime.install()
    yield
    enchant_runtime.uninstall()


def forgotten(seed: int = 3) -> dict:
    return enemies.the_forgotten(FACTIONS, random.Random(seed))


def controller_for(boss: dict) -> TowerAIController:
    return TowerAIController(
        boss,
        run_state.effects_from_relics(boss["relics"], boss["effects"]),
        {},
    )


# --------------------------------------------------------------------------
# building the boss
# --------------------------------------------------------------------------

def test_the_forgotten_uses_factions_you_did_not_pick():
    for seed in range(10):
        boss = enemies.the_forgotten(FACTIONS, random.Random(seed))
        first = {card_pool.color_tag_of(c) for c in boss["deck"]}
        second = {card_pool.color_tag_of(c) for c in boss["next_phase"]["deck"]}
        assert len(first) == len(second) == 1
        assert first.isdisjoint(FACTIONS)
        assert second.isdisjoint(FACTIONS)
        assert first != second


def test_the_forgotten_falls_back_when_almost_everything_was_picked():
    boss = enemies.the_forgotten(list(SELECTABLE_FACTIONS), random.Random(1))
    assert boss["deck"]
    assert boss["next_phase"]["deck"]


def test_both_lords_bring_relics():
    boss = forgotten()
    assert boss["relics"]
    assert boss["next_phase"]["relics"]


def test_the_opening_squad_fields_understrength_units():
    first = enemies.weak_enemy("warriors", first=True)
    assert first["effects"] == {"unit_hp_plus": -1, "unit_damage_plus": -1}
    assert first["raw"] is True

    later = enemies.weak_enemy("warriors")
    assert later["effects"] == {}
    assert later["raw"] is False


def test_every_act_one_squad_is_a_small_white_formation():
    for key, formation in enemies.WEAK_FORMATIONS.items():
        enemy = enemies.weak_enemy(key)
        assert enemy["deck"] == list(formation["deck"])
        assert 6 <= len(enemy["deck"]) <= 7
        assert all(code.endswith("W") for code in enemy["deck"])
        assert enemy["relics"] == []


def test_an_act_fields_each_squad_at_most_once():
    for act in (1, 2, 3):
        for seed in range(30):
            formations = [e["formation"] for e in enemies_of(act, seed)
                          if e["kind"] == "weak"]
            assert len(formations) == len(set(formations))


def test_the_act_one_boss_is_a_white_lord_with_one_relic():
    for seed in range(20):
        boss = enemies.white_lord(random.Random(seed))
        assert boss["label"] == "White Lord"
        assert boss["effects"] == {}
        assert len(boss["relics"]) == 1
        assert boss["relics"][0] in enemies.LORD_RANDOM_RELIC_POOL
        assert len(boss["deck"]) == 12
        assert all(code.endswith("W") for code in boss["deck"])


def test_the_white_lord_fields_the_whole_faction():
    from tower import card_pool

    boss = enemies.white_lord(random.Random(1))
    jobs = {card_pool.job_of(code) for code in boss["deck"]}
    assert jobs == {"ADC", "AP", "TANK", "HF", "LF", "ASS", "APT", "SP"}


def test_which_relic_the_white_lord_carries_varies():
    seen = {enemies.white_lord(random.Random(seed))["relics"][0]
            for seed in range(40)}
    assert len(seen) > 1


def enemies_of(act: int, seed: int) -> list[dict]:
    out: list[dict] = []
    act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
    for layer in act_map["layers"]:
        if "enemy" in layer:
            out.append(layer["enemy"])
        out += [o["enemy"] for o in layer.get("options", []) if "enemy" in o]
    return out


def test_no_enemy_anywhere_gets_a_global_stat_buff():
    """Difficulty is relics and AI skill only - never bigger numbers."""
    for act in (1, 2, 3):
        for seed in range(10):
            for enemy in enemies_of(act, seed):
                effects = enemy["effects"]
                assert effects.get("unit_hp_plus", 0) <= 0
                assert effects.get("unit_damage_plus", 0) <= 0
                assert effects.get("hand_plus", 0) <= 0
                assert effects.get("luck_plus", 0) <= 0
                phase = enemy.get("next_phase")
                if phase:
                    assert phase["effects"] == {}


def test_only_the_opening_squad_is_debuffed():
    for act in (1, 2, 3):
        for seed in range(10):
            for enemy in enemies_of(act, seed):
                if enemy["effects"]:
                    assert enemy.get("raw") is True


def test_elites_carry_relics_instead_and_more_of_them_later():
    for seed in range(10):
        for act in (2, 3):
            elite = enemies.elite_enemy(act, FACTIONS, random.Random(seed))
            assert elite["effects"] == {}
            assert len(elite["relics"]) == enemies.ELITE_RELIC_COUNT[act]


def test_relic_counts_climb_with_the_acts():
    assert enemies.NORMAL_RELIC_COUNT[1] == 0
    assert enemies.ELITE_RELIC_COUNT[1] == 0
    for counts in (enemies.NORMAL_RELIC_COUNT, enemies.ELITE_RELIC_COUNT):
        assert counts[1] < counts[2] < counts[3]
    for act in (2, 3):
        assert enemies.ELITE_RELIC_COUNT[act] > enemies.NORMAL_RELIC_COUNT[act]


def test_regular_warbands_start_carrying_relics_from_act_two():
    for seed in range(10):
        assert enemies.normal_enemy(1, FACTIONS, random.Random(seed))["relics"] == []
        for act in (2, 3):
            enemy = enemies.normal_enemy(act, FACTIONS, random.Random(seed))
            assert len(enemy["relics"]) == enemies.NORMAL_RELIC_COUNT[act]


def test_an_enemy_never_holds_two_relics_of_the_same_group():
    from tower.content import RELICS
    for act in (2, 3):
        for seed in range(40):
            for enemy in (enemies.normal_enemy(act, FACTIONS, random.Random(seed)),
                          enemies.elite_enemy(act, FACTIONS, random.Random(seed))):
                groups = [RELICS[r].get("group") for r in enemy["relics"]]
                groups = [g for g in groups if g]
                assert len(groups) == len(set(groups))
                assert len(enemy["relics"]) == len(set(enemy["relics"]))


def test_enemy_relics_are_ones_an_ai_can_actually_use():
    from tower.content import RELICS
    for relic_id in enemies.ENEMY_RELIC_POOL:
        assert relic_id in RELICS
        assert RELICS[relic_id]["tier"] != "curse"
        # nothing that only pays out between battles
        assert not (set(RELICS[relic_id].get("effects", {})) & {
            "gold_mult", "shop_discount", "gold_per_floor", "interest_rate",
            "free_rerolls", "credit_limit", "bench_plus", "deck_limit_override"})


def test_faction_locked_relics_only_reach_the_right_enemies():
    from tower.content import RELICS
    for act in (2, 3):
        for seed in range(30):
            enemy = enemies.elite_enemy(act, ["R", "B", "C", "BR"], random.Random(seed))
            for relic_id in enemy["relics"]:
                faction = RELICS[relic_id].get("faction")
                if faction:
                    assert faction in {card_pool.color_tag_of(c)
                                       for c in enemy["deck"]}


# --------------------------------------------------------------------------
# act 3 enchanted units
# --------------------------------------------------------------------------

def enchanted_count(deck) -> int:
    return sum(1 for code in deck if card_code.is_enchanted(code))


def test_only_act_three_fields_enchanted_units():
    for seed in range(20):
        for act in (1, 2):
            for enemy in enemies_of(act, seed):
                assert enchanted_count(enemy["deck"]) == 0


def test_act_three_enemies_bring_enchanted_units():
    for seed in range(20):
        for enemy in enemies_of(3, seed):
            expected = enemies.ENCHANTED_UNIT_COUNT[enemy["kind"]]
            assert enchanted_count(enemy["deck"]) == expected


def test_enemy_enchantments_are_ones_an_ai_can_use():
    from tower.content import ENCHANTS
    for key in enemies.ENEMY_ENCHANTS:
        assert key in ENCHANTS
        assert ENCHANTS[key]["kind"] != "curse"
    # a unit that cannot attack or that evaporates is no use to the tower
    assert "gigantism" not in enemies.ENEMY_ENCHANTS
    assert "ghost" not in enemies.ENEMY_ENCHANTS


def test_an_enchanted_enemy_unit_carries_exactly_one_enchantment():
    for seed in range(20):
        for enemy in enemies_of(3, seed):
            for code in enemy["deck"]:
                assert len(card_code.enchant_keys(code)) <= 1


def test_spells_in_an_enemy_deck_are_left_alone():
    for seed in range(20):
        for enemy in enemies_of(3, seed):
            for code in enemy["deck"]:
                if card_pool.is_magic(code):
                    assert not card_code.is_enchanted(code)


def test_both_forgotten_lords_field_enchanted_units():
    boss = forgotten(5)
    assert enchanted_count(boss["deck"]) == enemies.ENCHANTED_UNIT_COUNT["boss"]
    assert enchanted_count(boss["next_phase"]["deck"]) == \
        enemies.ENCHANTED_UNIT_COUNT["boss"]


def test_every_enemy_relic_is_a_real_relic():
    from tower.content import RELICS
    for act in (1, 2, 3):
        for seed in range(10):
            for enemy in enemies_of(act, seed):
                for relic_id in enemy.get("relics", []):
                    assert relic_id in RELICS
                for relic_id in (enemy.get("next_phase") or {}).get("relics", []):
                    assert relic_id in RELICS


def test_act_three_only_rolls_finished_bosses():
    seen = set()
    for seed in range(30):
        boss = enemies.act_boss(3, FACTIONS, random.Random(seed))
        seen.add(boss["label"])
    assert seen <= {"Traitor Lord", "The Forgotten"}


# --------------------------------------------------------------------------
# the phase change
# --------------------------------------------------------------------------

def test_beating_the_first_lord_resets_the_score_instead_of_winning():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()
    game_state.player2.deck = list(boss["deck"])
    game_state.score = -10

    assert controller.on_defeat(game_state, "player1") is True
    assert game_state.score == 0
    assert game_state.player2.deck == boss["next_phase"]["deck"]


def test_the_second_lord_inherits_the_board_and_hand():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()
    game_state.player2.hand = ["TANKW", "HEAL"]
    unit = place_card(game_state, "TANKW", "player2", 1, 1)

    controller.on_defeat(game_state, "player1")

    assert unit in game_state.player2.on_board
    assert len(game_state.player2.hand) == 2 + 3
    for code in game_state.player2.hand[:2]:
        assert card_code.has_enchant(code, "borrowed")


def test_the_old_lords_cards_never_reach_the_discard_pile():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()
    unit = place_card(game_state, "TANKW", "player2", 1, 1)

    controller.on_defeat(game_state, "player1")
    unit.health = 0

    class _Sink:
        dying_cards: list = []

    game_state.player2.recycle_cards(game_state, _Sink())
    assert game_state.player2.discard_pile.count("TANKW") == 0
    assert "TANKW*borrowed" not in game_state.player2.discard_pile


def test_a_borrowed_card_still_stays_in_hand_between_turns():
    game_state = make_game_state()
    game_state.player2.hand = ["TANKW*borrowed", "HEAL*ghost"]
    game_state.player2.turn_end(game_state)
    assert game_state.player2.hand == ["TANKW*borrowed"]


def test_the_second_lord_gets_a_fresh_draw_and_an_extra_attack():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()

    controller.on_defeat(game_state, "player1")
    assert len(game_state.player2.hand) == 3
    assert game_state.number_of_attacks["player2"] == 1
    assert all(card_pool.color_tag_of(c) ==
               card_pool.color_tag_of(boss["next_phase"]["deck"][0])
               for c in game_state.player2.hand)


def test_the_second_lord_brings_their_own_strategy_and_relics():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()
    before = controller.enemy.effects

    controller.on_defeat(game_state, "player1")
    assert controller.stage == boss["next_phase"]["strategy"]
    assert controller.enemy.effects is not before
    assert game_state.tower_min_damage["player2"] >= 0


def test_there_is_no_third_phase():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()

    assert controller.on_defeat(game_state, "player1") is True
    assert controller.on_defeat(game_state, "player1") is False


def test_losing_to_the_first_lord_ends_the_battle():
    boss = forgotten()
    controller = controller_for(boss)
    game_state = make_game_state()
    assert controller.on_defeat(game_state, "player2") is False


def test_a_single_phase_boss_is_unaffected():
    boss = enemies.traitor_lord(random.Random(1))
    controller = controller_for(boss)
    game_state = make_game_state()
    assert controller.on_defeat(game_state, "player1") is False


# --------------------------------------------------------------------------
# the dispatcher side of it
# --------------------------------------------------------------------------

def test_the_dispatcher_keeps_playing_when_the_hook_says_so():
    game_state = make_game_state()
    game_state.player1.deck = ["TANKW"] * 6
    game_state.player1.discard_pile = ["TANKW"] * 6
    game_state.player2.deck = ["TANKW"] * 6
    game_state.player2.discard_pile = ["TANKW"] * 6
    game_state.score = -game_state.win_threshold

    calls = []

    def survives(gs, winner):
        calls.append(winner)
        gs.score = 0
        return True

    game_state.tower_on_defeat = survives
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")
    result = dispatcher.dispatch(
        GameAction(player="player1", action_type="end_turn"), game_state)

    assert calls == ["player1"]
    assert result.quit is False
    assert result.end_turn is True


def test_the_dispatcher_still_ends_the_battle_without_a_hook():
    game_state = make_game_state()
    game_state.player1.deck = ["TANKW"] * 6
    game_state.player2.deck = ["TANKW"] * 6
    game_state.score = -game_state.win_threshold

    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")
    result = dispatcher.dispatch(
        GameAction(player="player1", action_type="end_turn"), game_state)

    assert result.quit is True
    assert result.message == "player1"
