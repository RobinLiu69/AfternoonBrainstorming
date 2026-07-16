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


INFINITE_RECONNECT: float = float("inf")
RECONNECT_TIMEOUT_OPTIONS: tuple[float, ...] = (30.0, 60.0, 120.0, 300.0, INFINITE_RECONNECT)

TIME_CONTROL_OPTIONS: dict[str, tuple[int, int]] = {
    "5min": (300, 0),
    "10min": (600, 0),
    "15min": (900, 0),
    "20min": (1200, 0),
    "5+5": (300, 5),
    "10+10": (600, 10),
    "15+10": (900, 10),
}
DEFAULT_TIME_CONTROL: str = "10min"


@dataclass
class LobbyState:
    host_seat: str = "player1"
    god_view: bool = False
    timer_mode: str = "timer"
    time_control: str = DEFAULT_TIME_CONTROL
    file_auto_delete: bool = False
    reconnect_timeout: float = 60.0

    peer_connected: bool = False
    spectator_count: int = 0
    latencies: dict = field(default_factory=dict)

    room_code: str = ""
    local_role: str = ""

    def peer_seat(self) -> str:
        return "player2" if self.host_seat == "player1" else "player1"

    def countdown_seconds(self) -> int:
        return TIME_CONTROL_OPTIONS.get(self.time_control, TIME_CONTROL_OPTIONS[DEFAULT_TIME_CONTROL])[0]

    def increment_seconds(self) -> int:
        return TIME_CONTROL_OPTIONS.get(self.time_control, TIME_CONTROL_OPTIONS[DEFAULT_TIME_CONTROL])[1]

    def to_dict(self) -> dict:
        return {
            "host_seat": self.host_seat,
            "god_view": self.god_view,
            "timer_mode": self.timer_mode,
            "time_control": self.time_control,
            "file_auto_delete": self.file_auto_delete,
            "reconnect_timeout": self.reconnect_timeout,
            "peer_connected": self.peer_connected,
            "spectator_count": self.spectator_count,
            "latencies": dict(self.latencies),
            "room_code": self.room_code,
        }

    def to_dict_for(self, viewer_role: str) -> dict:
        data = self.to_dict()
        data["your_role"] = viewer_role
        return data

    def apply_dict(self, data: dict) -> None:
        self.host_seat = data["host_seat"]
        self.god_view = data["god_view"]
        self.timer_mode = data["timer_mode"]
        self.time_control = data.get("time_control", self.time_control)
        self.file_auto_delete = data["file_auto_delete"]
        self.reconnect_timeout = data["reconnect_timeout"]
        self.peer_connected = data["peer_connected"]
        self.spectator_count = data["spectator_count"]
        self.latencies = data.get("latencies", {})
        self.room_code = data.get("room_code", self.room_code)
        new_role = data.get("your_role", "")
        if new_role:
            self.local_role = new_role
