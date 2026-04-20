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
from cards.card_orange import Adc, Ap, Tank, Hf, Lf, Ass, Apt, Sp
from cards.card_red import Adc as RedAdc, Tank as RedTank

S = CARD_SETTING["Orange"]


class TestOrangeAdc:
    def test_sets_moving_after_attack(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, RedTank, "player2", 2, 0)
        adc.numbness = False

        adc.attack(gs)
        assert adc.moving is True


class TestOrangeAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True

    def test_start_turn_adds_move_card_to_hand(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)

        before = len(gs.get_player("player1").hand)
        ap.start_turn(gs)
        assert len(gs.get_player("player1").hand) == before + 1
        assert gs.get_player("player1").hand[-1] == "MOVEO"


class TestOrangeTank:
    def test_been_attacked_adds_move_card_to_hand(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 1)

        before = len(gs.get_player("player1").hand)
        tank.been_attacked(enemy, 1, gs)
        assert len(gs.get_player("player1").hand) == before + 1
        assert gs.get_player("player1").hand[-1] == "MOVEO"


class TestOrangeHf:
    def test_after_movement_adds_extra_damage_and_anger(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)

        before = hf.extra_damage
        hf.after_movement(1, 0, gs)
        assert hf.extra_damage == before + S["HF"]["extra_damage_from_moving"]
        assert hf.anger is True

    def test_damage_bonus_adds_extra_damage(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        hf.extra_damage = 3

        result = hf.damage_bonus(5, target, gs)
        assert result == 8


class TestOrangeLf:
    def test_sets_moving_after_attack(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 0, 0)
        place_card(gs, RedTank, "player2", 1, 0)
        lf.numbness = False

        lf.attack(gs)
        assert lf.moving is True

    def test_after_movement_damages_nearest_enemy(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 1)

        before = enemy.health
        lf.after_movement(1, 1, gs)
        assert enemy.health < before


class TestOrangeAss:
    def test_after_movement_sets_anger(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 0, 0)

        ass.after_movement(1, 0, gs)
        assert ass.anger is True

    def test_kill_with_anger_increases_attack_count(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1
        ass.anger = True

        before = gs.number_of_attacks["player1"]
        do_attack(ass, gs)
        assert gs.number_of_attacks["player1"] == before + S["ASS"]["number_of_attack_increase_from_killed"]

    def test_kill_without_anger_no_attack_count_increase(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1
        ass.anger = False

        before = gs.number_of_attacks["player1"]
        do_attack(ass, gs)
        assert gs.number_of_attacks["player1"] == before


class TestOrangeApt:
    def test_after_movement_converts_armor_to_damage(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        apt.armor = 1

        before_damage = apt.damage
        apt.after_movement(1, 0, gs)
        assert apt.damage == before_damage + 1
        assert apt.armor == 0

    def test_move_broadcast_gives_ally_and_self_armor(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        ally = place_card(gs, RedAdc, "player1", 0, 1)

        before_apt = apt.armor
        before_ally = ally.armor
        apt.move_broadcast(ally, gs)
        assert apt.armor  == before_apt  + S["APT"]["armor_get_from_moving"]
        assert ally.armor == before_ally + S["APT"]["armor_get_from_moving"]


class TestOrangeSp:
    def test_move_broadcast_to_ally_damages_farthest_enemy(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        ally = place_card(gs, RedAdc, "player1", 0, 1)
        enemy = place_card(gs, RedAdc, "player2", 3, 3)

        before = enemy.health
        sp.move_broadcast(ally, gs)
        assert enemy.health < before
