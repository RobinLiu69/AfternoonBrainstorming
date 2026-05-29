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
    "green":  {"initial_luck": 65},
    "orange": {"free_moving_every_n_turns": 3},
    "boss":   {"unit_hp_plus": 1, "initial_hand_size": 4, "free_heal_every_n_turns": 5},
}

STAGE_BUFF_TEXT: dict[str, str] = {
    "green":  "AI starts with 65% luck (vs default 50%)",
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


def maintain_unit_buffs(stage: str, gs: "GameState", buffed_ids: set[str]) -> None:
    """Idempotent per-tick HP buff applier.

    `unit_hp_plus` needs to apply to every AI unit, but at game start on_board is
    empty and new units arrive over time. `buffed_ids` is owned by the AIController
    (one set per match) so the registry can't leak across games — battling.main
    calls `reset_instance_counter()` at every match start, so a module-level
    registry would mark fresh `c1`, `c2`, … instances as "already buffed" on the
    second campaign run and silently drop the +HP buff.
    """
    hp_plus = STAGE_BUFFS.get(stage, {}).get("unit_hp_plus", 0)
    if not hp_plus:
        return
    for c in gs.player2.on_board:
        if c.instance_id in buffed_ids:
            continue
        c.health += hp_plus
        c.max_health += hp_plus
        c.display_health = c.health
        buffed_ids.add(c.instance_id)


def apply_per_turn_buffs(stage: str, gs: "GameState") -> None:
    """Tick per-turn buffs (free moves, heals) at the start of an AI turn.

    Fires every N AI turns *starting from the N-th AI turn* — i.e. wait a full
    N AI turns before the first grant. The earlier-fire variant (turn 1, 7, …)
    leaks the first grant: on AI's first turn nothing is on the board to move
    or heal, and `turn_end` clears `number_of_movings` / `number_of_heals` so
    the buff is wasted.

    AI's k-th turn = game turn (2k − 1). We invert that to recover `ai_turn`
    and then check `ai_turn % N == 0`.
    """
    if gs.turn_number <= 0 or gs.turn_number % 2 == 0:
        return  # only fire on AI turns (odd game turns)

    buffs = STAGE_BUFFS.get(stage, {})
    ai_turn = (gs.turn_number + 1) // 2

    free_move_n = buffs.get("free_moving_every_n_turns", 0)
    if free_move_n and ai_turn % free_move_n == 0:
        gs.number_of_movings["player2"] = gs.number_of_movings.get("player2", 0) + 1

    free_heal_n = buffs.get("free_heal_every_n_turns", 0)
    if free_heal_n and ai_turn % free_heal_n == 0:
        gs.number_of_heals["player2"] = gs.number_of_heals.get("player2", 0) + 1


def apply_stage_one_shots(stage: str, gs: "GameState") -> None:
    """Stage-specific board / state setup applied once at the start of a match."""
    buffs = STAGE_BUFFS.get(stage, {})

    initial_luck = buffs.get("initial_luck")
    if initial_luck is not None:
        gs.players_luck["player2"] = int(initial_luck)
