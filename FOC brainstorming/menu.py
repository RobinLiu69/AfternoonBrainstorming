import pygame


from exhibits import exhibit, get_card_name_in_menu, all_exhibit_cards, HintBox
from player_info import Player
from game_screen import GameScreen
from board_block import initialize_board
from controls import key_pressed


def turn_page(page: int, count: int, last_page: int) -> int:
    if page + count < 0:
        return last_page-1
    elif page + count >= last_page:
        return 0
    else:
        return page + count

def main(game_screen: GameScreen, player1: Player, player2: Player) -> None:
    running = True
    board_list = initialize_board(12, game_screen)
    page = 0
    last_page = len(all_exhibit_cards)-1
    deck_editor = "player1"
    hint_box = HintBox(width=int(game_screen.block_size*2), height=int(game_screen.block_size))
    while running:
        game_screen.update()
        
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_screen.display_width/2-game_screen.block_size*2))/game_screen.block_size) if mouse_x > game_screen.display_width/2-game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_screen.display_height/2-game_screen.block_size*1.65))/game_screen.block_size) if mouse_y > game_screen.display_height/2-game_screen.block_size*1.65 else None
        
        exhibit(page, game_screen)
        
        for event in pygame.event.get():
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
                        game_screen.file_auto_delet = not game_screen.file_auto_delet
                    case pygame.K_s:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match deck_editor:
                                case "player1":
                                    player1.add_card_to_deck(get_card_name_in_menu(page, mouse_board_x, mouse_board_y))
                                case "player2":
                                    player2.add_card_to_deck(get_card_name_in_menu(page, mouse_board_x, mouse_board_y))
                    case pygame.K_c:
                        match deck_editor:
                            case "player1":
                                player1.pop_card_from_deck()
                            case "player2":
                                player2.pop_card_from_deck()
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
                        match game_screen.timer_mode:
                            case "timer":
                                game_screen.timer_mode = "countdown"
                            case "countdown":
                                game_screen.timer_mode = "timer"
                    case pygame.K_ESCAPE:
                        running = False
                        
            if event.type == pygame.QUIT:
                running = False
                quit()
        
        player1.menu_deck_display(deck_editor, game_screen)
        player2.menu_deck_display(deck_editor, game_screen)
        
        player1.menu_display_timer_state(game_screen)
        player1.menu_file_auto_delet_state(game_screen)
        
        for board in board_list.values():
            board.update(game_screen)
        
        if mouse_board_x is not None and mouse_board_y is not None:
            hint_box.update(mouse_x, mouse_y, get_card_name_in_menu(page, mouse_board_x, mouse_board_y), game_screen)
        
        
        pygame.display.update()
        game_screen.clock.tick(60)
