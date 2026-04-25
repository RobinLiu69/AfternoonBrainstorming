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
from tests.helpers import make_game_state, place_card, do_attack
from cards.card_purple import Ap, Tank, Hf, Ass
from cards.card_red import Adc as RedAdc

S = CARD_SETTING["Purple"]


class TestPurpleAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True

    def test_ability_resets_target_armor_to_zero(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.armor = 10

        do_attack(ap, gs)
        assert target.armor == 0

    def test_ability_resets_target_damage_to_original(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.damage = target.original_damage + 5

        do_attack(ap, gs)
        assert target.damage == target.original_damage


class TestPurpleTank:
    def test_move_broadcast_damages_enemy(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 0, 0)
        enemy = place_card(gs, RedAdc, "player2", 1, 0)

        before = enemy.health
        tank.move_broadcast(enemy, gs)
        assert enemy.health == before - S["TANK"]["movement_damage"]

    def test_move_broadcast_does_not_damage_ally(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 0, 0)
        ally = place_card(gs, RedAdc, "player1", 0, 1)

        before = ally.health
        result = tank.move_broadcast(ally, gs)
        assert result is False
        assert ally.health == before


class TestPurpleHf:
    def test_start_turn_adds_attacks_per_three_enemies_in_range(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, RedAdc, "player2", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)
        place_card(gs, RedAdc, "player2", 2, 0)

        before = gs.number_of_attacks["player1"]
        hf.on_refresh(gs)
        assert gs.number_of_attacks["player1"] == before + 1

    def test_start_turn_no_bonus_when_fewer_than_three_enemies(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, RedAdc, "player2", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.number_of_attacks["player1"]
        hf.on_refresh(gs)
        assert gs.number_of_attacks["player1"] == before


class TestPurpleAss:
    def test_kill_draws_card_when_enemy_outnumbers(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        place_card(gs, RedAdc, "player2", 2, 1)
        place_card(gs, RedAdc, "player2", 2, 2)
        place_card(gs, RedAdc, "player2", 3, 0)
        enemy.health = 1

        before = gs.card_to_draw["player1"]
        do_attack(ass, gs)
        assert gs.card_to_draw["player1"] > before

    def test_no_draw_when_gap_insufficient(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        place_card(gs, RedAdc, "player2", 2, 1)
        enemy.health = 1

        before = gs.card_to_draw["player1"]
        do_attack(ass, gs)
        assert gs.card_to_draw["player1"] == before
