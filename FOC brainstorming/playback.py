import pygame


from exhibits import HintBox, Card, get_card_name_in_battling, draw_text, WHITE
from player import Player
from board_block import GameScreen, Board, initialize_board
from controls import key_pressed
from attack_detection import attack_area_display
from UI import ScoreDisplay

def number_key(number: int, mouse_x: int, mouse_y: int, mouse_board_x: int | None, mouse_board_y: int | None, controller: str, player1: Player, player2: Player, on_board_neutral: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    if mouse_board_x is not None and mouse_board_y is not None:
        match controller:
            case "player1":
                player1.play_card(mouse_board_x, mouse_board_y, number-1, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
            case "player2":
                player2.play_card(mouse_board_x, mouse_board_y, number-1, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
    elif mouse_x < game_screen.display_width/2-game_screen.block_size*2 or mouse_x > game_screen.display_width/2+game_screen.block_size*2:
        if mouse_x < game_screen.display_width/2 and controller == "player1":
            name, i = player1.hand_card_hints(mouse_x, mouse_y, game_screen)
            if number-1 != i: return
            if name != "None":
                if player1.in_hand[i].endswith(" (+)"):
                    player1.in_hand[i] = player1.in_hand[i].replace(" (+)", "")
                else:
                    player1.in_hand[i] += " (+)"
        elif mouse_x > game_screen.display_width/2 and controller == "player2":
            name, i = player2.hand_card_hints(mouse_x, mouse_y, game_screen)
            if number-1 != i: return
            if name != "None":
                if player2.in_hand[i].endswith(" (+)"):
                    player2.in_hand[i] = player2.in_hand[i].replace(" (+)", "")
                else:
                    player2.in_hand[i] += " (+)"


def recycle_neutral(player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    for i, card in enumerate(on_board_neutral):
        if card.health <= 0 and card.can_be_killed(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            card.die(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            board_dict[str(card.board_x)+"-"+str(card.board_y)].occupy = False
            on_board_neutral.pop(i)

def update_neutral(player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    recycle_neutral(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
    for card in on_board_neutral:
        card.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)

def display_controller(controller: str, game_screen: GameScreen) -> None:
    draw_text(f"Ture: {controller}", game_screen.big_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*0.6, game_screen.display_height/2-game_screen.block_size*2.1, game_screen.surface)

def init_playback(game_screen: GameScreen):
    if game_screen.playback is not None:
        while True:
            line = game_screen.playback.readline()
            if line.split()[1] == "start":
                break

def next_move(controller: Player, player1: Player, player2: Player, on_board_neutral: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> Player:
    line = next_action(game_screen).split()
    action = line[1]
    print(line)
    match action:
        case "ended":
            match controller.name:
                case "player1":
                    controller.turn_end(game_screen)
                    next_action(game_screen)
                    controller = player2
                    controller.turn_start(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                case "player2":
                    controller.turn_end(game_screen)
                    controller = player1
                    next_action(game_screen)
                    controller.turn_start(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
            game_screen.data.score_records.append(game_screen.score)
        case "played":
            index = int(line[2].split("-")[0])
            board_x, board_y = map(int, line[-1].split("-"))
            controller.play_card(board_x, board_y, index, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
        case "used":
            match line[-2]:
                case "playing":
                    index = int(line[-1].split("-")[0])
                    print(index)
                    controller.play_card(0, 0, index, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                case "on":
                    match line[2]:
                        case "cube":
                            board_x, board_y = map(int, line[-1].split("-"))
                            controller.spawn_cude(board_x, board_y, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
                        case "heal":
                            board_x, board_y = map(int, line[-1].split("-"))
                            controller.heal_card(board_x, board_y, game_screen)
                        case "move":
                            board_x, board_y = map(int, line[-1].split("-"))
                            controller.move_card(board_x, board_y, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
        case "attacked":
            board_x, board_y = map(int, line[-1].split(".")[-1].split("-"))
            controller.attack(board_x, board_y, player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
    return controller

def next_action(game_screen: GameScreen) -> str:
    if game_screen.playback is not None:
        while True:
            line = game_screen.playback.readline()
            if line.split()[1] != "recycled" and line.split()[1] != "drew":
                break
        return line
    return "End"
    
def main(game_screen: GameScreen, player1: Player, player2: Player) -> str:
    running: bool = True
    board_dict = initialize_board(16, game_screen)
    hint_box = HintBox(width=int(game_screen.block_size*2), height=int(game_screen.block_size))
    on_board_neutral: list[Card] = []
    score_display = ScoreDisplay(width=int(game_screen.block_size*0.15), height=int(game_screen.block_size*0.15))
    player1.initialize(game_screen)
    player2.initialize(game_screen)
    controller: Player = player1
    init_playback(game_screen)
    winner: str = "None"
    delay = 0
    while running:
        on_board_cards = on_board_neutral + player1.on_board + player2.on_board
        game_screen.update()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_screen.display_width/2-game_screen.block_size*2))/game_screen.block_size) if mouse_x > game_screen.display_width/2-game_screen.block_size*2 and mouse_x < game_screen.display_width/2+game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_screen.display_height/2-game_screen.block_size*1.65))/game_screen.block_size) if mouse_y > game_screen.display_height/2-game_screen.block_size*1.65 and mouse_y < game_screen.display_height/2+game_screen.block_size*2.35 else None
        
        
        if mouse_board_x is not None and mouse_board_y is not None:
            attack_area_display(controller.name, mouse_board_x, mouse_board_y, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
       
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and delay == 0:
            controller = next_move(controller, player1, player2, on_board_neutral, board_dict, game_screen)
            delay = 10
        elif delay > 0:
            delay -= 1


        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_f:
                        hint_box.turn_on = not hint_box.turn_on
                    case pygame.K_RIGHT:
                        controller = next_move(controller, player1, player2, on_board_neutral, board_dict, game_screen)
            if event.type == pygame.QUIT:
                running = False
                return "quit"
        
        if game_screen.score <= -10:
            running = False
            winner = "player1"
        elif game_screen.score >= 10:
            running = False
            winner = "player2"
        
        score_display.display(controller.name, game_screen.score, on_board_cards, game_screen)
        display_controller(controller.name, game_screen)
        
        for board in board_dict.values():
            board.update(game_screen)
        
        match controller.name:
            case "player1":
                player1.update(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, True, game_screen)
                player2.update(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, False, game_screen)
            case "player2":
                player2.update(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, True, game_screen)
                player1.update(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, False, game_screen)
                
        update_neutral(player1.in_hand, player2.in_hand, on_board_neutral, player1.on_board, player2.on_board, board_dict, game_screen)
        
                
        if mouse_x < game_screen.display_width/2-game_screen.block_size*2 or mouse_x > game_screen.display_width/2+game_screen.block_size*2:
            if mouse_x < game_screen.display_width/2:
                hint_box.update(mouse_x, mouse_y, player1.hand_card_hints(mouse_x, mouse_y, game_screen)[0], game_screen)
            elif mouse_x > game_screen.display_width/2:
                hint_box.update(mouse_x, mouse_y, player2.hand_card_hints(mouse_x, mouse_y, game_screen)[0], game_screen)
        
        if mouse_board_x is not None and mouse_board_y is not None:
            hint_box.update(mouse_x, mouse_y, get_card_name_in_battling(on_board_cards, mouse_board_x, mouse_board_y), game_screen)
        
        
        pygame.display.update()
        game_screen.clock.tick(60)
    return winner
