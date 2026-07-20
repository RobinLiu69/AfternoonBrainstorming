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

from core.draft_state import DraftState
from core.lobby_state import LobbyState
from utils.logger import GameLogger, LogCategory


def log_match_prelude(logger: GameLogger, draft_state: Optional[DraftState],
                      lobby_state: Optional[LobbyState]) -> None:
    if lobby_state is not None:
        names = lobby_state.player_names
        seat_names = lobby_state.seat_names()
        p1_name = seat_names.get("player1", "")
        p2_name = seat_names.get("player2", "")
        logger.info(
            f"players player1={p1_name or 'player1'} player2={p2_name or 'player2'}",
            category=LogCategory.GAME_FLOW, to_jsonl=False,
            player1_name=p1_name, player2_name=p2_name,
            host_seat=lobby_state.host_seat,
        )
        for card, banner in lobby_state.bans.items():
            banner_name = names.get(banner) or banner
            logger.info(
                f"ban {card} by {banner_name}",
                category=LogCategory.GAME_FLOW, to_jsonl=False,
                ban_card=card, banned_by=banner, banned_by_name=banner_name,
            )

    if draft_state is not None:
        for player, kind, card in draft_state.pick_history:
            logger.info(
                f"draft {player} {kind} {card}",
                category=LogCategory.GAME_FLOW, to_jsonl=False,
                draft_event=kind, player=player, card=card,
            )
