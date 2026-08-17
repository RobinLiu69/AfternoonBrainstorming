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

import secrets
import threading
from typing import Any

SEATS: tuple[str, str] = ("player1", "player2")
WATCHER_ROLES: tuple[str, str] = ("spectator", "god")


class Roster:
    def __init__(self, host_seat: str = "player1", god_view: bool = False) -> None:
        self.host_seat = host_seat
        self.god_view = god_view
        self.host_playing = True
        self._lock = threading.RLock()
        self._members: list[tuple[Any, str]] = []
        self._tokens: dict[str, str] = {}
        self._evicted: set[Any] = set()

    def peer_seat(self) -> str:
        return "player2" if self.host_seat == "player1" else "player1"

    def open_seats(self) -> tuple[str, ...]:
        if self.host_playing:
            return (self.peer_seat(),)
        return (self.host_seat, self.peer_seat())

    def watcher_role(self) -> str:
        return "god" if self.god_view else "spectator"

    def add(self, conn: Any, role: str) -> None:
        with self._lock:
            self._members.append((conn, role))

    def drop(self, conn: Any) -> tuple[str, bool]:
        with self._lock:
            role = self.role_of(conn)
            was_evicted = conn in self._evicted
            self._evicted.discard(conn)
            self._members = [m for m in self._members if m[0] is not conn]
            return role, was_evicted

    def drop_many(self, conns: list) -> list[str]:
        with self._lock:
            dropped = [r for c, r in self._members if c in conns]
            self._members = [m for m in self._members if m[0] not in conns]
            for conn in conns:
                self._evicted.discard(conn)
            return dropped

    def clear(self) -> list:
        with self._lock:
            conns = [c for c, _r in self._members]
            self._members.clear()
            self._evicted.clear()
            return conns

    def members(self) -> list[tuple[Any, str]]:
        with self._lock:
            return list(self._members)

    def roles(self) -> list[str]:
        with self._lock:
            return [r for _c, r in self._members]

    def role_of(self, conn: Any) -> str:
        with self._lock:
            return next((r for c, r in self._members if c is conn), "")

    def conn_for(self, role: str) -> Any:
        with self._lock:
            return next((c for c, r in self._members if r == role), None)

    def has_role(self, role: str) -> bool:
        with self._lock:
            return any(r == role for _c, r in self._members)

    def count(self) -> int:
        with self._lock:
            return len(self._members)

    def count_watchers(self) -> int:
        with self._lock:
            return sum(1 for _c, r in self._members if r in WATCHER_ROLES)

    def reassign(self, conn: Any, new_role: str) -> bool:
        with self._lock:
            for i, (c, _r) in enumerate(self._members):
                if c is conn:
                    self._members[i] = (c, new_role)
                    return True
        return False

    def token_holder(self, token: str) -> str:
        with self._lock:
            return next((role for role, held in self._tokens.items() if held == token), "")

    def issue_token(self, role: str) -> str:
        with self._lock:
            token = secrets.token_urlsafe(16)
            self._tokens[role] = token
            return token

    def adopt_token(self, role: str, token: str) -> None:
        with self._lock:
            self._tokens[role] = token

    def move_token(self, old_role: str, new_role: str) -> None:
        with self._lock:
            if old_role in self._tokens:
                self._tokens[new_role] = self._tokens.pop(old_role)

    def clear_token(self, role: str) -> None:
        with self._lock:
            self._tokens.pop(role, None)

    def claim(self, intent: str, token: str | None, in_lobby: bool) -> tuple[str, str, list]:
        with self._lock:
            held_by = self.token_holder(token) if token else ""
            if held_by:
                return held_by, token, self._evict(held_by)  # type: ignore[return-value]

            taken = {r for _c, r in self._members}
            free = next((seat for seat in self.open_seats() if seat not in taken), "")
            if intent == "play" and free and in_lobby:
                return free, self.issue_token(free), []
            return self.watcher_role(), "", []

    def _evict(self, role: str) -> list:
        evicted = [c for c, r in self._members if r == role]
        self._members = [m for m in self._members if m[1] != role]
        self._evicted.update(evicted)
        return evicted

    def update_host_seat(self, new_seat: str) -> None:
        if new_seat not in SEATS or new_seat == self.host_seat:
            return
        old_host, old_peer = self.host_seat, self.peer_seat()
        self.host_seat = new_seat
        swap = ({old_peer: self.peer_seat()} if self.host_playing
                else {old_host: old_peer, old_peer: old_host})
        with self._lock:
            self._members = [(c, swap.get(r, r)) for c, r in self._members]
            self._tokens = {swap.get(r, r): t for r, t in self._tokens.items()}

    def update_god_view(self, god_view: bool) -> None:
        self.god_view = god_view
        stale = "spectator" if god_view else "god"
        fresh = self.watcher_role()
        with self._lock:
            self._members = [(c, fresh if r == stale else r) for c, r in self._members]
