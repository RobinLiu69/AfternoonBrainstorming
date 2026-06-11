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
from campaign import ai_query
from campaign.config_loader import CAMPAIGN_SETTINGS

_B = CAMPAIGN_SETTINGS["strategy_bonuses"]["orange"]
_P = _B["placement"]


def _move_reach_targets(card, gs) -> int:
    best = 0
    for (dx, dy) in ai_query.move_destinations_for(gs, card) + [(card.board_x, card.board_y)]:
        hits = ai_query.attack_targets_from_pos(gs, card.owner, dx, dy, card.attack_types)
        if len(hits) > best:
            best = len(hits)
    return best


class OrangeStrategy(Strategy):

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        bonus = 0.0
        if attacker.job_and_color == "ADCO":
            bonus += base_score * _B["adco_score_mult"]
            bonus += _move_reach_targets(attacker, gs) * _B["adco_reach_mult"]
        elif attacker.job_and_color == "LFO":
            bonus += _B["lfo_baseline"]
        elif attacker.job_and_color == "HFO":
            bonus += _B["hfo_baseline"]
            if attacker.extra_damage > 0:
                bonus += attacker.extra_damage * _B["hfo_extra_damage_mult"]
            targets = ai_query.attack_targets_at(gs, attacker)
            if len(targets) > 1:
                bonus += (len(targets) - 1) * _B["hfo_multi_target_bonus"]
        elif attacker.job_and_color == "ASSO":
            if attacker.anger:
                bonus += _B["asso_anger_bonus"]
            else:
                bonus += _B["asso_setup_bonus"]
        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        x, y = position
        bonus = 0.0

        if card_name in ("ADCO", "LFO", "HFO", "ASSO"):
            w = gs.board_config.width
            h = gs.board_config.height
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            openness = 4.0 - (abs(x - cx) + abs(y - cy))
            bonus += max(0.0, openness) * _P["mover_openness_mult"]

        if card_name == "TANKO":
            dist = ai_query.nearest_enemy_distance(gs, owner, x, y)
            if dist <= 1:
                bonus += _P["tanko_front_line"]

        if card_name == "SPO":
            friendly_movers = sum(
                1 for c in gs.get_player(owner).on_board
                if c.job_and_color in ("ADCO", "LFO", "HFO", "ASSO", "APTO")
                and abs(c.board_x - x) + abs(c.board_y - y) <= 2
            )
            bonus += friendly_movers * _P["spo_per_mover"]

        if card_name == "APTO":
            friendly_count = len([c for c in gs.get_player(owner).on_board if c.health > 0])
            bonus += min(friendly_count * _P["apto_per_friendly"], _P["apto_cap"])

        return base_score + bonus
