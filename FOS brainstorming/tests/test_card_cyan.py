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
from cards.card_cyan import Adc, Ap, Tank, Hf, Lf, Ass, Apt
from cards.card_red import Adc as RedAdc, Tank as RedTank
from cards.card_green import LuckyBlock

S = CARD_SETTING["Cyan"]


class TestCyanAdc:
    def test_upgrade_double_strike_lands_twice(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        adc.upgrade = True
        adc.numbness = False
        enemy = place_card(gs, RedTank, "player2", 2, 0)
        enemy.health = adc.damage * 3

        before = enemy.health
        adc.attack(gs)

        assert enemy.health == before - adc.damage * 2

    def test_ability_grants_coins(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, RedTank, "player2", 2, 0)

        before = gs.players_coin["player1"]
        do_attack(adc, gs)
        assert gs.players_coin["player1"] >= before + S["ADC"]["coin_gets"]


class TestCyanAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True

    def test_ability_grants_coins(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.players_coin["player1"]
        do_attack(ap, gs)
        assert gs.players_coin["player1"] >= before + S["AP"]["coin_gets"]


class TestCyanTank:
    def test_been_attacked_grants_coins(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 1)

        before = gs.players_coin["player1"]
        tank.been_attacked(enemy, 1, gs)
        assert gs.players_coin["player1"] == before + S["TANK"]["coin_gets"]

    def test_upgrade_damage_block_absorbs_hit(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 0, 0)
        tank.anger = True
        enemy = place_card(gs, RedAdc, "player2", 1, 0)

        blocked = tank.damage_block(5, enemy, gs)
        assert blocked is True
        assert tank.anger is False


class TestCyanHf:
    def test_ability_grants_coins(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.players_coin["player1"]
        do_attack(hf, gs)
        assert gs.players_coin["player1"] >= before + S["HF"]["coin_gets"]

    def test_upgrade_been_killed_sets_anger_and_boosts_damage(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        hf.upgrade = True
        enemy = place_card(gs, RedAdc, "player2", 1, 0)

        before_damage = hf.damage
        hf.been_killed(enemy, gs)
        assert hf.anger is True
        assert hf.damage == before_damage + S["HF"]["damage_bonus"]

    def test_can_be_killed_false_when_angry(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        hf.anger = True

        assert hf.can_be_killed(gs) is False

    def test_upgrade_lethal_hit_does_not_set_pending_death(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        hf.upgrade = True
        enemy = place_card(gs, RedAdc, "player2", 1, 0)
        hf.health = enemy.damage  # exactly lethal

        hf.damage_calculate(enemy.damage, enemy, gs)

        assert hf.health == 0
        assert hf.anger is True
        assert hf.pending_death is False

    def test_upgrade_lethal_hit_does_not_emit_death_event(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        hf.upgrade = True
        enemy = place_card(gs, RedAdc, "player2", 1, 0)
        hf.health = enemy.damage  # exactly lethal

        hf.damage_calculate(enemy.damage, enemy, gs)

        death_events = [e for e in gs.pending_combat_events if e.kind == "death"]
        assert len(death_events) == 0


class TestCyanLf:
    def test_ability_grants_coins(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        place_card(gs, RedAdc, "player2", 2, 1)

        before = gs.players_coin["player1"]
        do_attack(lf, gs)
        assert gs.players_coin["player1"] >= before + S["LF"]["coin_gets"]


class TestCyanAss:
    def test_kill_grants_coins(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        before = gs.players_coin["player1"]
        do_attack(ass, gs)
        assert gs.players_coin["player1"] >= before + S["ASS"]["coin_gets"]

    def test_damage_bonus_adds_extra_damage(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        ass.extra_damage = S["ASS"]["damage_bonus"]

        result = ass.damage_bonus(3, target, gs)
        assert result == 3 + S["ASS"]["damage_bonus"]
        assert ass.extra_damage == 0


class TestCyanApt:
    def test_damage_reduce_by_coins(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        gs.players_coin["player1"] = 10

        result = apt.damage_reduce(5, gs)
        assert result == 5 - (10 // S["APT"]["coin_per_damage_resistance"])

    def test_damage_reduce_capped_at_maximum(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        gs.players_coin["player1"] = 50

        result = apt.damage_reduce(10, gs)
        assert result == 10 - S["APT"]["maximum_damage_resistance"]
