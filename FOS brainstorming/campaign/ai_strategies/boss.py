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

_B = CAMPAIGN_SETTINGS["strategy_bonuses"]["boss"]


class BossStrategy(Strategy):

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        opp = gs.get_opponent_name(owner)
        opp_cards = [c for c in gs.get_player(opp).on_board if c.health > 0]
        if not opp_cards:
            return base_score

        avg_dmg = sum(c.damage + c.extra_damage for c in opp_cards) / len(opp_cards)
        avg_hp = sum(c.health for c in opp_cards) / len(opp_cards)

        bonus = 0.0
        if avg_dmg >= _B["heavy_dmg_threshold"] and card_name.startswith("TANK"):
            bonus += _B["tank_vs_heavy_dmg"]
        if avg_hp >= _B["beefy_hp_threshold"] and card_name.startswith("ASS"):
            bonus += _B["ass_vs_beefy"]
        return base_score + bonus

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        if gs.score < _B["trailing_threshold"]:
            return base_score + _B["trailing_attack_bonus"]
        return base_score
