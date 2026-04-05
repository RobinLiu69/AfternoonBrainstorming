from typing import Optional

import pygame

from core.draft_state import DraftState
from core.draft_dispatcher import DraftDispatcher
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.game_screen import GameScreen
from core.network_layer import LANClient, LANServer
from screens.draft.draft_action import collect_draft_actions
from screens.draft.exhibit_registry import ExhibitRegistry
from rendering.draft_renderer import DraftRenderer


def _to_board_x(mouse_x: int, gs: GameScreen) -> Optional[int]:
    left  = gs.display_width / 2 - gs.block_size * 2
    right = gs.display_width / 2 + gs.block_size * 2
    if left < mouse_x < right:
        return int((mouse_x - left) / gs.block_size)
    return None

def _to_board_y(mouse_y: int, gs: GameScreen) -> Optional[int]:
    top    = gs.display_height / 2 - gs.block_size * 1.65
    bottom = gs.display_height / 2 + gs.block_size * 1.35
    if top < mouse_y < bottom:
        return int((mouse_y - top) / gs.block_size)
    return None

def _turn_page(page: int, direction: int, total: int) -> int:
    return (page + direction) % total


def main(game_screen: GameScreen) -> Optional[DraftState]:
    registry = ExhibitRegistry()
    draft_state = DraftState()

    match "server":
        case "server":
            server = LANServer()
            dispatcher = DraftDispatcher(draft_state, mode="lan_server")
            dispatcher.attach_server(server)
            server.start()
        case _:
            client = LANClient("0.0.0.0")
            dispatcher = DraftDispatcher(draft_state, mode="lan_client")
            dispatcher.attach_client(client)
            client.on_state_update = draft_state._update_handler   # optional push handler
            client.connect()
        

    renderer = DraftRenderer(game_screen, registry)

    draft_state.board_config = BoardConfig(4, 3)
    draft_state.board_dict = initialize_board(game_screen, draft_state.board_config)

    page = 0
    hint_on = False
    confirm_count = 0
    clock = pygame.time.Clock()

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = _to_board_x(mouse_x, game_screen)
        mouse_board_y = _to_board_y(mouse_y, game_screen)

        actions = collect_draft_actions(draft_state.current_editor(), page, registry, mouse_board_x, mouse_board_y)

        for action in actions:

            if action.action_type == "quit":
                return None

            if action.action_type == "toggle_hint":
                hint_on = not hint_on
                continue

            if action.action_type == "page_next":
                page = _turn_page(page, 1, registry.page_count())
                continue

            if action.action_type == "page_prev":
                page = _turn_page(page, -1, registry.page_count())
                continue

            if action.action_type == "confirm_start":
                # if draft_state.can_advance():
                #     confirm_count += 1
                #     if confirm_count >= 2:
                draft_state.advance_phase()
                return draft_state
                # continue

            result = dispatcher.dispatch(action, draft_state)

            if result.ready_to_start:
                return draft_state

            if result.phase_advanced:
                page = 0

        renderer.render_frame(page, mouse_board_x, mouse_board_y, draft_state)

        pygame.display.update()
        clock.tick(60)