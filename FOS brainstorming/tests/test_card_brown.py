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
from cards.card_brown import Adc, Ap, Apt, Ass, Hf, Lf, Sp, Tank
from cards.card_white import Adc as WhiteAdc
from core.game_state import GameState
from shared.setting import CARD_SETTING
from tests.helpers import make_game_state, place_card

S = CARD_SETTING["Brown"]


def attack_with(card: Card, game_state: GameState) -> bool:
    card.numbness = False
    return card.attack(game_state)


class TestBrownAdc:
    def test_attacking_numbs_itself(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 1, 1)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        assert attack_with(adc, gs) is True
        assert adc.numbness is True

    def test_no_self_numbness_while_effects_are_disabled(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 1, 1)
        adc.effects_disabled = True
        place_card(gs, WhiteAdc, "player2", 1, 2)

        assert attack_with(adc, gs) is True
        assert adc.numbness is False

    def test_no_self_numbness_when_nothing_is_hit(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, Adc, "player1", 1, 1)

        assert attack_with(adc, gs) is False
        assert adc.numbness is False


class TestBrownAp:
    def test_attacking_gives_the_opponent_a_card(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 1, 1)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        before = gs.card_to_draw["player2"]
        attack_with(ap, gs)
        assert gs.card_to_draw["player2"] == before + S["AP"]["on_attack_enemy_draw"]

    def test_attacking_numbs_the_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 1, 1)
        target = place_card(gs, WhiteAdc, "player2", 1, 2)
        target.numbness = False

        attack_with(ap, gs)
        assert target.numbness is True

    def test_disabled_effects_drop_the_draw_but_keep_the_numbness(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 1, 1)
        ap.effects_disabled = True
        target = place_card(gs, WhiteAdc, "player2", 1, 2)
        target.numbness = False

        before = gs.card_to_draw["player2"]
        attack_with(ap, gs)
        assert gs.card_to_draw["player2"] == before
        assert target.numbness is True


class TestBrownTank:
    def test_being_attacked_numbs_the_nearest_ally(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        ally = place_card(gs, WhiteAdc, "player1", 1, 0)
        ally.numbness = False
        enemy = place_card(gs, WhiteAdc, "player2", 1, 2)

        attack_with(enemy, gs)
        assert tank.health < S["TANK"]["health"]
        assert ally.numbness is True

    def test_ally_is_spared_while_effects_are_disabled(self) -> None:
        gs = make_game_state()
        tank = place_card(gs, Tank, "player1", 1, 1)
        tank.effects_disabled = True
        ally = place_card(gs, WhiteAdc, "player1", 1, 0)
        ally.numbness = False
        enemy = place_card(gs, WhiteAdc, "player2", 1, 2)

        attack_with(enemy, gs)
        assert ally.numbness is False

    def test_lone_tank_survives_being_attacked(self) -> None:
        gs = make_game_state()
        place_card(gs, Tank, "player1", 1, 1)
        enemy = place_card(gs, WhiteAdc, "player2", 1, 2)

        assert attack_with(enemy, gs) is True


class TestBrownHfAttackCost:
    def _setup(self, knives: int):
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        hf.numbness = False
        victim = place_card(gs, WhiteAdc, "player2", 1, 2)
        gs.number_of_attacks["player1"] = knives
        return gs, hf, victim

    def test_one_blade_is_not_enough(self) -> None:
        gs, _hf, victim = self._setup(1)
        before = victim.health

        assert gs.player1.attack(1, 1, gs) is False
        assert victim.health == before
        assert gs.number_of_attacks["player1"] == 1

    def test_two_blades_attacks_and_costs_both(self) -> None:
        gs, _hf, victim = self._setup(2)
        before = victim.health

        assert gs.player1.attack(1, 1, gs) is True
        assert victim.health < before
        assert gs.number_of_attacks["player1"] == 0

    def test_three_blades_leaves_one(self) -> None:
        gs, _hf, _victim = self._setup(3)

        assert gs.player1.attack(1, 1, gs) is True
        assert gs.number_of_attacks["player1"] == 1

    def test_costs_one_blade_while_effects_are_disabled(self) -> None:
        gs, hf, victim = self._setup(1)
        hf.effects_disabled = True
        before = victim.health

        assert hf.attack_cost(gs) == 1
        assert gs.player1.attack(1, 1, gs) is True
        assert victim.health < before
        assert gs.number_of_attacks["player1"] == 0

    def test_cost_follows_effects_without_needing_an_attack_first(self) -> None:
        gs, hf, _victim = self._setup(2)
        sp = place_card(gs, Sp, "player1", 0, 0)
        sp.numbness = False

        assert hf.attack_cost(gs) == 2
        sp.ability(hf, gs)
        assert hf.attack_cost(gs) == 1

        hf.effects_disabled = False
        assert hf.attack_cost(gs) == 2


class TestBrownLf:
    def test_kill_scores_for_the_opponent(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        victim = place_card(gs, WhiteAdc, "player2", 1, 2)
        victim.health = 1

        before = gs.score
        attack_with(lf, gs)
        assert gs.score == before + S["LF"]["on_kill_enemy_points"]

    def test_kill_by_player2_scores_the_other_way(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player2", 1, 1)
        victim = place_card(gs, WhiteAdc, "player1", 1, 2)
        victim.health = 1

        before = gs.score
        attack_with(lf, gs)
        assert gs.score == before - S["LF"]["on_kill_enemy_points"]

    def test_no_score_without_a_kill(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        survivor = place_card(gs, Tank, "player2", 1, 2)

        before = gs.score
        attack_with(lf, gs)
        assert 0 < survivor.health < S["TANK"]["health"]
        assert gs.score == before

    def test_no_score_while_effects_are_disabled(self) -> None:
        gs = make_game_state()
        lf = place_card(gs, Lf, "player1", 1, 1)
        lf.effects_disabled = True
        victim = place_card(gs, WhiteAdc, "player2", 1, 2)
        victim.health = 1

        before = gs.score
        attack_with(lf, gs)
        assert victim.health == 0
        assert gs.score == before


class TestBrownAss:
    def test_kill_skips_the_next_draw(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        victim = place_card(gs, WhiteAdc, "player2", 2, 2)
        victim.health = 1

        attack_with(ass, gs)
        assert gs.skip_turn_draw["player1"] is True

    def test_no_kill_keeps_the_draw(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        survivor = place_card(gs, Tank, "player2", 2, 2)

        attack_with(ass, gs)
        assert 0 < survivor.health < S["TANK"]["health"]
        assert gs.skip_turn_draw["player1"] is False

    def test_disabled_effects_keep_the_draw(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        ass.effects_disabled = True
        victim = place_card(gs, WhiteAdc, "player2", 2, 2)
        victim.health = 1

        attack_with(ass, gs)
        assert victim.health == 0
        assert gs.skip_turn_draw["player1"] is False


class TestBrownApt:
    def test_deploy_shields_every_living_enemy(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        near = place_card(gs, WhiteAdc, "player2", 3, 3)
        far = place_card(gs, WhiteAdc, "player2", 2, 3)

        apt.deploy(gs)
        assert near.armor == S["APT"]["on_play_enemy_shield"]
        assert far.armor == S["APT"]["on_play_enemy_shield"]

    def test_deploy_skips_dead_enemies(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        corpse = place_card(gs, WhiteAdc, "player2", 3, 3)
        corpse.health = 0

        apt.deploy(gs)
        assert corpse.armor == 0

    def test_refresh_shields_every_living_enemy(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        enemy = place_card(gs, WhiteAdc, "player2", 3, 3)

        apt.refresh(gs)
        assert enemy.armor == S["APT"]["on_refresh_enemy_shield"]

    def test_disabled_effects_shield_nobody(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 0, 0)
        apt.effects_disabled = True
        enemy = place_card(gs, WhiteAdc, "player2", 3, 3)

        apt.deploy(gs)
        apt.refresh(gs)
        assert enemy.armor == 0

    def test_attack_buffs_the_nearest_ally(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)
        ally = place_card(gs, WhiteAdc, "player1", 1, 0)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        buff = S["APT"]["on_attack_buff_nearest_ally"]
        before_atk, before_armor = ally.damage, ally.armor
        attack_with(apt, gs)
        assert ally.damage == before_atk + buff["atk"]
        assert ally.armor == before_armor + buff["armor"]

    def test_giant_ally_gets_the_bonus_on_top(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)
        ally = place_card(gs, Lf, "player1", 1, 0)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        buff = S["APT"]["on_attack_buff_nearest_ally"]
        bonus = S["APT"]["bonus_if_giant"]
        before_atk, before_armor = ally.damage, ally.armor
        attack_with(apt, gs)
        assert ally.damage == before_atk + buff["atk"] + bonus["atk"]
        assert ally.armor == before_armor + buff["armor"] + bonus["armor"]

    def test_ally_buff_survives_disabled_effects(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)
        apt.effects_disabled = True
        ally = place_card(gs, WhiteAdc, "player1", 1, 0)
        place_card(gs, WhiteAdc, "player2", 1, 2)

        buff = S["APT"]["on_attack_buff_nearest_ally"]
        before = ally.damage
        attack_with(apt, gs)
        assert ally.damage == before + buff["atk"]


class TestBrownSp:
    def _setup(self):
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 1, 1)
        hf.numbness = False
        sp = place_card(gs, Sp, "player1", 0, 0)
        sp.numbness = False
        return gs, hf, sp

    def test_rage_suppresses_ally_effects(self) -> None:
        gs, hf, sp = self._setup()
        assert hf.effects_off() is False

        sp.ability(hf, gs)
        assert sp.anger is True
        assert hf.effects_off() is True
        assert hf.attack_cost(gs) == 1

    def test_attacking_enters_rage(self) -> None:
        gs, hf, sp = self._setup()
        place_card(gs, WhiteAdc, "player2", 3, 3)

        attack_with(sp, gs)
        assert sp.anger is True
        assert hf.effects_off() is True

    def test_death_restores_ally_effects(self) -> None:
        gs, hf, sp = self._setup()
        sp.ability(hf, gs)

        sp.health = 0
        sp.on_killed_by(hf, gs)

        assert hf.effects_off() is False
        assert hf.attack_cost(gs) == 2

    def test_nullify_restores_ally_effects(self) -> None:
        gs, hf, sp = self._setup()
        sp.ability(hf, gs)

        sp.set_nullify(True, gs)
        assert hf.effects_off() is False

        sp.set_nullify(False, gs)
        assert hf.effects_off() is True

    def test_second_angry_sp_keeps_effects_suppressed(self) -> None:
        gs, hf, sp = self._setup()
        other = place_card(gs, Sp, "player1", 0, 1)
        other.numbness = False
        sp.ability(hf, gs)
        other.ability(hf, gs)

        sp.health = 0
        sp.on_killed_by(hf, gs)

        assert hf.effects_off() is True
        assert hf.attack_cost(gs) == 1

    def test_enemy_angry_sp_does_not_suppress(self) -> None:
        gs, hf, _sp = self._setup()
        enemy_sp = place_card(gs, Sp, "player2", 3, 3)
        enemy_sp.numbness = False
        enemy_sp.ability(hf, gs)

        assert hf.effects_off() is False
        assert hf.attack_cost(gs) == 2

    def test_giant_deployed_after_sp_died_keeps_effects(self) -> None:
        gs, hf, sp = self._setup()
        sp.ability(hf, gs)
        sp.health = 0
        sp.on_killed_by(hf, gs)

        latecomer = place_card(gs, Hf, "player1", 2, 2)
        latecomer.deploy(gs)
        assert latecomer.effects_off() is False

    def test_giant_deployed_while_sp_is_angry_is_suppressed(self) -> None:
        gs, hf, sp = self._setup()
        sp.ability(hf, gs)

        latecomer = place_card(gs, Hf, "player1", 2, 2)
        latecomer.deploy(gs)
        assert latecomer.effects_off() is True


class TestOrdinaryCardsStillCostOne:
    def test_single_blade_card_attacks_with_one_blade(self) -> None:
        gs = make_game_state()
        adc = place_card(gs, WhiteAdc, "player1", 1, 1)
        adc.numbness = False
        victim = place_card(gs, WhiteAdc, "player2", 1, 2)
        gs.number_of_attacks["player1"] = 1
        before = victim.health

        assert adc.attack_cost(gs) == 1
        assert gs.player1.attack(1, 1, gs) is True
        assert victim.health < before
        assert gs.number_of_attacks["player1"] == 0
