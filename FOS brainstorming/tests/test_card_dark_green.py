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
from cards.card_dark_green import Adc, Ap, Tank, Hf, Lf, Ass, Apt
from cards.card_red import Adc as RedAdc

S = CARD_SETTING["DarkGreen"]


class TestDarkGreenAdc:
    def test_update_sets_extra_damage_from_totem(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        gs.players_totem["player1"] = 8

        adc.update(gs)
        assert adc.extra_damage == 8 // S["ADC"]["damage_divisor"]

    def test_damage_bonus_adds_extra_damage(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        adc.extra_damage = 3

        result = adc.damage_bonus(5, target, gs)
        assert result == 8


class TestDarkGreenAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True

    def test_ability_engraves_totem(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.players_totem["player1"]
        do_attack(ap, gs)
        assert gs.players_totem["player1"] == before + S["AP"]["engraved_totem"]


class TestDarkGreenTank:
    def test_been_attacked_engraves_totem(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 1)

        before = gs.players_totem["player1"]
        tank.been_attacked(enemy, 1, gs)
        assert gs.players_totem["player1"] == before + S["TANK"]["engraved_totem"]


class TestDarkGreenHf:
    def test_ability_heals_self(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)
        hf.health = hf.max_health - 2

        before = hf.health
        do_attack(hf, gs)
        assert hf.health > before

    def test_start_turn_damages_self_and_engraves_totem(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)

        before_health = hf.health
        before_totem = gs.players_totem["player1"]
        hf.on_refresh(gs)
        assert hf.health < before_health
        assert gs.players_totem["player1"] == before_totem + S["HF"]["engraved_totem"]


class TestDarkGreenLf:
    def test_ability_engraves_totem(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        place_card(gs, RedAdc, "player2", 2, 1)

        before = gs.players_totem["player1"]
        do_attack(lf, gs)
        assert gs.players_totem["player1"] == before + S["LF"]["engraved_totem"]


class TestDarkGreenAss:
    def test_kill_engraves_totem_and_zeroes_own_health(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        before_totem = gs.players_totem["player1"]
        do_attack(ass, gs)
        assert gs.players_totem["player1"] == before_totem + S["ASS"]["engraved_totem"]
        assert ass.health == 0


class TestDarkGreenApt:
    def test_update_sets_extra_damage_from_totem(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        gs.players_totem["player1"] = 6

        apt.update(gs)
        assert apt.extra_damage == 3

    def test_damage_bonus_adds_extra_damage(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        apt.extra_damage = 4

        result = apt.damage_bonus(5, target, gs)
        assert result == 9

    def test_after_damage_calculated_gains_armor(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)

        before = apt.armor
        apt.after_damage_calculated(target, 6, gs)
        assert apt.armor == before + 3
