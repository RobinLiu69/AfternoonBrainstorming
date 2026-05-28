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
    gs = make_game_state()
    card = place_card(gs, "ADCW", "player2", 0, 0)
    base_hp = card.health
    maintain_unit_buffs("boss", gs)
    maintain_unit_buffs("boss", gs)
    maintain_unit_buffs("boss", gs)
    assert card.health == base_hp + 1
    assert getattr(card, "_boss_hp_applied", False)


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


def test_per_turn_buffs_grant_free_moves_to_orange():
    from campaign.boss_config import apply_per_turn_buffs
    gs = make_game_state()
    initial = gs.number_of_movings.get("player2", 0)
    gs.turn_number = 7  # AI turn (odd) at 3-cycle boundary: 7 % 6 == 1
    apply_per_turn_buffs("orange", gs)
    assert gs.number_of_movings["player2"] == initial + 1


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
