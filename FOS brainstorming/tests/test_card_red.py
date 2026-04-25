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
from cards.card_red import Adc, Ap, Tank, Hf, Lf, Ass, Apt, Sp

S = CARD_SETTING["Red"]


class TestRedAdc:
    def test_damage_increases_after_attack(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, Tank, "player2", 2, 0)

        before = adc.damage
        do_attack(adc, gs)
        assert adc.damage == before + S["ADC"]["damage_increase"]

    def test_allied_sp_damage_increases_after_attack(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        sp = place_card(gs, Sp, "player1", 0, 1)
        place_card(gs, Tank, "player2", 2, 0)

        before = sp.damage
        do_attack(adc, gs)
        assert sp.damage == before + S["ADC"]["damage_increase"]

    def test_enemy_sp_not_buffed(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        enemy_sp = place_card(gs, Sp, "player2", 3, 0)
        place_card(gs, Tank, "player2", 2, 0)

        before = enemy_sp.damage
        do_attack(adc, gs)
        assert enemy_sp.damage == before

    def test_no_attack_when_no_target(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)

        before = adc.damage
        result = do_attack(adc, gs)
        assert result is False
        assert adc.damage == before


class TestRedAp:
    def test_target_becomes_numb(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, Adc, "player2", 1, 0)

        target.numbness = False
        do_attack(ap, gs)
        assert target.numbness is True

    def test_damage_stolen_from_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, Adc, "player2", 1, 0)

        steal = int(target.damage * (S["AP"]["attack_steal_rate"] / 100))
        ap_before = ap.damage
        target_before = target.damage

        do_attack(ap, gs)
        assert ap.damage     == ap_before + steal
        assert target.damage == target_before - steal

    def test_allied_sp_receives_stolen_damage(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        sp = place_card(gs, Sp, "player1", 0, 1)
        target = place_card(gs, Adc, "player2", 1, 0)

        steal = int(target.damage * (S["AP"]["attack_steal_rate"] / 100))
        sp_before = sp.damage
        do_attack(ap, gs)
        assert sp.damage == sp_before + steal


class TestRedTank:
    def test_nearest_ally_gains_armor_on_hit(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        ally = place_card(gs, Adc, "player1", 1, 2)
        enemy = place_card(gs, Adc, "player2", 2, 1)

        before = ally.armor
        tank.damage_calculate(1, enemy, gs, ability=False)
        assert ally.armor == before + S["TANK"]["armor_increase"]

    def test_allied_sp_gains_armor_on_hit(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        place_card(gs, Adc, "player1", 1, 2)
        sp = place_card(gs, Sp, "player1", 3, 3)
        enemy = place_card(gs, Adc, "player2", 2, 1)

        before = sp.armor
        tank.damage_calculate(1, enemy, gs, ability=False)
        assert sp.armor == before + S["TANK"]["armor_increase"]

    def test_tank_itself_not_double_armored(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 0, 0)
        enemy = place_card(gs, Adc, "player2", 1, 0)

        before = tank.armor
        tank.damage_calculate(1, enemy, gs, ability=False)
        assert tank.armor == before


class TestRedHf:
    def test_health_decreases_on_attack(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, Adc, "player2", 2, 1)

        before = hf.health
        do_attack(hf, gs)
        assert hf.health == before - S["HF"]["health_decrease"]

    def test_damage_increases_on_attack(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, Adc, "player2", 2, 1)

        before = hf.damage
        do_attack(hf, gs)
        assert hf.damage == before + S["HF"]["damage_increase"]

    def test_anger_activates_at_zero_health(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, Adc, "player2", 2, 1)

        hf.health = 1
        do_attack(hf, gs)
        assert hf.anger is True

    def test_anger_blocks_death(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        hf.anger = True
        assert hf.can_be_killed(gs) is False

    def test_no_anger_without_zero_health(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, Adc, "player2", 2, 1)

        hf.health = 5
        do_attack(hf, gs)
        assert hf.anger is False


class TestRedLf:
    def test_self_gains_armor_and_damage(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        place_card(gs, Adc, "player2", 2, 1)

        before_armor = lf.armor
        before_damage = lf.damage
        do_attack(lf, gs)
        assert lf.armor  == before_armor  + S["LF"]["armor_increase"]
        assert lf.damage == before_damage + S["LF"]["damage_increase"]

    def test_allied_sp_gains_armor_and_damage(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        sp = place_card(gs, Sp, "player1", 0, 0)
        place_card(gs, Adc, "player2", 2, 1)

        before_armor = sp.armor
        before_damage = sp.damage
        do_attack(lf, gs)
        assert sp.armor  == before_armor  + S["LF"]["armor_increase"]
        assert sp.damage == before_damage + S["LF"]["damage_increase"]


class TestRedAss:
    def test_nearest_ally_buffed_on_kill(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        ally = place_card(gs, Adc, "player1", 1, 2)
        enemy = place_card(gs, Adc, "player2", 2, 0)
        enemy.health = 1

        before = ally.damage
        do_attack(ass, gs)
        assert ally.damage == before + S["ASS"]["damage_increase"]

    def test_allied_sp_buffed_on_kill(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        place_card(gs, Adc, "player1", 1, 2)
        sp = place_card(gs, Sp, "player1", 3, 3)
        enemy = place_card(gs, Adc, "player2", 2, 0)
        enemy.health = 1

        before = sp.damage
        do_attack(ass, gs)
        assert sp.damage == before + S["ASS"]["damage_increase"]

    def test_no_buff_when_no_kill(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        ally = place_card(gs, Adc, "player1", 1, 2)
        place_card(gs, Tank, "player2", 2, 0)

        before = ally.damage
        do_attack(ass, gs)
        assert ally.damage == before


class TestRedApt:
    def test_self_gains_stats(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        place_card(gs, Tank, "player2", 1, 0)

        before_armor = apt.armor
        before_damage = apt.damage
        do_attack(apt, gs)
        assert apt.armor  == before_armor  + S["APT"]["armor_increase"]
        assert apt.damage == before_damage + S["APT"]["damage_increase"]

    def test_nearest_ally_gains_stats(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        ally = place_card(gs, Adc, "player1", 0, 1)
        place_card(gs, Tank, "player2", 1, 0)

        before_armor = ally.armor
        before_damage = ally.damage
        do_attack(apt, gs)
        assert ally.armor  == before_armor  + S["APT"]["armor_increase"]
        assert ally.damage == before_damage + S["APT"]["damage_increase"]

    def test_allied_sp_gains_stats(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        place_card(gs, Adc, "player1", 0, 1)
        sp = place_card(gs, Sp, "player1", 3, 3)
        place_card(gs, Tank, "player2", 1, 0)

        before_armor = sp.armor
        before_damage = sp.damage
        do_attack(apt, gs)
        assert sp.armor  == before_armor  + S["APT"]["armor_increase"]
        assert sp.damage == before_damage + S["APT"]["damage_increase"]
