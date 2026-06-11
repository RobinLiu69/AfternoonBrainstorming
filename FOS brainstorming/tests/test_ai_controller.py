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

from campaign.ai_controller import AIController, AI_TURN_START_DELAY_MS, AI_ACTION_DELAY_MS
from cards.card_white import Adc, Ass
from tests.helpers import make_game_state, place_card


def _ai_turn(gs):
    gs.turn_number = 1


def test_unknown_stage_raises():
    with pytest.raises(ValueError):
        AIController("nonexistent_stage")


def test_tick_returns_empty_when_not_ais_turn():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    gs.turn_number = 0
    assert ai.tick(gs, 0) == []


def test_tick_returns_empty_on_first_observation_then_emits_after_delay():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)

    first = ai.tick(gs, 0)
    assert first == []

    too_early = ai.tick(gs, AI_TURN_START_DELAY_MS - 1)
    assert too_early == []

    ready = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(ready) == 1
    assert ready[0].player == "player2"


def test_tick_ends_turn_when_no_actions_available():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.player2.hand = []
    gs.player2.draw_pile = []
    gs.player2.discard_pile = []

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "end_turn"


def test_tick_throttles_between_actions():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.player2.hand = ["ADCW"]

    ai.tick(gs, 0)
    first = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(first) == 1

    immediate = ai.tick(gs, AI_TURN_START_DELAY_MS + 2)
    assert immediate == []

    later = ai.tick(gs, AI_TURN_START_DELAY_MS + AI_ACTION_DELAY_MS + 2)
    assert len(later) == 1


def test_tick_paused_returns_empty():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.paused = True
    assert ai.tick(gs, AI_TURN_START_DELAY_MS + 10) == []


def test_tick_waits_for_pending_combat_events():
    from shared.combat_event import CombatEvent
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.pending_combat_events.append(CombatEvent(kind="hurt", board_x=0, board_y=0))
    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert actions == []


def test_tick_waits_for_renderer_busy_signal():
    from campaign.ai_controller import AI_BUSY_RECHECK_MS
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    ai.tick(gs, 0, renderer_busy=True)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1, renderer_busy=True)
    assert actions == []
    later = AI_TURN_START_DELAY_MS + 1 + AI_BUSY_RECHECK_MS + 5
    actions_after = ai.tick(gs, later, renderer_busy=False)
    assert len(actions_after) == 1


def test_prefers_lethal_board_attack_over_placement():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 1

    attacker = place_card(gs, Adc, "player2", 1, 1)
    attacker.numbness = False
    victim = place_card(gs, Ass, "player1", 1, 2)
    victim.numbness = False
    victim.health = 1

    gs.player2.hand = ["TANKW"]

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "attack"
    assert (actions[0].board_x, actions[0].board_y) == (1, 1)


def test_hoards_when_no_kill_setup_even_when_trailing():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    gs.score = -7

    attacker = place_card(gs, Adc, "player2", 0, 0)
    attacker.numbness = False
    chump = place_card(gs, Adc, "player1", 1, 0)
    chump.numbness = False

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "end_turn"


def test_attacks_when_trailing_if_chip_chains_into_a_kill():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 2
    gs.player2.hand = []
    gs.score = -7

    chipper = place_card(gs, "TANKW", "player2", 0, 0)
    chipper.numbness = False
    finisher = place_card(gs, Adc, "player2", 3, 0)
    finisher.numbness = False
    victim = place_card(gs, "ASSW", "player1", 1, 0)
    victim.numbness = False
    victim.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "attack"


def test_saves_attacks_when_only_low_value_chips_available():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []

    attacker = place_card(gs, "TANKW", "player2", 0, 0)
    attacker.numbness = False
    chump = place_card(gs, "TANKW", "player1", 1, 0)
    chump.numbness = False

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "end_turn"


def test_holds_ass_in_hand_when_no_kill_or_defense_available():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 0
    gs.player2.hand = ["ASSW"]

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "end_turn"


def test_prefers_ass_lethal_placement_over_generic_placement():
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 0

    victim = place_card(gs, Adc, "player1", 2, 2)
    victim.numbness = False
    gs.player2.hand = ["ASSW", "ADCW"]

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "play_card"
    assert gs.player2.hand[actions[0].hand_index] == "ASSW"
    assert (actions[0].board_x, actions[0].board_y) in {(1, 1), (1, 3), (3, 1), (3, 3)}


def test_heal_not_emitted_when_no_heal_counter():
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 0
    gs.number_of_heals["player2"] = 0
    gs.player2.hand = []

    wounded = place_card(gs, "TANKW", "player2", 0, 0)
    wounded.numbness = False
    wounded.health = 3
    wounded.max_health = 15

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type != "heal"


def test_heal_targets_wounded_friendly_when_counter_available():
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 0
    gs.number_of_heals["player2"] = 1
    gs.player2.hand = []

    wounded = place_card(gs, "TANKW", "player2", 0, 0)
    wounded.numbness = False
    wounded.health = 3
    wounded.max_health = 15

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "heal"
    assert (actions[0].board_x, actions[0].board_y) == (0, 0)


def test_heal_skipped_when_deficit_too_small():
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 0
    gs.number_of_heals["player2"] = 1
    gs.player2.hand = []

    almost_full = place_card(gs, "TANKW", "player2", 0, 0)
    almost_full.numbness = False
    almost_full.max_health = 15
    almost_full.health = 14

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type != "heal"


def test_heal_picks_critical_unit_over_lightly_chipped_one():
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 0
    gs.number_of_heals["player2"] = 1
    gs.player2.hand = []

    critical = place_card(gs, "TANKW", "player2", 0, 0)
    critical.numbness = False
    critical.max_health = 15
    critical.health = 2

    chipped = place_card(gs, "TANKW", "player2", 3, 3)
    chipped.numbness = False
    chipped.max_health = 15
    chipped.health = 10

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "heal"
    assert (actions[0].board_x, actions[0].board_y) == (0, 0)


def test_heal_runs_after_lethal_attack_priority():
    ai = AIController("boss", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 1
    gs.number_of_heals["player2"] = 1
    gs.player2.hand = []

    attacker = place_card(gs, Adc, "player2", 0, 1)
    attacker.numbness = False
    victim = place_card(gs, Ass, "player1", 0, 2)
    victim.numbness = False
    victim.health = 1

    wounded = place_card(gs, "TANKW", "player2", 3, 3)
    wounded.numbness = False
    wounded.max_health = 15
    wounded.health = 3

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "attack"
    assert (actions[0].board_x, actions[0].board_y) == (0, 1)
