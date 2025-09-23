import pygame


from exhibits import HintBox, Card, get_card_in_battling, draw_text, WHITE
from player import Player
from board_block import GameScreen, Board, initialize_board
from controls import key_pressed
from attack_detection import attack_area_display
from UI import ScoreDisplay

def number_key(number: int, mouse_x: int, mouse_y: int, mouse_board_x: int | None, mouse_board_y: int | None, controller: str, player1: Player, player2: Player, on_board_neutral: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    if mouse_board_x is not None and mouse_board_y is not None:
        match controller:
            case "player1":
                player1.play_card(mouse_board_x, mouse_board_y, number-1, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
            case "player2":
                player2.play_card(mouse_board_x, mouse_board_y, number-1, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
    elif mouse_x < game_screen.display_width/2-game_screen.block_size*2 or mouse_x > game_screen.display_width/2+game_screen.block_size*2:
        if mouse_x < game_screen.display_width/2 and controller == "player1":
            name, i = player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)
            if number-1 != i: return
            if name != "None":
                if player1.hand[i].endswith(" (+)"):
                    player1.hand[i] = player1.hand[i].replace(" (+)", "")
                else:
                    player1.hand[i] += " (+)"
        elif mouse_x > game_screen.display_width/2 and controller == "player2":
            name, i = player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)
            if number-1 != i: return
            if name != "None":
                if player2.hand[i].endswith(" (+)"):
                    player2.hand[i] = player2.hand[i].replace(" (+)", "")
                else:
                    player2.hand[i] += " (+)"


def recycle_neutral(player1_hand: list[str], player2_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    for i, card in enumerate(on_board_neutral):
        if card.health <= 0 and card.can_be_killed(player1_hand, player2_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            card.die(player1_hand, player2_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            board_dict[str(card.board_x)+"-"+str(card.board_y)].occupy = False
            on_board_neutral.pop(i)

def update_neutral(player1_hand: list[str], player2_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    recycle_neutral(player1_hand, player2_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
    for card in on_board_neutral:
        card.update(player1_hand, player2_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)

def display_controller(controller: str, game_screen: GameScreen) -> None:
    draw_text(f"Ture: {controller}", game_screen.big_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*0.6, game_screen.display_height/2-game_screen.block_size*2.1, game_screen.surface)
    
    
def main(game_screen: GameScreen, player1: Player, player2: Player) -> str:
    running: bool = True
    board_dict = initialize_board(16, game_screen)
    hint_box = HintBox(width=int(game_screen.block_size*2), height=int(game_screen.block_size))
    on_board_neutral: list[Card] = []
    score_display = ScoreDisplay(width=int(game_screen.block_size*0.15), height=int(game_screen.block_size*0.15))
    player1.initialize(game_screen)
    player2.initialize(game_screen)
    controller: str = "player1"

    card_info = ["None", 0]

    if game_screen.log is not None: game_screen.log.write("player1 start\n")
    winner: str = "None"
    while running:
        on_board_cards = on_board_neutral + player1.on_board + player2.on_board
        game_screen.update()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_screen.display_width/2-game_screen.block_size*2))/game_screen.block_size) if mouse_x > game_screen.display_width/2-game_screen.block_size*2 and mouse_x < game_screen.display_width/2+game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_screen.display_height/2-game_screen.block_size*1.65))/game_screen.block_size) if mouse_y > game_screen.display_height/2-game_screen.block_size*1.65 and mouse_y < game_screen.display_height/2+game_screen.block_size*2.35 else None
        
        
        if mouse_board_x is not None and mouse_board_y is not None:
            attack_area_display(controller, mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
       
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        match controller:
                            case "player1":
                                if player1.selected_card_index != -1:
                                    player1.play_card(mouse_board_x, mouse_board_y, player1.selected_card_index, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                    player1.selected_card_index = -1
                                    card_info = ()
                                if mouse_x < game_screen.display_width/2-game_screen.block_size*2:
                                    card_info = player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)
                                if card_info and card_info[0] != "None":
                                    player1.selecte_card_from_hand(card_info[1])
                                    if player1.selected_card_index == -1:
                                        card_info[0] = "None"
                            case "player2":
                                if player2.selected_card_index != -1:
                                    player2.play_card(mouse_board_x, mouse_board_y, player2.selected_card_index, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                    player2.selected_card_index = -1
                                    card_info = ()
                                if mouse_x > game_screen.display_width/2+game_screen.block_size*2:
                                    card_info = player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)
                                if card_info and card_info[0] != "None":
                                    player2.selecte_card_from_hand(card_info[1])
                                    if player2.selected_card_index == -1:
                                        card_info[0] = "None"
                    case 3:
                        match controller:
                            case "player1":
                                player1.selected_card_index = -1
                            case "player2":
                                player2.selected_card_index = -1
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_f:
                        hint_box.turn_on = not hint_box.turn_on
                    case pygame.K_e:
                        card_info = ["None", 0]
                        match controller:
                            case "player1":
                                controller = "player2"
                                player1.turn_end(game_screen)
                                player2.turn_start(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                            case "player2":
                                controller = "player1"
                                player2.turn_end(game_screen)
                                player1.turn_start(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                        game_screen.data.score_records.append(game_screen.score)
                        if game_screen.score <= -10:
                            winner = "player1"
                            running = False
                        elif game_screen.score >= 10:
                            running = False
                            winner = "player2"
                    case pygame.K_a:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.attack(mouse_board_x, mouse_board_y, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.attack(mouse_board_x, mouse_board_y, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_p:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.spawn_cude(mouse_board_x, mouse_board_y, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.spawn_cude(mouse_board_x, mouse_board_y, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_h:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.heal_card(mouse_board_x, mouse_board_y, game_screen)
                                case "player2":
                                    player2.heal_card(mouse_board_x, mouse_board_y, game_screen)
                    case pygame.K_m:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.move_card(mouse_board_x, mouse_board_y, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.move_card(mouse_board_x, mouse_board_y, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_1:
                        number_key(1, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_2:
                        number_key(2, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_3:
                        number_key(3, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_4:
                        number_key(4, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_5:
                        number_key(5, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_6:
                        number_key(6, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_7:
                        number_key(7, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_8:
                        number_key(8, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_9:
                        number_key(9, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_0:
                        number_key(10, mouse_x, mouse_y, mouse_board_x, mouse_board_y, controller, player1, player2, on_board_neutral, board_dict, game_screen)
                    case pygame.K_SPACE:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, -1, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, -1, player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                        
            if event.type == pygame.QUIT:
                return "quit"
           
        
        score_display.display(controller, game_screen.score, on_board_cards, game_screen)
        display_controller(controller, game_screen)
        
        for board in board_dict.values():
            board.update(game_screen)
        
        match controller:
            case "player1":
                player1.update(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, True, game_screen)
                player2.update(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, False, game_screen)
            case "player2":
                player2.update(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, True, game_screen)
                player1.update(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, False, game_screen)
                
        update_neutral(player1.hand, player2.hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
        
        if player1.time_out:
            winner = "player2"
            running = False
        if player2.time_out:
            winner = "player1"
            running = False
                
        if mouse_x < game_screen.display_width/2-game_screen.block_size*2 or mouse_x > game_screen.display_width/2+game_screen.block_size*2:
            if mouse_x < game_screen.display_width/2:
                hint_box.update(mouse_x, mouse_y, player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)[0], game_screen)
            elif mouse_x > game_screen.display_width/2:
                hint_box.update(mouse_x, mouse_y, player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)[0], game_screen)
        
        if mouse_board_x is not None and mouse_board_y is not None:
            hint_box.update(mouse_x, mouse_y, get_card_in_battling(on_board_cards, mouse_board_x, mouse_board_y), game_screen)
        
        
        pygame.display.update()
        game_screen.clock.tick(60)
    return winner
