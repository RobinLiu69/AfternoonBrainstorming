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


class BossStrategy(Strategy):
    """Mixed elite. Reads the player's board composition and shifts emphasis:
    - Player runs high-damage cards → bias toward placing protective TANKs.
    - Player stacks high-HP units → bias toward landing ASS hits to whittle them.

    Hard-tier baseline + composition recognition.
    """

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        opp = gs.get_opponent_name(owner)
        opp_cards = [c for c in gs.get_player(opp).on_board if c.health > 0]
        if not opp_cards:
            return base_score

        avg_dmg = sum(c.damage + c.extra_damage for c in opp_cards) / len(opp_cards)
        avg_hp = sum(c.health for c in opp_cards) / len(opp_cards)

        bonus = 0.0
        # Heavy-hitting opponent → reinforce front line.
        if avg_dmg >= 4 and card_name.startswith("TANK"):
            bonus += 5.0
        # Beefy opponent → favor ASS deployment (deploy-and-strike).
        if avg_hp >= 6 and card_name.startswith("ASS"):
            bonus += 6.0
        return base_score + bonus

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        # When trailing, attack more aggressively (lower threshold via flat boost).
        # When leading, behave normally — score is signed, positive = boss leads.
        if gs.score < -2:
            return base_score + 5.0
        return base_score
