import os, json
from dataclasses import dataclass, field
from typing import cast, TYPE_CHECKING

from core.game_statistics import GameStatistics, StatType
from utils.type_hint import JobDictionary, CardSetting
from utils.logger import GameLogger

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral
    from core.board_block import Board
    from core.board_config import BoardConfig
    from cards.base import Card

__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__)).replace("core", "")

with open(f"{__FOLDER_PATH}/setting/setting.json", "r", encoding="utf-8") as file:
    SETTING: dict[str, str] = json.loads(file.read())

with open(f"{__FOLDER_PATH}/setting/job_dictionary.json", "r", encoding="utf-8") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())

with open(f"{__FOLDER_PATH}/setting/card_setting.json", "r", encoding="utf-8") as file:
    CARD_SETTING: CardSetting = json.loads(file.read())

with open(f"{__FOLDER_PATH}/setting/card_hints.json", "r", encoding="utf-8") as file:
    CARDS_HINTS_DICTIONARY: dict[str, str] = json.loads(file.read())

BLACK: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Black"].split(", "))))
WHITE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["White"].split(", "))))
BLUE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Blue"].split(", "))))
RED: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Red"].split(", "))))
GREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Green"].split(", "))))
ORANGE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Orange"].split(", "))))
PURPLE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Purple"].split(", "))))
DARKGREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["DarkGreen"].split(", "))))
CYAN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Cyan"].split(", "))))
FUCHSIA: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Fuchsia"].split(", "))))

with open(f"{__FOLDER_PATH}/setting/setting.json", "r", encoding="utf-8") as file:
    SETTING: dict[str, str] = json.loads(file.read())


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