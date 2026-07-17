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

import webbrowser

from core.game_screen import GameScreen
from cards.factory import CardFactory

from screens import playback
from screens.menu import start_screen, settings_screen, play_screen

from campaign import run_loop as campaign_run_loop
from endless import run_loop as endless_run_loop

CardFactory.register_all()


def main() -> None:
    game_screen = GameScreen()

    while True:
        mode = start_screen.main(game_screen)

        match mode:
            case "play":
                play_screen.main(game_screen)
            case "campaign":
                campaign_run_loop.main(game_screen)
            case "tower":
                endless_run_loop.main(game_screen)
            case "playback":
                playback.main(game_screen)
            case "settings":
                settings_screen.main(game_screen)
            case "donate":
                webbrowser.open('https://fiveoclockshadowdev.github.io/website/donate.html')
            case _:
                return


if __name__ == "__main__":
    main()
