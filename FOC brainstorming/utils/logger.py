# core/advanced_logger.py
import logging, os
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

class LogCategory(Enum):
    GAME_FLOW = "game_flow"
    CARD_ACTION = "card_action"
    COMBAT = "combat"
    SYSTEM = "system"
    DEBUG = "debug"


@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    data: dict = field(default_factory=dict)
    
    def to_string(self) -> str:
        time_str = self.timestamp.strftime('%H:%M:%S')
        return f"[{time_str}] [{self.category.value}] {self.message}"


@dataclass
class GameLogger:
    log_file: Optional[Path] = None
    enable_console: bool = True
    enable_file: bool = True
    max_memory_logs: int = 1000
    
    _logger: logging.Logger = field(init=False, repr=False)
    _memory_logs: List[LogEntry] = field(init=False, default_factory=list, repr=False)
    _subscribers: List[Callable[[LogEntry], None]] = field(init=False, default_factory=list, repr=False)
    
    def __post_init__(self) -> None:
        self._logger = logging.getLogger('FOC_Game_Logger')
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()
        
        formatter = logging.Formatter(
            '%(asctime)s - [%(category)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if self.enable_file:
            if self.log_file is None:
                __FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__)).replace("utils", "")
                self.log_file = Path(f"{__FOLDER_PATH}/battle_records/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
            
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
    
    def log(self, level: LogLevel, category: LogCategory, message: str, **data) -> None:
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            data=data
        )
        
        self._memory_logs.append(entry)
        if len(self._memory_logs) > self.max_memory_logs:
            self._memory_logs.pop(0)
        
        extra = {'category': category.value}
        self._logger.log(level.value, message, extra=extra)
        
        for subscriber in self._subscribers:
            subscriber(entry)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **data) -> None:
        self.log(LogLevel.INFO, category, message, **data)
    
    def debug(self, message: str, category: LogCategory = LogCategory.DEBUG, **data) -> None:
        self.log(LogLevel.DEBUG, category, message, **data)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **data) -> None:
        self.log(LogLevel.WARNING, category, message, **data)
    
    def log_turn_start(self, player_name: str, turn_number: int) -> None:
        self.info(
            f"Turn {turn_number}: {player_name} started",
            category=LogCategory.GAME_FLOW,
            player=player_name,
            turn=turn_number
        )
    
    def log_card_drew(self, player_name: str, card_name: str) -> None:
        self.info(
            f"{player_name} drew {card_name}",
            category=LogCategory.CARD_ACTION,
            player_name=player_name,
            card_name=card_name
        )
    
    def log_card_played(self, player_name: str, card_name: str, position: tuple[int, int]) -> None:
        self.info(
            f"{player_name} played {card_name} at {position}",
            category=LogCategory.CARD_ACTION,
            player=player_name,
            card=card_name,
            position=position
        )
    
    def log_card_moved(self, player_name: str, card_name: str, start_position: tuple[int, int], target_position: tuple[int, int]) -> None:
        self.info(
            f"{player_name} moved {card_name} from {start_position} to {target_position}",
            category=LogCategory.CARD_ACTION,
            player_name=player_name,
            card_name=card_name,
            start_position=start_position,
            target_position=target_position
        )

    def log_attack(self, attacker: str, target: str, damage: int) -> None:
        self.info(
            f"{attacker} attacked {target} for {damage} damage",
            category=LogCategory.COMBAT,
            attacker=attacker,
            target=target,
            damage=damage
        )

    def log_card_recycled(self, player_name: str, card_name: str, position: tuple[int, int]) -> None:
        self.info(
            f"{player_name} recycled {card_name} at {position}",
            category=LogCategory.GAME_FLOW,
            player_name=player_name,
            card_name=card_name,
            position=position
        )
    
    def subscribe(self, callback: Callable[[LogEntry], None]) -> None:
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[LogEntry], None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def get_recent_logs(self, count: int = 10, category: Optional[LogCategory] = None) -> List[LogEntry]:
        logs = self._memory_logs
        
        if category:
            logs = [log for log in logs if log.category == category]
        
        return logs[-count:]
    
    def get_combat_logs(self) -> List[LogEntry]:
        return [log for log in self._memory_logs if log.category == LogCategory.COMBAT]
    
    def clear_memory_logs(self) -> None:
        self._memory_logs.clear()