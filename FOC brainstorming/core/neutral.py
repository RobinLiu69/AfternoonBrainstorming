
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.board_block import Board
    from core.player import Player
    from core.game_screen import GameScreen
    from core.game_state import GameState
    from cards.base import Card


@dataclass(kw_only=True)
class Neutral:
    name: str = "neutral"
    on_board: list[Card] = field(default_factory=list)

    def recycle_cards(self, game_state: GameState) -> None:
        for i, card in enumerate(self.on_board):
            if card.health <= 0 and card.can_be_killed(game_state):
                card.die(game_state)
                game_state.board_dict[card.board_x, card.board_y].occupy = False
                self.on_board.pop(i)

    def update(self, game_state: GameState) -> None:
        self.recycle_cards(game_state)
        for card in self.on_board:
            card.update(game_state)