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
    def create(cls, card_name: str, owner: str, board_x: int, board_y: int) -> Card:
        card_class = cls._registry.get(card_name)
        if card_class:
            return card_class(owner, board_x, board_y)
        raise ValueError(f"Unknown card: {card_name}")


def spawn_card(board_x: int, board_y: int, card_name: str, owner: str, target_board: list[Card], game_state: GameState) -> bool:
    if not spawn_check(board_x, board_y, game_state): return False
    card = CardFactory.create(card_name, owner, board_x, board_y)
    card.deploy(game_state)
    game_state.board_dict[board_x, board_y].occupy = True
    target_board.append(card)
    return True

def spawn_check(board_x: int, board_y: int, game_state: GameState) -> bool:
    return game_state.board_config.is_valid_position(board_x, board_y) and not game_state.board_dict[board_x, board_y].occupy