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

from dataclasses import dataclass, field
from typing import Literal, Optional

from core.board_config import BoardConfig
from core.board_block import Board
from core.match_settings import MatchSettings

from shared.setting import JOB_DICTIONARY, JOB_ORDER

BPPhase = Literal["p1_first6", "p2_pick12", "p1_last6", "done"]


def tournament_ban_list() -> list[str]:
    bans: list[str] = []
    for page_array in JOB_DICTIONARY["colors_array"]:
        for color_tag, _color_name in list(page_array.items())[:-1]:
            for card_type in JOB_ORDER:
                bans.append(f"{card_type}{color_tag}")
    return bans


TOURNAMENT_BANS: frozenset[str] = frozenset(tournament_ban_list())


@dataclass
class DraftState:
    local_player: str = ""
    player1_deck: list[str] = field(default_factory=list)
    player2_deck: list[str] = field(default_factory=list)
    ban_deck: list[str] = field(default_factory=list)
    phase: BPPhase = "p1_first6"
    
    board_config: BoardConfig = field(default_factory=BoardConfig)
    board_dict: dict[tuple[int, int], Board] = field(default_factory=dict)


    settings: MatchSettings = field(default_factory=MatchSettings)

    paused: bool = False
    pause_reason: str = ""
    pause_seconds_remaining: float = 0.0

    net_spectator_count: int = 0
    net_latencies: dict = field(default_factory=dict)

    pick_history: list[tuple[str, str, str]] = field(default_factory=list)

    def get_visible_deck(self, viewer: str, owner: str) -> range:
        deck = self.player1_deck if owner == "player1" else self.player2_deck
        if viewer == owner or viewer == "god":
            return range(len(deck))
        else:
            return range(min(6, len(deck)))
        
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
            "ban_deck": list(self.ban_deck),
            "phase": self.phase,
            **self.settings.to_dict(),
            "paused": self.paused,
            "pause_reason": self.pause_reason,
            "pause_seconds_remaining": self.pause_seconds_remaining,
        }

    def to_dict_for(self, viewer: str) -> dict:
        data = self.to_dict()
        data["player1_deck"] = self._mask_deck("player1", viewer)
        data["player2_deck"] = self._mask_deck("player2", viewer)
        return data

    def _mask_deck(self, owner: str, viewer: str) -> list[str]:
        deck = self.player1_deck if owner == "player1" else self.player2_deck
        if viewer == owner or viewer == "god":
            return list(deck)
        return list(deck[:6]) + ["?"] * max(0, len(deck) - 6)

    def apply_dict(self, data: dict) -> None:
        self.player1_deck = data["player1_deck"]
        self.player2_deck = data["player2_deck"]
        self.ban_deck = data.get("ban_deck", self.ban_deck)
        self.phase = data["phase"]
        self.settings.apply_dict(data)
        self.paused = data.get("paused", False)
        self.pause_reason = data.get("pause_reason", "")
        self.pause_seconds_remaining = data.get("pause_seconds_remaining", 0.0)

    def add_ban(self, ban_list: Optional[list[str]] = None) -> None:
        if ban_list is not None:
            self.ban_deck.extend(ban_list)

    def init_ban_deck(self) -> None:
        self.ban_deck = []
        if self.settings.ruleset == "tournament":
            self.ban_deck = tournament_ban_list()
                        
    def is_banned(self, card_name: str) -> bool:
        return card_name in self.ban_deck