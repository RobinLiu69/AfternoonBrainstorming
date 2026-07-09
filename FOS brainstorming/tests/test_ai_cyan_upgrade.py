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

from shared.setting import CARD_SETTING
from campaign.ai_controller import AIController
from tests.helpers import make_game_state, place_card


def _controller() -> AIController:
    ai = AIController("white", player_name="player2")
    ai.strategy.placement_min_score = -999.0
    ai.strategy.attack_min_score = 999.0
    return ai


def test_toggles_upgrade_then_plays_same_cell():
    ai = _controller()
    gs = make_game_state()
    gs.turn_number = 1
    gs.player2.hand = ["ADCC"]
    gs.players_coin["player2"] = 50

    action = ai._decide_next(gs)
    assert action is not None
    assert action.action_type == "toggle_upgrade"
    assert action.hand_index == 0

    idx, x, y = ai._pending_upgrade_play
    gs.player2.hand[idx] = "ADCC (+)"
    follow = ai._decide_next(gs)
    assert follow.action_type == "play_card"
    assert follow.hand_index == idx
    assert (follow.board_x, follow.board_y) == (x, y)


def test_plays_base_card_when_coins_short():
    ai = _controller()
    gs = make_game_state()
    gs.turn_number = 1
    gs.player2.hand = ["ADCC"]
    gs.players_coin["player2"] = CARD_SETTING["Cyan"]["ADC"]["cost"] - 1

    action = ai._decide_next(gs)
    assert action.action_type == "play_card"


def test_reverts_upgrade_when_cell_becomes_occupied():
    ai = _controller()
    gs = make_game_state()
    gs.turn_number = 1
    gs.player2.hand = ["TANKC"]
    gs.players_coin["player2"] = 50

    action = ai._decide_next(gs)
    assert action.action_type == "toggle_upgrade"
    idx, x, y = ai._pending_upgrade_play
    gs.player2.hand[idx] = "TANKC (+)"
    gs.board_dict[(x, y)].occupy = True

    revert = ai._decide_next(gs)
    assert revert.action_type == "toggle_upgrade"
    assert revert.hand_index == idx
    assert ai._pending_upgrade_play is None


def test_non_cyan_card_never_toggles():
    ai = _controller()
    gs = make_game_state()
    gs.turn_number = 1
    gs.player2.hand = ["ADCW"]
    gs.players_coin["player2"] = 50

    action = ai._decide_next(gs)
    assert action.action_type == "play_card"


def test_upgraded_spc_discounts_price():
    ai = _controller()
    gs = make_game_state()
    base_price = ai._cyan_upgrade_price(gs, "ADC")

    spc = place_card(gs, "SPC", "player2", 0, 0)
    spc.upgrade = True
    discounted = ai._cyan_upgrade_price(gs, "ADC")
    assert discounted == base_price - CARD_SETTING["Cyan"]["SP"]["cost_reduction"]
