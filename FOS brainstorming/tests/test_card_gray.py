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

from cards.base import Card
from cards.card_gray import Adc, Ap, Apt, Ass, Hf, Lf, Sp, Tank, Wight
from cards.card_white import Adc as WhiteAdc, Tank as WhiteTank
from core.game_state import GameState
from shared.card_code import BARROW_CODE, WIGHT_CODE
from shared.setting import CARD_SETTING
from tests.helpers import make_game_state, place_card

S = CARD_SETTING["Gray"]


def attack_with(card: Card, game_state: GameState) -> bool:
    card.numbness = False
    return card.attack(game_state)


def kill_off(card: Card, game_state: GameState) -> None:
    game_state.judge.deal(card.health + card.armor, card, game_state)
    game_state.get_player(card.owner).recycle_cards(game_state, _Sink())


class _Sink:
    def __init__(self) -> None:
        self.dying_cards: list[Card] = []


def barrows(game_state: GameState, owner: str) -> int:
    return game_state.get_player(owner).hand.count(BARROW_CODE)


class TestBarrowGeneration:
    def test_any_wight_card_dying_hands_its_owner_a_barrow(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 0, 0)

        kill_off(tank, gs)
        assert barrows(gs, "player1") == 1

    def test_a_summoned_wight_dying_hands_out_nothing(self) -> None:
        gs = make_game_state()
        wight = place_card(gs, Wight, "player1", 0, 0)

        kill_off(wight, gs)
        assert barrows(gs, "player1") == 0

    def test_a_nullified_card_dying_hands_out_nothing(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 0, 0)
        tank.nullify = True

        kill_off(tank, gs)
        assert barrows(gs, "player1") == 0

    def test_a_dead_wight_never_reaches_the_discard_pile(self) -> None:
        gs = make_game_state()
        wight = place_card(gs, Wight, "player1", 0, 0)

        kill_off(wight, gs)
        assert gs.get_player("player1").discard_pile == []

    def test_playing_a_barrow_summons_a_wight_and_spends_the_card(self) -> None:
        gs = make_game_state()
        player = gs.get_player("player1")
        player.hand.append(BARROW_CODE)

        player.play_card(2, 2, 0, gs)

        assert player.hand == []
        assert player.discard_pile == []
        assert [c.job_and_color for c in player.on_board] == [WIGHT_CODE]

    def test_a_barrow_played_onto_a_taken_cell_stays_in_hand(self) -> None:
        gs = make_game_state()
        player = gs.get_player("player1")
        place_card(gs, WhiteAdc, "player1", 2, 2)
        player.hand.append(BARROW_CODE)

        player.play_card(2, 2, 0, gs)

        assert player.hand == [BARROW_CODE]


class TestWight:
    def test_it_enters_awake_but_cannot_spend_a_knife(self) -> None:
        gs = make_game_state()
        wight = place_card(gs, Wight, "player1", 1, 1)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        assert wight.numbness is False
        assert wight.attack(gs) is False

    def test_it_never_scores(self) -> None:
        gs = make_game_state()
        wight = place_card(gs, Wight, "player1", 1, 1)

        wight.settle(gs)
        assert gs.score == 0

    def test_it_can_move_and_be_healed(self) -> None:
        gs = make_game_state()
        wight = place_card(gs, Wight, "player1", 1, 1)
        wight.health = 1

        assert wight.heal(1, gs) is True
        assert wight.health == S["WIGHT"]["health"]

        wight.moving = True
        assert wight.move(1, 2, gs) is True


class TestGrayAdc:
    def test_its_wights_fire_for_its_own_damage(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, Wight, "player1", 0, 1)
        target = place_card(gs, WhiteTank, "player2", 1, 1)
        victim = place_card(gs, WhiteTank, "player2", 3, 0)
        before_target = target.health
        before_victim = victim.health

        assert attack_with(adc, gs) is True
        assert victim.health == before_victim - adc.damage
        assert target.health == before_target - adc.damage

    def test_wights_outside_the_attack_range_stay_put(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, Wight, "player1", 1, 1)
        place_card(gs, WhiteTank, "player2", 3, 0)
        target = place_card(gs, WhiteTank, "player2", 2, 1)
        before = target.health

        attack_with(adc, gs)
        assert target.health == before

    def test_an_enemy_wight_is_never_conscripted(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, Wight, "player2", 0, 1)
        target = place_card(gs, WhiteTank, "player2", 3, 0)
        before = target.health

        attack_with(adc, gs)
        assert target.health == before - adc.damage

    def test_a_whiffed_attack_conscripts_nobody(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)
        place_card(gs, Wight, "player1", 0, 1)

        assert attack_with(adc, gs) is False

    def test_dying_hands_out_two_barrows(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 0, 0)

        kill_off(adc, gs)
        assert barrows(gs, "player1") == 1 + S["ADC"]["extra_barrow_on_death"]


class TestGrayAp:
    def test_landing_an_attack_hands_out_a_barrow(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 1, 1)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        attack_with(ap, gs)
        assert barrows(gs, "player1") == S["AP"]["barrow_on_attack"]

    def test_a_whiffed_attack_hands_out_nothing(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 1, 1)

        attack_with(ap, gs)
        assert barrows(gs, "player1") == 0


class TestGrayTank:
    def test_being_hit_splashes_itself_and_the_nearest_enemy(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        attacker = place_card(gs, WhiteTank, "player2", 1, 2)
        reflect = S["TANK"]["reflect_damage"]
        before_tank = tank.health
        before_attacker = attacker.health

        attack_with(attacker, gs)

        assert tank.health == before_tank - attacker.damage - reflect
        assert attacker.health == before_attacker - reflect

    def test_two_of_them_trading_hits_terminates(self) -> None:
        gs = make_game_state()
        mine = place_card(gs, Tank, "player1", 1, 1)
        theirs = place_card(gs, Tank, "player2", 1, 2)
        reflect = S["TANK"]["reflect_damage"]

        attack_with(theirs, gs)

        assert mine.health == mine.max_health - theirs.damage - reflect * 2
        assert theirs.health == theirs.max_health - reflect * 2


class TestGrayHf:
    def test_its_wights_fire_for_a_flat_two(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        place_card(gs, Wight, "player1", 1, 2)
        place_card(gs, WhiteTank, "player2", 0, 1)
        victim = place_card(gs, WhiteTank, "player2", 1, 3)
        before = victim.health

        assert attack_with(hf, gs) is True
        assert victim.health == before - S["HF"]["wight_strike_damage"]

    def test_dying_shrinks_the_enemies_it_covered(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        near = place_card(gs, WhiteTank, "player2", 1, 2)
        far = place_card(gs, WhiteTank, "player2", 3, 3)
        debuff = S["HF"]["on_death_enemy_debuff"]
        near_health = near.health
        near_damage = near.damage

        kill_off(hf, gs)

        assert near.health == near_health - debuff["health"]
        assert near.display_health == near.health
        assert near.damage == near_damage - debuff["atk"]
        assert far.health == far.max_health

    def test_the_debuff_never_pushes_stats_below_zero(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        target = place_card(gs, WhiteTank, "player2", 1, 2)
        target.health = 1
        target.damage = 0

        kill_off(hf, gs)

        assert target.health == 0
        assert target.damage == 0


class TestGrayLf:
    def test_entering_eats_the_nearest_ally_for_shield_and_damage(self) -> None:
        gs = make_game_state()
        food = place_card(gs, WhiteTank, "player1", 0, 1)
        food.health -= 3
        food.damage += 2
        stolen_health = food.health
        stolen_damage = food.damage

        lf = Lf("player1", 0, 0)
        lf.deploy(gs)

        assert lf.armor == stolen_health
        assert lf.extra_damage == stolen_damage
        assert food.health == 0

    def test_the_eaten_ally_still_pays_out_its_barrow(self) -> None:
        gs = make_game_state()
        place_card(gs, Tank, "player1", 0, 1)

        lf = Lf("player1", 0, 0)
        lf.deploy(gs)
        gs.get_player("player1").recycle_cards(gs, _Sink())

        assert barrows(gs, "player1") == 1

    def test_entering_alone_is_harmless(self) -> None:
        gs = make_game_state()

        lf = Lf("player1", 0, 0)
        lf.deploy(gs)

        assert lf.armor == 0
        assert lf.extra_damage == 0


class TestGrayAss:
    def test_a_kill_sharpens_it(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        prey = place_card(gs, WhiteAdc, "player2", 2, 2)
        prey.health = 1
        before = ass.damage

        attack_with(ass, gs)
        assert ass.damage == before + S["ASS"]["damage_gain_per_kill"]

    def test_dying_unsharpened_hands_out_the_base_barrow_only(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)

        kill_off(ass, gs)
        assert barrows(gs, "player1") == 1

    def test_every_point_of_damage_past_four_is_another_barrow(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        ass.damage = S["ASS"]["barrow_damage_threshold"] + 3

        kill_off(ass, gs)
        assert barrows(gs, "player1") == 4


class TestGrayApt:
    def test_dying_buffs_the_nearest_ally(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)
        ally = place_card(gs, WhiteTank, "player1", 1, 2)
        buff = S["APT"]["on_death_ally_buff"]
        before_damage = ally.damage

        kill_off(apt, gs)

        assert ally.armor == buff["armor"]
        assert ally.damage == before_damage + buff["atk"]

    def test_dying_alone_is_harmless(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)

        kill_off(apt, gs)
        assert barrows(gs, "player1") == 1


class TestGraySp:
    def test_every_friendly_wight_fires_wherever_it_stands(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        place_card(gs, Wight, "player1", 0, 1)
        far = place_card(gs, WhiteTank, "player2", 3, 3)
        near = place_card(gs, WhiteTank, "player2", 1, 0)
        before_far = far.health
        before_near = near.health

        assert attack_with(sp, gs) is True

        assert far.health == before_far - sp.damage
        assert near.health == before_near - S["SP"]["wight_strike_damage"]

    def test_a_kill_hands_out_a_barrow(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        prey = place_card(gs, WhiteAdc, "player2", 3, 3)
        prey.health = 1

        attack_with(sp, gs)
        assert barrows(gs, "player1") == S["SP"]["barrow_on_kill"]
