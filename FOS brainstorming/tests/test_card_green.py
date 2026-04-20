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

from core.setting import CARD_SETTING
from tests.helpers import make_game_state, place_card, do_attack
from cards.card_green import Ap, Hf, Ass, Apt, Sp, LuckyBlock
from cards.card_red import Adc as RedAdc

S = CARD_SETTING["Green"]


class TestGreenAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True


class TestGreenHf:
    def test_ability_against_luckyblock_increases_luck(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        lb = place_card(gs, LuckyBlock, "player2", 1, 0)

        before = gs.players_luck["player1"]
        hf.ability(lb, gs)
        assert gs.players_luck["player1"] == before + S["HF"]["luck_increase"]

    def test_ability_against_non_luckyblock_no_luck_change(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.players_luck["player1"]
        hf.ability(target, gs)
        assert gs.players_luck["player1"] == before


class TestGreenAss:
    def test_kill_increases_own_luck_and_decreases_opponent(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        before_own = gs.players_luck["player1"]
        before_opponent = gs.players_luck["player2"]
        do_attack(ass, gs)
        assert gs.players_luck["player1"] == before_own + 5
        assert gs.players_luck["player2"] == before_opponent - S["ASS"]["luck_increase"]


class TestGreenApt:
    def test_start_turn_spawns_luckyblocks_on_adjacent_cells(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)

        before = len(gs.neutral.on_board)
        apt.start_turn(gs)
        assert len(gs.neutral.on_board) == before + 4


class TestGreenSp:
    def test_deploy_increases_luck(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)

        before = gs.players_luck["player1"]
        sp.deploy(gs)
        assert gs.players_luck["player1"] == before + S["SP"]["luck_increase"]

    def test_deploy_spawns_luckyblock_when_luck_sufficient(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        gs.players_luck["player1"] = 50

        before = len(gs.neutral.on_board)
        sp.deploy(gs)
        assert len(gs.neutral.on_board) == before + 1
