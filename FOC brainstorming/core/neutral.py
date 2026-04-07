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

    def recycle_cards(self, game_state: GameState, game_renderer: GameRenderer) -> None:
        for i, card in enumerate(self.on_board):
            if card.health <= 0 and card.can_be_killed(game_state):
                card.die(game_state)
                game_renderer.card_renderer.release(card.instance_id)
                game_state.board_dict[card.board_x, card.board_y].occupy = False
                self.on_board.pop(i)

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