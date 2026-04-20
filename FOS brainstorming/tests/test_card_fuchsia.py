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
from cards.card_fuchsia import Adc, Ap, Ass, Apt
from cards.card_red import Adc as RedAdc

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


class TestFuchsiaAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True


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
