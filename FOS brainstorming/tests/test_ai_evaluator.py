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

from campaign import ai_evaluator
from cards.card_white import Adc, Tank, Ass, Sp
from tests.helpers import make_game_state, place_card


def test_parse_card_name_white_adc():
    job, color = ai_evaluator.parse_card_name("ADCW")
    assert job == "ADC"
    assert color == "White"


def test_parse_card_name_unknown_returns_empty():
    job, color = ai_evaluator.parse_card_name("HEAL")
    assert job == ""
    assert color == ""


def test_card_base_stats_returns_health_damage():
    health, damage = ai_evaluator.card_base_stats("ADCW")
    assert health > 0
    assert damage > 0


def test_evaluate_placement_rejects_occupied_position():
    gs = make_game_state()
    place_card(gs, Tank, "player1", 1, 1)
    score = ai_evaluator.evaluate_placement("ADCW", (1, 1), gs, "player2")
    assert score < 0


def test_evaluate_placement_rejects_out_of_bounds():
    gs = make_game_state()
    score = ai_evaluator.evaluate_placement("ADCW", (5, 5), gs, "player2")
    assert score < 0


def test_evaluate_placement_sp_prefers_corner_far_from_enemies():
    gs = make_game_state()
    place_card(gs, Adc, "player1", 0, 0)
    corner_far = ai_evaluator.evaluate_placement("SPW", (3, 3), gs, "player2")
    center = ai_evaluator.evaluate_placement("SPW", (2, 2), gs, "player2")
    assert corner_far > center


def test_evaluate_placement_tank_prefers_near_enemies():
    gs = make_game_state()
    place_card(gs, Adc, "player1", 0, 0)
    near = ai_evaluator.evaluate_placement("TANKW", (1, 0), gs, "player2")
    far = ai_evaluator.evaluate_placement("TANKW", (3, 3), gs, "player2")
    assert near > far


def test_evaluate_attack_returns_zero_if_no_targets():
    gs = make_game_state()
    attacker = place_card(gs, Tank, "player1", 0, 0)
    attacker.numbness = False
    place_card(gs, Tank, "player2", 3, 3)
    score, target = ai_evaluator.evaluate_attack(attacker, gs)
    assert score <= 0
    assert target is None


def test_evaluate_attack_returns_negative_for_numb_attacker():
    gs = make_game_state()
    attacker = place_card(gs, Adc, "player1", 1, 1)
    place_card(gs, Tank, "player2", 1, 2)
    score, target = ai_evaluator.evaluate_attack(attacker, gs)
    assert score < 0


def test_evaluate_attack_rewards_kill():
    gs = make_game_state()
    attacker = place_card(gs, Adc, "player1", 1, 1)
    attacker.numbness = False
    victim = place_card(gs, Ass, "player2", 1, 2)
    score, target = ai_evaluator.evaluate_attack(attacker, gs)
    assert score > 100
    assert target is victim


def test_evaluate_attack_picks_higher_threat_target_when_tie_in_damage():
    gs = make_game_state()
    attacker = place_card(gs, Adc, "player1", 1, 1)
    attacker.numbness = False
    weak = place_card(gs, Tank, "player2", 0, 1)
    weak.numbness = False
    strong = place_card(gs, Adc, "player2", 1, 0)
    strong.numbness = False
    score, target = ai_evaluator.evaluate_attack(attacker, gs)
    assert target is strong
    assert score > 0
    _ = weak


def test_lethal_placement_bonus_for_ass_adjacent_to_killable_enemy():
    """ASS deploys non-numb, so placing it next to a killable enemy enables a same-turn kill."""
    gs = make_game_state()
    victim = place_card(gs, Adc, "player1", 2, 2)
    victim.numbness = False

    score = ai_evaluator.lethal_placement_bonus("ASSW", (1, 1), gs, "player2")
    assert score >= 100.0


def test_lethal_placement_bonus_zero_when_not_in_range():
    gs = make_game_state()
    place_card(gs, Adc, "player1", 0, 0)
    score = ai_evaluator.lethal_placement_bonus("ASSW", (3, 3), gs, "player2")
    assert score == 0.0


def test_lethal_placement_bonus_zero_for_numb_on_deploy_cards():
    """ADC/TANK/HF/LF deploy numb — they can't attack same turn, so no lethal bonus."""
    gs = make_game_state()
    victim = place_card(gs, Ass, "player1", 1, 1)
    victim.numbness = False
    victim.health = 1

    for card_name in ("ADCW", "TANKW", "HFW", "LFW", "APTW"):
        score = ai_evaluator.lethal_placement_bonus(card_name, (1, 2), gs, "player2")
        assert score == 0.0, f"{card_name} should not get lethal bonus on deploy"


def test_defensive_placement_bonus_blocks_ass_kill_spot():
    gs = make_game_state()
    place_card(gs, Adc, "player2", 3, 0)
    bonus = ai_evaluator.defensive_placement_bonus("TANKW", (2, 1), gs, "player2")
    assert bonus > 0


def test_defensive_placement_bonus_zero_for_unrelated_position():
    gs = make_game_state()
    place_card(gs, Adc, "player2", 3, 0)
    bonus = ai_evaluator.defensive_placement_bonus("TANKW", (0, 3), gs, "player2")
    assert bonus == 0.0


def test_defensive_placement_bonus_sums_when_blocking_saves_multiple():
    """One cell can be the kill spot for two diagonally-placed friendlies."""
    gs = make_game_state()
    place_card(gs, Adc, "player2", 1, 0)
    place_card(gs, Adc, "player2", 1, 2)
    # ASS at (2, 1) small_x would hit (1, 0), (3, 0), (1, 2), (3, 2) — both ADCs threatened
    one = ai_evaluator.defensive_placement_bonus("TANKW", (2, 1), gs, "player2")
    gs2 = make_game_state()
    place_card(gs2, Adc, "player2", 1, 0)
    single = ai_evaluator.defensive_placement_bonus("TANKW", (2, 1), gs2, "player2")
    assert one > single


def test_ai_picks_blocker_over_safe_corner_when_adc_is_threatened():
    """User scenario: AI's corner ADC is one ASS-deploy away from death. Block (2,1)."""
    gs = make_game_state()
    place_card(gs, Adc, "player2", 3, 0)

    block_spot = ai_evaluator.evaluate_placement("TANKW", (2, 1), gs, "player2")
    safe_corner = ai_evaluator.evaluate_placement("TANKW", (0, 3), gs, "player2")
    assert block_spot > safe_corner


def test_threat_placement_bonus_rewards_having_targets_in_range():
    gs = make_game_state()
    place_card(gs, Adc, "player1", 0, 0)
    in_range = ai_evaluator.threat_placement_bonus("ASSW", (1, 1), gs, "player2")
    no_targets = ai_evaluator.threat_placement_bonus("ASSW", (3, 3), gs, "player2")
    assert in_range > no_targets


def test_estimate_score_per_turn_normal_unit():
    assert ai_evaluator.estimate_score_per_turn("ADCW") == 1
    assert ai_evaluator.estimate_score_per_turn("TANKW") == 1
    assert ai_evaluator.estimate_score_per_turn("ASSW") == 1


def test_estimate_score_per_turn_sp_uses_extra_score():
    """White SP has extra_score=1, so scores 2 points per turn."""
    assert ai_evaluator.estimate_score_per_turn("SPW") == 2


def test_estimate_score_per_turn_zero_for_neutrals_and_spells():
    assert ai_evaluator.estimate_score_per_turn("CUBE") == 0
    assert ai_evaluator.estimate_score_per_turn("HEAL") == 0
    assert ai_evaluator.estimate_score_per_turn("MOVE") == 0


def test_score_income_bonus_higher_for_sp():
    assert ai_evaluator.score_income_bonus("SPW") > ai_evaluator.score_income_bonus("ADCW")


def test_evaluate_attack_kill_bonus_higher_for_sp_than_equal_damage_unit():
    """Killing SP denies 2 pts/turn, killing a same-damage non-scorer denies 1."""
    gs = make_game_state()
    attacker = place_card(gs, Adc, "player1", 1, 1)
    attacker.numbness = False
    sp_target = place_card(gs, Sp, "player2", 1, 0)
    sp_target.numbness = False
    sp_score, _ = ai_evaluator.evaluate_attack(attacker, gs)

    gs2 = make_game_state()
    attacker2 = place_card(gs2, Adc, "player1", 1, 1)
    attacker2.numbness = False
    ass_target = place_card(gs2, Ass, "player2", 1, 0)
    ass_target.numbness = False
    ass_target.damage = 5  # same damage as SP for fair comparison
    ass_score, _ = ai_evaluator.evaluate_attack(attacker2, gs2)

    assert sp_score > ass_score


def test_evaluate_placement_sp_outscores_equivalent_unit_for_score_income():
    """At the same safe corner, SP should beat a stat-equivalent unit because of score income."""
    gs = make_game_state()
    sp_score = ai_evaluator.evaluate_placement("SPW", (0, 0), gs, "player2")
    ass_score = ai_evaluator.evaluate_placement("ASSW", (3, 3), gs, "player2")
    assert sp_score > ass_score


def test_protection_bonus_penalizes_unprotected_squishy_dps():
    """No tank on board → ADC/SP/AP get a penalty for deploying naked."""
    gs = make_game_state()
    assert ai_evaluator.protection_bonus("ADCW", gs, "player2") < 0
    assert ai_evaluator.protection_bonus("SPW",  gs, "player2") < 0
    assert ai_evaluator.protection_bonus("APW",  gs, "player2") < 0


def test_protection_bonus_rewards_dps_with_front_line():
    """A friendly TANK / HF / LF on board flips the penalty into a bonus."""
    gs = make_game_state()
    place_card(gs, "TANKW", "player2", 0, 0)
    assert ai_evaluator.protection_bonus("ADCW", gs, "player2") > 0


def test_protection_bonus_zero_for_tank_class():
    """TANK / HF / LF aren't gated by the front-line check."""
    gs = make_game_state()
    assert ai_evaluator.protection_bonus("TANKW", gs, "player2") == 0.0
    assert ai_evaluator.protection_bonus("HFW",   gs, "player2") == 0.0
    assert ai_evaluator.protection_bonus("LFW",   gs, "player2") == 0.0


def test_strategy_prefers_tank_over_adc_on_empty_board():
    """First placement of the game with both options in hand: TANK should win
    so that ADC waits for the front line."""
    from campaign.ai_strategies.white import WhiteStrategy
    s = WhiteStrategy()
    gs = make_game_state()
    gs.player2.hand = ["ADCW", "TANKW"]
    best = s.best_placement(gs, "player2")
    assert best is not None
    assert best.card_name == "TANKW"


def test_strategy_releases_adc_after_tank_is_down():
    """After the front line is established, ADC placement clears the penalty."""
    from campaign.ai_strategies.white import WhiteStrategy
    s = WhiteStrategy()
    gs = make_game_state()
    place_card(gs, "TANKW", "player2", 0, 0)
    gs.player2.hand = ["ADCW"]
    best = s.best_placement(gs, "player2")
    assert best is not None
    assert best.card_name == "ADCW"


def test_future_ass_threat_penalty_scales_with_empty_diagonal_neighbors():
    """ADCW (5 HP, killable by ASS) at center has 4 empty small_x neighbors
    (each is a kill-spot opponent can deploy ASS at) — penalty quadruples
    compared to a corner where only one such cell exists."""
    gs = make_game_state()
    center = ai_evaluator.future_ass_threat_penalty("ADCW", (1, 1), gs)
    corner = ai_evaluator.future_ass_threat_penalty("ADCW", (0, 0), gs)
    assert center < corner  # both negative; center is more negative
    assert center < 0
    assert corner < 0


def test_future_ass_threat_zero_for_high_hp_units():
    """HF (9 HP), TANK (15 HP), LF (>5 HP) survive a 5-damage ASS swing — no penalty."""
    gs = make_game_state()
    assert ai_evaluator.future_ass_threat_penalty("HFW", (1, 1), gs) == 0.0
    assert ai_evaluator.future_ass_threat_penalty("TANKW", (1, 1), gs) == 0.0
    assert ai_evaluator.future_ass_threat_penalty("LFW", (1, 1), gs) == 0.0


def test_future_ass_threat_zero_when_diagonal_neighbors_occupied():
    """If all small_x adjacent cells are filled (no ASS deploy slot), no threat."""
    gs = make_game_state()
    for x, y in ((0, 0), (2, 0), (0, 2), (2, 2)):
        place_card(gs, "TANKW", "player1", x, y)
    assert ai_evaluator.future_ass_threat_penalty("ADCW", (1, 1), gs) == 0.0


def test_adcw_placement_prefers_corner_over_center_under_ass_threat():
    """The classic user complaint: AI placed ADCW in the open. With the threat
    penalty, corners (1 vulnerable cell) clearly beat center (4 vulnerable cells)."""
    gs = make_game_state()
    corner = ai_evaluator.evaluate_placement("ADCW", (0, 0), gs, "player2")
    center = ai_evaluator.evaluate_placement("ADCW", (1, 1), gs, "player2")
    assert corner > center


def test_hf_placement_prefers_center_over_corner_due_to_reach():
    """HF (small_cross + small_x) covers 8 cells in center vs 3 in corner — center wins."""
    gs = make_game_state()
    corner = ai_evaluator.evaluate_placement("HFW", (0, 0), gs, "player2")
    center = ai_evaluator.evaluate_placement("HFW", (1, 1), gs, "player2")
    assert center > corner


def test_reach_bonus_zero_for_nearest_attackers():
    """SP/AP/APT shouldn't get a reach bonus — their range is enemy-dependent."""
    gs = make_game_state()
    assert ai_evaluator.reach_bonus("SPW", (0, 0), gs) == 0.0
    assert ai_evaluator.reach_bonus("APW", (1, 1), gs) == 0.0


def test_evaluate_placement_avoids_immediate_kill_spot():
    """If opponent's existing attackers can wipe out the placement, score gets a big hit."""
    gs = make_game_state()
    enemy = place_card(gs, Adc, "player1", 1, 1)
    enemy.numbness = False
    gs.number_of_attacks["player1"] = 1
    # Player2 places ASS at (0, 1) — in enemy ADC's large_cross range (5 dmg vs ASS 2 HP = dead)
    unsafe = ai_evaluator.evaluate_placement("ASSW", (0, 1), gs, "player2")
    safe = ai_evaluator.evaluate_placement("ASSW", (3, 3), gs, "player2")
    assert safe > unsafe


def test_hand_threat_penalty_applies_to_ass():
    assert ai_evaluator.hand_threat_penalty("ASSW") < 0
    assert ai_evaluator.hand_threat_penalty("TANKW") == 0


def test_ass_placement_without_kill_or_defense_skipped_after_threshold():
    """ASS deployed only for value (kill / defense). A generic placement should fall under threshold."""
    gs = make_game_state()
    # No friendly to defend, no enemy in attack range — ASS placement is just a stat-dump.
    score = ai_evaluator.evaluate_placement("ASSW", (0, 0), gs, "player2")
    assert score < 1.0  # below the controller's placement_min_score


def test_evaluate_placement_ass_lethal_outscores_safe_corner_placement():
    """AI should prefer placing ASS where it kills now over placing it safely far away."""
    gs = make_game_state()
    victim = place_card(gs, Adc, "player1", 0, 0)
    victim.numbness = False

    lethal_spot = ai_evaluator.evaluate_placement("ASSW", (1, 1), gs, "player2")
    safe_corner = ai_evaluator.evaluate_placement("ASSW", (3, 3), gs, "player2")
    assert lethal_spot > safe_corner
    assert lethal_spot >= 100.0
