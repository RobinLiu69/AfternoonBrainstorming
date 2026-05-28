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


def _move_reach_targets(card, gs) -> int:
    """How many enemy cells the card's attack pattern would cover from at least one
    8-neighbor destination. Approximates the unit's effective attack range after move."""
    best = 0
    for (dx, dy) in ai_query.move_destinations_for(gs, card) + [(card.board_x, card.board_y)]:
        hits = ai_query.attack_targets_from_pos(gs, card.owner, dx, dy, card.attack_types)
        if len(hits) > best:
            best = len(hits)
    return best


class OrangeStrategy(Strategy):
    """Mobile-counter faction. Attack-then-move is the engine — almost every orange
    unit triggers a follow-up effect after movement:
      ADCO: launches a second attack from the destination.
      LFO:  damages nearest enemy from destination.
      HFO:  gains +damage (anger), persists until settle.
      ASSO: kills with anger refund extra attack count.

    Strategy:
    - Attack scores get a boost: each attack actually arms a follow-up.
    - Placement bias toward central, open positions so post-attack move has options.
    - The AIController separately emits the actual move actions after an attack
      sets `moving=True`, picking destinations with the most after-move impact.
    """

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        bonus = 0.0
        # Two-hit threat: ADCO swings a second time after moving. Treat as 1.6×.
        if attacker.job_and_color == "ADCO":
            bonus += base_score * 0.4
            bonus += _move_reach_targets(attacker, gs) * 2.0
        elif attacker.job_and_color == "LFO":
            bonus += 8.0  # the nearest-enemy chain damage from after_movement
        elif attacker.job_and_color == "HFO":
            # HFO: small_cross + small_x = up to 8 cells per swing. Each attack sets
            # moving=True; each subsequent move stacks +1 extra_damage (config
            # `Orange.HF.extra_damage_from_moving`). Within a turn this snowballs:
            #   attack(1d) → move → attack(2d) → move → attack(3d) → …
            # Multi-target reach + scaling damage = the orange win-condition unit.
            bonus += 12.0
            # Already-ramped HFO this turn: every remaining attack rides the stack.
            if attacker.extra_damage > 0:
                bonus += attacker.extra_damage * 6.0
            # Multi-target bonus for AoE swings.
            targets = ai_query.attack_targets_at(gs, attacker)
            if len(targets) > 1:
                bonus += (len(targets) - 1) * 5.0
        elif attacker.job_and_color == "ASSO":
            # ASSO economy: post-move kills with anger=True refund 1 attack count.
            #   1st link: attack normally (anger off) — kill grants moving=True, no refund.
            #   move → after_movement sets anger=True.
            #   2nd link: kill with anger → +1 attack refund (net cost: 0). Chain repeats.
            # Score the link based on whether anger is already armed.
            if attacker.anger:
                bonus += 25.0  # this kill will refund the attack and re-arm moving
            else:
                bonus += 4.0   # set up the chain
        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        x, y = position
        bonus = 0.0

        if card_name in ("ADCO", "LFO", "HFO", "ASSO"):
            # Central positions have 8 move neighbors; corners only 3. Mobility matters.
            w = gs.board_config.width
            h = gs.board_config.height
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            openness = 4.0 - (abs(x - cx) + abs(y - cy))
            bonus += max(0.0, openness) * 2.0

        if card_name == "TANKO":
            # TANKO generates a MOVEO when attacked — front-line bias.
            dist = ai_query.nearest_enemy_distance(gs, owner, x, y)
            if dist <= 1:
                bonus += 8.0

        if card_name == "SPO":
            # SPO triggers when ANY teammate moves; goes near our movers.
            friendly_movers = sum(
                1 for c in gs.get_player(owner).on_board
                if c.job_and_color in ("ADCO", "LFO", "HFO", "ASSO", "APTO")
                and abs(c.board_x - x) + abs(c.board_y - y) <= 2
            )
            bonus += friendly_movers * 4.0

        if card_name == "APTO":
            # APTO buffs all teammates' armor when ANY teammate moves. Place where it
            # broadcasts to many friendlies.
            friendly_count = len([c for c in gs.get_player(owner).on_board if c.health > 0])
            bonus += min(friendly_count * 2.5, 12.0)

        return base_score + bonus
