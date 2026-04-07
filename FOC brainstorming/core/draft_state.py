from dataclasses import dataclass, field
from typing import Literal

from core.board_config import BoardConfig
from core.board_block import Board


BPPhase = Literal["p1_first6", "p2_pick12", "p1_last6", "done"]


@dataclass
class DraftState:
    local_player: str = ""
    player1_deck: list[str] = field(default_factory=list)
    player2_deck: list[str] = field(default_factory=list)
    phase: BPPhase = "p1_first6"
    
    board_config: BoardConfig = field(default_factory=BoardConfig)
    board_dict: dict[tuple[int, int], Board] = field(default_factory=dict)


    timer_mode: str = "timer"
    file_auto_delete: bool = False

    def get_visible_deck(self, viewer: str, owner: str) -> list[str]:
        deck = self.player1_deck if owner == "player1" else self.player2_deck
        
        if viewer == owner:
            return deck
        else:
            return deck[:6]
        
    def get_deck(self, owner: str) -> list[str]:
        return self.player1_deck if owner == "player1" else self.player2_deck
        
    def current_editor(self) -> str:
        match self.phase:
            case "p1_first6": return "player1"
            case "p2_pick12": return "player2"
            case "p1_last6": return "player1"
            case _: return ""

    def can_advance(self) -> bool:
        match self.phase:
            case "p1_first6": return len(self.player1_deck) >= 6
            case "p2_pick12": return len(self.player2_deck) >= 12
            case "p1_last6": return len(self.player1_deck) >= 12
            case "done": return True

    def advance_phase(self) -> None:
        match self.phase:
            case "p1_first6": self.phase = "p2_pick12"
            case "p2_pick12": self.phase = "p1_last6"
            case "p1_last6": self.phase = "done"

    def to_dict(self) -> dict:
        return {
            "player1_deck": self.player1_deck,
            "player2_deck": self.player2_deck,
            "phase": self.phase,
            "timer_mode": self.timer_mode,
            "file_auto_delete": self.file_auto_delete,
        }
 
    def apply_dict(self, data: dict) -> None:
        self.player1_deck = data["player1_deck"]
        self.player2_deck = data["player2_deck"]
        self.phase = data["phase"]
        self.timer_mode = data["timer_mode"]
        self.file_auto_delete = data["file_auto_delete"]