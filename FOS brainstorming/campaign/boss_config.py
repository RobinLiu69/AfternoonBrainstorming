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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_state import GameState


STAGE_BUFFS: dict[str, dict] = {
    "green":  {"extra_lucky_blocks": 1},
    "orange": {"free_moving_every_n_turns": 3},
    "boss":   {"unit_hp_plus": 1, "initial_hand_size": 4, "free_heal_every_n_turns": 5},
}

STAGE_BUFF_TEXT: dict[str, str] = {
    "green":  "AI starts with +1 lucky block on board",
    "orange": "AI gains +1 movement every 3 turns",
    "boss":   "AI units +1 HP\nAI starts with 4 cards\nAI gains +1 heal every 5 turns",
}


def apply_initial_buffs(stage: str, gs: "GameState") -> None:
    """One-shot buffs that depend on Player.initialize() having run.

    Caller must invoke this AFTER battling.main has called player.initialize() — at
    `build_campaign_game_state` time the draw_pile is still empty so draw_card is a
    no-op. AIController triggers this exactly once via `_ensure_initialized`.
    """
    buffs = STAGE_BUFFS.get(stage, {})

    extra_hand = buffs.get("initial_hand_size", 0)
    if extra_hand > len(gs.player2.hand):
        deficit = extra_hand - len(gs.player2.hand)
        for _ in range(deficit):
            gs.player2.draw_card(gs)


def maintain_unit_buffs(stage: str, gs: "GameState") -> None:
    """Idempotent per-tick HP buff applier.

    `unit_hp_plus` needs to apply to every AI unit, but at game start on_board is empty
    and new units arrive over time. Tagging buffed cards with `_boss_hp_applied`
    prevents double-buffing on subsequent ticks.
    """
    hp_plus = STAGE_BUFFS.get(stage, {}).get("unit_hp_plus", 0)
    if not hp_plus:
        return
    for c in gs.player2.on_board:
        if getattr(c, "_boss_hp_applied", False):
            continue
        c.health += hp_plus
        c.max_health += hp_plus
        c.display_health = c.health
        c._boss_hp_applied = True


def apply_per_turn_buffs(stage: str, gs: "GameState") -> None:
    """Tick per-turn buffs (free moves, heals). Called at AI's turn_start."""
    buffs = STAGE_BUFFS.get(stage, {})

    free_move_n = buffs.get("free_moving_every_n_turns", 0)
    if free_move_n and gs.turn_number > 0 and gs.turn_number % (free_move_n * 2) == 1:
        gs.number_of_movings["player2"] = gs.number_of_movings.get("player2", 0) + 1

    free_heal_n = buffs.get("free_heal_every_n_turns", 0)
    if free_heal_n and gs.turn_number > 0 and gs.turn_number % (free_heal_n * 2) == 1:
        gs.number_of_heals["player2"] = gs.number_of_heals.get("player2", 0) + 1


def apply_stage_one_shots(stage: str, gs: "GameState") -> None:
    """Stage-specific board setup (e.g. green's extra lucky block)."""
    buffs = STAGE_BUFFS.get(stage, {})

    extra_lucky = buffs.get("extra_lucky_blocks", 0)
    if extra_lucky:
        from cards.factory import CardFactory
        from campaign.ai_query import empty_positions
        for _ in range(extra_lucky):
            empties = empty_positions(gs)
            if not empties:
                break
            cx, cy = gs.board_config.get_center_position()
            empties.sort(key=lambda p: abs(p[0] - cx) + abs(p[1] - cy), reverse=True)
            tx, ty = empties[0]
            block = CardFactory.create("LUCKYBLOCK", "neutral", tx, ty)
            gs.neutral.on_board.append(block)
            gs.board_dict[tx, ty].occupy = True
