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


class BlueStrategy(Strategy):
    """Token-tempo faction. 3 tokens → free draw (huge tempo). Almost every blue card
    generates tokens on some trigger; HFB consumes tokens for bonus damage.

    Strategy:
    - Build tokens via any damage / kill (most blue attacks generate at least 1 token).
    - Place TANKB in front so opponent attacks generate tokens passively.
    - With high tokens, HFB hits hardest; route attacks through it.
    - Approaching 3 tokens, push one more attack to trigger the draw.
    """

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        tokens = gs.players_token.get(attacker.owner, 0)

        bonus = 0.0

        # Approaching the 3-token threshold → next attack triggers a free draw. Big.
        if tokens == 2:
            bonus += 16.0
        elif tokens == 1:
            bonus += 6.0

        # HFB: extra_damage equals current tokens, so its real damage scales with tokens.
        # Project the resulting damage on a worthwhile target.
        if attacker.job_and_color == "HFB" and tokens >= 1:
            targets = ai_query.attack_targets_at(gs, attacker)
            for t in targets:
                effective = (attacker.damage + tokens) - max(0, t.armor)
                if 0 < effective and t.health <= effective:
                    bonus += 20.0
                    break
                bonus += min(effective, t.health) * 1.5
            # Hard cap so HFB doesn't outrun guaranteed kills from other attackers.
            bonus = min(bonus, 60.0)

        # ADCB/LFB/ASSB generate tokens from kills or damage — they're always good
        # vs token-rich blues, so encourage them to swing.
        if attacker.job_and_color in ("ADCB", "LFB", "ASSB"):
            bonus += 4.0

        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        x, y = position
        bonus = 0.0

        if card_name == "TANKB":
            # TANKB gets tokens when attacked. Closer to enemies = more attacks taken.
            dist = ai_query.nearest_enemy_distance(gs, owner, x, y)
            if dist <= 1:
                bonus += 12.0
            elif dist <= 2:
                bonus += 5.0

        if card_name == "HFB":
            tokens = gs.players_token.get(owner, 0)
            if tokens == 0:
                bonus -= 4.0  # without tokens HFB is just an average HF
            elif tokens >= 2:
                bonus += 10.0  # ready to burst

        if card_name == "APB":
            # APB gives tokens AND inflicts numbness on its target — high tempo card.
            bonus += 5.0

        if card_name == "LFB":
            # LFB's ability fires per damage event, so any LF that can hit something is good.
            tokens = gs.players_token.get(owner, 0)
            if tokens < 2:
                bonus += 4.0  # invest in ramping tokens

        if card_name == "APTB":
            # APTB recycles damage into tokens via armor — synergy needs enemies in range.
            bonus += 3.0

        return base_score + bonus
