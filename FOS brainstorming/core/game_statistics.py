# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class StatType(Enum):
    CARD_USE = "card_use_count"
    HIT = "hit_count"
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_TAKEN = "damage_taken"
    DAMAGE_TAKEN_COUNT = "damage_taken_count"
    SCORED = "scored"
    ABILITY = "ability_count"
    HEALING = "healing_amount"
    HEAL_USE = "use_heal_count"
    MOVE = "move_count"
    MOVE_USE = "use_move_count"
    CUBE_USE = "cube_used_count"
    KILLED = "killed_count"
    DEATH = "death_count"
    TOKEN_USE = "use_token_count"
    ROUNDS_SURVIVED = "rounds_survived"


@dataclass
class GameStatistics:
    _stats: Dict[StatType, Dict[str, int]] = field(default_factory=dict)
    
    score_history: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        for stat_type in StatType:
            self._stats[stat_type] = {}
    
    def increment(self, stat_type: StatType, key: str, value: int = 1):
        stats = self._stats[stat_type]
        stats[key] = stats.get(key, 0) + value
    
    def get(self, stat_type: StatType, key: str) -> int:
        return self._stats[stat_type].get(key, 0)
    
    def get_all(self, stat_type: StatType) -> Dict[str, int]:
        return self._stats[stat_type].copy()
    
    def add_card_use(self, player: str, count: int = 1):
        self.increment(StatType.CARD_USE, player, count)
    
    def add_hit(self, card_id: str, count: int = 1):
        self.increment(StatType.HIT, card_id, count)
    
    def add_damage_dealt(self, card_id: str, damage: int):
        self.increment(StatType.DAMAGE_DEALT, card_id, damage)
    
    def add_damage_taken(self, card_id: str, damage: int):
        self.increment(StatType.DAMAGE_TAKEN, card_id, damage)
        self.increment(StatType.DAMAGE_TAKEN_COUNT, card_id, 1)
    
    def add_kill(self, card_id: str):
        self.increment(StatType.KILLED, card_id, 1)
    
    def add_death(self, card_id: str):
        self.increment(StatType.DEATH, card_id, 1)
    
    def add_score_record(self, score: int):
        self.score_history.append(score)
    
    def get_kda(self, card_id: str) -> float:
        kills = self.get(StatType.KILLED, card_id)
        deaths = max(1, self.get(StatType.DEATH, card_id))
        return kills / deaths
    
    def get_avg_damage(self, card_id: str) -> float:
        damage = self.get(StatType.DAMAGE_DEALT, card_id)
        hits = max(1, self.get(StatType.HIT, card_id))
        return damage / hits
    
    def get_survival_index(self, card_id: str) -> float:
        scored = self.get(StatType.SCORED, card_id)
        avg_dmg = self.get_avg_damage(card_id)
        damage_taken = self.get(StatType.DAMAGE_TAKEN, card_id)
        hit_taken = max(1, self.get(StatType.DAMAGE_TAKEN_COUNT, card_id))
        rounds = max(1, self.get(StatType.ROUNDS_SURVIVED, card_id))
        
        return ((scored*5) + (avg_dmg*2) + (damage_taken / hit_taken * 2)) / rounds
    
    def export_for_charts(self) -> Dict[str, Dict[str, int]]:
        return {
            stat_type.value: self.get_all(stat_type)
            for stat_type in StatType
        }
    
    def export_player_stats(self, player: str) -> Dict[str, Dict[str, int]]:
        result = {}
        for stat_type in StatType:
            player_data = {
                key: value
                for key, value in self._stats[stat_type].items()
                if key.startswith(player)
            }
            if player_data:
                result[stat_type.value] = player_data
        return result