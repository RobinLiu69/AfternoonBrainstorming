import pygame

from core.game_state import GameState, WHITE
from core.game_screen import GameScreen, draw_text
from core.battling_dispatcher import BattlingdDispatcher
from core.board_config import BoardConfig
from core.board_block import initialize_board
from rendering.game_renderer import GameRenderer
from screens.battling.battling_action import collect_actions


def number_key(number: int, mouse_x: int, mouse_y: int, mouse_board_x: int | None, mouse_board_y: int | None, controller: str, game_state: GameState) -> None:
    if mouse_board_x is not None and mouse_board_y is not None:
        match controller:
            case "player1":
                game_state.player1.play_card(mouse_board_x, mouse_board_y, number-1, game_state)
            case "player2":
                game_state.player2.play_card(mouse_board_x, mouse_board_y, number-1, game_state)
    # elif mouse_x < game_screen.display_width/2-game_screen.block_size*2 or mouse_x > game_screen.display_width/2+game_screen.block_size*2:
    #     if mouse_x < game_screen.display_width/2 and controller == "player1":
    #         name, i = game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)
    #         if number-1 != i: return
    #         if name != "None":
    #             if game_state.player1.hand[i].endswith(" (+)"):
    #                 game_state.player1.hand[i] = game_state.player1.hand[i].replace(" (+)", "")
    #             else:
    #                 game_state.player1.hand[i] += " (+)"
    #     elif mouse_x > game_screen.display_width/2 and controller == "player2":
    #         name, i = game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)
    #         if number-1 != i: return
    #         if name != "None":
    #             if game_state.player2.hand[i].endswith(" (+)"):
    #                 game_state.player2.hand[i] = game_state.player2.hand[i].replace(" (+)", "")
    #             else:
    #                 game_state.player2.hand[i] += " (+)"


def display_controller(controller: str, game_screen: GameScreen) -> None:
    draw_text(f"Ture: {controller}", game_screen.big_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*0.6, game_screen.display_height/2-game_screen.block_size*2.1, game_screen.surface)

def to_board_x(mouse_x: int, game_screen: GameScreen) -> int | None:
    return int((mouse_x-(game_screen.display_width/2-game_screen.block_size*2))/game_screen.block_size) if mouse_x > game_screen.display_width/2-game_screen.block_size*2 and mouse_x < game_screen.display_width/2+game_screen.block_size*2 else None

def to_board_y(mouse_y: int, game_screen: GameScreen) -> int | None:
    return int((mouse_y-(game_screen.display_height/2-game_screen.block_size*1.65))/game_screen.block_size) if mouse_y > game_screen.display_height/2-game_screen.block_size*1.65 and mouse_y < game_screen.display_height/2+game_screen.block_size*2.35 else None

def main(game_state: GameState, game_screen: GameScreen) -> str:
    running: bool = True

    game_state.board_config = BoardConfig()

    game_renderer = GameRenderer(game_screen)

    game_state.board_dict = initialize_board(game_screen, game_state.board_config)
    
    game_state.player1.initialize(game_state, game_screen)
    game_state.player2.initialize(game_state, game_screen)
    controller: str = "player1"

    card_info = ["None", 0]

    dispatcher = BattlingdDispatcher(mode="local")

    game_state.game_logger.log_turn_start("player1", game_state.turn_number)
    
    winner: str = "None"
    clock = pygame.time.Clock()
    while running:

        mouse_x, mouse_y = pygame.mouse.get_pos()

        board_x = to_board_x(mouse_x, game_screen)
        board_y = to_board_y(mouse_y, game_screen)

        actions = collect_actions(controller, card_info, game_state, game_screen)

        for action in actions:
            result = dispatcher.dispatch(action, game_state)
            if result.end_turn:
                controller = "player2" if controller == "player1" else "player1"
            if result.quit:
                if result.message:
                    winner = result.message
                running = False
                print("quit")


        game_state.get_player(controller).logic_update(game_state, True)
        game_state.get_opponent(controller).logic_update(game_state, False)
        
        game_renderer.render_frame(controller, mouse_x, mouse_y, board_x, board_y, game_state)
        game_state.update()

        if game_state.player1.time_out:
            winner = "player2"
            running = False
        if game_state.player2.time_out:
            winner = "player1"
            running = False
        
        # if mouse_x < game_screen.display_width/2-game_screen.block_size*2 or mouse_x > game_screen.display_width/2+game_screen.block_size*2:
        #     if mouse_x < game_screen.display_width/2:
        #         hint_box.update(mouse_x, mouse_y, game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)[0], game_screen)
        #     elif mouse_x > game_screen.display_width/2:
        #         hint_box.update(mouse_x, mouse_y, game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen)[0], game_screen)
        
        # if mouse_board_x is not None and mouse_board_y is not None:
        #     card = get_card_in_battling(game_state.get_all_cards(), mouse_board_x, mouse_board_y)
        #     if card and card.job_and_color != "None":
        #         hint_box.update(mouse_x, mouse_y, card, game_screen)
        
        pygame.display.update()
        clock.tick(60)
    return winner
