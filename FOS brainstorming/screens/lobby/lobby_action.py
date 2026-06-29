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

from dataclasses import dataclass
from typing import Literal, Optional


LobbyActionType = Literal[
    "set_god_view",
    "set_timer_mode",
    "set_file_auto_delete",
    "set_reconnect_timeout",
    "swap_seats",
    "switch_to_spectator",
    "switch_to_player",
    "start_match",
    "quit",
]


@dataclass
class LobbyAction:
    player: str
    action_type: LobbyActionType
    bool_value: Optional[bool] = None
    str_value: Optional[str] = None
    float_value: Optional[float] = None
