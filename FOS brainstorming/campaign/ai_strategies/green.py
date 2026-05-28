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
    """Lucky-chaos faction. The win condition is lucky blocks on the board:

    - APTG passively spawns blocks every turn in its small_cross.
    - LFG that attacks a block deals chain damage to nearest enemy + 25% refund attack.
    - HFG that breaks a block gains +luck and spawns another block.
    - ADCG attack has 50% to spawn block on its row/col.

    Strategy: build a block farm with APTG, then let LFG / HFG consume them for value.
    """

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        blocks = _lucky_blocks(gs)

        if attacker.job_and_color == "LFG":
            # LFG breaking a block → chain damage to nearest enemy. The chain damage
            # equals LFG's damage value, so essentially a free second attack on top of
            # the block kill. Massive value when blocks are adjacent.
            for b in blocks:
                if abs(b.board_x - attacker.board_x) + abs(b.board_y - attacker.board_y) == 1:
                    return base_score + 45.0

        if attacker.job_and_color == "HFG":
            # HFG breaks blocks for +luck and spawns a new block — snowball value.
            for b in blocks:
                d = abs(b.board_x - attacker.board_x) + abs(b.board_y - attacker.board_y)
                if d == 1 or (abs(b.board_x - attacker.board_x) == 1 and abs(b.board_y - attacker.board_y) == 1):
                    return base_score + 30.0

        if attacker.job_and_color == "ADCG":
            # ADCG attacks have 50% to spawn a block; if its row/col has empties, valuable
            row_col_empties = sum(
                1 for (x, y), b in gs.board_dict.items()
                if (x == attacker.board_x or y == attacker.board_y)
                and not (x == attacker.board_x and y == attacker.board_y)
                and not b.occupy
            )
            if row_col_empties > 0:
                return base_score + min(8.0, row_col_empties * 2.0)

        return base_score

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        x, y = position
        blocks = _lucky_blocks(gs)

        # APTG: must be placed where surrounding cells are empty — its block farm yield
        # equals the count of empty small_cross neighbors.
        if card_name == "APTG":
            yield_per_turn = _adjacent_empty_cells(gs, x, y)
            return base_score + yield_per_turn * 8.0 + 6.0

        # LFG: place adjacent to existing blocks (or APTG) so it can chain damage.
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
            return base_score + adj_block * 18.0 + adj_apt * 10.0

        # HFG: same idea — bonus next to existing or future block sources.
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
            return base_score + adj_block * 14.0 + adj_apt * 8.0

        # SPG: deploy spawns more blocks if luck is high enough. Reward when luck is built up.
        if card_name == "SPG":
            luck = gs.players_luck.get(owner, 0)
            return base_score + min(20.0, luck * 0.4)

        return base_score
