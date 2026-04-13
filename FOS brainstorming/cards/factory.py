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
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.board_block import Board
    from core.game_state import GameState
    from cards.base import Card


class CardFactory:
    _registry = {}
    
    @classmethod
    def register(cls, card_name: str, card_class: type) -> None:
        cls._registry[card_name] = card_class
    
    @classmethod
    def create(cls, card_name: str, owner: str, board_x: int, board_y: int, **kwargs) -> Card:
        card_class = cls._registry.get(card_name)
        if card_class:
            return card_class(owner, board_x, board_y, **kwargs)
        raise ValueError(f"Unknown card: {card_name}")

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        card_class = cls._registry.get(data["job_and_color"])
        if card_class is None:
            raise ValueError(f"Unknown job_and_color: {data['job_and_color']!r}")
        
        try:
            init_args = card_class.init_args_from_dict(data)
            card = card_class(**init_args)
        except TypeError as e:
            print(f"[factory] fallback to __new__ for {data['job_and_color']}: {e}")
            card = card_class.__new__(card_class)
            card.__post_init__()
        
        card.instance_id = data["instance_id"]
        card.apply_dict(data)
        return card


def spawn_card(board_x: int, board_y: int, card_name: str, owner: str, target_board: list[Card], game_state: GameState, **kwargs) -> bool:
    if not spawn_check(board_x, board_y, game_state): return False
    card = CardFactory.create(card_name, owner, board_x, board_y, **kwargs)
    card.deploy(game_state)
    game_state.board_dict[board_x, board_y].occupy = True
    target_board.append(card)
    return True


def spawn_check(board_x: int, board_y: int, game_state: GameState) -> bool:
    return game_state.board_config.is_valid_position(board_x, board_y) and not game_state.board_dict[board_x, board_y].occupy