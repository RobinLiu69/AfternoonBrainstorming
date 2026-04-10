# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright 2024-2026 Robin Liu / FOC Studio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------

import json
from dataclasses import dataclass
from typing import Literal, Optional


ActionType = Literal[
    "attack", "play_card", "move_select", "move_to",
    "heal", "spawn_cube", "end_turn", "toggle_hint", "toggle_upgrade", "quit"
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