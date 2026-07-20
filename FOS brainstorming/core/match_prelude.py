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
        if names:
            host_name = names.get("host", "")
            peer_name = names.get("peer", "")
            logger.info(
                f"players {lobby_state.host_seat}={host_name or 'host'} "
                f"{lobby_state.peer_seat()}={peer_name or 'peer'}",
                category=LogCategory.GAME_FLOW,
                host_seat=lobby_state.host_seat,
                host_name=host_name, peer_name=peer_name,
            )
        for card, banner in lobby_state.bans.items():
            banner_name = names.get(banner) or banner
            logger.info(
                f"ban {card} by {banner_name}",
                category=LogCategory.GAME_FLOW,
                ban_card=card, banned_by=banner, banned_by_name=banner_name,
            )

    if draft_state is not None:
        for player, kind, card in draft_state.pick_history:
            logger.info(
                f"draft {player} {kind} {card}",
                category=LogCategory.GAME_FLOW,
                draft_event=kind, player=player, card=card,
            )
