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


BASE_HAND_SIZE: int = 3
BASE_LUCK: int = 50


def maintain_side_unit_buffs(effects: dict, gs: "GameState", player_name: str, buffed_ids: set[str]) -> None:
    hp_plus = effects.get("unit_hp_plus", 0)
    dmg_plus = effects.get("unit_damage_plus", 0)
    job_hp = effects.get("job_hp_plus", {})
    job_dmg = effects.get("job_damage_plus", {})
    if not (hp_plus or dmg_plus or job_hp or job_dmg):
        return
    for c in gs.get_player(player_name).on_board:
        if c.instance_id in buffed_ids:
            continue
        hp = hp_plus + job_hp.get(c.job, 0)
        dmg = dmg_plus + job_dmg.get(c.job, 0)
        if hp:
            c.health = max(1, c.health + hp)
            c.max_health = max(1, c.max_health + hp)
            c.display_health = c.health
        if dmg:
            c.damage = max(0, c.damage + dmg)
            c.original_damage = max(0, c.original_damage + dmg)
        buffed_ids.add(c.instance_id)


def apply_side_one_shots(effects: dict, gs: "GameState", player_name: str) -> None:
    luck_plus = effects.get("luck_plus", 0)
    if luck_plus:
        gs.players_luck[player_name] = max(0, min(100, BASE_LUCK + int(luck_plus)))


def apply_side_initial_hand(effects: dict, gs: "GameState", player_name: str) -> None:
    hand_plus = effects.get("hand_plus", 0)
    if not hand_plus:
        return
    player = gs.get_player(player_name)
    target = max(1, BASE_HAND_SIZE + int(hand_plus))
    while len(player.hand) < target:
        before = len(player.hand)
        player.draw_card(gs)
        if len(player.hand) == before:
            break
    while len(player.hand) > target:
        player.discard_pile.append(player.hand.pop())


def apply_side_per_turn(effects: dict, gs: "GameState", player_name: str) -> dict[str, int]:
    granted = {"heals": 0, "movings": 0}
    if player_name == "player2":
        if gs.turn_number % 2 == 0:
            return granted
        side_turn = (gs.turn_number + 1) // 2
    else:
        if gs.turn_number % 2 == 1:
            return granted
        side_turn = gs.turn_number // 2 + 1

    free_move_n = effects.get("free_moving_every_n_turns", 0)
    if free_move_n and side_turn % free_move_n == 0:
        gs.number_of_movings[player_name] = gs.number_of_movings.get(player_name, 0) + 1
        granted["movings"] = 1

    free_heal_n = effects.get("free_heal_every_n_turns", 0)
    if free_heal_n and side_turn % free_heal_n == 0:
        gs.number_of_heals[player_name] = gs.number_of_heals.get(player_name, 0) + 1
        granted["heals"] = 1

    return granted
