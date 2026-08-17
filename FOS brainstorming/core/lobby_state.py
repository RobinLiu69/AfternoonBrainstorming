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

import re
from dataclasses import dataclass, field

from shared.setting import CARD_SETTING, JOB_DICTIONARY, JOB_ORDER
from core.match_settings import (
    MATCH_SETTING_NAMES,
    MatchSettings,
    RULESET_OPTIONS,
    TIME_CONTROL_OPTIONS,
)


INFINITE_RECONNECT: float = float("inf")
RECONNECT_TIMEOUT_OPTIONS: tuple[float, ...] = (30.0, 60.0, 120.0, 300.0, INFINITE_RECONNECT)

MAX_BANS_PER_PLAYER: int = 4

MAX_NAME_LENGTH: int = 16
PLAYER_NAME_PATTERN = re.compile(rf"^[A-Za-z0-9_]{{1,{MAX_NAME_LENGTH}}}$")

BANNABLE_MAGIC_CARDS: frozenset[str] = frozenset({"CUBES", "HEAL", "MOVE"})


def is_bannable_card(name: str) -> bool:
    if name in BANNABLE_MAGIC_CARDS:
        return True
    for tag, color_name in JOB_DICTIONARY["colors_dict"].items():
        if name.endswith(tag) and name[:-len(tag)] in JOB_ORDER:
            return name[:-len(tag)] in CARD_SETTING.get(color_name, {})
    return False


SETTING_OPTIONS: dict[str, tuple] = {
    "timer_mode": ("timer", "countdown"),
    "time_control": tuple(TIME_CONTROL_OPTIONS),
    "ruleset": RULESET_OPTIONS,
    "file_auto_delete": (False, True),
    "god_view": (False, True),
    "reconnect_timeout": RECONNECT_TIMEOUT_OPTIONS,
}


@dataclass
class LobbyState:
    host_seat: str = "player1"
    god_view: bool = False
    reconnect_timeout: float = 60.0
    settings: MatchSettings = field(default_factory=MatchSettings)

    host_playing: bool = True
    host_watching: bool = False
    peer_connected: bool = False
    host_seat_connected: bool = False
    spectator_count: int = 0
    latencies: dict = field(default_factory=dict)

    room_code: str = ""
    local_role: str = ""

    in_ban_draft: bool = False
    bans: dict[str, str] = field(default_factory=dict)
    player_names: dict[str, str] = field(default_factory=dict)

    def peer_seat(self) -> str:
        return "player2" if self.host_seat == "player1" else "player1"

    def open_seats(self) -> tuple[str, ...]:
        if self.host_playing:
            return (self.peer_seat(),)
        return (self.host_seat, self.peer_seat())

    def seat_identity(self, seat: str) -> str:
        return "host" if seat == self.host_seat else "peer"

    def seat_filled(self, seat: str) -> bool:
        if seat == self.host_seat:
            return self.host_playing or self.host_seat_connected
        return self.peer_connected

    def watcher_count(self) -> int:
        return self.spectator_count + (1 if self.host_watching else 0)

    def both_seats_filled(self) -> bool:
        return self.seat_filled(self.host_seat) and self.seat_filled(self.peer_seat())

    def ban_count(self, seat: str) -> int:
        return sum(1 for banner in self.bans.values() if banner == seat)

    def display_name(self, identity: str) -> str:
        return self.player_names.get(identity, "")

    def seat_names(self) -> dict[str, str]:
        names: dict[str, str] = {}
        host_name = self.player_names.get("host", "")
        peer_name = self.player_names.get("peer", "")
        if host_name:
            names[self.host_seat] = host_name
        if peer_name:
            names[self.peer_seat()] = peer_name
        return names

    def set_value(self, name: str, value) -> None:
        if name in MATCH_SETTING_NAMES:
            setattr(self.settings, name, value)
        else:
            setattr(self, name, value)

    def to_dict(self) -> dict:
        return {
            "host_seat": self.host_seat,
            "god_view": self.god_view,
            "reconnect_timeout": self.reconnect_timeout,
            **self.settings.to_dict(),
            "host_playing": self.host_playing,
            "host_watching": self.host_watching,
            "peer_connected": self.peer_connected,
            "host_seat_connected": self.host_seat_connected,
            "spectator_count": self.spectator_count,
            "latencies": dict(self.latencies),
            "room_code": self.room_code,
            "in_ban_draft": self.in_ban_draft,
            "bans": dict(self.bans),
            "player_names": dict(self.player_names),
        }

    def to_dict_for(self, viewer_role: str) -> dict:
        data = self.to_dict()
        data["your_role"] = viewer_role
        return data

    def apply_dict(self, data: dict) -> None:
        self.host_seat = data["host_seat"]
        self.god_view = data["god_view"]
        self.reconnect_timeout = data["reconnect_timeout"]
        self.settings.apply_dict(data)
        self.host_playing = data.get("host_playing", True)
        self.host_watching = data.get("host_watching", False)
        self.peer_connected = data["peer_connected"]
        self.host_seat_connected = data.get("host_seat_connected", False)
        self.spectator_count = data["spectator_count"]
        self.latencies = data.get("latencies", {})
        self.room_code = data.get("room_code", self.room_code)
        self.in_ban_draft = data.get("in_ban_draft", False)
        self.bans = dict(data.get("bans", {}))
        self.player_names = dict(data.get("player_names", {}))
        new_role = data.get("your_role", "")
        if new_role:
            self.local_role = new_role
