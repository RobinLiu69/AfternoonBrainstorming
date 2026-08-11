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

from typing import TYPE_CHECKING, overload

from cards.defs import CARD_DEFS, CardDef
from cards.events import Event

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.runtime import Card


class CardFactory:
    """Builds cards from their definitions.

    ``_registry`` is the live definition table, so existing callers that test
    membership (``"ADCR" in CardFactory._registry``) keep working.
    """

    _registry: dict[str, CardDef] = CARD_DEFS

    @classmethod
    def register(cls, card_name: str, definition: CardDef) -> None:
        cls._registry[card_name] = definition

    @classmethod
    def register_all(cls) -> None:
        from cards.definitions import load_all
        load_all()

    @overload
    @classmethod
    def create(cls, card_name: CardDef, owner: str, board_x: int, board_y: int, **kwargs) -> "Card": ...
    @overload
    @classmethod
    def create(cls, card_name: str, owner: str, board_x: int, board_y: int, **kwargs) -> "Card": ...

    @classmethod
    def create(cls, card_name, owner: str, board_x: int, board_y: int, **kwargs) -> "Card":
        if isinstance(card_name, CardDef):
            return card_name(owner, board_x, board_y, **kwargs)
        cls.register_all()
        definition = cls._registry.get(card_name)
        if definition is None:
            raise ValueError(f"Unknown card: {card_name}")
        return definition(owner, board_x, board_y, **kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        from cards.runtime import Card
        cls.register_all()
        if data["job_and_color"] not in cls._registry:
            raise ValueError(f"Unknown job_and_color: {data['job_and_color']!r}")
        return Card.from_dict(data)


def spawn_card(
    board_x: int,
    board_y: int,
    card_name: str,
    owner: str,
    target_board: list,
    game_state: "GameState",
    **kwargs,
) -> bool:
    """Place a card, if the square is free and the card can be paid for."""
    if not spawn_check(board_x, board_y, game_state):
        return False

    from cards.actions import DeployCost
    card = CardFactory.create(card_name, owner, board_x, board_y, **kwargs)
    card.bind(game_state)

    cost = DeployCost(card=card, gs=game_state)
    game_state.effects.replace(game_state, Event.DEPLOY_COST, cost, [card])
    if cost.cancelled:
        return False

    # Deployment resolves before the card joins the board, so an arrival effect
    # sees the state it is arriving into. Several cards depend on this.
    card.deploy(game_state)
    game_state.board_dict[board_x, board_y].occupy = True
    target_board.append(card)
    return True


def spawn_check(board_x: int, board_y: int, game_state: "GameState") -> bool:
    return (
        game_state.board_config.is_valid_position(board_x, board_y)
        and not game_state.board_dict[board_x, board_y].occupy
    )
