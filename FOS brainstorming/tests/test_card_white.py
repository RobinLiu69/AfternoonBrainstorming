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
from cards.card_white import Ap, Apt, Sp
from cards.card_red import Adc as RedAdc

S = CARD_SETTING["White"]


class TestWhiteAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True


class TestWhiteApt:
    def test_ability_gives_self_and_nearest_ally_armor(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        ally = place_card(gs, RedAdc, "player1", 0, 1)
        place_card(gs, RedAdc, "player2", 1, 0)

        before_apt = apt.armor
        before_ally = ally.armor
        do_attack(apt, gs)
        assert apt.armor  == before_apt  + apt.damage
        assert ally.armor == before_ally + apt.damage


class TestWhiteSp:
    def test_end_turn_returns_extra_score_when_not_numb(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        sp.numbness = False

        result = sp.on_settle()
        assert result == 1 + S["SP"]["extra_score"]

    def test_end_turn_returns_zero_when_numb(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        sp.numbness = True

        result = sp.on_settle()
        assert result == 0
