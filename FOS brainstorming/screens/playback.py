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

from core.game_screen import GameScreen
from core.replay_source import ReplaySource
from screens import replay_prelude, replay_select
from screens.battling import battling_replay
from screens.battling.finalize import finalize_battle


def _replay_metadata(replay_path) -> dict:
    try:
        return ReplaySource(replay_path).metadata
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"[playback] could not read replay metadata: {e}")
        return {}


def main(game_screen: GameScreen) -> None:
    replay_path = replay_select.main(game_screen)
    if replay_path is None:
        return

    if not replay_prelude.main(game_screen, _replay_metadata(replay_path)):
        return

    game_state = battling_replay.main(game_screen, replay_path)
    if game_state:
        winner = "player1" if game_state.score < 0 else "player2"
        finalize_battle(game_state, game_screen, winner)
