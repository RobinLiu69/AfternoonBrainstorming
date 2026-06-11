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

_B = CAMPAIGN_SETTINGS["strategy_bonuses"]["red"]
_P = _B["placement"]


def _damage_grown(card) -> int:
    return max(0, card.damage - getattr(card, "original_damage", card.damage))


class RedStrategy(Strategy):

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        bonus = 0.0

        grown = _damage_grown(attacker)
        if grown > 0:
            bonus += grown * _B["damage_grown_per_stack"]

        if attacker.job_and_color == "HFR":
            bonus += _B["hfr_baseline"]
            if attacker.anger:
                bonus += _B["hfr_anger_bonus"]

        if attacker.job_and_color == "ADCR":
            bonus += _B["adcr_baseline"]

        if attacker.job_and_color == "APR":
            bonus += _B["apr_baseline"]
            targets = ai_query.attack_targets_at(gs, attacker)
            if targets:
                bonus += max(t.damage for t in targets) * _B["apr_target_damage_mult"]

        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        return base_score + _P.get(card_name, 0.0)
