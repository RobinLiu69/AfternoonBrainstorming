# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendering.game_renderer import GameRenderer
    from core.game_state import GameState
    from cards.base import Card


@dataclass(kw_only=True)
class Neutral:
    name: str = "neutral"
    on_board: list[Card] = field(default_factory=list)

    def recycle_cards(self, game_state:GameState, game_renderer: GameRenderer) -> None:
        to_remove = []
        for card in self.on_board:
            if card.health <= 0 and card.can_be_killed(game_state):
                card.die(game_state)
                game_renderer.dying_cards.append(card)
                game_state.board_dict[card.board_x, card.board_y].occupy = False
                game_state.game_logger.log_card_recycled(self.name, card.job_and_color, (card.board_x, card.board_y))
                to_remove.append(card)
        for card in to_remove:
            self.on_board.remove(card)

    def update(self, game_state: GameState, game_renderer: GameRenderer) -> None:
        self.recycle_cards(game_state, game_renderer)

    def to_dict(self) -> dict:
        return {"on_board": [c.to_dict() for c in self.on_board]}

    def apply_dict(self, data: dict, old_by_iid: dict, all_cards_by_iid: dict, game_renderer: GameRenderer) -> None:
        from cards.factory import CardFactory
        new_on_board = []
        for card_data in data["on_board"]:
            iid = card_data["instance_id"]
            existing = old_by_iid.get(iid)
            if existing is not None:
                existing.apply_dict(card_data)
                new_on_board.append(existing)
                all_cards_by_iid[iid] = existing
            else:
                fresh = CardFactory.from_dict(card_data)
                new_on_board.append(fresh)
                all_cards_by_iid[iid] = fresh
 
        self.on_board = new_on_board