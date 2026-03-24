
from dataclasses import dataclass, field

from core.board_block import Board
from core.player import Player
from core.spawn import spawn_card
from core.game_screen import GameScreen, draw_text
from cards.card import Card


@dataclass(kw_only=True)
class Neutral:
    name: str = "neutral"
    on_board: list[Card] = field(default_factory=list)

    def recycle_cards(self, player1: Player, player2: Player, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for i, card in enumerate(self.on_board):
            if card.health <= 0 and card.can_be_killed(player1, player2, self, board_dict, game_screen):
                card.die(player1, player2, self, board_dict, game_screen)
                board_dict[str(card.board_x)+"-"+str(card.board_y)].occupy = False
                self.on_board.pop(i)

    def update(self, player1: Player, player2: Player, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.recycle_cards(player1, player2, board_dict, game_screen)
        for card in self.on_board:
            card.update(player1, player2, self, board_dict, game_screen)