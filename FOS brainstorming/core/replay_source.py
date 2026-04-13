# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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
from pathlib import Path
from typing import Optional, Any

from core.game_action import GameAction


class ReplaySource:
    def __init__(self, jsonl_path: Path) -> None:
        self.jsonl_path: Path = Path(jsonl_path)
        self._entries: list[dict[str, Any]] = []
        self._action_indices: list[int] = []
        self._cursor: int = 0
        self.metadata: dict[str, Any] = {}
        
        self._load()
        self._extract_metadata()
    
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
                if entry.get("is_action") is True:
                    self._action_indices.append(idx)
    
    def _extract_metadata(self) -> None:
        first_action_idx = self._action_indices[0] if self._action_indices else len(self._entries)
        
        for entry in self._entries[:first_action_idx]:
            msg: str = entry.get("message", "")
            
            if "rng_seed" in entry:
                self.metadata["rng_seed"] = entry["rng_seed"]
            
            if "version" in entry:
                self.metadata["version"] = entry["version"]

            if msg.startswith("player1 deck "):
                self.metadata["player1_deck"] = msg[len("player1 deck "):].split("-") if msg[len("player1 deck "):] else []
            elif msg.startswith("player2 deck "):
                self.metadata["player2_deck"] = msg[len("player2 deck "):].split("-") if msg[len("player1 deck "):] else []
            
            if msg.startswith("timer mode "):
                self.metadata["timer_mode"] = msg[len("timer mode "):].strip()
    
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