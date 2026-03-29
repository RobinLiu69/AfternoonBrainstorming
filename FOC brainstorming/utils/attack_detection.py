import pygame
from typing import TYPE_CHECKING

from cards.base import Card

if TYPE_CHECKING:
    from core.game_state import GameState
    from core.game_screen import  GameScreen
    from core.board_block import Board


def attack_area_display(controller: str, board_x: int, board_y: int, game_state: GameState) -> None:
    target_cards = tuple(filter(lambda card: card.board_x == board_x and card.board_y == board_y, game_state.get_all_cards()))
    if target_cards:
        target_card: Card = target_cards[0]
        color = (0, 0, 0)
        
        if target_card.owner == controller:
            color = (200, 200, 200)
        else:
            color = (200, 0, 0)
        card_attack_blocks = target_card.attack_area_display(game_state)
        for board_x, board_y in card_attack_blocks:
            draw_board(color, board_x, board_y, game_state.game_screen)

def draw_board(color: tuple[int, int, int], board_x: int, board_y: int, game_screen: GameScreen) -> None:
    image = pygame.surface.Surface((game_screen.block_size, game_screen.block_size))
    image.fill(color)
    image.set_alpha(60)
    rect = (((game_screen.display_width/2)-(game_screen.block_size*2))+(board_x*game_screen.block_size)+(game_screen.block_size*0), (game_screen.display_height/2)-(game_screen.block_size*1.675)+(board_y*game_screen.block_size)+(game_screen.block_size*0), game_screen.block_size, game_screen.block_size)
    game_screen.surface.blit(image, rect)
    