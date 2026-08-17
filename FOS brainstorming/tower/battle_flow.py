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

"""Running one battle.  Used by the layer loop and by events that pick a fight."""

from __future__ import annotations

from core.game_screen import GameScreen
from screens.battling import battling

from tower import battle_builder, battle_prep, run_state
from tower.tower_ai import TowerAIController


def fight(game_screen: GameScreen, run: dict, enemy: dict) -> str:
    """Returns ``"win"``, ``"lose"`` or ``"abandon"``."""
    player_effects = run_state.battle_effects(run)
    enemy_effects = run_state.effects_from_relics(enemy.get("relics", []),
                                                  enemy.get("effects", {}))

    if battle_prep.main(game_screen, run, enemy, player_effects, enemy_effects) != "start":
        return "abandon"

    game_state = battle_builder.build_game_state(run, enemy)
    controller = TowerAIController(enemy, enemy_effects, player_effects)
    winner = battling.main(game_state, game_screen, mode="campaign", ai_controller=controller)

    if winner == "player1":
        run["battles_won"] = run.get("battles_won", 0) + 1
        return "win"
    if winner == "player2":
        return "lose"
    return "abandon"
