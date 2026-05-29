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
    """Minimal stand-in: an object with `job_and_color` for evaluator helpers that
    only need the name string."""
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


def test_red_attack_bonus_rewards_damage_growth():
    """Red abilities bump `self.damage` directly, not `extra_damage`; the strategy
    must read the delta against `original_damage`."""
    s = RedStrategy()
    gs = make_game_state()
    adc = place_card(gs, "ADCR", "player2", 0, 0)
    fresh = s.attack_bonus(adc, gs, 10.0)
    adc.damage += 3  # simulate 3 ramps from ability triggers
    ramped = s.attack_bonus(adc, gs, 10.0)
    assert ramped >= fresh + 15.0  # +3 * 6 from _damage_grown


def test_red_strategy_prefers_hfr_over_tankr():
    """User-reported issue: AI should swing HFR (ramper) instead of TANKR (low damage)."""
    s = RedStrategy()
    gs = make_game_state()
    tankr = place_card(gs, "TANKR", "player2", 0, 0)
    hfr = place_card(gs, "HFR", "player2", 1, 0)
    # Same base score input — strategy bonus should split them clearly.
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
    """ASSO with anger=True kills → +1 attack refund. AI should value this over a
    standard ASSO swing."""
    from campaign.ai_strategies.orange import OrangeStrategy
    s = OrangeStrategy()
    gs = make_game_state()
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    fresh = s.attack_bonus(asso, gs, 10.0)
    asso.anger = True
    angered = s.attack_bonus(asso, gs, 10.0)
    assert angered >= fresh + 18.0


def test_evaluator_skips_suicide_penalty_for_anger_hfr_attacker():
    """HFR with anger=True can't be killed this turn — don't apply suicide penalty."""
    gs = make_game_state()
    hfr = place_card(gs, "HFR", "player2", 1, 1)
    hfr.numbness = False
    hfr.health = 1  # low HP; would normally trigger suicide check
    danger = place_card(gs, "ADCW", "player1", 1, 2)
    danger.numbness = False
    danger.damage = 5

    score_no_anger, _ = ai_evaluator.evaluate_attack(hfr, gs)
    hfr.anger = True
    score_with_anger, _ = ai_evaluator.evaluate_attack(hfr, gs)
    assert score_with_anger > score_no_anger


def test_evaluator_doesnt_count_kill_on_anger_hfr_target():
    """Hitting an enemy HFR with anger=True isn't a real kill — skip the kill bonus."""
    gs = make_game_state()
    attacker = place_card(gs, "ADCW", "player2", 1, 1)
    attacker.numbness = False
    enemy_hfr = place_card(gs, "HFR", "player1", 1, 2)
    enemy_hfr.numbness = False
    enemy_hfr.health = 1
    no_anger_score, _ = ai_evaluator.evaluate_attack(attacker, gs)
    enemy_hfr.anger = True
    anger_score, _ = ai_evaluator.evaluate_attack(attacker, gs)
    assert no_anger_score >= anger_score + 80  # kill bonus (~100) stripped


def test_adcb_placement_bonus_scales_with_token_engines():
    """ADCB on board catches every future token_draw event — more engines
    means more expected free attacks down the road."""
    s = BlueStrategy()
    gs = make_game_state()
    lone = s.placement_bonus("ADCB", (0, 0), gs, "player2", 10.0)

    gs2 = make_game_state()
    place_card(gs2, "APB", "player2", 1, 1)
    place_card(gs2, "LFB", "player2", 2, 2)
    place_card(gs2, "TANKB", "player2", 3, 3)
    with_engines = s.placement_bonus("ADCB", (0, 0), gs2, "player2", 10.0)
    assert with_engines >= lone + 10.0  # 3 engines × +4 each


def test_apb_swing_with_armed_adcb_gets_chain_bonus():
    """APB attack at tokens=2 + non-numb ADCB on board → token threshold crosses,
    draw fires, ADCB enqueues a free attack. Score must reflect the chain."""
    s = BlueStrategy()
    gs = make_game_state()
    gs.players_token["player2"] = 1  # APB hit adds 2 → threshold = 3
    gs.how_many_token_to_draw_a_card = 3
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 2)
    no_adcb = s.attack_bonus(apb, gs, 10.0)

    armed_adcb = place_card(gs, "ADCB", "player2", 0, 0)
    armed_adcb.numbness = False
    with_adcb = s.attack_bonus(apb, gs, 10.0)
    assert with_adcb >= no_adcb + 10.0


def test_numb_adcb_doesnt_arm_token_draw_chain():
    """First token_draw on a just-deployed ADCB only clears numbness; no free attack."""
    s = BlueStrategy()
    gs = make_game_state()
    gs.players_token["player2"] = 1
    gs.how_many_token_to_draw_a_card = 3
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 2)
    no_adcb = s.attack_bonus(apb, gs, 10.0)

    numb_adcb = place_card(gs, "ADCB", "player2", 0, 0)
    numb_adcb.numbness = True  # just placed
    with_numb_adcb = s.attack_bonus(apb, gs, 10.0)
    assert with_numb_adcb == no_adcb


def test_expected_tokens_from_apb_attack_scales_with_targets():
    """APB ability fires per damage event → +2 tokens per target hit."""
    from campaign.ai_strategies.blue import expected_tokens_from_attack
    gs = make_game_state()
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 2)  # nearest target
    assert expected_tokens_from_attack(apb, gs) == 2


def test_expected_tokens_from_lfb_multi_target_attack():
    """LFB ability fires once per damage event — small_cross can chip 2+
    enemies → 1 token each."""
    from campaign.ai_strategies.blue import expected_tokens_from_attack
    gs = make_game_state()
    lfb = place_card(gs, "LFB", "player2", 1, 1)
    lfb.numbness = False
    place_card(gs, "ADCW", "player1", 1, 0)
    place_card(gs, "ADCW", "player1", 0, 1)
    place_card(gs, "ADCW", "player1", 2, 1)
    assert expected_tokens_from_attack(lfb, gs) == 3


def test_blue_apb_attack_outranks_adcb_for_token_economy():
    """Same target board — APB's +2 token yield should beat ADCB's chip swing."""
    s = BlueStrategy()
    gs = make_game_state()
    apb = place_card(gs, "APB", "player2", 1, 1)
    apb.numbness = False
    adcb = place_card(gs, "ADCB", "player2", 3, 3)
    adcb.numbness = False
    place_card(gs, "ADCW", "player1", 0, 0)  # nearest, also in adcb's large_cross row
    s_apb = s.attack_bonus(apb, gs, 10.0)
    s_adcb = s.attack_bonus(adcb, gs, 10.0)
    assert s_apb > s_adcb


def test_spb_placement_deferred_when_other_units_in_hand():
    """SPB deploy hits scale with on_board count. Each other deployable unit in
    hand should defer SPB so we maximize the deploy fan-out."""
    s = BlueStrategy()
    gs = make_game_state()
    place_card(gs, "ADCW", "player1", 1, 0)
    gs.player2.hand = ["SPB"]
    solo = s.placement_bonus("SPB", (0, 0), gs, "player2", 10.0)

    gs2 = make_game_state()
    place_card(gs2, "ADCW", "player1", 1, 0)
    gs2.player2.hand = ["SPB", "TANKB", "ADCB", "APB"]
    crowded = s.placement_bonus("SPB", (0, 0), gs2, "player2", 10.0)
    # 3 other unit-playables × −5 each = −15 vs solo hand
    assert crowded < solo - 10.0


def test_blue_spb_placement_penalized_when_no_enemies():
    """SPB deploy fires into nothing when no enemies on board — heavy hold."""
    s = BlueStrategy()
    gs = make_game_state()
    no_enemies = s.placement_bonus("SPB", (0, 0), gs, "player2", 10.0)
    assert no_enemies <= 0  # base + penalty puts it at or below zero
    gs2 = make_game_state()
    place_card(gs2, "ADCW", "player1", 1, 0)
    with_enemies = s.placement_bonus("SPB", (0, 0), gs2, "player2", 10.0)
    assert with_enemies > no_enemies


def test_blue_spb_attack_outranks_other_blue_attackers():
    """SPB is the dedicated 5-damage core. Strategy should prefer SPB over a
    same-token-count blue ADC swing."""
    s = BlueStrategy()
    gs = make_game_state()
    spb = place_card(gs, "SPB", "player2", 0, 0)
    adcb = place_card(gs, "ADCB", "player2", 3, 0)
    s_spb = s.attack_bonus(spb, gs, 10.0)
    s_adcb = s.attack_bonus(adcb, gs, 10.0)
    assert s_spb > s_adcb


def test_blue_spb_placement_scales_with_discard_pile():
    """SPB deploy hits N enemies where N = on_board + discard_pile. Late-game
    deploy should score noticeably higher than an empty-pile early deploy."""
    s = BlueStrategy()
    early = make_game_state()
    place_card(early, "ADCW", "player1", 1, 0)
    early_score = s.placement_bonus("SPB", (0, 0), early, "player2", 10.0)

    late = make_game_state()
    place_card(late, "ADCW", "player1", 1, 0)
    late.player2.discard_pile = ["TANKB"] * 5  # 5 spent cards
    late_score = s.placement_bonus("SPB", (0, 0), late, "player2", 10.0)
    assert late_score > early_score


def test_blue_adcb_placement_bonus_when_token_draw_imminent():
    """ADCB on board at the moment tokens hit 3 → numbness clears or extra
    attack fires. AI should bias deploy when tokens are at 2."""
    s = BlueStrategy()
    gs = make_game_state()
    gs.players_token["player2"] = 2
    high = s.placement_bonus("ADCB", (0, 0), gs, "player2", 10.0)
    gs.players_token["player2"] = 0
    low = s.placement_bonus("ADCB", (0, 0), gs, "player2", 10.0)
    assert high > low + 10.0


def test_blue_lfb_placement_holds_when_board_sparse():
    """LFB ability fires per damage event. Without enemies to chip, deploying
    early wastes the ramp potential — score should drop."""
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
    # Player1 has a high-damage roster
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
    """maintain_unit_buffs applies +1 HP to each AI unit exactly once."""
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
    """Each AIController owns its own buffed-id set, so the second campaign
    match must re-buff freshly-instantiated cards even if the global
    instance counter recycled the same id (battling.main resets it)."""
    from campaign.boss_config import maintain_unit_buffs
    from cards.base import reset_instance_counter

    # Match 1: buff a card.
    buffed_m1: set[str] = set()
    reset_instance_counter()
    gs1 = make_game_state()
    c1 = place_card(gs1, "ADCW", "player2", 0, 0)
    maintain_unit_buffs("boss", gs1, buffed_m1)
    assert c1.health == 5 + 1  # ADCW base 5 HP + 1 buff
    first_id = c1.instance_id

    # Match 2: counter reset → new card likely has the same instance_id;
    # a FRESH buffed-id set must still treat it as un-buffed.
    buffed_m2: set[str] = set()
    reset_instance_counter()
    gs2 = make_game_state()
    c2 = place_card(gs2, "ADCW", "player2", 0, 0)
    maintain_unit_buffs("boss", gs2, buffed_m2)
    assert c2.health == 5 + 1  # +1 HP buff applied in match 2
    # If counter recycled, this would have been skipped under the old bug.
    assert c2.instance_id == first_id  # confirm the counter does recycle


def test_ai_controller_runs_initial_buffs_when_board_ready():
    """build_campaign_game_state intentionally defers buffs; AIController applies
    them as soon as board_dict + player2 init are ready."""
    from campaign.ai_controller import AIController
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    # board_dict is populated by make_game_state. Pre-load player2's deck so initialize-
    # style state is present.
    gs.player2.draw_pile = ["ADCW"] * 6
    gs.player2.hand = ["ADCW", "ADCW", "ADCW"]  # already drew 3
    ai.tick(gs, 0)
    assert ai._initialized
    assert len(gs.player2.hand) == 4  # boss initial_hand_size = 4


def test_green_stage_boosts_ai_initial_luck():
    """Green stage one-shot: AI starts at 65% luck instead of the 50% default."""
    from campaign.boss_config import apply_stage_one_shots
    gs = make_game_state()
    assert gs.players_luck["player2"] == 50  # default
    apply_stage_one_shots("green", gs)
    assert gs.players_luck["player2"] == 65
    # Other sides untouched
    assert gs.players_luck["player1"] == 50


def test_per_turn_buffs_grant_free_moves_to_orange():
    """Orange's +1 movings fires every 3rd AI turn. First grant is the 3rd AI
    turn (game turn 5) so the AI has had time for its initial deploys to settle
    and become non-numb / move-eligible."""
    from campaign.boss_config import apply_per_turn_buffs
    gs = make_game_state()
    initial = gs.number_of_movings.get("player2", 0)

    # AI turn 1 (game turn 1) — no fire, would be wasted on numb deploys.
    gs.turn_number = 1
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial

    # AI turn 2 (game turn 3) — no fire.
    gs.turn_number = 3
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial

    # AI turn 3 (game turn 5) — first +1 movings.
    gs.turn_number = 5
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 1

    # AI turn 4 (game turn 7) — no fire (only 1 AI turn since last grant).
    gs.turn_number = 7
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 1

    # AI turn 6 (game turn 11) — second +1 movings.
    gs.turn_number = 11
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 2

    # Player1 turn (even game turn) — never fires regardless of cadence.
    gs.turn_number = 10
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 2


def test_per_turn_heal_buff_fires_every_5_ai_turns_for_boss():
    """Boss's +1 heal every 5 AI turns: fires at AI turn 5, 10, 15 →
    game turn 9, 19, 29."""
    from campaign.boss_config import apply_per_turn_buffs
    gs = make_game_state()
    initial = gs.number_of_heals.get("player2", 0)
    for turn in (1, 3, 5, 7):
        gs.turn_number = turn
        apply_per_turn_buffs("boss", gs)
    assert gs.number_of_heals["player2"] == initial  # nothing yet

    gs.turn_number = 9  # AI turn 5
    apply_per_turn_buffs("boss", gs)
    assert gs.number_of_heals["player2"] == initial + 1

    gs.turn_number = 19  # AI turn 10
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
    assert not deck_builder._can_add(deck, "ADCW")  # 2 already
    assert deck_builder._can_add(deck, "TANKW")
    full = deck + ["HEAL"] * 3
    assert not deck_builder._can_add(full, "HEAL")  # 3 already
    twelve = ["ADCW", "TANKW", "HFW", "LFW", "ASSW", "APTW", "SPW", "APW",
              "HEAL", "MOVE", "CUBES", "ADCR"]
    assert not deck_builder._can_add(twelve, "TANKR")  # deck full


def test_numb_attacker_not_resurrected_by_faction_bonus():
    """GreenStrategy.attack_bonus adds +30 for HFG adjacent to a lucky block. If we let
    that bonus stack on top of evaluator's -1 numb sentinel, AI picks a numb attacker
    and loops forever (the engine refuses the action, attack count never drops)."""
    from campaign.ai_strategies.green import GreenStrategy
    from cards.factory import CardFactory
    s = GreenStrategy()
    gs = make_game_state()
    hf = place_card(gs, "HFG", "player2", 1, 1)
    hf.numbness = True  # just-deployed HFG
    # adjacent lucky block — triggers the faction bonus
    block = CardFactory.create("LUCKYBLOCK", "neutral", 2, 1)
    gs.neutral.on_board.append(block)
    gs.board_dict[2, 1].occupy = True
    gs.number_of_attacks["player2"] = 1

    best = s.best_attack(gs, "player2")
    assert best is None


def test_aptg_is_never_picked_as_attacker():
    """APTG's attack() returns False unconditionally — picking it loops the AI forever.
    Evaluator must short-circuit before issuing an attack action for it."""
    gs = make_game_state()
    apt = place_card(gs, "APTG", "player2", 1, 1)
    apt.numbness = False
    target = place_card(gs, "ADCW", "player1", 1, 2)
    target.numbness = False
    score, _ = ai_evaluator.evaluate_attack(apt, gs)
    assert score < 0  # filtered out by NON_ATTACKING_CARDS


def test_green_strategy_best_attack_skips_aptg_even_with_kill_in_range():
    from campaign.ai_strategies.green import GreenStrategy
    s = GreenStrategy()
    gs = make_game_state()
    apt = place_card(gs, "APTG", "player2", 1, 1)
    apt.numbness = False
    target = place_card(gs, "ADCW", "player1", 1, 2)
    target.numbness = False
    target.health = 1  # one-shot for APTG damage if attack were possible
    gs.number_of_attacks["player2"] = 1
    best = s.best_attack(gs, "player2")
    assert best is None  # no other attacker present, and APTG must be skipped


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
    """Two friendly attackers in range: chip + finish chain → big bonus."""
    gs = make_game_state()
    gs.number_of_attacks["player2"] = 2
    chipper = place_card(gs, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    finisher = place_card(gs, "ADCW", "player2", 3, 0)  # large_cross row reaches (1, 0)
    finisher.numbness = False
    victim = place_card(gs, "ASSW", "player1", 1, 0)
    victim.numbness = False
    victim.health = 3  # ADC's 4 damage one-shots after TANK chips 1 → 2 HP remaining

    bonus = ai_evaluator.followup_kill_bonus(chipper, victim, gs, chip_damage=1)
    assert bonus > 0


def test_followup_kill_bonus_zero_when_no_friendly_can_finish():
    """No other attacker → no chain, chip is wasted work."""
    gs = make_game_state()
    gs.number_of_attacks["player2"] = 2
    chipper = place_card(gs, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    victim = place_card(gs, "ADCW", "player1", 1, 0)
    victim.numbness = False
    bonus = ai_evaluator.followup_kill_bonus(chipper, victim, gs, chip_damage=1)
    assert bonus == 0.0


def test_followup_kill_bonus_zero_with_only_one_attack_count():
    """Need ≥ 2 attacks to fire chip + follow-up in the same turn."""
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
    """Without a chain, the chip score takes a small hit. Same scenario with a
    finisher in range should out-score the lone-chipper version."""
    # Lone chipper: no finisher available.
    gs1 = make_game_state()
    gs1.number_of_attacks["player2"] = 2
    chipper = place_card(gs1, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    victim1 = place_card(gs1, "ADCW", "player1", 1, 0)
    victim1.numbness = False
    score_lonely, _ = ai_evaluator.evaluate_attack(chipper, gs1)

    # With finisher in range.
    gs2 = make_game_state()
    gs2.number_of_attacks["player2"] = 2
    chipper2 = place_card(gs2, "TANKW", "player2", 0, 0)
    chipper2.numbness = False
    finisher = place_card(gs2, "ADCW", "player2", 1, 1)  # large_cross reaches (1, 0)
    finisher.numbness = False
    victim2 = place_card(gs2, "ADCW", "player1", 1, 0)
    victim2.numbness = False
    victim2.health = 3  # finisher can one-shot at 3 HP after chip → 2 HP
    score_chain, _ = ai_evaluator.evaluate_attack(chipper2, gs2)

    assert score_chain > score_lonely + 10.0


def test_target_priority_bonus_distinguishes_high_value_jobs():
    """ADC and SP are the priority chip/kill targets — they should out-score TANK/HF
    on equivalent attacks."""
    assert ai_evaluator.target_priority_bonus(_card("ADCW")) > 0
    assert ai_evaluator.target_priority_bonus(_card("SPW")) > 0
    assert ai_evaluator.target_priority_bonus(_card("TANKW")) == 0
    assert ai_evaluator.target_priority_bonus(_card("HFW")) == 0


def test_evaluate_attack_chip_adc_outranks_chip_tank():
    """White TANK chip damage vs ADC (4HP, dmg 3) should beat chip vs TANK (15HP,
    dmg 1) by the priority bonus + threat-damage gap."""
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
    """White attacker chip-scoring 12 should pass the new lowered threshold."""
    from campaign.ai_controller import AIController
    ai = AIController("white")
    assert ai.strategy.attack_min_score <= 10.0


def test_orange_hfo_attack_bonus_scales_with_ramp_and_multitarget():
    from campaign.ai_strategies.orange import OrangeStrategy
    s = OrangeStrategy()
    gs = make_game_state()
    hfo = place_card(gs, "HFO", "player2", 1, 1)
    hfo.numbness = False
    # No targets, no ramps — baseline only.
    baseline = s.attack_bonus(hfo, gs, 10.0)

    # Add multiple targets in HFO's 8-cell reach.
    a = place_card(gs, "ADCW", "player1", 0, 0)
    b = place_card(gs, "ADCW", "player1", 2, 0)
    c = place_card(gs, "ADCW", "player1", 0, 2)
    a.numbness = b.numbness = c.numbness = False
    multi = s.attack_bonus(hfo, gs, 10.0)
    assert multi > baseline

    # Ramped HFO (already moved once) — extra_damage > 0 should compound.
    hfo.extra_damage = 2
    ramped = s.attack_bonus(hfo, gs, 10.0)
    assert ramped > multi + 10.0


def test_orange_hfo_move_destination_prefers_dense_target_zones():
    from campaign.ai_evaluator import score_move_destination
    gs = make_game_state()
    hfo = place_card(gs, "HFO", "player2", 1, 1)
    hfo.numbness = False
    # Single enemy at (0,0): in HFO's small_x reach from destination (1,0), out of
    # range from destination (1,2) on the other side of the board.
    place_card(gs, "ADCW", "player1", 0, 0)
    toward = score_move_destination(hfo, (1, 0), gs)
    away = score_move_destination(hfo, (1, 2), gs)
    assert toward > away


def test_ai_plays_moveo_when_orange_unit_can_use_it():
    """MOVEO in hand → AI plays it to convert into +1 movings."""
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = ["MOVEO"]
    adco = place_card(gs, "ADCO", "player2", 1, 1)
    adco.numbness = False  # ready to move (numb units can't move per player.move_card)

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "play_card"
    assert gs.player2.hand[actions[0].hand_index] == "MOVEO"


def test_ai_doesnt_play_moveo_when_no_unit_can_consume_movings():
    """No orange unit on board → MOVEO would be wasted (movings reset at turn_end)."""
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = ["MOVEO"]
    # no units on board

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert actions == [] or actions[0].action_type != "play_card" or \
        gs.player2.hand[actions[0].hand_index] != "MOVEO"


def test_ai_uses_banked_movings_to_start_unit_move():
    """After MOVEO played, number_of_movings > 0; AI clicks unit cell to set moving=True."""
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.number_of_movings["player2"] = 1
    gs.player2.hand = []
    adco = place_card(gs, "ADCO", "player2", 1, 1)
    adco.numbness = False
    place_card(gs, "ADCW", "player1", 0, 0)  # gives a destination worth scoring

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)  # selects ADCO's own cell


def test_asso_post_kill_emits_move_select_action():
    """Step 1 of the ASSO refund chain: after ASSO.killed sets moving=True, the
    AI should drive the move chain (first emit move_to on ASSO's own cell to
    set mouse_selected=True)."""
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False
    asso.moving = True  # simulate state right after killed callback
    # An enemy further away gives the destination scorer something to chase.
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)


def test_asso_selected_picks_destination_with_killable_target():
    """Step 2: ASSO already mouse_selected, the AI should pick the destination
    whose small_x reach lands on a killable enemy (sets up the anger chain)."""
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
    # Enemy at (3,3) is small_x-killable from destination (2,2) only.
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (2, 2)


def test_asso_with_anger_and_killable_target_emits_attack():
    """Step 3: after the move resolved (anger=True), the AI must commit the
    kill swing — that's the swing that triggers `+1 attack` refund."""
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    asso = place_card(gs, "ASSO", "player2", 2, 2)
    asso.numbness = False
    asso.anger = True  # just resolved after_movement
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "attack"
    assert (actions[0].board_x, actions[0].board_y) == (2, 2)


def test_asso_chain_drives_two_kills_with_one_net_attack():
    """End-to-end: ASSO + 2 reachable killable enemies, going through the
    dispatcher. The chain should kill both enemies and refund the second
    attack (start with 2 attacks, after chain still have ≥ 1)."""
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

    a = place_card(gs, "ADCW", "player1", 0, 0)  # small_x of (1,1) → first kill
    a.numbness = False
    a.health = 3

    b = place_card(gs, "ADCW", "player1", 3, 3)  # small_x of (2,2) → second kill (chain)
    b.numbness = False
    b.health = 3

    # Drive the AI for enough ticks to attack → move-select → move-dest → attack.
    # In real play the renderer ingests pending_combat_events into the animator;
    # here we drain them manually so the AI doesn't sit in the renderer_busy gate.
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
    # Started with 2 attacks. First kill: −1 (no refund). Second kill via anger
    # chain: −1 +1 refund. Net spend = 1, remaining attacks ≥ 1.
    assert gs.number_of_attacks["player2"] >= 1


def test_score_move_destination_picks_asso_over_adco():
    """When both an ASSO and an ADCO could profitably move, ASSO's kill-setup
    destination must score higher — that's what biases `_start_unit_move` to
    spend banked movings on the refund chain rather than ADCO's chase."""
    from campaign.ai_evaluator import score_move_destination
    gs = make_game_state()
    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False
    adco = place_card(gs, "ADCO", "player2", 0, 3)
    adco.numbness = False
    enemy = place_card(gs, "ADCW", "player1", 3, 3)
    enemy.numbness = False
    enemy.health = 3

    # Best ASSO destination: (2,2) — small_x reaches the killable (3,3).
    asso_score = score_move_destination(asso, (2, 2), gs)
    # ADCO with large_cross from (1,3) reaches (3,3); but no kill formula applies
    # so we only see a chip score.
    adco_score = score_move_destination(adco, (1, 3), gs)
    assert asso_score > adco_score


def test_ai_plays_moveo_then_chains_to_asso_anger_kill():
    """MOVEO + ASSO chain (no prior kill required): AI plays MOVEO → moves ASSO
    → after_movement arms anger → attack → kill refunds the spent attack."""
    from core.battling_dispatcher import BattlingDispatcher
    from campaign.ai_controller import AIController
    ai = AIController("orange", player_name="player2")

    gs = make_game_state()
    dispatcher = BattlingDispatcher(gs, mode="campaign")
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = ["MOVEO"]

    asso = place_card(gs, "ASSO", "player2", 1, 1)
    asso.numbness = False  # ASSO doesn't get numbness by default but be explicit
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

    # Victim dead via MOVEO → move → anger → kill chain.
    assert victim.health <= 0
    # Started with 1 attack. Kill with anger refunds +1 → end with ≥ 1.
    assert gs.number_of_attacks["player2"] >= 1
    # MOVEO consumed from hand.
    assert "MOVEO" not in gs.player2.hand


def test_orange_post_attack_move_action_is_emitted():
    """Orange ADCO with moving=True should drive an AI move_to action chain."""
    from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS
    ai = AIController("orange", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 1
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = []
    adc = place_card(gs, "ADCO", "player2", 1, 1)
    adc.moving = True  # simulate post-attack state
    place_card(gs, "ADCW", "player1", 0, 2)  # gives a destination worth scoring

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    # First emission selects the moving unit by clicking on its own cell.
    assert actions[0].action_type == "move_to"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)
