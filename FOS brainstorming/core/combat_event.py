# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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

from dataclasses import dataclass


@dataclass
class CombatEvent:
    kind: str           # "attack" | "hurt" | "float"
    board_x: int        # relevant unit's board x
    board_y: int        # relevant unit's board y
    target_x: int = 0   # target board x (used by "attack" for direction)
    target_y: int = 0   # target board y (used by "attack" for direction)
    damage: int = 0     # used by "float" to render the number
    delay: float = 0.0  # seconds before this event starts playing
    post_health: int = -1

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "board_x": self.board_x,
            "board_y": self.board_y,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "damage": self.damage,
            "delay": self.delay,
            "post_health": self.post_health
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CombatEvent":
        return cls(
            kind=d["kind"],
            board_x=d["board_x"],
            board_y=d["board_y"],
            target_x=d.get("target_x", 0),
            target_y=d.get("target_y", 0),
            damage=d.get("damage", 0),
            delay=d.get("delay", 0.0),
            post_health=d.get("post_health", -1)
        )