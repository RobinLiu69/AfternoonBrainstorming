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

import pytest

from cards.factory import CardFactory
from campaign import ai_evaluator


def _card(name: str):
    class _Stub:
        pass
    obj = _Stub()
    obj.job_and_color = name
    return obj
from campaign.ai_controller import AIController
from campaign.ai_strategies.red import RedStrategy
from campaign.ai_strategies.blue import BlueStrategy
from campaign.ai_strategies.green import GreenStrategy
from campaign.ai_strategies.orange import OrangeStrategy
from campaign.ai_strategies.boss import BossStrategy
from tests.helpers import make_game_state, place_card


@pytest.mark.parametrize("stage", ["white", "red", "blue", "green", "orange", "boss"])
def test_every_stage_constructs_controller(stage):
    ai = AIController(stage)
    assert ai.strategy is not None


def test_red_apr_attack_bonus_scales_with_target_damage():
    s = RedStrategy()
    gs = make_game_state()
    apr = place_card(gs, "APR", "player2", 1, 1)
    apr.numbness = False
    weak = place_card(gs, "TANKW", "player1", 0, 0)
    weak_score = s.attack_bonus(apr, gs, 10.0)

    gs2 = make_game_state()
    apr2 = place_card(gs2, "APR", "player2", 1, 1)
    apr2.numbness = False
    strong = place_card(gs2, "ADCW", "player1", 0, 0)
    strong_score = s.attack_bonus(apr2, gs2, 10.0)
    assert strong_score > weak_score


def test_panic_threshold_floor_skips_low_value_chips_when_behind():
    from campaign.ai_controller import AIController, MIN_PANIC_THRESHOLD
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    gs.score = -10
    assert ai._effective_attack_min(gs) == MIN_PANIC_THRESHOLD


def test_panic_threshold_does_not_block_lethal_attacks():
    from campaign.ai_controller import AIController, MIN_PANIC_THRESHOLD, LETHAL_SCORE_THRESHOLD
    ai = AIController("white", player_name="player2")
    assert MIN_PANIC_THRESHOLD < LETHAL_SCORE_THRESHOLD


def test_evaluate_attack_aggregate_disabled_for_nearest_pattern():
    gs = make_game_state()
    ap = place_card(gs, "APW", "player2", 1, 1)
    ap.numbness = False
    for x, y in ((0, 0), (2, 0), (0, 2)):
        e = place_card(gs, "ASSW", "player1", x, y)
        e.numbness = False
        e.health = 1
    score, _ = ai_evaluator.evaluate_attack(ap, gs)
    assert score < 250.0


def test_evaluate_attack_aggregate_active_for_aoe_pattern():
    gs = make_game_state()
    hfw = place_card(gs, "HFW", "player2", 1, 1)
    hfw.numbness = False
    for x, y in ((0, 0), (1, 0), (2, 1)):
        e = place_card(gs, "ASSW", "player1", x, y)
        e.numbness = False
        e.health = 1
    score, _ = ai_evaluator.evaluate_attack(hfw, gs)
    assert score >= 250.0


def test_evaluate_attack_aggregates_multi_kill_bonus():
    gs1 = make_game_state()
    adc1 = place_card(gs1, "ADCW", "player2", 1, 1)
    adc1.numbness = False
    a = place_card(gs1, "ASSW", "player1", 1, 0)
    a.numbness = False
    a.health = 2
    single_score, _ = ai_evaluator.evaluate_attack(adc1, gs1)

    gs2 = make_game_state()
    adc2 = place_card(gs2, "ADCW", "player2", 1, 1)
    adc2.numbness = False
    a2 = place_card(gs2, "ASSW", "player1", 1, 0)
    a2.numbness = False
    a2.health = 2
    b2 = place_card(gs2, "ASSW", "player1", 0, 1)
    b2.numbness = False
    b2.health = 2
    multi_score, _ = ai_evaluator.evaluate_attack(adc2, gs2)
    assert multi_score >= single_score + 80.0


def test_green_hfg_attack_bonus_scales_with_block_count():
    from campaign.ai_strategies.green import GreenStrategy
    from cards.factory import CardFactory
    s = GreenStrategy()
    gs = make_game_state()
    hfg = place_card(gs, "HFG", "player2", 1, 1)
    one_score = s.attack_bonus(hfg, gs, 10.0)
    for x, y in ((2, 1), (0, 1), (1, 0)):
        gs.neutral.on_board.append(CardFactory.create("LUCKYBLOCK", "neutral", x, y))
    three_score = s.attack_bonus(hfg, gs, 10.0)
    assert three_score >= one_score + 60.0


def test_green_lfg_attack_bonus_scales_with_block_count():
    from campaign.ai_strategies.green import GreenStrategy
    from cards.factory import CardFactory
    s = GreenStrategy()
    gs = make_game_state()
    lfg = place_card(gs, "LFG", "player2", 1, 1)
    one_score = s.attack_bonus(lfg, gs, 10.0)
    for x, y in ((2, 1), (0, 1), (1, 0)):
        gs.neutral.on_board.append(CardFactory.create("LUCKYBLOCK", "neutral", x, y))
    three_score = s.attack_bonus(lfg, gs, 10.0)
    assert three_score >= one_score + 90.0


def test_red_attack_bonus_rewards_damage_growth():
    s = RedStrategy()
    gs = make_game_state()
    adc = place_card(gs, "ADCR", "player2", 0, 0)
    fresh = s.attack_bonus(adc, gs, 10.0)
    adc.damage += 3
    ramped = s.attack_bonus(adc, gs, 10.0)
    assert ramped >= fresh + 15.0


def test_red_strategy_prefers_hfr_over_tankr():
    s = RedStrategy()
    gs = make_game_state()
    tankr = place_card(gs, "TANKR", "player2", 0, 0)
    hfr = place_card(gs, "HFR", "player2", 1, 0)
    assert s.attack_bonus(hfr, gs, 5.0) > s.attack_bonus(tankr, gs, 5.0)


def test_red_hfr_anger_attack_gets_huge_bonus():
    s = RedStrategy()
    gs = make_game_state()
    hfr = place_card(gs, "HFR", "player2", 1, 1)
    no_anger = s.attack_bonus(hfr, gs, 10.0)
    hfr.anger = True
    angered = s.attack_bonus(hfr, gs, 10.0)
    assert angered >= no_anger + 20.0


def test_orange_asso_anger_attack_outranks_idle_attack():
    from campaign.ai_strategies.orange import OrangeStrategy
    s = OrangeStrategy()
    gs = make_game_state()
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    fresh = s.attack_bonus(asso, gs, 10.0)
    asso.anger = True
    angered = s.attack_bonus(asso, gs, 10.0)
    assert angered >= fresh + 18.0


def test_evaluator_skips_suicide_penalty_for_anger_hfr_attacker():
    gs = make_game_state()
    hfr = place_card(gs, "HFR", "player2", 1, 1)
    hfr.numbness = False
    hfr.health = 3
    danger = place_card(gs, "ADCW", "player1", 2, 2)
    danger.numbness = False
    danger.damage = 5

    score_no_anger, _ = ai_evaluator.evaluate_attack(hfr, gs)
    hfr.anger = True
    score_with_anger, _ = ai_evaluator.evaluate_attack(hfr, gs)
    assert score_with_anger > score_no_anger


def test_evaluator_doesnt_count_kill_on_anger_hfr_target():
    gs = make_game_state()
    attacker = place_card(gs, "ADCW", "player2", 1, 1)
    attacker.numbness = False
    enemy_hfr = place_card(gs, "HFR", "player1", 1, 2)
    enemy_hfr.numbness = False
    enemy_hfr.health = 1
    no_anger_score, _ = ai_evaluator.evaluate_attack(attacker, gs)
    enemy_hfr.anger = True
    anger_score, _ = ai_evaluator.evaluate_attack(attacker, gs)
    assert no_anger_score >= anger_score + 80


def test_adcb_placement_bonus_scales_with_token_engines():
    s = BlueStrategy()
    gs = make_game_state()
    lone = s.placement_bonus("ADCB", (0, 0), gs, "player2", 10.0)

    gs2 = make_game_state()
    place_card(gs2, "APB", "player2", 1, 1)
    place_card(gs2, "LFB", "player2", 2, 2)
    place_card(gs2, "TANKB", "player2", 3, 3)
    with_engines = s.placement_bonus("ADCB", (0, 0), gs2, "player2", 10.0)
    assert with_engines >= lone + 10.0


def test_apb_swing_with_armed_adcb_gets_chain_bonus():
    s = BlueStrategy()
    gs = make_game_state()
    gs.players_token["player2"] = 1
    gs.tokens_to_draw_a_card = 3
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 2)
    no_adcb = s.attack_bonus(apb, gs, 10.0)

    armed_adcb = place_card(gs, "ADCB", "player2", 0, 0)
    armed_adcb.numbness = False
    with_adcb = s.attack_bonus(apb, gs, 10.0)
    assert with_adcb >= no_adcb + 10.0


def test_numb_adcb_doesnt_arm_token_draw_chain():
    s = BlueStrategy()
    gs = make_game_state()
    gs.players_token["player2"] = 1
    gs.tokens_to_draw_a_card = 3
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 2)
    no_adcb = s.attack_bonus(apb, gs, 10.0)

    numb_adcb = place_card(gs, "ADCB", "player2", 0, 0)
    numb_adcb.numbness = True
    with_numb_adcb = s.attack_bonus(apb, gs, 10.0)
    assert with_numb_adcb == no_adcb


def test_expected_tokens_from_apb_attack_scales_with_targets():
    from campaign.ai_strategies.blue import expected_tokens_from_attack
    gs = make_game_state()
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 2)
    assert expected_tokens_from_attack(apb, gs) == 2


def test_expected_tokens_from_lfb_multi_target_attack():
    from campaign.ai_strategies.blue import expected_tokens_from_attack
    gs = make_game_state()
    lfb = place_card(gs, "LFB", "player2", 1, 1)
    lfb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 0)
    place_card(gs, "ADCW", "player1", 0, 1)
    place_card(gs, "ADCW", "player1", 2, 1)
    assert expected_tokens_from_attack(lfb, gs) == 3


def test_blue_apb_attack_outranks_adcb_for_token_economy():
    s = BlueStrategy()
    gs = make_game_state()
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    adcb = place_card(gs, "ADCB", "player2", 3, 3)
    adcb.numbness = False
    place_card(gs, "ADCW", "player1", 0, 0)
    s_apb = s.attack_bonus(apb, gs, 10.0)
    s_adcb = s.attack_bonus(adcb, gs, 10.0)
    assert s_apb > s_adcb


def test_spb_placement_deferred_when_other_units_in_hand():
    s = BlueStrategy()
    gs = make_game_state()
    place_card(gs, "ADCW", "player1", 1, 0)
    gs.player2.hand = ["SPB"]
    solo = s.placement_bonus("SPB", (0, 0), gs, "player2", 10.0)

    gs2 = make_game_state()
    place_card(gs2, "ADCW", "player1", 1, 0)
    gs2.player2.hand = ["SPB", "TANKB", "ADCB", "APB"]
    crowded = s.placement_bonus("SPB", (0, 0), gs2, "player2", 10.0)
    assert crowded < solo - 10.0


def test_blue_spb_placement_penalized_when_no_enemies():
    s = BlueStrategy()
    gs = make_game_state()
    no_enemies = s.placement_bonus("SPB", (0, 0), gs, "player2", 10.0)
    assert no_enemies <= 0
    gs2 = make_game_state()
    place_card(gs2, "ADCW", "player1", 1, 0)
    with_enemies = s.placement_bonus("SPB", (0, 0), gs2, "player2", 10.0)
    assert with_enemies > no_enemies


def test_blue_spb_attack_outranks_other_blue_attackers():
    s = BlueStrategy()
    gs = make_game_state()
    spb = place_card(gs, "SPB", "player2", 0, 0)
    adcb = place_card(gs, "ADCB", "player2", 3, 0)
    s_spb = s.attack_bonus(spb, gs, 10.0)
    s_adcb = s.attack_bonus(adcb, gs, 10.0)
    assert s_spb > s_adcb


def test_blue_spb_placement_scales_with_discard_pile():
    s = BlueStrategy()
    early = make_game_state()
    place_card(early, "ADCW", "player1", 1, 0)
    early_score = s.placement_bonus("SPB", (0, 0), early, "player2", 10.0)

    late = make_game_state()
    place_card(late, "ADCW", "player1", 1, 0)
    late.player2.discard_pile = ["TANKB"] * 5
    late_score = s.placement_bonus("SPB", (0, 0), late, "player2", 10.0)
    assert late_score > early_score


def test_blue_adcb_placement_bonus_when_token_draw_imminent():
    s = BlueStrategy()
    gs = make_game_state()
    gs.players_token["player2"] = 2
    high = s.placement_bonus("ADCB", (0, 0), gs, "player2", 10.0)
    gs.players_token["player2"] = 0
    low = s.placement_bonus("ADCB", (0, 0), gs, "player2", 10.0)
    assert high > low + 10.0


def test_blue_lfb_placement_holds_when_board_sparse():
    s = BlueStrategy()
    gs = make_game_state()
    sparse = s.placement_bonus("LFB", (0, 0), gs, "player2", 10.0)

    gs2 = make_game_state()
    place_card(gs2, "ADCW", "player1", 1, 0)
    place_card(gs2, "ADCW", "player1", 0, 1)
    rich = s.placement_bonus("LFB", (0, 0), gs2, "player2", 10.0)
    assert rich > sparse


def test_blue_attack_bonus_peaks_at_two_tokens():
    s = BlueStrategy()
    gs = make_game_state()
    adc = place_card(gs, "ADCB", "player2", 0, 0)
    gs.players_token["player2"] = 0
    base0 = s.attack_bonus(adc, gs, 10.0)
    gs.players_token["player2"] = 2
    base2 = s.attack_bonus(adc, gs, 10.0)
    assert base2 > base0


def test_green_lf_attack_bonus_when_adjacent_to_lucky_block():
    s = GreenStrategy()
    gs = make_game_state()
    lf = place_card(gs, "LFG", "player2", 1, 1)
    no_block = s.attack_bonus(lf, gs, 10.0)
    block = CardFactory.create("LUCKYBLOCK", "neutral", 2, 1)
    gs.neutral.on_board.append(block)
    with_block = s.attack_bonus(lf, gs, 10.0)
    assert with_block > no_block


def test_orange_placement_rewards_open_positions_for_movers():
    s = OrangeStrategy()
    gs = make_game_state()
    center = s.placement_bonus("ADCO", (1, 1), gs, "player2", 10.0)
    corner = s.placement_bonus("ADCO", (0, 0), gs, "player2", 10.0)
    assert center > corner


def test_boss_placement_prefers_tank_against_high_damage_opponent():
    s = BossStrategy()
    gs = make_game_state()
    adc1 = place_card(gs, "ADCW", "player1", 0, 0)
    adc1.damage = 5
    adc2 = place_card(gs, "ADCW", "player1", 0, 1)
    adc2.damage = 5
    with_tank = s.placement_bonus("TANKB", (2, 2), gs, "player2", 10.0)
    with_adc = s.placement_bonus("ADCR", (2, 2), gs, "player2", 10.0)
    assert with_tank > with_adc


def test_campaign_save_unlock_progression(tmp_path, monkeypatch):
    import campaign.campaign_save as cs
    fake_path = str(tmp_path / "campaign_progress.json")
    monkeypatch.setattr(cs, "SAVE_PATH", fake_path)

    initial = cs.load()
    assert initial["unlocked"] == ["white"]

    state = cs.mark_cleared("white")
    assert "white" in state["cleared"]
    assert "red" in state["unlocked"]
    assert cs.is_unlocked("red", state)


def test_boss_buffs_extra_hand_size():
    from campaign.boss_config import apply_initial_buffs
    gs = make_game_state()
    gs.player2.deck = ["ADCW", "ADCW", "ADCW", "ADCW", "ADCW", "ADCW"]
    gs.player2.draw_pile = gs.player2.deck.copy()
    apply_initial_buffs("boss", gs)
    assert len(gs.player2.hand) == 4


def test_boss_unit_hp_buff_is_idempotent():
    from campaign.boss_config import maintain_unit_buffs
    buffed: set[str] = set()
    gs = make_game_state()
    card = place_card(gs, "ADCW", "player2", 0, 0)
    base_hp = card.health
    maintain_unit_buffs("boss", gs, buffed)
    maintain_unit_buffs("boss", gs, buffed)
    maintain_unit_buffs("boss", gs, buffed)
    assert card.health == base_hp + 1
    assert card.instance_id in buffed


def test_boss_unit_hp_buff_applies_again_in_new_match():
    from campaign.boss_config import maintain_unit_buffs
    from cards.base import reset_instance_counter

    buffed_m1: set[str] = set()
    reset_instance_counter()
    gs1 = make_game_state()
    c1 = place_card(gs1, "ADCW", "player2", 0, 0)
    maintain_unit_buffs("boss", gs1, buffed_m1)
    assert c1.health == 5 + 1
    first_id = c1.instance_id

    buffed_m2: set[str] = set()
    reset_instance_counter()
    gs2 = make_game_state()
    c2 = place_card(gs2, "ADCW", "player2", 0, 0)
    maintain_unit_buffs("boss", gs2, buffed_m2)
    assert c2.health == 5 + 1
    assert c2.instance_id == first_id


def test_ai_controller_runs_initial_buffs_when_board_ready():
    from campaign.ai_controller import AIController
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    gs.player2.draw_pile = ["ADCW"] * 6
    gs.player2.hand = ["ADCW", "ADCW", "ADCW"]
    ai.tick(gs, 0)
    assert ai._initialized
    assert len(gs.player2.hand) == 4


def test_green_stage_boosts_ai_initial_luck():
    from campaign.boss_config import apply_stage_one_shots
    gs = make_game_state()
    assert gs.players_luck["player2"] == 50
    apply_stage_one_shots("green", gs)
    assert gs.players_luck["player2"] == 65
    assert gs.players_luck["player1"] == 50


def test_per_turn_buffs_grant_free_moves_to_orange():
    from campaign.boss_config import apply_per_turn_buffs
    gs = make_game_state()
    initial = gs.number_of_movings.get("player2", 0)

    gs.turn_number = 1
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial

    gs.turn_number = 3
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial

    gs.turn_number = 5
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 1

    gs.turn_number = 7
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 1

    gs.turn_number = 11
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 2

    gs.turn_number = 10
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 2


def test_per_turn_heal_buff_fires_every_5_ai_turns_for_boss():
    from campaign.boss_config import apply_per_turn_buffs
    gs = make_game_state()
    initial = gs.number_of_heals.get("player2", 0)
    for turn in (1, 3, 5, 7):
        gs.turn_number = turn
        apply_per_turn_buffs("boss", gs)
    assert gs.number_of_heals["player2"] == initial

    gs.turn_number = 9
    apply_per_turn_buffs("boss", gs)
    assert gs.number_of_heals["player2"] == initial + 1

    gs.turn_number = 19
    apply_per_turn_buffs("boss", gs)
    assert gs.number_of_heals["player2"] == initial + 2


def test_campaign_settings_loaded():
    from campaign.config_loader import CAMPAIGN_SETTINGS
    assert "ai_delay_ms" in CAMPAIGN_SETTINGS
    assert "thresholds" in CAMPAIGN_SETTINGS
    assert CAMPAIGN_SETTINGS["thresholds"]["attack_min_score"] == 15.0


def test_deck_builder_unlock_progression():
    from campaign import deck_builder
    assert deck_builder._unlocked_color_codes("white", set()) == ["W"]
    assert deck_builder._unlocked_color_codes("red", set()) == ["W", "R"]
    assert deck_builder._unlocked_color_codes("blue", {"white"}) == ["W", "B"]
    assert deck_builder._unlocked_color_codes("blue", {"white", "red"}) == ["W", "B", "R"]
    assert set(deck_builder._unlocked_color_codes("boss", set())) == {"W", "R", "B", "G", "O"}


def test_deck_builder_registry_filters_pages_by_unlock():
    from campaign import deck_builder
    from screens.draft.exhibit_registry import ExhibitRegistry
    base = ExhibitRegistry()

    white_only = deck_builder._CampaignExhibitRegistry(base, ["W"])
    page_colors = {
        deck_builder._color_code_of(c.job_and_color)
        for i in range(white_only.page_count())
        for c in white_only.get_page(i)
    }
    assert page_colors == {"W"}

    multi = deck_builder._CampaignExhibitRegistry(base, ["W", "R"])
    page_colors = {
        deck_builder._color_code_of(c.job_and_color)
        for i in range(multi.page_count())
        for c in multi.get_page(i)
    }
    assert page_colors == {"W", "R"}


def test_deck_builder_magic_row_always_available():
    from campaign import deck_builder
    from screens.draft.exhibit_registry import ExhibitRegistry
    base = ExhibitRegistry()
    registry = deck_builder._CampaignExhibitRegistry(base, ["W"])
    names = {c.job_and_color for c in registry.get_magic_row()}
    assert {"HEAL", "MOVE", "CUBES"}.issubset(names)


def test_deck_builder_can_add_respects_per_card_limits():
    from campaign import deck_builder
    deck = ["ADCW", "ADCW"]
    assert not deck_builder._can_add(deck, "ADCW")
    assert deck_builder._can_add(deck, "TANKW")
    full = deck + ["HEAL"] * 3
    assert not deck_builder._can_add(full, "HEAL")
    twelve = ["ADCW", "TANKW", "HFW", "LFW", "ASSW", "APTW", "SPW", "APW",
              "HEAL", "MOVE", "CUBES", "ADCR"]
    assert not deck_builder._can_add(twelve, "TANKR")


def test_numb_attacker_not_resurrected_by_faction_bonus():
    from campaign.ai_strategies.green import GreenStrategy
    from cards.factory import CardFactory
    s = GreenStrategy()
    gs = make_game_state()
    hf = place_card(gs, "HFG", "player2", 1, 1)
    hf.numbness = True
    block = CardFactory.create("LUCKYBLOCK", "neutral", 2, 1)
    gs.neutral.on_board.append(block)
    gs.board_dict[2, 1].occupy = True
    gs.number_of_attacks["player2"] = 1

    best = s.best_attack(gs, "player2")
    assert best is None


def test_aptg_is_never_picked_as_attacker():
    gs = make_game_state()
    apt = place_card(gs, "APTG", "player2", 1, 1)
    apt.numbness = False
    target = place_card(gs, "ADCW", "player1", 1, 2)
    target.numbness = False
    score, _ = ai_evaluator.evaluate_attack(apt, gs)
    assert score < 0


def test_green_strategy_best_attack_skips_aptg_even_with_kill_in_range():
    from campaign.ai_strategies.green import GreenStrategy
    s = GreenStrategy()
    gs = make_game_state()
    apt = place_card(gs, "APTG", "player2", 1, 1)
    apt.numbness = False
    target = place_card(gs, "ADCW", "player1", 1, 2)
    target.numbness = False
    target.health = 1
    gs.number_of_attacks["player2"] = 1
    best = s.best_attack(gs, "player2")
    assert best is None


def test_green_lfg_attack_bonus_when_adjacent_to_lucky_block():
    from campaign.ai_strategies.green import GreenStrategy
    from cards.factory import CardFactory
    s = GreenStrategy()
    gs = make_game_state()
    lf = place_card(gs, "LFG", "player2", 1, 1)
    base = s.attack_bonus(lf, gs, 10.0)
    block = CardFactory.create("LUCKYBLOCK", "neutral", 2, 1)
    gs.neutral.on_board.append(block)
    boosted = s.attack_bonus(lf, gs, 10.0)
    assert boosted >= base + 40.0


def test_green_aptg_placement_rewards_empty_neighbors():
    from campaign.ai_strategies.green import GreenStrategy
    s = GreenStrategy()
    gs = make_game_state()
    center = s.placement_bonus("APTG", (1, 1), gs, "player2", 10.0)
    place_card(gs, "TANKG", "player2", 0, 1)
    place_card(gs, "TANKG", "player2", 1, 0)
    blocked = s.placement_bonus("APTG", (1, 1), gs, "player2", 10.0)
    assert center > blocked


def test_blue_hfb_attack_scales_with_tokens():
    from campaign.ai_strategies.blue import BlueStrategy
    s = BlueStrategy()
    gs = make_game_state()
    hf = place_card(gs, "HFB", "player2", 1, 1)
    place_card(gs, "ADCW", "player1", 1, 2)
    gs.players_token["player2"] = 0
    no_tokens = s.attack_bonus(hf, gs, 10.0)
    gs.players_token["player2"] = 2
    with_tokens = s.attack_bonus(hf, gs, 10.0)
    assert with_tokens > no_tokens


def test_followup_kill_bonus_when_chain_completes_kill():
    gs = make_game_state()
    gs.number_of_attacks["player2"] = 2
    chipper = place_card(gs, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    finisher = place_card(gs, "ADCW", "player2", 3, 0)
    finisher.numbness = False
    victim = place_card(gs, "ASSW", "player1", 1, 0)
    victim.numbness = False
    victim.health = 3

    bonus = ai_evaluator.followup_kill_bonus(chipper, victim, gs, chip_damage=1)
    assert bonus > 0


def test_followup_kill_bonus_zero_when_no_friendly_can_finish():
    gs = make_game_state()
    gs.number_of_attacks["player2"] = 2
    chipper = place_card(gs, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    victim = place_card(gs, "ADCW", "player1", 1, 0)
    victim.numbness = False
    bonus = ai_evaluator.followup_kill_bonus(chipper, victim, gs, chip_damage=1)
    assert bonus == 0.0


def test_followup_kill_bonus_zero_with_only_one_attack_count():
    gs = make_game_state()
    gs.number_of_attacks["player2"] = 1
    chipper = place_card(gs, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    finisher = place_card(gs, "ADCW", "player2", 1, 1)
    finisher.numbness = False
    victim = place_card(gs, "ASSW", "player1", 1, 0)
    victim.numbness = False
    victim.health = 3
    bonus = ai_evaluator.followup_kill_bonus(chipper, victim, gs, chip_damage=1)
    assert bonus == 0.0


def test_evaluate_attack_wasted_chip_penalty_applied():
    gs1 = make_game_state()
    gs1.number_of_attacks["player2"] = 2
    chipper = place_card(gs1, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    victim1 = place_card(gs1, "ADCW", "player1", 1, 0)
    victim1.numbness = False
    score_lonely, _ = ai_evaluator.evaluate_attack(chipper, gs1)

    gs2 = make_game_state()
    gs2.number_of_attacks["player2"] = 2
    chipper2 = place_card(gs2, "TANKW", "player2", 0, 0)
    chipper2.numbness = False
    finisher = place_card(gs2, "ADCW", "player2", 1, 1)
    finisher.numbness = False
    victim2 = place_card(gs2, "ADCW", "player1", 1, 0)
    victim2.numbness = False
    victim2.health = 3
    score_chain, _ = ai_evaluator.evaluate_attack(chipper2, gs2)

    assert score_chain > score_lonely + 10.0


def test_target_priority_bonus_distinguishes_high_value_jobs():
    assert ai_evaluator.target_priority_bonus(_card("ADCW")) > 0
    assert ai_evaluator.target_priority_bonus(_card("SPW")) > 0
    assert ai_evaluator.target_priority_bonus(_card("TANKW")) == 0
    assert ai_evaluator.target_priority_bonus(_card("HFW")) == 0


def test_evaluate_attack_chip_adc_outranks_chip_tank():
    gs = make_game_state()
    attacker = place_card(gs, "TANKW", "player2", 1, 1)
    attacker.numbness = False
    adc = place_card(gs, "ADCW", "player1", 1, 0)
    adc.numbness = False
    tank = place_card(gs, "TANKW", "player1", 0, 1)
    tank.numbness = False
    score, target = ai_evaluator.evaluate_attack(attacker, gs)
    assert target is adc


def test_white_attack_min_score_lowered_via_faction_override():
    from campaign.ai_controller import AIController
    ai = AIController("white")
    assert ai.strategy.attack_min_score <= 10.0


def test_orange_hfo_attack_bonus_scales_with_ramp_and_multitarget():
    from campaign.ai_strategies.orange import OrangeStrategy
    s = OrangeStrategy()
    gs = make_game_state()
    hfo = place_card(gs, "HFO", "player2", 1, 1)
    hfo.numbness = False
    baseline = s.attack_bonus(hfo, gs, 10.0)

    a = place_card(gs, "ADCW", "player1", 0, 0)
    b = place_card(gs, "ADCW", "player1", 2, 0)
    c = place_card(gs, "ADCW", "player1", 0, 2)
    a.numbness = b.numbness = c.numbness = False
    multi = s.attack_bonus(hfo, gs, 10.0)
    assert multi > baseline

    hfo.extra_damage = 2
    ramped = s.attack_bonus(hfo, gs, 10.0)
    assert ramped > multi + 10.0


def test_orange_hfo_move_destination_prefers_dense_target_zones():
    from campaign.ai_evaluator import score_move_destination
    gs = make_game_state()
    hfo = place_card(gs, "HFO", "player2", 1, 1)
    hfo.numbness = False
    place_card(gs, "ADCW", "player1", 0, 0)
    toward = score_move_destination(hfo, (1, 0), gs)
    away = score_move_destination(hfo, (1, 2), gs)
    assert toward > away


def test_ai_plays_moveo_when_orange_unit_can_use_it():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = ["MOVEO"]
    adco = place_card(gs, "ADCO", "player2", 1, 1)
    adco.numbness = False

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "play_card"
    assert gs.player2.hand[actions[0].hand_index] == "MOVEO"


def test_ai_doesnt_play_moveo_when_no_unit_can_consume_movings():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = ["MOVEO"]

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert actions == [] or actions[0].action_type != "play_card" or \
        gs.player2.hand[actions[0].hand_index] != "MOVEO"


def test_ai_uses_banked_movings_to_start_unit_move():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.number_of_movings["player2"] = 1
    gs.player2.hand = []
    adco = place_card(gs, "ADCO", "player2", 1, 1)
    adco.numbness = False
    place_card(gs, "ADCW", "player1", 0, 0)

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)


def test_asso_post_kill_emits_move_select_action():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False
    asso.moving = True
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)


def test_asso_selected_picks_destination_with_killable_target():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False
    asso.moving = True
    asso.mouse_selected = True
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (2, 2)


def test_asso_with_anger_and_killable_target_emits_attack():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    asso = place_card(gs, "ASSO", "player2", 2, 2)
    asso.numbness = False
    asso.anger = True
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "attack"
    assert (actions[0].board_x, actions[0].board_y) == (2, 2)


def test_asso_chain_drives_two_kills_with_one_net_attack():
    from core.battling_dispatcher import BattlingDispatcher
    from campaign.ai_controller import AIController
    ai = AIController("orange", player_name="player2")

    gs = make_game_state()
    dispatcher = BattlingDispatcher(gs, mode="campaign")
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 2
    gs.player2.hand = []

    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False

    a = place_card(gs, "ADCW", "player1", 0, 0)
    a.numbness = False
    a.health = 3

    b = place_card(gs, "ADCW", "player1", 3, 3)
    b.numbness = False
    b.health = 3

    now_ms = 0
    for _ in range(40):
        actions = ai.tick(gs, now_ms)
        for action in actions:
            dispatcher.dispatch(action, gs)
        gs.pending_combat_events.clear()
        if a.health <= 0 and b.health <= 0:
            break
        now_ms += 700

    assert a.health <= 0
    assert b.health <= 0
    assert gs.number_of_attacks["player2"] >= 1


def test_score_move_destination_picks_asso_over_adco():
    from campaign.ai_evaluator import score_move_destination
    gs = make_game_state()
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False
    adco = place_card(gs, "ADCO", "player2", 0, 3)
    adco.numbness = False
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    asso_score = score_move_destination(asso, (2, 2), gs)
    adco_score = score_move_destination(adco, (1, 3), gs)
    assert asso_score > adco_score


def test_ai_plays_moveo_then_chains_to_asso_anger_kill():
    from core.battling_dispatcher import BattlingDispatcher
    from campaign.ai_controller import AIController
    ai = AIController("orange", player_name="player2")

    gs = make_game_state()
    dispatcher = BattlingDispatcher(gs, mode="campaign")
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = ["MOVEO"]

    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False
    asso.anger = False

    victim = place_card(gs, "ADCW", "player1", 3, 3)
    victim.numbness = False
    victim.health = 3

    now_ms = 0
    for _ in range(40):
        actions = ai.tick(gs, now_ms)
        for action in actions:
            dispatcher.dispatch(action, gs)
        gs.pending_combat_events.clear()
        if victim.health <= 0:
            break
        now_ms += 700

    assert victim.health <= 0
    assert gs.number_of_attacks["player2"] >= 1
    assert "MOVEO" not in gs.player2.hand


def test_orange_post_attack_move_action_is_emitted():
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = []
    adc = place_card(gs, "ADCO", "player2", 1, 1)
    adc.moving = True
    place_card(gs, "ADCW", "player1", 0, 2)

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)


def test_doomed_attacker_skips_wasted_chip_penalty():
    gs = make_game_state()
    adcr = place_card(gs, "ADCR", "player2", 3, 3)
    adcr.numbness = False
    adcr.health = 1
    adcr.damage = 2

    place_card(gs, "ADCW", "player1", 0, 3)
    place_card(gs, "ASSW", "player1", 1, 3)
    place_card(gs, "APTW", "player1", 3, 1)

    score, target = ai_evaluator.evaluate_attack(adcr, gs)
    assert score > 13
    assert target is not None


def test_doomed_attacker_skips_suicide_penalty():
    gs = make_game_state()
    attacker = place_card(gs, "ADCW", "player2", 1, 1)
    attacker.numbness = False
    attacker.health = 1
    big = place_card(gs, "TANKW", "player1", 1, 2)
    big.numbness = False
    big.damage = 5

    score, _ = ai_evaluator.evaluate_attack(attacker, gs)
    assert score >= 0


def test_non_doomed_attacker_still_gets_wasted_chip_penalty():
    gs = make_game_state()
    attacker = place_card(gs, "TANKW", "player2", 0, 0)
    attacker.numbness = False
    attacker.health = 15
    target = place_card(gs, "TANKW", "player1", 1, 0)
    target.numbness = False
    target.health = 15

    score, _ = ai_evaluator.evaluate_attack(attacker, gs)
    assert score < 0
