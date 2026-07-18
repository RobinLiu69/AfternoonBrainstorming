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

import base64
from typing import Optional

from core.game_state import GameState
from core.game_screen import GameScreen
from core.network_layer import LANServer
from screens.end_game import end_game


def _broadcast_log_backup(game_state: GameState, server: LANServer) -> None:
    logger = game_state.game_logger
    log_path = logger.log_file
    jsonl_path = logger._jsonl_path
    if log_path is None or jsonl_path is None:
        return

    logger.close()
    try:
        log_b64 = base64.b64encode(log_path.read_bytes()).decode("ascii")
        jsonl_b64 = base64.b64encode(jsonl_path.read_bytes()).decode("ascii")
    except OSError as e:
        print(f"[finalize] failed to read log files for backup: {e}")
        return
    server.broadcast_log_files(log_path.name, log_b64, jsonl_path.name, jsonl_b64)


def finalize_battle(game_state: GameState, game_screen: GameScreen, winner: str,
                    server: Optional[LANServer] = None) -> None:
    game_state.game_logger.info(f"winner {winner}")
    game_state.game_logger.info(f"player1 timer {game_state.player1.time_display}")
    game_state.game_logger.info(f"player2 timer {game_state.player2.time_display}")
    game_state.game_logger.info(f"{game_state.game_statistics.export_for_charts()}")
    game_state.game_logger.info(f"{game_state.game_statistics.score_history}")

    if server is not None:
        _broadcast_log_backup(game_state, server)

    end_game.main(winner, game_state, game_screen)
