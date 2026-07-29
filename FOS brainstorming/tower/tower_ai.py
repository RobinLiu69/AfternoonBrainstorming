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

"""The tower's AI controller.

The battle loop ticks this every frame, and it is the only object that sees
both sides, so it is also where the run's relic effects get pushed into the
battle - the player's as well as the enemy's.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from campaign.ai_controller import AIController

from tower import battle_effects

if TYPE_CHECKING:
    from core.game_state import GameState


class TowerAIController(AIController):

    def __init__(self, enemy: dict, enemy_effects: dict, player_effects: dict):
        super().__init__(enemy["strategy"], player_name="player2")
        for key, value in enemy.get("strategy_overrides", {}).items():
            if hasattr(self.strategy, key):
                setattr(self.strategy, key, value)
        self.enemy_effects: dict = dict(enemy_effects)
        self.player_effects: dict = dict(player_effects)
        self._player_buffed_ids: set[str] = set()
        self._player_turn_seen: int = -1

    def _maintain_units(self, gs: "GameState") -> None:
        battle_effects.maintain_unit_buffs(
            self.enemy_effects, gs, "player2", self._buffed_unit_ids)
        battle_effects.maintain_unit_buffs(
            self.player_effects, gs, "player1", self._player_buffed_ids)
        if gs.turn_number % 2 == 0 and gs.turn_number != self._player_turn_seen:
            self._player_turn_seen = gs.turn_number
            battle_effects.apply_per_turn(self.player_effects, gs, "player1")

    def _per_turn(self, gs: "GameState") -> None:
        battle_effects.apply_per_turn(self.enemy_effects, gs, "player2")

    def _apply_one_shots(self, gs: "GameState") -> None:
        return

    def _apply_initial(self, gs: "GameState") -> None:
        battle_effects.apply_initial_hand(self.enemy_effects, gs, "player2")
        battle_effects.apply_initial_hand(self.player_effects, gs, "player1")
