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
    first = enemies.weak_enemy(random.Random(1), 0)
    assert first["effects"] == {"unit_hp_plus": -1, "unit_damage_plus": -1}

    for index in (1, 2):
        assert enemies.weak_enemy(random.Random(1), index)["effects"] == {}


def test_the_act_one_boss_gets_relics_but_no_stat_boost():
    boss = enemies.head_instructor(random.Random(1))
    assert boss["effects"] == {}
    assert set(boss["relics"]) == {"dorans_shield", "prepared_pack"}

    effects = run_state.effects_from_relics(boss["relics"], boss["effects"])
    assert effects["first_unit_hp_plus"] == 2
    assert effects["hand_plus"] == 1
    assert "unit_hp_plus" not in effects
    assert "unit_damage_plus" not in effects


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
                    assert enemy["label"] == "Raw Recruits"


def test_elites_carry_relics_instead_and_more_of_them_later():
    for seed in range(10):
        for act in (2, 3):
            elite = enemies.elite_enemy(act, FACTIONS, random.Random(seed))
            assert elite["effects"] == {}
            assert len(elite["relics"]) == enemies.ELITE_RELIC_COUNT[act]


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
