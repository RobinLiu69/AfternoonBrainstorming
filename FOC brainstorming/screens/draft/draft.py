from typing import Optional

import pygame

from core.draft_state import DraftState
from core.draft_dispatcher import DraftDispatcher
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.game_screen import GameScreen
from core.network_layer import LANClient, LANServer
from core.scene_exit import DraftExitReason
from screens.draft.draft_action import collect_draft_actions
from screens.draft.exhibit_registry import ExhibitRegistry
from rendering.draft_renderer import DraftRenderer


def _to_board_x(mouse_x: int, game_screen: GameScreen) -> Optional[int]:
    left = game_screen.display_width / 2 - game_screen.block_size * 2
    right = game_screen.display_width / 2 + game_screen.block_size * 2
    if left < mouse_x < right:
        return int((mouse_x - left) / game_screen.block_size)
    return None


def _to_board_y(mouse_y: int, game_screen: GameScreen) -> Optional[int]:
    top = game_screen.display_height / 2 - game_screen.block_size * 1.65
    bottom = game_screen.display_height / 2 + game_screen.block_size * 1.35
    if top < mouse_y < bottom:
        return int((mouse_y - top) / game_screen.block_size)
    return None


def _turn_page(page: int, direction: int, total: int) -> int:
    return (page + direction) % total


def main(game_screen: GameScreen, mode: str = "local",
         server: Optional[LANServer] = None, client: Optional[LANClient] = None) -> DraftExitReason:
    registry = ExhibitRegistry()
    draft_state = DraftState()
    draft_state.board_config = BoardConfig(4, 3)
    draft_state.board_dict = initialize_board(game_screen, draft_state.board_config)

    dispatcher = DraftDispatcher(draft_state, mode=mode)

    match mode:
        case "lan_server":
            assert server is not None, "lan_server mode requires a LANServer"
            dispatcher.attach_server(server)
            if not server.is_running:
                server.start()
            draft_state.local_player = "player1"

        case "lan_client":
            assert client is not None, "lan_client mode requires a LANClient"
            dispatcher.attach_client(client)
            if not client.is_connected:
                role, initial_state = client.connect()
            else:
                role, initial_state = client.role, client.initial_state
            
            if initial_state:
                draft_state.apply_dict(initial_state)
            draft_state.local_player = role or "player2"

        case _:
            draft_state.local_player = "player1"

    renderer = DraftRenderer(game_screen, registry)

    page = 0
    hint_on = False
    last_phase = draft_state.phase
    clock = pygame.time.Clock()

    while True:
        if mode == "local":
            draft_state.local_player = draft_state.current_editor()

        if mode == "lan_client" and client is not None:
            handoff = client.consume_pending_scene()
            if handoff is not None:
                _scene, next_state = handoff
                return DraftExitReason(
                    kind="scene_handoff",
                    next_scene_state=next_state,
                )

        if draft_state.phase != last_phase:
            page = 0
            last_phase = draft_state.phase
        
        if draft_state.phase == "done" and mode != "lan_client":
            return DraftExitReason(kind="finished", draft_state=draft_state)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = _to_board_x(mouse_x, game_screen)
        mouse_board_y = _to_board_y(mouse_y, game_screen)

        actions = collect_draft_actions(
            draft_state.local_player, page, registry,
            mouse_board_x, mouse_board_y,
        )

        for action in actions:
            if action.action_type == "quit":
                return DraftExitReason(kind="quit")

            if action.action_type == "toggle_hint":
                hint_on = not hint_on
                continue

            if action.action_type == "page_next":
                page = _turn_page(page, 1, registry.page_count())
                continue
            
            if action.action_type == "page_prev":
                page = _turn_page(page, -1, registry.page_count())
                continue

            dispatcher.dispatch(action, draft_state)

        renderer.render_frame(page, mouse_board_x, mouse_board_y, draft_state, hint_on)
        pygame.display.update()
        clock.tick(60)