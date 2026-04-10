import atexit
import json
import logging
import os
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List, Any, TextIO
from dataclasses import dataclass, field
from enum import Enum

from core.setting import FOLDER_PATH


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class LogCategory(Enum):
    GAME_FLOW = "game_flow"
    CARD_ACTION = "card_action"
    SPECIAL_ACTION = "special_action"
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
    enable_jsonl: bool = True
    max_memory_logs: int = 1000
    
    _logger: logging.Logger = field(init=False, repr=False)
    _memory_logs: List[LogEntry] = field(init=False, default_factory=list, repr=False)
    _subscribers: List[Callable[[LogEntry], None]] = field(init=False, default_factory=list, repr=False)
    _jsonl_fp: Optional[TextIO] = field(init=False, default=None, repr=False)
    _jsonl_path: Optional[Path] = field(init=False, default=None, repr=False)
    _closed: bool = field(init=False, default=False, repr=False)
    _write_lock: threading.Lock = field(init=False, default_factory=threading.Lock, repr=False)

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
                self.log_file = Path(f"{FOLDER_PATH}/battle_records/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
        
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
        
        if self.enable_file and self.enable_jsonl and self.log_file is not None:
            try:
                self._jsonl_path = self.log_file.with_suffix('.jsonl')
                self._jsonl_fp = open(self._jsonl_path, 'w', encoding='utf-8')
            except OSError as e:
                print(f"[GameLogger] Failed to open jsonl file: {e}")
                self._jsonl_fp = None
        
        atexit.register(self.close)
    
    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        with self._write_lock:
            if self._jsonl_fp is not None:
                try:
                    self._jsonl_fp.flush()
                    self._jsonl_fp.close()
                except Exception as e:
                    print(f"[GameLogger] jsonl close failed: {e}")
                finally:
                    self._jsonl_fp = None
    
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
        
        if self._jsonl_fp is not None and not self._closed:
            try:
                record: dict[str, Any] = {
                    'timestamp': entry.timestamp.isoformat(),
                    'level': level.name,
                    'category': category.value,
                    'message': message,
                }
                for k, v in data.items():
                    record[k] = list(v) if isinstance(v, tuple) else v

                line = json.dumps(record, default=str, ensure_ascii=False) + '\n'

                with self._write_lock:
                    self._jsonl_fp.write(line)
                    self._jsonl_fp.flush()
            
            except Exception as e:
                print(f"[GameLogger] jsonl write failed: {e}")
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **data) -> None:
        self.log(LogLevel.INFO, category, message, **data)
    
    def debug(self, message: str, category: LogCategory = LogCategory.DEBUG, **data) -> None:
        self.log(LogLevel.DEBUG, category, message, **data)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **data) -> None:
        self.log(LogLevel.WARNING, category, message, **data)
    
    def log_action(self, action: Any, player: str) -> None:
        self.info(
            f"ACTION {player} {action.action_type}",
            category=LogCategory.GAME_FLOW,
            is_action=True,
            action_type=action.action_type,
            action_player=action.player,
            board_x=action.board_x,
            board_y=action.board_y,
            hand_index=action.hand_index,
        )

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

    def log_launch_attack(self, attacker: str, position: tuple[int, int]) -> None:
        self.info(
            f"{attacker} launcked attack at {position} ",
            category=LogCategory.COMBAT,
            attacker=attacker,
            position=position
        )

    def log_attack(self, attacker: str, attacker_position: tuple[int, int], target: str, target_position: tuple[int, int], damage: int) -> None:
        self.info(
            f"{attacker}{attacker_position} attacked {target}{target_position} for {damage} damage",
            category=LogCategory.COMBAT,
            attacker=attacker,
            attacker_position=attacker_position,
            target=target,
            target_position=target_position,
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