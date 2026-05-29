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
    """AI shouldn't fire its next action while the renderer is still animating."""
    from shared.combat_event import CombatEvent
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.pending_combat_events.append(CombatEvent(kind="hurt", board_x=0, board_y=0))
    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert actions == []


def test_tick_waits_for_renderer_busy_signal():
    """`pending_combat_events` is cleared after one frame; `renderer_busy` is the
    follow-up signal for animations still mid-flight in combat_animator."""
    from campaign.ai_controller import AI_BUSY_RECHECK_MS
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    ai.tick(gs, 0, renderer_busy=True)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1, renderer_busy=True)
    assert actions == []
    # After the busy gate clears, the AI still respects its busy-recheck delay.
    later = AI_TURN_START_DELAY_MS + 1 + AI_BUSY_RECHECK_MS + 5
    actions_after = ai.tick(gs, later, renderer_busy=False)
    assert len(actions_after) == 1


def test_prefers_lethal_board_attack_over_placement():
    """A killing strike from an existing unit is cheaper than placing — go for the attack."""
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


def test_attacks_chip_damage_when_trailing_in_score():
    """When losing, the AI must spend attacks on chip damage rather than hoarding them."""
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []
    gs.score = -7  # player2 (AI) badly losing

    attacker = place_card(gs, Adc, "player2", 0, 0)
    attacker.numbness = False
    chump = place_card(gs, Adc, "player1", 1, 0)
    chump.numbness = False
    chump.damage = 1  # forces non-lethal chip — score ~11 normally below threshold

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "attack"


def test_saves_attacks_when_only_low_value_chips_available():
    """attack_min_score gates chip damage; with no kill in sight AI should hoard attacks."""
    ai = AIController("white", player_name="player2")
    gs = make_game_state()
    _ai_turn(gs)
    gs.number_of_attacks["player2"] = 1
    gs.player2.hand = []

    # Use TANKW as attacker (1 dmg) and a non-priority TANKW target so the chip
    # score stays well below white's threshold even with the new target-priority
    # bonus (which only fires for ADC / SP).
    attacker = place_card(gs, "TANKW", "player2", 0, 0)
    attacker.numbness = False
    chump = place_card(gs, "TANKW", "player1", 1, 0)
    chump.numbness = False

    ai.tick(gs, 0)
    actions = ai.tick(gs, AI_TURN_START_DELAY_MS + 1)
    assert len(actions) == 1
    assert actions[0].action_type == "end_turn"


def test_holds_ass_in_hand_when_no_kill_or_defense_available():
    """No killable enemy and no friendly to defend — ASS in hand stays as a threat."""
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
    """With ASS in hand and a killable enemy in small_x range, AI should place ASS to kill — not a stat-dump ADC elsewhere."""
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
