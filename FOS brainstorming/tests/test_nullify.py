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

from tests.helpers import make_game_state, place_card, do_attack
from cards.factory import CardFactory
from cards.card_white import Ap as WhiteAp
from cards.card_blue import Tank as BlueTank, Apt as BlueApt
from cards.card_cyan import Adc as CyanAdc, Apt as CyanApt
from cards.card_red import Adc as RedAdc, Tank as RedTank, Hf as RedHf
from cards.card_fuchsia import Apt as FuchsiaApt, Ass as FuchsiaAss


class TestNullifiedAttacker:
    def test_ability_does_not_fire_but_damage_still_lands(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, WhiteAp, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False
        before = target.health

        ap.nullify = True
        do_attack(ap, gs)

        assert target.numbness is False
        assert target.health == before - ap.damage

    def test_custom_attack_falls_back_to_plain_attack(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, CyanAdc, "player1", 0, 0)
        adc.upgrade = True
        enemy = place_card(gs, RedTank, "player2", 1, 0)
        before = enemy.health

        adc.nullify = True
        do_attack(adc, gs)

        assert enemy.health == before - adc.damage

    def test_upgraded_cyan_adc_attacks_twice_when_not_nullified(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, CyanAdc, "player1", 0, 0)
        adc.upgrade = True
        enemy = place_card(gs, RedTank, "player2", 1, 0)
        before = enemy.health

        do_attack(adc, gs)

        assert enemy.health == before - adc.damage * 2

    def test_killed_hook_does_not_fire(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, FuchsiaAss, "player1", 1, 1)
        victim = place_card(gs, RedAdc, "player2", 2, 2)
        victim.health = 1

        ass.nullify = True
        do_attack(ass, gs)

        assert victim.health == 0
        assert len(ass.shadows) == 0


class TestNullifiedVictim:
    def test_been_attacked_does_not_fire_but_damage_still_lands(self) -> None:
        gs = make_game_state()
        attacker = place_card(gs, RedAdc, "player1", 0, 0)
        tank = place_card(gs, BlueTank, "player2", 1, 0)
        before = tank.health

        tank.nullify = True
        do_attack(attacker, gs)

        assert gs.players_token["player2"] == 0
        assert tank.health < before

    def test_damage_reduce_is_ignored(self) -> None:
        gs = make_game_state()
        gs.players_coin["player1"] = 50
        attacker = place_card(gs, RedAdc, "player2", 1, 0)
        apt = place_card(gs, CyanApt, "player1", 0, 0)
        apt.upgrade = True
        apt.health = 10
        apt.max_health = 10

        apt.damage_calculate(5, attacker, gs)
        assert apt.health == 8

        apt.nullify = True
        apt.damage_calculate(5, attacker, gs)
        assert apt.health == 3

    def test_can_be_killed_override_is_ignored(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, RedHf, "player1", 0, 0)
        hf.anger = True

        assert hf.can_be_killed(gs) is False

        hf.nullify = True
        assert hf.can_be_killed(gs) is True


class TestNullifiedFieldEffects:
    def test_nullified_card_does_not_intercept_damage(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, FuchsiaApt, "player1", 0, 0)
        apt.deploy(gs)
        shadow = apt.shadows[0]
        ally = place_card(gs, RedAdc, "player1", shadow.board_x, shadow.board_y)
        attacker = place_card(gs, RedAdc, "player2", 1, 0)
        before = ally.health

        apt.nullify = True
        ally.damage_calculate(4, attacker, gs)

        assert apt.armor == 0
        assert ally.health == before - 4

    def test_field_effects_chain_instead_of_overwriting(self) -> None:
        gs = make_game_state()
        apt1 = place_card(gs, FuchsiaApt, "player1", 0, 0)
        apt2 = place_card(gs, FuchsiaApt, "player1", 3, 0)
        ally = place_card(gs, RedAdc, "player1", 2, 2)
        apt1.spawn_shadow("player1", 2, 2)
        apt2.spawn_shadow("player1", 2, 2)
        attacker = place_card(gs, RedAdc, "player2", 1, 2)
        ally.health = 20

        ally.damage_calculate(10, attacker, gs)

        assert apt1.armor == 5
        assert apt2.armor == 2
        assert ally.health == 17


class TestNullifiedColorHooks:
    def test_blue_after_token_does_not_fire(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, BlueTank, "player1", 0, 0)
        apt = place_card(gs, BlueApt, "player1", 1, 1)

        tank.got_token(gs)
        assert apt.armor == 1

        apt.nullify = True
        tank.got_token(gs)
        assert apt.armor == 1


class TestNullifySerialization:
    def test_nullify_round_trips_through_dict(self) -> None:
        gs = make_game_state()
        card = place_card(gs, RedAdc, "player1", 0, 0)
        card.nullify = True

        data = card.to_dict()
        assert data["nullify"] is True

        clone = CardFactory.from_dict(data)
        assert clone.nullify is True
