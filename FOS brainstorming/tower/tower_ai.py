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

from campaign.ai_controller import AIController, STRATEGY_REGISTRY
from shared import card_code

from tower import run_state
from tower.battle_effects import SideRuntime, install_side_channels

if TYPE_CHECKING:
    from core.game_state import GameState


PHASE_DRAW: int = 3


class TowerAIController(AIController):

    def __init__(self, enemy: dict, enemy_effects: dict, player_effects: dict):
        super().__init__(enemy["strategy"], player_name="player2")
        self._apply_overrides(enemy.get("strategy_overrides", {}))
        self.enemy = SideRuntime(enemy_effects, "player2")
        self.player = SideRuntime(player_effects, "player1")
        self.next_phase: dict | None = enemy.get("next_phase")
        self.phase_label: str = enemy.get("phase_label", "")
        self._channels_installed: bool = False

    def _apply_overrides(self, overrides: dict) -> None:
        for key, value in overrides.items():
            if hasattr(self.strategy, key):
                setattr(self.strategy, key, value)

    # ---------------- multi-phase bosses ----------------

    def _install_channels(self, gs: "GameState") -> None:
        install_side_channels(gs, {"player1": self.player.effects,
                                   "player2": self.enemy.effects})

    def on_defeat(self, gs: "GameState", winner: str) -> bool:
        """Called before a winner is declared.  True keeps the battle going."""
        if winner != "player1" or not self.next_phase:
            return False

        phase = self.next_phase
        self.next_phase = phase.get("next_phase")
        self.phase_label = phase.get("phase_label", "")

        boss = gs.player2
        # everything the previous lord brought stays, but it is not theirs to keep
        boss.hand = [card_code.add_enchant(code, "borrowed") for code in boss.hand]
        for card in boss.on_board:
            code = getattr(card, "tower_code", "") or card.job_and_color
            card.tower_code = card_code.add_enchant(code, "borrowed")

        boss.deck = list(phase["deck"])
        boss.draw_pile = []
        boss.discard_pile = list(phase["deck"])
        boss.revealed_deck = list(phase["deck"][:6])
        for _ in range(PHASE_DRAW):
            boss.draw_card(gs)

        gs.score = 0
        gs.number_of_attacks["player2"] = gs.number_of_attacks.get("player2", 0) + 1

        self.strategy = STRATEGY_REGISTRY[phase["strategy"]]()
        self.stage = phase["strategy"]
        self._apply_overrides(phase.get("strategy_overrides", {}))

        self.enemy.effects = run_state.effects_from_relics(
            phase.get("relics", []), phase.get("effects", {}))
        self._install_channels(gs)

        gs.game_logger.info(f"tower boss phase change -> {self.phase_label}")
        return True

    def _maintain_units(self, gs: "GameState") -> None:
        if not self._channels_installed:
            self._install_channels(gs)
            gs.tower_on_defeat = self.on_defeat
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
