from card import Card, GameScreen, Board, Generator, random, pygame, cast, WHITE, RED, BOARD_SIZE

def attack_areas(board_x: int, board_y: int,  attack_types: str, other_cards: tuple[Card], board_dict: dict[str, Board]) -> Generator[tuple[int, int], None, None]:
    board_position = board_x + (board_y * 4)
    board_list = tuple((board_dict.values()))
    for attack_type in attack_types.split(" "):
        match attack_type:
            case "small_cross":
                for board in board_list:
                    if ((board.board_x == board_x-1 and board.board_y == board_y) or (board.board_x == board_x+1 and board.board_y == board_y) or (board.board_x == board_x and board.board_y == board_y-1) or (board.board_x == board_x and board.board_y == board_y+1)):
                        yield board.board_x, board.board_y
            case "large_cross":
                for board in board_list:
                    if ((board.board_x == board_x or board.board_y == board_y) and board.board_position != board_position):
                        yield board.board_x, board.board_y
            case "small_x":
                for board in board_list:
                    if ((board.board_x == board_x+1 and board.board_y == board_y+1) or (board.board_x == board_x-1 and board.board_y == board_y+1) or (board.board_x == board_x-1 and board.board_y == board_y-1) or (board.board_x == board_x+1 and board.board_y == board_y-1)):
                        yield board.board_x, board.board_y
            case "large_x":
                pass
            case"nearest":
                for card in other_cards:
                    if card.been_targeted:
                        yield card.board_x, card.board_y
                    
                nearby_cards: list["Card"] = sorted(other_cards, key=lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y))
                if nearby_cards:
                    temp_card = nearby_cards[0]
                    nearet_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y) == abs(temp_card.board_x-board_x)+abs(temp_card.board_y-board_y), nearby_cards))
                    for card in nearet_cards: yield card.board_x, card.board_y
                
            case "farthest":
                for card in other_cards:
                    if card.been_targeted:
                        yield card.board_x, card.board_y
                    
                faraway_cards: list["Card"] = sorted(other_cards, key=lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y), reverse=True)
                if faraway_cards:
                    temp_card = faraway_cards[0]
                    farthest_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y) == abs(temp_card.board_x-board_x)+abs(temp_card.board_y-board_y), faraway_cards))
                    for card in farthest_cards: yield card.board_x, card.board_y
    return None

def attack_area_display(controller: str, board_x: int, board_y: int, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen) -> None:
    target_cards = tuple(filter(lambda card: card.board_x == board_x and card.board_y == board_y and card.job_and_color != "SHADOW", on_board_neutral+player1_on_board+player2_on_board))
    if target_cards:
        target_card: Card = target_cards[0]
        other_cards: tuple[Card] = cast(tuple[Card], tuple(filter(lambda card: card.owner != target_card.owner, on_board_neutral+player1_on_board+player2_on_board)))
        match target_card.job_and_color:
            case "ADCF":
                if target_card.attack_types is not None:
                    if target_card.owner == controller:
                        color = (200, 200, 200)
                    else:
                        color = (200, 0, 0)
                    card_attack_blocks = attack_areas(target_card.board_x, target_card.board_y, target_card.attack_types, other_cards, board_dict)
                    for board_x, board_y in card_attack_blocks:
                        draw_board(color, board_x, board_y, game_screen)
                        
                    card_attack_blocks = attack_areas(BOARD_SIZE[0]-1-target_card.board_x, BOARD_SIZE[1]-1-target_card.board_y, target_card.attack_types, other_cards, board_dict)
                    for board_x, board_y in card_attack_blocks:
                        draw_board(color, board_x, board_y, game_screen)
            case _:
                if target_card.attack_types is not None:
                    if target_card.owner == controller:
                        color = (200, 200, 200)
                    else:
                        color = (200, 0, 0)
                    card_attack_blocks = attack_areas(target_card.board_x, target_card.board_y, target_card.attack_types, other_cards, board_dict)
                    for board_x, board_y in card_attack_blocks:
                        draw_board(color, board_x, board_y, game_screen)

def draw_board(color: tuple[int, int, int], board_x: int, board_y: int, game_screen: GameScreen) -> None:
    image = pygame.surface.Surface((game_screen.block_size, game_screen.block_size))
    image.fill(color)
    image.set_alpha(60)
    rect = (((game_screen.display_width/2)-(game_screen.block_size*2))+(board_x*game_screen.block_size)+(game_screen.block_size*0), (game_screen.display_height/2)-(game_screen.block_size*1.675)+(board_y*game_screen.block_size)+(game_screen.block_size*0), game_screen.block_size, game_screen.block_size)
    game_screen.surface.blit(image, rect)
    