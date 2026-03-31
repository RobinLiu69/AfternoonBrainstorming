from dataclasses import dataclass
from typing import Literal, Optional
import json

ActionType = Literal[
    "attack", "play_card", "move_select", "move_to",
    "heal", "spawn_cube", "end_turn", "quit"
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