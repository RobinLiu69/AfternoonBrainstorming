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


def _damage_grown(card) -> int:
    """How much the card's damage has grown over its base. Red ADCR/HFR/LFR/APR/ASSR
    all bump `self.damage` directly (not `extra_damage`) on their on-hit/kill ability,
    so this is the canonical "has this unit ramped" check."""
    return max(0, card.damage - getattr(card, "original_damage", card.damage))


class RedStrategy(Strategy):
    """Damage-snowball faction. Red abilities permanently bump `self.damage` on hit:

    - ADCR ability: +damage_increase every hit. Pure ramper, no downside.
    - HFR ability: +damage_increase every hit but self-takes 1 dmg; gains `anger`
      (can_be_killed=False) when its health reaches 0 — effectively immortal that turn.
    - LFR ability: +armor and +damage on hit.
    - ASSR killed: nearest ally +damage. ASS itself doesn't ramp, but feeds others.
    - SPR is the broadcast target for everyone's growth (a stat reservoir).

    Strategy: HFR is the dedicated burst attacker. Once it has 1-2 ramps it should
    keep firing — even at low HP it's still useful because anger gates death. ADCR is
    the safe ramper. Protect SPR (it accumulates everyone else's bonus).
    """

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        bonus = 0.0

        # Already-ramped units have proven value — keep feeding them attacks.
        grown = _damage_grown(attacker)
        if grown > 0:
            bonus += grown * 6.0  # +6 per +1 stacked damage

        # HFR is the primary attacker: every swing pushes its damage curve forward.
        # When `anger` is on (it hit 0 HP via self-harm), it can't be killed — pile in.
        if attacker.job_and_color == "HFR":
            bonus += 8.0  # baseline preference to swing HFR
            if attacker.anger:
                bonus += 20.0  # immortal this turn, fire freely

        # ADCR scales on every hit too — encourage swings over a low-damage TANKR poke.
        if attacker.job_and_color == "ADCR":
            bonus += 5.0

        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        bonus = 0.0
        if card_name == "LFR":
            bonus += 5.0  # LFR survives each turn and ramps on hit
        if card_name == "SPR":
            # SPR is the team's stat reservoir — it inherits every red ability bonus
            # broadcast. Place it safely (base scoring already biases SP toward corners).
            bonus += 4.0
        if card_name == "HFR":
            # HFR is precious as a ramper — bias center/safe so it survives to fire
            # multiple times.
            bonus += 3.0
        return base_score + bonus
