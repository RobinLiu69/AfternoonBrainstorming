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

from core.lobby_state import LobbyState
from utils.logger import GameLogger, LogCategory


def log_player_names(logger: GameLogger, lobby_state: Optional[LobbyState]) -> None:
    if lobby_state is None:
        return
    seat_names = lobby_state.seat_names()
    p1_name = seat_names.get("player1", "")
    p2_name = seat_names.get("player2", "")
    logger.info(
        f"players player1={p1_name or 'player1'} player2={p2_name or 'player2'}",
        category=LogCategory.GAME_FLOW,
        player1_name=p1_name, player2_name=p2_name,
        host_seat=lobby_state.host_seat,
    )


def resolve_ban_draft(lobby_state: Optional[LobbyState]) -> dict[str, str]:
    if lobby_state is None:
        return {}
    seat_names = lobby_state.seat_names()
    resolved: dict[str, str] = {}
    for card, identity in lobby_state.bans.items():
        seat = lobby_state.host_seat if identity == "host" else lobby_state.peer_seat()
        resolved[card] = seat_names.get(seat) or seat
    return resolved


def _log_ban_line(logger: GameLogger, banner: str, cards: list[str]) -> None:
    if not cards:
        return
    logger.info(
        f"ban {'-'.join(cards)} by {banner}",
        category=LogCategory.GAME_FLOW,
        ban_cards=list(cards), banned_by_name=banner,
    )


def log_ban_draft(logger: GameLogger, ban_draft: dict[str, str]) -> None:
    grouped: dict[str, list[str]] = {}
    for card, banner in ban_draft.items():
        grouped.setdefault(banner, []).append(card)
    for banner, cards in grouped.items():
        _log_ban_line(logger, banner, cards)


def judge_bans_of(ban_deck: list[str], ban_draft: dict[str, str]) -> list[str]:
    return [card for card in ban_deck if card not in ban_draft]


def log_judge_bans(logger: GameLogger, cards: list[str]) -> None:
    _log_ban_line(logger, "judge", cards)


def log_match_prelude(logger: GameLogger, lobby_state: Optional[LobbyState]) -> None:
    """Write the non-secret match header (player names + bans).

    Competitions transmit only the jsonl, so this goes to both the .log and the
    .jsonl (to_jsonl defaults True) — names and bans are known to both players.
    Secret info (final decks, rng_seed) is NOT written here; it is logged at
    game over so it never sits in the file mid-match (see fog-of-war).
    Per-pick add/remove churn is intentionally not recorded at all.
    """
    if lobby_state is None:
        return
    log_player_names(logger, lobby_state)
    names = lobby_state.player_names
    for card, banner in lobby_state.bans.items():
        banner_name = names.get(banner) or banner
        logger.info(
            f"ban {card} by {banner_name}",
            category=LogCategory.GAME_FLOW,
            ban_card=card, banned_by=banner, banned_by_name=banner_name,
        )
