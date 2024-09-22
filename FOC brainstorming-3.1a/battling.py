import spawn, pygame
from typing import Callable, cast


from exhibits import get_card_name_in_battling, HintBox, Card
from player_info import Player
from board_block import GameScreen, Board, initialize_board
from controls import key_pressed
from UI import ScoreDisplay

def recycle_neutral(on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    for i, card in enumerate(on_board_neutral):
        if card.health <= 0 and card.can_be_killed([], on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            board_dict[str(card.board_x)+"-"+str(card.board_y)].occupy = False
            on_board_neutral.pop(i)

def update_neutral(on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    recycle_neutral(on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
    for card in on_board_neutral:
        card.update(game_screen)

def main(game_screen: GameScreen, player1: Player, player2: Player) -> None:
    running = True
    board_dict = initialize_board(16, game_screen)
    hint_box = HintBox(width=int(game_screen.block_size*2), height=int(game_screen.block_size))
    on_board_neutral: list[Card] = []
    score_display = ScoreDisplay(width=int(game_screen.block_size*0.15), height=int(game_screen.block_size*0.15))
    player1.initialize(game_screen)
    player2.initialize(game_screen)
        
    controller = "player1"
    while running:
        on_board_cards = on_board_neutral + player1.on_board + player2.on_board
        game_screen.update()
        
        for board in board_dict.values():
            board.update(game_screen)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_screen.display_width/2-game_screen.block_size*2))/game_screen.block_size) if mouse_x > game_screen.display_width/2-game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_screen.display_height/2-game_screen.block_size*1.65))/game_screen.block_size) if mouse_y > game_screen.display_height/2-game_screen.block_size*1.65 else None
        
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_f:
                        hint_box.turn_on = not hint_box.turn_on
                    case pygame.K_e:
                        match controller:
                            case "player1":
                                controller = "player2"
                                player1.turn_end(game_screen)
                                player2.turn_start(game_screen)
                            case "player2":
                                controller = "player1"
                                player2.turn_end(game_screen)
                                player1.turn_start(game_screen)
                    case pygame.K_a:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.attack(mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board ,player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.attack(mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board ,player2.on_board, board_dict, game_screen)
                    case pygame.K_p:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.spawn_cude(mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.spawn_cude(mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
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
                                    player1.move_card(mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board ,player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.move_card(mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board ,player2.on_board, board_dict, game_screen)
                    case pygame.K_1:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 0, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 0, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_2:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 1, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 1, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_3:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 2, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 2, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_4:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 3, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 3, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_5:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 4, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 4, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_6:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 5, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 5, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_7:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 6, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 6, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_8:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 7, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 7, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_9:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 8, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 8, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_0:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, 9, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, 9, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                    case pygame.K_SPACE:
                        if mouse_board_x is not None and mouse_board_y is not None:
                            match controller:
                                case "player1":
                                    player1.play_card(mouse_board_x, mouse_board_y, -1, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                                case "player2":
                                    player2.play_card(mouse_board_x, mouse_board_y, -1, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                        
            if event.type == pygame.QUIT:
                running = False
        score_display.display_blocks(controller, game_screen.score, on_board_cards, game_screen)
        match controller:
            case "player1":
                player1.update(on_board_neutral, player1.on_board ,player2.on_board, board_dict, True, game_screen)
                player2.update(on_board_neutral, player1.on_board ,player2.on_board, board_dict, False, game_screen)
            case "player2":
                player2.update(on_board_neutral, player1.on_board ,player2.on_board, board_dict, True, game_screen)
                player1.update(on_board_neutral, player1.on_board ,player2.on_board, board_dict, False, game_screen)
        update_neutral(on_board_neutral, player1.on_board ,player2.on_board, board_dict, game_screen)
        
        
                
        if mouse_board_x is not None and mouse_board_y is not None:
            hint_box.update(mouse_x, mouse_y, get_card_name_in_battling(on_board_cards, mouse_board_x, mouse_board_y), game_screen)
        
        pygame.display.update()
        game_screen.clock.tick(60)
