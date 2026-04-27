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

from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, overload

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.base import Card

_CardType = TypeVar("_CardType", bound="Card")


class CardFactory:
    _registry = {}
    _all_registered = False

    @classmethod
    def register(cls, card_name: str, card_class: type) -> None:
        cls._registry[card_name] = card_class

    @classmethod
    def register_all(cls) -> None:
        if cls._all_registered:
            return
        cls._all_registered = True
        from cards import (
            base, card_red, card_blue, card_cyan, card_dark_green, card_fuchsia,
            card_green, card_orange, card_purple, card_white,
        )

    @overload
    @classmethod
    def create(cls, card_name: type[_CardType], owner: str, board_x: int, board_y: int, **kwargs) -> _CardType: ...
    @overload
    @classmethod
    def create(cls, card_name: str, owner: str, board_x: int, board_y: int, **kwargs) -> "Card": ...

    @classmethod
    def create(cls, card_name, owner: str, board_x: int, board_y: int, **kwargs):
        if isinstance(card_name, type):
            return card_name(owner, board_x, board_y, **kwargs)
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
    price_check = getattr(card, "price_check", None)
    if price_check is not None and not price_check(game_state):
        return False
    card.deploy(game_state)
    game_state.board_dict[board_x, board_y].occupy = True
    target_board.append(card)
    return True


def spawn_check(board_x: int, board_y: int, game_state: GameState) -> bool:
    return game_state.board_config.is_valid_position(board_x, board_y) and not game_state.board_dict[board_x, board_y].occupy