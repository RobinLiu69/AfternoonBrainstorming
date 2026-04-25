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

from enum import Enum


class StatType(Enum):
    CARD_USE = "card_use_count"
    HIT = "hit_count"
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_TAKEN = "damage_taken"
    DAMAGE_TAKEN_COUNT = "damage_taken_count"
    SCORED = "scored"
    ABILITY = "ability_count"
    HEALING = "healing_amount"
    HEAL_USE = "use_heal_count"
    MOVE = "move_count"
    MOVE_USE = "use_move_count"
    CUBE_USE = "cube_used_count"
    KILLED = "killed_count"
    DEATH = "death_count"
    TOKEN_USE = "use_token_count"
    ROUNDS_SURVIVED = "rounds_survived"
