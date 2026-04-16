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

import pygame

from core.game_state import GameState
from core.game_screen import GameScreen, to_board_x, to_board_y
from core.game_action import GameAction
from utils.controls import key_pressed


def collect_actions(controller: str, card_info: list, game_state: GameState, game_screen: GameScreen) -> list[GameAction]:
    actions: list[GameAction] = []
    mouse_x, mouse_y = pygame.mouse.get_pos()

    board_x = to_board_x(mouse_x, game_screen)
    board_y = to_board_y(mouse_y, game_screen)
    
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            match event.button:
                case 1:
                    if game_state.get_player(controller).selected_card_index != -1:
                        if board_x is not None and board_y is not None:
                            actions.append(GameAction(
                                player=controller,
                                action_type="play_card",
                                board_x=board_x,
                                board_y=board_y,
                                hand_index=game_state.get_player(controller).selected_card_index
                            ))
                            game_state.get_player(controller).selected_card_index = -1
                            card_info = []
                    if (mouse_x < game_screen.display_width/2 - game_screen.block_size*2) if controller == "player1" else (mouse_x > game_screen.display_width/2+game_screen.block_size*2):
                        card_info = list(game_state.get_player(controller).get_hand_name_by_mouse_pos(mouse_x, mouse_y, game_screen))
                    if card_info and card_info[0] != "None" and isinstance(card_info[1], int):
                        game_state.get_player(controller).selecte_card_from_hand(card_info[1])
                        if game_state.get_player(controller).selected_card_index == -1:
                            card_info[0] = "None"
                case 3:
                    game_state.get_player(controller).selected_card_index = -1
                    card_info[0] = "None"
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            match key_pressed(keys):
                case pygame.K_a:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="attack",
                            board_x=board_x,
                            board_y=board_y
                        ))
                case pygame.K_h:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="heal",
                            board_x=board_x,
                            board_y=board_y
                        ))
                case pygame.K_p:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="spawn_cube",
                            board_x=board_x,
                            board_y=board_y
                        ))
                case pygame.K_f:
                    actions.append(GameAction(player=controller, action_type="toggle_hint"))
                case pygame.K_v:
                    actions.append(GameAction(player=controller, action_type="toggle_animation"))
                case pygame.K_e:
                    actions.append(GameAction(
                        player=controller,
                        action_type="end_turn"
                    ))
                case pygame.K_m:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="move_to",
                            board_x=board_x,
                            board_y=board_y
                        ))
                case pygame.K_1:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=0
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=0))
                case pygame.K_2:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=1
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=1))
                case pygame.K_3:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=2
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=2))
                case pygame.K_4:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=3
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=3))
                case pygame.K_5:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=4
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=4))
                case pygame.K_6:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=5
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=5))
                case pygame.K_7:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=6
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=6))
                case pygame.K_8:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=7
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=7))
                case pygame.K_9:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=8
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=8))
                case pygame.K_0:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=9
                        ))
                    else:
                        actions.append(GameAction(
                            player=controller, action_type="toggle_upgrade",
                            hand_index=9))
                case pygame.K_SPACE:
                    if board_x is not None and board_y is not None:
                        actions.append(GameAction(
                            player=controller,
                            action_type="play_card",
                            board_x=board_x,
                            board_y=board_y,
                            hand_index=-1
                        ))
                case pygame.K_ESCAPE:
                    actions.append(GameAction(player=controller, action_type="quit"))                    
            if event.type == pygame.QUIT:
                actions.append(GameAction(player=controller, action_type="quit"))
    return actions