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

from shared.setting import VERSION
from core.game_state import GameState
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral
from utils.logger import GameLogger


def build_game_state(run: dict, enemy: dict) -> GameState:
    """The player fights with the deck only - the bench stays in camp."""
    player1 = Player(name="player1", deck=list(run["deck"]),
                     hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=list(enemy["deck"]),
                     hand=[], on_board=[], draw_pile=[], discard_pile=[])

    logger = GameLogger(enable_file=True, enable_console=True, enable_jsonl=True)
    game_state = GameState(player1, player2, Neutral(), BoardConfig(), game_logger=logger)
    game_state.timer_mode = "timer"

    logger.info(f"tower act {run['act']} layer {run['layer']} vs {enemy['label']}")
    logger.info(f"player1 deck {'-'.join(player1.deck)}")
    logger.info(f"player2 deck {'-'.join(player2.deck)}")
    logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)
    logger.info(f"version {VERSION}", version=VERSION)
    return game_state
