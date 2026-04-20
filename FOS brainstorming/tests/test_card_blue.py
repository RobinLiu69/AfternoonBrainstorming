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
from cards.card_blue import Adc, Ap, Tank, Hf, Lf, Ass, Apt
from cards.card_red import Adc as RedAdc, Tank as RedTank

S = CARD_SETTING["Blue"]
TOKEN_THRESHOLD = 3


class TestBlueAdc:
    def test_kill_grants_tokens(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 3, 1)
        enemy.health = 1

        before = gs.players_token["player1"]
        do_attack(adc, gs)
        assert gs.players_token["player1"] >= before + S["ADC"]["token_gets"]

    def test_kill_triggers_draw_at_threshold(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        gs.players_token["player1"] = TOKEN_THRESHOLD - S["ADC"]["token_gets"]
        before_draw = gs.card_to_draw["player1"]
        do_attack(adc, gs)
        assert gs.card_to_draw["player1"] > before_draw

    def test_token_draw_removes_numbness(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        adc.numbness = True

        adc.token_draw(gs)
        assert adc.numbness is False

    def test_token_draw_enqueues_attack_when_not_numb(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        adc.numbness = False

        adc.token_draw(gs)
        assert len(gs.pending_attacks) == 1


class TestBlueAp:
    def test_target_numbed(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True

    def test_tokens_granted_on_attack(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.players_token["player1"]
        do_attack(ap, gs)
        assert gs.players_token["player1"] >= before + S["AP"]["token_gets"]


class TestBlueTank:
    def test_tokens_granted_on_hit(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 1)

        before = gs.players_token["player1"]
        tank.damage_calculate(1, enemy, gs, ability=False)
        assert gs.players_token["player1"] == before + S["TANK"]["token_gets"]


class TestBlueHf:
    def test_extra_damage_matches_token_count(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        gs.players_token["player1"] = 5

        hf.update(gs)
        assert hf.extra_damage == 5

    def test_damage_bonus_adds_extra_damage(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 0, 1)

        gs.players_token["player1"] = 4
        hf.update(gs)

        result = hf.damage_bonus(hf.damage, target, gs)
        assert result == hf.damage + 4


class TestBlueLf:
    def test_tokens_granted_on_attack(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        place_card(gs, RedAdc, "player2", 2, 1)

        before = gs.players_token["player1"]
        do_attack(lf, gs)
        assert gs.players_token["player1"] >= before + S["LF"]["token_gets"]


class TestBlueAss:
    def test_tokens_granted_on_kill(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        before = gs.players_token["player1"]
        do_attack(ass, gs)
        assert gs.players_token["player1"] >= before + S["ASS"]["token_gets"]

    def test_no_tokens_without_kill(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        place_card(gs, RedTank, "player2", 2, 0)

        before = gs.players_token["player1"]
        do_attack(ass, gs)
        assert gs.players_token["player1"] == before


class TestBlueApt:
    def test_gains_armor_on_token(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)

        before = apt.armor
        apt.after_token(gs)
        assert apt.armor == before + 1

    def test_ability_generates_tokens_from_armor(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)

        divisor = S["APT"]["token_from_armor_divisor"]
        apt.armor = divisor * 2

        before = gs.players_token["player1"]
        do_attack(apt, gs)
        assert gs.players_token["player1"] >= before + 2
