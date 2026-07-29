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

The battle loop ticks this every frame and it is the only object that sees
both sides, so it also drives the relic and enchantment runtime for the
player as well as the enemy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from campaign.ai_controller import AIController

from tower.battle_effects import SideRuntime, install_side_channels

if TYPE_CHECKING:
    from core.game_state import GameState


class TowerAIController(AIController):

    def __init__(self, enemy: dict, enemy_effects: dict, player_effects: dict):
        super().__init__(enemy["strategy"], player_name="player2")
        for key, value in enemy.get("strategy_overrides", {}).items():
            if hasattr(self.strategy, key):
                setattr(self.strategy, key, value)
        self.enemy = SideRuntime(enemy_effects, "player2")
        self.player = SideRuntime(player_effects, "player1")
        self._channels_installed: bool = False

    def _maintain_units(self, gs: "GameState") -> None:
        if not self._channels_installed:
            install_side_channels(gs, {"player1": self.player.effects,
                                       "player2": self.enemy.effects})
            self._channels_installed = True

        self.enemy.maintain(gs)
        self.player.maintain(gs)
        if gs.turn_number % 2 == 0 and self.player.started:
            self.player.on_turn_start(gs)

    def _per_turn(self, gs: "GameState") -> None:
        self.enemy.on_turn_start(gs)

    def _apply_one_shots(self, gs: "GameState") -> None:
        return

    def _apply_initial(self, gs: "GameState") -> None:
        self.enemy.on_battle_start(gs)
        self.player.on_battle_start(gs)
