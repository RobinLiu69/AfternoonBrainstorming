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

from __future__ import annotations

from campaign.ai_strategies.base import Strategy
from campaign.config_loader import CAMPAIGN_SETTINGS

_B = CAMPAIGN_SETTINGS["strategy_bonuses"]["green"]
_P = _B["placement"]


def _lucky_blocks(gs):
    return [c for c in gs.neutral.on_board if c.job_and_color == "LUCKYBLOCK"]


def _adjacent_empty_cells(gs, x, y) -> int:
    count = 0
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nx, ny = x + dx, y + dy
        if gs.board_config.is_valid_position(nx, ny) and not gs.board_dict[nx, ny].occupy:
            count += 1
    return count


class GreenStrategy(Strategy):

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        blocks = _lucky_blocks(gs)

        if attacker.job_and_color == "LFG":
            ax, ay = attacker.board_x, attacker.board_y
            blocks_in_range = sum(
                1 for b in blocks
                if abs(b.board_x - ax) + abs(b.board_y - ay) == 1
            )
            if blocks_in_range > 0:
                return base_score + _B["lfg_per_block"] * blocks_in_range

        if attacker.job_and_color == "HFG":
            ax, ay = attacker.board_x, attacker.board_y
            blocks_in_range = sum(
                1 for b in blocks
                if max(abs(b.board_x - ax), abs(b.board_y - ay)) == 1
            )
            if blocks_in_range > 0:
                return base_score + _B["hfg_per_block"] * blocks_in_range

        if attacker.job_and_color == "ADCG":
            row_col_empties = sum(
                1 for (x, y), b in gs.board_dict.items()
                if (x == attacker.board_x or y == attacker.board_y)
                and not (x == attacker.board_x and y == attacker.board_y)
                and not b.occupy
            )
            if row_col_empties > 0:
                return base_score + min(_B["adcg_cap"], row_col_empties * _B["adcg_per_empty_cell"])

        return base_score

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        x, y = position
        blocks = _lucky_blocks(gs)

        if card_name == "APTG":
            yield_per_turn = _adjacent_empty_cells(gs, x, y)
            return base_score + yield_per_turn * _P["aptg_yield_mult"] + _P["aptg_baseline"]

        if card_name == "LFG":
            adj_block = sum(
                1 for b in blocks
                if abs(b.board_x - x) + abs(b.board_y - y) == 1
            )
            adj_apt = sum(
                1 for c in gs.get_player(owner).on_board
                if c.job_and_color == "APTG"
                and abs(c.board_x - x) + abs(c.board_y - y) == 1
            )
            return base_score + adj_block * _P["lfg_adj_block"] + adj_apt * _P["lfg_adj_apt"]

        if card_name == "HFG":
            adj_block = sum(
                1 for b in blocks
                if max(abs(b.board_x - x), abs(b.board_y - y)) == 1
            )
            adj_apt = sum(
                1 for c in gs.get_player(owner).on_board
                if c.job_and_color == "APTG"
                and max(abs(c.board_x - x), abs(c.board_y - y)) == 1
            )
            return base_score + adj_block * _P["hfg_adj_block"] + adj_apt * _P["hfg_adj_apt"]

        if card_name == "SPG":
            luck = gs.players_luck.get(owner, 0)
            return base_score + min(_P["spg_cap"], luck * _P["spg_luck_mult"])

        return base_score
