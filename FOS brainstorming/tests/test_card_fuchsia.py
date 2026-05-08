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
from cards.card_fuchsia import Adc, Ap, Ass, Apt, Hf, Sp
from cards.card_red import Adc as RedAdc, Tank as RedTank

S = CARD_SETTING["Fuchsia"]


class TestFuchsiaAdc:
    def test_deploy_spawns_shadow_at_symmetric_position(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)

        adc.deploy(gs)
        assert len(adc.shadows) == 1
        sx, sy = gs.board_config.get_symmetric_pos(0, 0)
        assert adc.shadows[0].board_x == sx
        assert adc.shadows[0].board_y == sy

    def test_attack_also_triggers_shadow_attack(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        enemy = place_card(gs, RedTank, "player2", 3, 0)
        
        before = enemy.health

        adc.deploy(gs)

        do_attack(adc, gs)
        
        assert enemy.health == before - adc.damage * 2


class TestFuchsiaAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True


class TestFuchsiaHf:
    def test_attack_also_triggers_shadow_attack(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        enemy = place_card(gs, RedTank, "player2", 1, 2)

        before = enemy.health

        hf.deploy(gs)

        do_attack(hf, gs)

        assert enemy.health == before - hf.damage * 2


class TestFuchsiaAss:
    def test_killed_spawns_shadow_at_victim_position(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        do_attack(ass, gs)
        assert len(ass.shadows) == 1
        assert ass.shadows[0].board_x == 2
        assert ass.shadows[0].board_y == 0

    def test_spawned_shadow_attacks_normally(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        victim = place_card(gs, RedTank, "player2", 2, 2)
        victim.health = 1

        do_attack(ass, gs)

        enemy = place_card(gs, RedTank, "player2", 3, 3)
        before = enemy.health

        do_attack(ass, gs)

        assert enemy.health == before - ass.damage

    def test_shadow_kill_spawns_shadow_at_victim_position(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        first_victim = place_card(gs, RedTank, "player2", 2, 2)
        first_victim.health = 1

        do_attack(ass, gs)

        second_victim = place_card(gs, RedTank, "player2", 3, 3)
        second_victim.health = 1

        do_attack(ass, gs)

        assert len(ass.shadows) == 2
        positions = {(s.board_x, s.board_y) for s in ass.shadows}
        assert (3, 3) in positions


class TestFuchsiaSp:
    def test_deploy_spawns_immovable_shadow_on_farthest_fuchsia_ally(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        near_ally = place_card(gs, Adc, "player1", 1, 0)
        far_ally = place_card(gs, Hf, "player1", 3, 2)

        sp.deploy(gs)

        sx, sy = gs.board_config.get_symmetric_pos(0, 0)
        assert len(far_ally.shadows) == 1
        assert len(near_ally.shadows) == 0
        assert (far_ally.shadows[0].board_x, far_ally.shadows[0].board_y) == (sx, sy)
        assert far_ally.shadows[0].movable is False
        assert far_ally.shadows[0].attack_types == far_ally.attack_types


class TestFuchsiaApt:
    def test_deploy_spawns_shadow(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)

        apt.deploy(gs)
        assert len(apt.shadows) == 1

    def test_shadow_damage_block_gives_linker_armor(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        apt.deploy(gs)
        shadow = apt.shadows[0]

        attacker = place_card(gs, RedAdc, "player2", 1, 0)
        before = apt.armor
        shadow.damage_block(4, attacker, gs)
        assert apt.armor == before + 2

    def test_on_field_effect_trigger_gains_armor_when_shadow_covers_ally(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        apt.deploy(gs)
        shadow = apt.shadows[0]
        ally = place_card(gs, RedAdc, "player1", shadow.board_x, shadow.board_y)
        attacker = place_card(gs, RedAdc, "player2", 1, 0)

        before = apt.armor
        result = apt.on_field_effect_trigger(ally, 10, attacker, gs)
        assert result is not None
        assert apt.armor == before + 5
