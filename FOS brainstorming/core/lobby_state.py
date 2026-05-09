# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
# -----------------------------------------------------------------

from dataclasses import dataclass


RECONNECT_TIMEOUT_OPTIONS: tuple[float, ...] = (30.0, 60.0, 120.0, 300.0)


@dataclass
class LobbyState:
    host_seat: str = "player1"
    god_view: bool = False
    timer_mode: str = "timer"
    file_auto_delete: bool = False
    reconnect_timeout: float = 60.0

    peer_connected: bool = False
    spectator_count: int = 0

    local_role: str = ""

    def peer_seat(self) -> str:
        return "player2" if self.host_seat == "player1" else "player1"

    def to_dict(self) -> dict:
        return {
            "host_seat": self.host_seat,
            "god_view": self.god_view,
            "timer_mode": self.timer_mode,
            "file_auto_delete": self.file_auto_delete,
            "reconnect_timeout": self.reconnect_timeout,
            "peer_connected": self.peer_connected,
            "spectator_count": self.spectator_count,
        }

    def to_dict_for(self, viewer_role: str) -> dict:
        data = self.to_dict()
        data["your_role"] = viewer_role
        return data

    def apply_dict(self, data: dict) -> None:
        self.host_seat = data["host_seat"]
        self.god_view = data["god_view"]
        self.timer_mode = data["timer_mode"]
        self.file_auto_delete = data["file_auto_delete"]
        self.reconnect_timeout = data["reconnect_timeout"]
        self.peer_connected = data["peer_connected"]
        self.spectator_count = data["spectator_count"]
        new_role = data.get("your_role", "")
        if new_role:
            self.local_role = new_role
