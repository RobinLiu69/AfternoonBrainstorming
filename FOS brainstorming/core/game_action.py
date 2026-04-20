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

import json
from dataclasses import dataclass
from typing import Literal, Optional


ActionType = Literal[
    "attack", "play_card", "move_select", "move_to",
    "heal", "spawn_cube", "end_turn", "toggle_hint", "toggle_upgrade", "quit",
    "toggle_animation",
]


@dataclass
class GameAction:
    player: str
    action_type: ActionType
    board_x: Optional[int] = None
    board_y: Optional[int] = None
    hand_index: Optional[int] = None

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, s: str) -> "GameAction":
        return cls(**json.loads(s))


@dataclass
class ActionResult:
    success:  bool
    end_turn: bool = False
    message:  str  = ""
    quit: bool = False