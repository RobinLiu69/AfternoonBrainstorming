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

"""Enchantments, applied to a unit the moment it is deployed.

Implemented: the flat stat enchantments (Sharp, Fortified, Berserk, the two
statted Artisan grades).

Still to do - these need per-instance behaviour overrides or a per-turn hook,
and land with the rest of the relic runtime:
Dispersed, Mana, Radiant, Steady, Plated, Ghostly, Flying Sword, Artisan:Mend,
Burning, Bleeding, Rusted.
"""

from __future__ import annotations

from typing import Any

from shared import card_code

from tower.content import ENCHANTS


def apply(card: Any, keys: tuple[str, ...], game_state: Any) -> None:
    hp = 0
    damage = 0
    for key in keys:
        data = ENCHANTS.get(key)
        if data is None:
            continue
        hp += int(data.get("hp", 0))
        damage += int(data.get("damage", 0))

    if hp:
        card.health = max(1, card.health + hp)
        card.max_health = max(1, card.max_health + hp)
        card.display_health = card.health
    if damage:
        card.damage = max(0, card.damage + damage)
        card.original_damage = max(0, card.original_damage + damage)


def install() -> None:
    card_code.set_enchant_hook(apply)


def uninstall() -> None:
    card_code.set_enchant_hook(None)
