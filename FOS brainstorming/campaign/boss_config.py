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

from campaign.config_loader import CAMPAIGN_SETTINGS

if TYPE_CHECKING:
    from core.game_state import GameState


STAGE_BUFFS: dict[str, dict] = CAMPAIGN_SETTINGS["stage_buffs"]
_BUFF_TEXT_TEMPLATES: dict[str, str] = CAMPAIGN_SETTINGS["stage_buff_text_templates"]


def stage_buff_text(stage: str) -> str:
    buffs = STAGE_BUFFS.get(stage, {})
    lines = [
        _BUFF_TEXT_TEMPLATES[k].format(value=v)
        for k, v in buffs.items()
        if k in _BUFF_TEXT_TEMPLATES
    ]
    return "\n".join(lines)


STAGE_BUFF_TEXT: dict[str, str] = {
    stage: stage_buff_text(stage) for stage in STAGE_BUFFS
}


def apply_initial_buffs(stage: str, gs: "GameState") -> None:
    buffs = STAGE_BUFFS.get(stage, {})

    extra_hand = buffs.get("initial_hand_size", 0)
    if extra_hand > len(gs.player2.hand):
        deficit = extra_hand - len(gs.player2.hand)
        for _ in range(deficit):
            gs.player2.draw_card(gs)


def maintain_unit_buffs(stage: str, gs: "GameState", buffed_ids: set[str]) -> None:
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
    if gs.turn_number <= 0 or gs.turn_number % 2 == 0:
        return

    buffs = STAGE_BUFFS.get(stage, {})
    ai_turn = (gs.turn_number + 1) // 2

    free_move_n = buffs.get("free_moving_every_n_turns", 0)
    if free_move_n and ai_turn % free_move_n == 0:
        gs.number_of_movings["player2"] = gs.number_of_movings.get("player2", 0) + 1

    free_heal_n = buffs.get("free_heal_every_n_turns", 0)
    if free_heal_n and ai_turn % free_heal_n == 0:
        gs.number_of_heals["player2"] = gs.number_of_heals.get("player2", 0) + 1


def apply_stage_one_shots(stage: str, gs: "GameState") -> None:
    buffs = STAGE_BUFFS.get(stage, {})

    initial_luck = buffs.get("initial_luck")
    if initial_luck is not None:
        gs.players_luck["player2"] = int(initial_luck)
