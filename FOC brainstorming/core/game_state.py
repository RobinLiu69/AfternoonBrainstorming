from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import cast, TYPE_CHECKING

from core.setting import SETTING
from core.game_statistics import GameStatistics, StatType
from utils.logger import GameLogger

# if TYPE_CHECKING:
from core.player import Player
from core.neutral import Neutral
from core.board_block import Board
from core.board_config import BoardConfig
from cards.base import Card


@dataclass
class GameState:
    player1: Player
    player2: Player
    neutral: Neutral

    board_config: BoardConfig
    board_dict: dict[tuple[int, int], Board] = field(default_factory=dict)


    game_logger: GameLogger = field(default_factory=GameLogger)
    game_statistics: GameStatistics = field(default_factory=GameStatistics)

    player_timer: dict[str, str] = field(default_factory=lambda: {"player1": "0", "player2": "0"})
    timer_mode: str = "timer"
        
    coutdown_time = int(SETTING["countdown_time"])
    file_auto_delete: bool = False

    score: int = 0
    turn_number: int = 0

    players_luck: dict[str, int] = field(default_factory=lambda: {"player1": 50, "player2": 50, "neutral": 50})
    how_many_token_to_draw_a_card: int = int(SETTING["how_many_token_to_draw_a_card"])
    players_token: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0, "neutral": 0})
    players_totem: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0, "neutral": 0})
    players_coin: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0})
    card_to_draw: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0})
    
    number_of_attacks: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0})
    number_of_movings: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0})
    number_of_cudes: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0})
    number_of_heals: dict[str, int] = field(default_factory=lambda: {"player1": 0, "player2": 0})

    def update(self) -> None:
        for card in self.player1.on_board:
            card.update(self)
        for card in self.player2.on_board:
            card.update(self)
        for card in self.neutral.on_board:
            card.update(self)

    def get_opponent_name(self, owner: str) -> str:
        return "player2" if owner == "player1" else "player1"
    
    def get_opponent(self, owner: str) -> Player:
        return self.player2 if owner == "player1" else self.player1

    def get_player(self, owner: str) -> Player:
        return self.player1 if owner == "player1" else self.player2
    
    def get_player_cards(self, owner: str) -> list[Card]:
        return self.player1.on_board if owner == "player1" else self.player2.on_board
    
    def get_opponent_cards(self, owner: str) -> list[Card]:
        return self.player2.on_board if owner == "player1" else self.player1.on_board
    
    def get_all_cards(self) -> list[Card]:
        return (self.player1.on_board + self.player2.on_board + self.neutral.on_board)
    
    def get_both_player_cards(self) -> list[Card]:
        return (self.player1.on_board + self.player2.on_board)

    def get_side_cards(self, owner: str, get_opponent: bool = False) -> list[Card]:
        player_cards = self.get_player_cards(owner) if not get_opponent else self.get_opponent_cards(owner)
        return player_cards + self.neutral.on_board

    def to_dict(self) -> dict:
        return {
            "player1": self.player1.to_dict(),
            "player2": self.player2.to_dict(),
            "neutral": self.neutral.to_dict(),
            "board_config": self.board_config.to_dict(),
            "game_logger": self.game_logger.to_dict(),
            "game_statistics": self.game_statistics.to_dict(),

            "board_dict": {
                f"{x},{y}": board.to_dict()
                for (x, y), board in self.board_dict.items()
            },

            "player_timer": self.player_timer,
            "timer_mode": self.timer_mode,
            "countdown_time": self.coutdown_time,
            "file_auto_delete": self.file_auto_delete,
            "score": self.score,
            "turn_number": self.turn_number,
            "players_luck": self.players_luck,
            "players_token": self.players_token,
            "players_totem": self.players_totem,
            "players_coin": self.players_coin,
            "card_to_draw": self.card_to_draw,
            "number_of_attacks": self.number_of_attacks,
            "number_of_movings": self.number_of_movings,
            "number_of_cudes": self.number_of_cudes,
            "number_of_heals": self.number_of_heals
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        state = cls(
            player1= Player.from_dict(data["player1"]),
            player2= Player.from_dict(data["player2"]),
            neutral= Neutral.from_dict(data["neutral"]),
            board_config=BoardConfig.from_dict(data["board_config"]),
        )
        # restore board_dict — "x,y" strings back to (x, y) tuple keys
        state.board_dict = {
            tuple(int(v) for v in key.split(",")): Board.from_dict(val)
            for key, val in data["board_dict"].items()
        }
        state.game_logger = GameLogger.from_dict(data["game_logger"])
        state.game_statistics = GameStatistics.from_dict(data["game_statistics"])

        state.player_timer = data["player_timer"]
        state.timer_mode = data["timer_mode"]
        state.file_auto_delete = data["file_auto_delete"]
        state.score = data["score"]
        state.turn_number = data["turn_number"]
        state.players_luck = data["players_luck"]
        state.players_token = data["players_token"]
        state.players_totem = data["players_totem"]
        state.players_coin = data["players_coin"]
        state.card_to_draw = data["card_to_draw"]
        state.number_of_attacks = data["number_of_attacks"]
        state.number_of_movings = data["number_of_movings"]
        state.number_of_cudes = data["number_of_cudes"]
        state.number_of_heals = data["number_of_heals"]
        return state