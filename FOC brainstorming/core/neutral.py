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
                game_renderer.card_renderer.release(card.get_uid())
                game_state.board_dict[card.board_x, card.board_y].occupy = False
                self.on_board.pop(i)

    def update(self, game_state: GameState, game_renderer: GameRenderer) -> None:
        self.recycle_cards(game_state, game_renderer)

    def to_dict(self) -> dict:
        return {
            # "name": self.name,
            "on_board": list(card.to_dict() for card in self.on_board)
        }

    @classmethod
    def from_dict(cls, data: dict) -> Neutral:
        neutral = cls()
        neutral.on_board = data["data"]
        return neutral