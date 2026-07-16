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

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, TYPE_CHECKING

from core.game_action import GameAction

if TYPE_CHECKING:
    from core.game_state import GameState


class ReplaySource:
    def __init__(self, jsonl_path: Path) -> None:
        self.jsonl_path: Path = Path(jsonl_path)
        self._entries: list[dict[str, Any]] = []
        self._action_indices: list[int] = []
        self._cursor: int = 0
        self.metadata: dict[str, Any] = {}
        self.action_timestamps: list[Optional[float]] = []
        self.start_timestamp: Optional[float] = None

        self._load()
        self._extract_metadata()

    @staticmethod
    def _parse_timestamp(raw) -> Optional[float]:
        if not isinstance(raw, str):
            return None
        try:
            return datetime.fromisoformat(raw).timestamp()
        except ValueError:
            return None

    def _load(self) -> None:
        if not self.jsonl_path.exists():
            raise FileNotFoundError(f"Replay file not found: {self.jsonl_path}")

        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[ReplaySource] skipping malformed line {line_no}: {e}")
                    continue

                idx = len(self._entries)
                self._entries.append(entry)
                timestamp = self._parse_timestamp(entry.get("timestamp"))
                if self.start_timestamp is None and timestamp is not None:
                    self.start_timestamp = timestamp
                if entry.get("is_action") is True:
                    self._action_indices.append(idx)
                    self.action_timestamps.append(timestamp)
    
    def _extract_metadata(self) -> None:
        for entry in self._entries:
            msg: str = entry.get("message", "")

            if "rng_seed" in entry:
                self.metadata["rng_seed"] = entry["rng_seed"]

            if "version" in entry:
                self.metadata["version"] = entry["version"]

            if msg.startswith("player1 deck "):
                self.metadata["player1_deck"] = msg[len("player1 deck "):].split("-") if msg[len("player1 deck "):] else []
            elif msg.startswith("player2 deck "):
                self.metadata["player2_deck"] = msg[len("player2 deck "):].split("-") if msg[len("player2 deck "):] else []

            if msg.startswith("timer mode "):
                self.metadata["timer_mode"] = msg[len("timer mode "):].strip()

            if msg.startswith("time control "):
                self.metadata["time_control"] = msg[len("time control "):].strip()
                if "countdown_seconds" in entry:
                    self.metadata["countdown_seconds"] = entry["countdown_seconds"]
                if "increment_seconds" in entry:
                    self.metadata["increment_seconds"] = entry["increment_seconds"]

            if msg.startswith("campaign stage "):
                self.metadata["campaign_stage"] = msg[len("campaign stage "):].strip()
    
    def next_action(self) -> Optional[GameAction]:
        if self._cursor >= len(self._action_indices):
            return None
        
        entry_idx = self._action_indices[self._cursor]
        self._cursor += 1
        entry = self._entries[entry_idx]
        
        try:
            return GameAction(
                player=entry["action_player"],
                action_type=entry["action_type"],
                board_x=entry.get("board_x"),
                board_y=entry.get("board_y"),
                hand_index=entry.get("hand_index"),
            )
        except KeyError as e:
            print(f"[ReplaySource] action entry missing field {e}: {entry}")
            return self.next_action()
    
    def peek_action(self) -> Optional[GameAction]:
        saved = self._cursor
        action = self.next_action()
        self._cursor = saved
        return action
    
    def reset(self) -> None:
        self._cursor = 0
    
    def seek_to_action(self, action_index: int) -> None:
        self._cursor = max(0, min(action_index, len(self._action_indices)))
    
    @property
    def exhausted(self) -> bool:
        return self._cursor >= len(self._action_indices)
    
    @property
    def total_actions(self) -> int:
        return len(self._action_indices)
    
    @property
    def current_action_index(self) -> int:
        return self._cursor
    
    def get_all_entries(self) -> list[dict[str, Any]]:
        return list(self._entries)
    
    @staticmethod
    def list_available_replays(battle_records_dir: str) -> list[Path]:
        directory = Path(battle_records_dir)
        if not directory.exists():
            return []
        jsonl_files = sorted(
            directory.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return jsonl_files


class ReplayClock:
    def __init__(self, source: ReplaySource, game_state: "GameState") -> None:
        self._timestamps = source.action_timestamps
        self._start = source.start_timestamp
        self._game_state = game_state
        self._last_ts: Optional[float] = self._start
        self.enabled = (self._start is not None
                        and any(t is not None for t in self._timestamps))

    def reset(self) -> None:
        self._last_ts = self._start
        game_state = self._game_state
        for player in (game_state.player1, game_state.player2):
            player.start_time = -1
            if not self.enabled:
                player.time_display = "--:--"
        if self.enabled:
            self._refresh()

    def before_action(self, action_index: int) -> None:
        if not self.enabled or not (0 <= action_index < len(self._timestamps)):
            return
        timestamp = self._timestamps[action_index]
        if timestamp is None or self._last_ts is None:
            return
        consumed = max(0.0, timestamp - self._last_ts)
        self._last_ts = timestamp
        game_state = self._game_state
        current = (game_state.player1 if game_state.turn_number % 2 == 0
                   else game_state.player2)
        if game_state.timer_mode == "countdown":
            current.elapsed_time = max(0.0, current.elapsed_time - consumed)
        else:
            current.elapsed_time += consumed
        self._refresh()

    def after_action(self) -> None:
        if self.enabled:
            self._refresh()

    def _refresh(self) -> None:
        self._game_state.player1._refresh_time_display()
        self._game_state.player2._refresh_time_display()