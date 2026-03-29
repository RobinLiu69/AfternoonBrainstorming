import pygame
from typing import TYPE_CHECKING

from core.UI import HintBox
from core.board_config import BoardConfig
from core.board_block import initialize_board
from utils.controls import key_pressed
from utils.exhibits import exhibit, get_card_name_in_menu, all_exhibit_cards

if TYPE_CHECKING:
    from core.game_state import GameState
    from core.game_screen import GameScreen
    from core.player import Player

def turn_page(page: int, count: int, last_page: int) -> int:
    if page + count < 0:
        return last_page-1
    elif page + count >= last_page:
        return 0
    else:
        return page + count

def main(game_state: GameState) -> bool:
    running = True

    game_state.board_config = BoardConfig(4, 3)

    game_state.board_dict = initialize_board(game_state.game_screen, game_state.board_config)
    page = 0
    scrool_cooldown = 0
    last_page = len(all_exhibit_cards)-1
    deck_editor = "player1"
    hint_box = HintBox(width=int(game_state.game_screen.block_size*2), height=int(game_state.game_screen.block_size))
    clock = pygame.time.Clock()
    while running:
        game_state.game_screen.update()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_state.game_screen.display_width/2-game_state.game_screen.block_size*2))/game_state.game_screen.block_size) if mouse_x > game_state.game_screen.display_width/2-game_state.game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_state.game_screen.display_height/2-game_state.game_screen.block_size*1.65))/game_state.game_screen.block_size) if mouse_y > game_state.game_screen.display_height/2-game_state.game_screen.block_size*1.65 else None

        exhibit(page, game_state)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        match deck_editor:
                            case "player1":
                                game_state.player1.add_card_to_deck(get_card_name_in_menu(page, mouse_board_x, mouse_board_y))
                            case "player2":
                                game_state.player2.add_card_to_deck(get_card_name_in_menu(page, mouse_board_x, mouse_board_y))
                    case 3:
                        target_card_name = get_card_name_in_menu(page, mouse_board_x, mouse_board_y)
                        if target_card_name == "None":
                            match deck_editor:
                                case "player1":
                                    game_state.player1.pop_card_from_deck()
                                case "player2":
                                    game_state.player2.pop_card_from_deck()
                        else:
                            match deck_editor:
                                case "player1":
                                    game_state.player1.remove_card_from_deck(target_card_name)
                                case "player2":
                                    game_state.player2.remove_card_from_deck(target_card_name)
            if event.type == pygame.MOUSEWHEEL:
                if scrool_cooldown == 0:
                    page = turn_page(page, event.y, last_page)
                    scrool_cooldown = 0.2
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_SPACE:
                        page = turn_page(page, 1, last_page)
                    case pygame.K_a:
                        page = turn_page(page, -1, last_page)
                    case pygame.K_d:
                        page = turn_page(page, 1, last_page)
                    case pygame.K_f:
                        hint_box.turn_on = not hint_box.turn_on
                    case pygame.K_y:
                        game_state.file_auto_delet = not game_state.file_auto_delet
                    case pygame.K_s:
                        if mouse_board_x is not None and mouse_board_y is not None :
                            match deck_editor:
                                case "player1":
                                    game_state.player1.add_card_to_deck(get_card_name_in_menu(page, mouse_board_x, mouse_board_y))
                                case "player2":
                                    game_state.player2.add_card_to_deck(get_card_name_in_menu(page, mouse_board_x, mouse_board_y))
                    case pygame.K_c:
                        match deck_editor:
                            case "player1":
                                game_state.player1.pop_card_from_deck()
                            case "player2":
                                game_state.player2.pop_card_from_deck()
                    case pygame.K_e:
                        match deck_editor:
                            case "secret1":
                                deck_editor = "player1"
                            case "player1":
                                deck_editor = "secret2"
                            case "secret2":
                                deck_editor = "player2"
                            case "player2":
                                deck_editor = "secret1"
                    case pygame.K_r:
                        if deck_editor == "secret": running = False
                        deck_editor = "secret"
                    case pygame.K_t:
                        match game_state.timer_mode:
                            case "timer":
                                game_state.timer_mode = "countdown"
                            case "countdown":
                                game_state.timer_mode = "timer"
                    case pygame.K_ESCAPE:
                        running = False
                        
            if event.type == pygame.QUIT:
                return False
        
        game_state.player1.menu_deck_display(deck_editor, game_state.game_screen)
        game_state.player2.menu_deck_display(deck_editor, game_state.game_screen)
        
        game_state.player1.menu_display_timer_state(game_state)
        game_state.player1.menu_file_auto_delet_state(game_state)
        
        for board in game_state.board_dict.values():
            board.update(game_state.game_screen, game_state.board_config)
        
        if mouse_board_x is not None  and mouse_board_y is not None:
            hint_box.update(mouse_x, mouse_y, get_card_name_in_menu(page, mouse_board_x, mouse_board_y), game_state.game_screen)
        
        
        pygame.display.update()
        dt = clock.tick(60)/1000

        if scrool_cooldown != 0:
            scrool_cooldown = round(scrool_cooldown - dt, 2)

    return True