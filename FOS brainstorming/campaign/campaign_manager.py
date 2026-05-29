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

from campaign.ai_decks import STAGE_AI_DECKS, STAGE_PLAYER_DECKS


def build_campaign_game_state(
    stage: str,
    file_auto_delete: bool = False,
    player_deck_override: list[str] | None = None,
) -> GameState:
    """Default `file_auto_delete=False` so .log + .jsonl persist under
    `battle_records/` and the player can replay campaign matches from the
    Playback menu, identical to local 2P games."""
    p1_deck = (player_deck_override or STAGE_PLAYER_DECKS[stage]).copy()
    p2_deck = STAGE_AI_DECKS[stage].copy()

    player1 = Player(name="player1", deck=p1_deck, hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=p2_deck, hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    logger = GameLogger(enable_file=not file_auto_delete, enable_console=True, enable_jsonl=not file_auto_delete)
    game_state = GameState(player1, player2, neutral, BoardConfig(), game_logger=logger)
    game_state.timer_mode = "timer"
    game_state.file_auto_delete = file_auto_delete
    # Note: stage buffs (initial hand, board lucky blocks, +HP) are applied later by
    # AIController._ensure_initialized — at this point board_dict is still empty and
    # players haven't been initialized() yet, so draws/spawns would no-op.

    game_state.game_logger.info(f"campaign stage {stage}")
    game_state.game_logger.info(f"player1 deck {'-'.join(player1.deck)}")
    game_state.game_logger.info(f"player2 deck {'-'.join(player2.deck)}")
    game_state.game_logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)
    game_state.game_logger.info(f"version {VERSION}", version=VERSION)
    return game_state
