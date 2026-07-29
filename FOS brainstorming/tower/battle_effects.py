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

"""Pushing a side's merged relic effects into a live battle.

Implemented so far: the stat and starting-hand keys.  The rest of the relic
runtime (reshuffle triggers, per-turn orbs and coins, attack economy, spell
hooks) lands with the relic pass.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_state import GameState


BASE_HAND_SIZE: int = 3


def maintain_unit_buffs(effects: dict, gs: "GameState", player_name: str,
                        buffed_ids: set[str]) -> None:
    """Apply flat buffs to units the moment they show up on the board."""
    hp_plus = effects.get("unit_hp_plus", 0)
    dmg_plus = effects.get("unit_damage_plus", 0)
    job_hp = effects.get("job_hp_plus", {})
    job_dmg = effects.get("job_damage_plus", {})
    first_hp = effects.get("first_unit_hp_plus", 0)
    first_dmg = effects.get("first_unit_damage_plus", 0)

    if not (hp_plus or dmg_plus or job_hp or job_dmg or first_hp or first_dmg):
        return

    for card in gs.get_player(player_name).on_board:
        if card.instance_id in buffed_ids:
            continue
        first = not buffed_ids
        hp = hp_plus + job_hp.get(card.job, 0) + (first_hp if first else 0)
        dmg = dmg_plus + job_dmg.get(card.job, 0) + (first_dmg if first else 0)
        if hp:
            card.health = max(1, card.health + hp)
            card.max_health = max(1, card.max_health + hp)
            card.display_health = card.health
        if dmg:
            card.damage = max(0, card.damage + dmg)
            card.original_damage = max(0, card.original_damage + dmg)
        buffed_ids.add(card.instance_id)


def apply_initial_hand(effects: dict, gs: "GameState", player_name: str) -> None:
    hand_plus = int(effects.get("hand_plus", 0))
    if not hand_plus:
        return
    player = gs.get_player(player_name)
    target = max(1, BASE_HAND_SIZE + hand_plus)
    while len(player.hand) < target:
        before = len(player.hand)
        player.draw_card(gs)
        if len(player.hand) == before:
            break
    while len(player.hand) > target:
        player.discard_pile.append(player.hand.pop())


def apply_per_turn(effects: dict, gs: "GameState", player_name: str) -> None:
    """Reserved for the relic runtime pass."""
    return
