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
from cards.card_green import Ap, Hf, Ass, Apt, Sp, Tank, LuckyBlock
from cards.card_red import Adc as RedAdc
from cards.card_white import Adc as WhiteAdc

S = CARD_SETTING["Green"]


class TestGreenAp:
    def test_ability_numbs_target(self) -> None:
        gs = make_game_state()
        ap = place_card(gs, Ap, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)
        target.numbness = False

        do_attack(ap, gs)
        assert target.numbness is True


class TestGreenHf:
    def test_ability_against_luckyblock_increases_luck(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        lb = place_card(gs, LuckyBlock, "player2", 1, 0)

        before = gs.players_luck["player1"]
        hf.ability(lb, gs)
        assert gs.players_luck["player1"] == before + S["HF"]["luck_increase"]

    def test_ability_against_non_luckyblock_no_luck_change(self) -> None:
        gs = make_game_state()
        hf = place_card(gs, Hf, "player1", 0, 0)
        target = place_card(gs, RedAdc, "player2", 1, 0)

        before = gs.players_luck["player1"]
        hf.ability(target, gs)
        assert gs.players_luck["player1"] == before


class TestGreenAss:
    def test_kill_increases_own_luck_and_decreases_opponent(self) -> None:
        gs = make_game_state()
        ass = place_card(gs, Ass, "player1", 1, 1)
        enemy = place_card(gs, RedAdc, "player2", 2, 0)
        enemy.health = 1

        before_own = gs.players_luck["player1"]
        before_opponent = gs.players_luck["player2"]
        do_attack(ass, gs)
        assert gs.players_luck["player1"] == before_own + 5
        assert gs.players_luck["player2"] == before_opponent - S["ASS"]["enemy_luck_loss"]


class TestGreenApt:
    def test_start_turn_spawns_luckyblocks_on_adjacent_cells(self) -> None:
        gs = make_game_state()
        apt = place_card(gs, Apt, "player1", 1, 1)

        before = len(gs.neutral.on_board)
        apt.on_refresh(gs)
        assert len(gs.neutral.on_board) == before + 4


class TestGreenSp:
    def test_deploy_increases_luck(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)

        before = gs.players_luck["player1"]
        sp.deploy(gs)
        assert gs.players_luck["player1"] == before + S["SP"]["luck_increase"]

    def test_deploy_spawns_luckyblock_when_luck_sufficient(self) -> None:
        gs = make_game_state()
        sp = place_card(gs, Sp, "player1", 0, 0)
        gs.players_luck["player1"] = 50

        before = len(gs.neutral.on_board)
        sp.deploy(gs)
        assert len(gs.neutral.on_board) == before + 1


def _fortune_labels(game_state) -> list[str]:
    return [event.text for event in game_state.pending_combat_events
            if event.kind == "float" and event.text]


class TestFortuneFloats:
    def test_breaking_a_lucky_block_floats_the_effect_it_rolled(self) -> None:
        labels: dict[str, bool] = {}
        for seed in range(120):
            gs = make_game_state(rng_seed=seed)
            breaker = place_card(gs, WhiteAdc, "player1", 1, 1)
            gs.neutral.on_board.append(LuckyBlock("neutral", 1, 2))
            gs.board_dict[(1, 2)].occupy = True

            do_attack(breaker, gs)
            for event in gs.pending_combat_events:
                if event.kind == "float" and event.text:
                    labels[event.text] = event.good
                    assert (event.board_x, event.board_y) == breaker.get_position()

        assert set(labels) == {
            "+4 ARMOR", "ATK x2", "FREE STRIKE", "FREE MOVE", "SPAWN BLOCKS",
            "ARMOR GONE", "NUMBED", "HP HALVED", "ATK HALVED", "-2 HP",
        }
        assert all(labels[good] for good in ("+4 ARMOR", "ATK x2", "FREE STRIKE", "FREE MOVE", "SPAWN BLOCKS"))
        assert not any(labels[bad] for bad in ("ARMOR GONE", "NUMBED", "HP HALVED", "ATK HALVED", "-2 HP"))

    def test_a_green_ap_attack_floats_its_roll_too(self) -> None:
        assert any(
            _fortune_labels(self._green_ap_attack(seed)) for seed in range(40)
        )

    def test_a_green_tank_being_hit_floats_its_roll_too(self) -> None:
        assert any(
            _fortune_labels(self._green_tank_hit(seed)) for seed in range(40)
        )

    @staticmethod
    def _green_ap_attack(seed: int):
        gs = make_game_state(rng_seed=seed)
        ap = place_card(gs, Ap, "player1", 1, 1)
        place_card(gs, RedAdc, "player2", 1, 2)
        do_attack(ap, gs)
        return gs

    @staticmethod
    def _green_tank_hit(seed: int):
        gs = make_game_state(rng_seed=seed)
        place_card(gs, Tank, "player1", 1, 1)
        attacker = place_card(gs, RedAdc, "player2", 1, 2)
        do_attack(attacker, gs)
        return gs
