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

from typing import Optional

from core.game_screen import GameScreen
from core.network_layer import LANClient
from screens.notices import notice_screen, server_closed_screen


def main(game_screen: GameScreen) -> None:
    notice_screen.main(game_screen, "Connection Timeout",
                       "no response from the host")


def show_for(game_screen: GameScreen, client: Optional[LANClient]) -> None:
    if client is not None and client.timed_out:
        main(game_screen)
    else:
        server_closed_screen.main(game_screen)
