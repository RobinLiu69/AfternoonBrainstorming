# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

from typing import Optional

import pygame

from core.network_layer import LANServer, LANClient
from core.setting import WHITE
from core.game_state import GameState
from core.game_screen import GameScreen, draw_text, to_board_x, to_board_y
from core.battling_dispatcher import BattlingDispatcher
from core.game_statistics import StatType
from core.board_config import BoardConfig
from core.board_block import initialize_board
from rendering.game_renderer import GameRenderer
from screens.battling.battling_action import collect_actions


def number_key(number: int, mouse_x: int, mouse_y: int,
               mouse_board_x: int | None, mouse_board_y: int | None,
               controller: str, game_state: GameState) -> None:
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

def _sweep_dead_cards_visually(game_state: GameState, game_renderer: GameRenderer) -> None:
    for container in (game_state.player1.on_board, game_state.player2.on_board, game_state.neutral.on_board):
        survivors = []
        for card in container:
            if card.health <= 0 and card.can_be_killed(game_state):
                game_renderer.card_renderer.release(card.instance_id)
                if (card.board_x, card.board_y) in game_state.board_dict:
                    game_state.board_dict[card.board_x, card.board_y].occupy = False
            else:
                survivors.append(card)
        container[:] = survivors


def display_controller(controller: str, game_screen: GameScreen) -> None:
    draw_text(f"Ture: {controller}", game_screen.big_text_font,
              WHITE, game_screen.display_width/2 - game_screen.block_size*0.6,
              game_screen.display_height/2 - game_screen.block_size*2.1, game_screen.surface)


def main(game_state: GameState, game_screen: GameScreen, mode: str = "local",
         server: Optional[LANServer] = None, client: Optional[LANClient] = None,
         initial_state_dict: Optional[dict] = None) -> str:
    from cards.base import reset_instance_counter
    reset_instance_counter()

    running: bool = True

    game_state.board_config = BoardConfig()
    game_renderer = GameRenderer(game_screen)
    game_state.board_dict = initialize_board(game_screen, game_state.board_config)

    dispatcher = BattlingDispatcher(game_state=game_state, mode=mode)
    dispatcher.attach_renderer(game_renderer)

    is_client = (mode == "lan_client")
    is_server = (mode == "lan_server")

    if is_server:
        assert server is not None, "lan_server mode requires a LANServer"
        dispatcher.attach_server(server)


    if is_client:
        assert client is not None, "lan_client mode requires a LANClient"
        dispatcher.attach_client(client)
        if initial_state_dict is not None:
            game_state.apply_dict(initial_state_dict, game_renderer)


    if not is_client:
        game_state.player1.initialize(game_state, game_screen)
        game_state.player2.initialize(game_state, game_screen)

    if is_server and server:
        server.broadcast_scene("battling", game_state.to_dict())
 
    game_state.player1.initialize_display(game_state, game_screen)
    game_state.player2.initialize_display(game_state, game_screen)

    controller: str = "player1"
    hint_on = False
    card_info = ["None", 0]
 
    game_state.game_logger.log_turn_start("player1", game_state.turn_number)
 
    winner: str = "None"
    clock = pygame.time.Clock()

    if is_client and client:
        print(f"[Battling] entering loop as client.role={client.role!r}")

    while running:
        dt = clock.tick(60) / 1000.0

        if is_client and client:
            game_over = client.consume_pending_game_over()
            if game_over is not None:
                winner_name, stats = game_over
                charts = stats.get("export_for_charts", {})
                for stat_name, kv in charts.items():
                    for stype in StatType:
                        if stype.value == stat_name:
                            for k, v in kv.items():
                                game_state.game_statistics.increment(stype, k, v)
                            break
                game_state.game_statistics.score_history = stats.get("score_history", [])
                winner = winner_name
                running = False
                break

        if is_client and client:
            local_controller = client.role
        elif is_server:
            local_controller = "player1"
        else:
            local_controller = controller

        mouse_x, mouse_y = pygame.mouse.get_pos()
        board_x = to_board_x(mouse_x, game_screen)
        board_y = to_board_y(mouse_y, game_screen)

        actions = collect_actions(local_controller, card_info, game_state, game_screen)

        for action in actions:
            result = dispatcher.dispatch(action, game_state)

            if action.action_type == "toggle_hint":
                hint_on = not hint_on
                continue

            if mode == "local":
                if result.end_turn:
                    controller = "player2" if controller == "player1" else "player1"
                if result.quit:
                    if result.message:
                        winner = result.message
                    running = False
            

        if is_server and dispatcher.pending_winner is not None:
            winner = dispatcher.pending_winner
            running = False

        if not is_client:
            prev_snapshot = None
            if is_server:
                prev_snapshot = (
                    len(game_state.player1.hand),
                    len(game_state.player2.hand),
                    len(game_state.player1.draw_pile),
                    len(game_state.player2.draw_pile),
                    dict(game_state.card_to_draw),
                    dict(game_state.players_token),
                )

            game_state.get_player(controller).logic_update(game_state, game_renderer, True)
            game_state.get_opponent(controller).logic_update(game_state, game_renderer, False)
            game_state.neutral.update(game_state, game_renderer)
            game_state.update()

            if is_server and prev_snapshot is not None:
                new_snapshot = (
                    len(game_state.player1.hand),
                    len(game_state.player2.hand),
                    len(game_state.player1.draw_pile),
                    len(game_state.player2.draw_pile),
                    dict(game_state.card_to_draw),
                    dict(game_state.players_token),
                )
                if new_snapshot != prev_snapshot:
                    dispatcher._broadcast_state(game_state)


            if game_state.player1.time_out:
                winner = "player2"
                running = False
            if game_state.player2.time_out:
                winner = "player1"
                running = False

            if not running and winner not in ("None", ""):
                if is_server:
                    dispatcher._broadcast_state(game_state)
                    dispatcher._broadcast_game_over(winner, game_state)
        
        if is_client:
            _sweep_dead_cards_visually(game_state, game_renderer)
        
            if controller == local_controller:
                game_state.get_player(local_controller)._update_timer_logic(game_state.timer_mode)
            else:
                game_state.get_opponent(local_controller)._update_timer_logic(game_state.timer_mode)

        if not (mode == "local"):
            controller = "player1" if (game_state.turn_number % 2 == 0) else "player2"


        game_renderer.render_frame(local_controller, controller, mouse_x, mouse_y, board_x, board_y, game_state, hint_on, dt)
        pygame.display.update()
    
    game_state.game_logger.close()
    return winner