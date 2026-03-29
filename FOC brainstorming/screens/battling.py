import pygame

from core.game_state import GameState, WHITE
from core.game_screen import draw_text
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral
from core.board_block import initialize_board
from core.UI import ScoreDisplay, HintBox
from utils.exhibits import get_card_in_battling
from utils.controls import key_pressed
from utils.attack_detection import attack_area_display


def number_key(number: int, mouse_x: int, mouse_y: int, mouse_board_x: int | None, mouse_board_y: int | None, controller: str, game_state: GameState) -> None:
    if mouse_board_x is not None and mouse_board_y is not None:
        match controller:
            case "player1":
                game_state.player1.play_card(mouse_board_x, mouse_board_y, number-1, game_state)
            case "player2":
                game_state.player2.play_card(mouse_board_x, mouse_board_y, number-1, game_state)
    # elif mouse_x < game_state.game_screen.display_width/2-game_state.game_screen.block_size*2 or mouse_x > game_state.game_screen.display_width/2+game_state.game_screen.block_size*2:
    #     if mouse_x < game_state.game_screen.display_width/2 and controller == "player1":
    #         name, i = game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_state.game_screen)
    #         if number-1 != i: return
    #         if name != "None":
    #             if game_state.player1.hand[i].endswith(" (+)"):
    #                 game_state.player1.hand[i] = game_state.player1.hand[i].replace(" (+)", "")
    #             else:
    #                 game_state.player1.hand[i] += " (+)"
    #     elif mouse_x > game_state.game_screen.display_width/2 and controller == "player2":
    #         name, i = game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_state.game_screen)
    #         if number-1 != i: return
    #         if name != "None":
    #             if game_state.player2.hand[i].endswith(" (+)"):
    #                 game_state.player2.hand[i] = game_state.player2.hand[i].replace(" (+)", "")
    #             else:
    #                 game_state.player2.hand[i] += " (+)"

def display_controller(controller: str, game_state: GameState) -> None:
    draw_text(f"Ture: {controller}", game_state.game_screen.big_text_font, WHITE, game_state.game_screen.display_width/2-game_state.game_screen.block_size*0.6, game_state.game_screen.display_height/2-game_state.game_screen.block_size*2.1, game_state.game_screen.surface)
    
    
def main(game_state: GameState) -> str:
    running: bool = True

    game_state.board_config = BoardConfig()

    game_state.board_dict = initialize_board(game_state.game_screen, game_state.board_config)
    hint_box = HintBox(width=int(game_state.game_screen.block_size*2), height=int(game_state.game_screen.block_size))
    score_display = ScoreDisplay(width=int(game_state.game_screen.block_size*0.15), height=int(game_state.game_screen.block_size*0.15))
    
    game_state.player1.initialize(game_state)
    game_state.player2.initialize(game_state)
    controller: str = "player1"

    card_info = ["None", 0]

    game_state.game_logger.log_turn_start("player1", game_state.turn_number)
    
    winner: str = "None"
    clock = pygame.time.Clock()
    while running:
        game_state.game_screen.update()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_state.game_screen.display_width/2-game_state.game_screen.block_size*2))/game_state.game_screen.block_size) if mouse_x > game_state.game_screen.display_width/2-game_state.game_screen.block_size*2 and mouse_x < game_state.game_screen.display_width/2+game_state.game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_state.game_screen.display_height/2-game_state.game_screen.block_size*1.65))/game_state.game_screen.block_size) if mouse_y > game_state.game_screen.display_height/2-game_state.game_screen.block_size*1.65 and mouse_y < game_state.game_screen.display_height/2+game_state.game_screen.block_size*2.35 else None
        
        
        if mouse_board_x is not None and mouse_board_y is not None:
            attack_area_display(controller, mouse_board_x, mouse_board_y, game_state)

        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        match controller:
                            case "player1":
                                if game_state.player1.selected_card_index != -1:
                                    if mouse_board_x is not None and mouse_board_y is not None:
                                        game_state.player1.play_card(mouse_board_x, mouse_board_y, game_state.player1.selected_card_index, game_state)
                                        game_state.player1.selected_card_index = -1
                                        card_info[0] = "None"
                                if mouse_x < game_state.game_screen.display_width/2-game_state.game_screen.block_size*2:
                                    card_info = list(game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_state.game_screen))
                                if card_info and card_info[0] != "None" and isinstance(card_info[1], int):
                                    game_state.player1.selecte_card_from_hand(card_info[1])
                                    if game_state.player1.selected_card_index == -1:
                                        card_info[0] = "None"
                            case "player2":
                                if game_state.player2.selected_card_index != -1:
                                    if mouse_board_x is not None and mouse_board_y is not None:
                                        game_state.player2.play_card(mouse_board_x, mouse_board_y, game_state.player2.selected_card_index, game_state)
                                        game_state.player2.selected_card_index = -1
                                        card_info[0] = "None"
                                if mouse_x > game_state.game_screen.display_width/2+game_state.game_screen.block_size*2:
                                    card_info = list(game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_state.game_screen))
                                if card_info and card_info[0] != "None" and isinstance(card_info[1], int):
                                    game_state.player2.selecte_card_from_hand(card_info[1])
                                    if game_state.player2.selected_card_index == -1:
                                        card_info[0] = "None"
                    case 3:
                        match controller:
                            case "player1":
                                game_state.player1.selected_card_index = -1
                                card_info[0] = "None"
                            case "player2":
                                game_state.player2.selected_card_index = -1
                                card_info[0] = "None"

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_f:
                        hint_box.turn_on = not hint_box.turn_on
                    case pygame.K_e:
                        card_info = ["None", 0]
                        game_state.turn_number += 1
                        match controller:
                            case "player1":
                                controller = "player2"
                                game_state.player1.turn_end(game_state)
                                game_state.player2.turn_start(game_state)
                            case "player2":
                                controller = "player1"
                                game_state.player2.turn_end(game_state)
                                game_state.player1.turn_start(game_state)
                        game_state.game_statistics.add_score_record(game_state.score)
                        if game_state.score <= -10:
                            winner = "player1"
                            running = False
                        elif game_state.score >= 10:
                            running = False
                            winner = "player2"
                    case pygame.K_a:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    game_state.player1.attack(mouse_board_x, mouse_board_y, game_state)
                                case "player2":
                                    game_state.player2.attack(mouse_board_x, mouse_board_y, game_state)
                    case pygame.K_p:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    game_state.player1.spawn_cude(mouse_board_x, mouse_board_y, game_state)
                                case "player2":
                                    game_state.player2.spawn_cude(mouse_board_x, mouse_board_y, game_state)
                    case pygame.K_h:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    game_state.player1.heal_card(mouse_board_x, mouse_board_y, game_state)
                                case "player2":
                                    game_state.player2.heal_card(mouse_board_x, mouse_board_y, game_state)
                    case pygame.K_m:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    game_state.player1.move_card(mouse_board_x, mouse_board_y, game_state)
                                case "player2":
                                    game_state.player2.move_card(mouse_board_x, mouse_board_y, game_state)
                    case pygame.K_1:
                        number_key(1, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_2:
                        number_key(2, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_3:
                        number_key(3, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_4:
                        number_key(4, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_5:
                        number_key(5, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_6:
                        number_key(6, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_7:
                        number_key(7, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_8:
                        number_key(8, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_9:
                        number_key(9, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_0:
                        number_key(10, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, game_state)
                    case pygame.K_SPACE:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    game_state.player1.play_card(mouse_board_x, mouse_board_y, -1, game_state)
                                case "player2":
                                    game_state.player2.play_card(mouse_board_x, mouse_board_y, -1, game_state)
                        
            if event.type == pygame.QUIT:
                return "quit"
           
        
        score_display.display(controller, game_state)
        display_controller(controller, game_state)
        
        for board in game_state.board_dict.values():
            board.update(game_state.game_screen, game_state.board_config)
        
        match controller:
            case "player1":
                game_state.player1.update(game_state, True)
                game_state.player2.update(game_state, False)
            case "player2":
                game_state.player2.update(game_state, True)
                game_state.player1.update(game_state, False)
                
        game_state.neutral.update(game_state)
        
        if game_state.player1.time_out:
            winner = "player2"
            running = False
        if game_state.player2.time_out:
            winner = "player1"
            running = False
                
        if mouse_x < game_state.game_screen.display_width/2-game_state.game_screen.block_size*2 or mouse_x > game_state.game_screen.display_width/2+game_state.game_screen.block_size*2:
            if mouse_x < game_state.game_screen.display_width/2:
                hint_box.update(mouse_x, mouse_y, game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_state.game_screen)[0], game_state.game_screen)
            elif mouse_x > game_state.game_screen.display_width/2:
                hint_box.update(mouse_x, mouse_y, game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_state.game_screen)[0], game_state.game_screen)
        
        if mouse_board_x is not None and mouse_board_y is not None:
            card = get_card_in_battling(game_state.get_all_cards(), mouse_board_x, mouse_board_y)
            if card and card.job_and_color != "None":
                hint_box.update(mouse_x, mouse_y, card, game_state.game_screen)
        
        
        pygame.display.update()
        clock.tick(60)
    return winner
