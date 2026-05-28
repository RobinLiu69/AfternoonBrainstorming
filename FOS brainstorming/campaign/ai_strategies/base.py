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
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from campaign import ai_evaluator, ai_query
from campaign.config_loader import CAMPAIGN_SETTINGS

if TYPE_CHECKING:
    from core.game_state import GameState


@dataclass
class PlacementChoice:
    hand_index: int
    card_name: str
    x: int
    y: int
    score: float


@dataclass
class AttackChoice:
    x: int
    y: int
    score: float


class Strategy:
    """Default strategy. Subclass to override scoring for specific factions.

    The AI evaluates one action at a time and re-reads the live GameState every tick,
    so strategies are stateless query objects, not turn planners.
    """

    placement_min_score: float = float(CAMPAIGN_SETTINGS["thresholds"]["placement_min_score"])
    attack_min_score: float = float(CAMPAIGN_SETTINGS["thresholds"]["attack_min_score"])
    """Below this, attacks are skipped and the attack count is saved for next turn.
    Lethal hits score 100+ so they always pass; non-lethal chips (~11-14) are filtered."""

    def best_placement(self, gs: "GameState", owner: str) -> Optional[PlacementChoice]:
        player = gs.get_player(owner)
        empties = ai_query.empty_positions(gs)
        if not empties:
            return None

        best: Optional[PlacementChoice] = None
        for hi, card_name in enumerate(player.hand):
            if not ai_query.is_playable_unit_card(card_name):
                continue
            real_name = card_name[:-4] if card_name.endswith(" (+)") else card_name
            for (x, y) in empties:
                score = ai_evaluator.evaluate_placement(real_name, (x, y), gs, owner)
                score = self.placement_bonus(real_name, (x, y), gs, owner, score)
                if best is None or score > best.score:
                    best = PlacementChoice(hi, card_name, x, y, score)
        return best

    def best_attack(self, gs: "GameState", owner: str) -> Optional[AttackChoice]:
        if gs.number_of_attacks[owner] <= 0:
            return None

        best: Optional[AttackChoice] = None
        for card in ai_query.friendly_cards(gs, owner):
            score, _target = ai_evaluator.evaluate_attack(card, gs)
            # Negative score is a hard sentinel from the evaluator (numb attacker,
            # non-attacker job, no targets in range). Faction bonuses must not
            # resurrect such candidates — otherwise the AI fires an attack action
            # that the engine refuses, attack_count never decrements, and the AI
            # locks in an infinite loop selecting the same illegal attacker.
            if score < 0:
                continue
            score = self.attack_bonus(card, gs, score)
            if score <= 0:
                continue
            if best is None or score > best.score:
                best = AttackChoice(card.board_x, card.board_y, score)
        return best

    def placement_bonus(
        self, card_name: str, position: tuple[int, int],
        gs: "GameState", owner: str, base_score: float,
    ) -> float:
        return base_score

    def attack_bonus(self, attacker, gs: "GameState", base_score: float) -> float:
        return base_score
