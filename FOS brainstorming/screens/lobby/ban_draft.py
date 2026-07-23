# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
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

from shared.setting import WHITE
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.draft_state import TOURNAMENT_BANS
from core.game_screen import GameScreen, draw_text
from core.lobby_state import LobbyState, MAX_BANS_PER_PLAYER, is_bannable_card
from core.lobby_dispatcher import LobbyDispatcher
from core.network_layer import LANServer, LANClient
from cards.factory import CardFactory
from rendering.board_renderer import BoardRenderer
from rendering.card_renderer import CardRenderer
from rendering.sprite_registry import SpriteRegistry
from screens.draft.exhibit_registry import ExhibitRegistry
from screens.lobby.lobby_action import LobbyAction
from screens.widgets import make_back_button

_BAN_IDENTITIES = ("host", "peer")


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


def _cell_origin(game_screen: GameScreen, board_x: int, board_y: int) -> tuple[float, float]:
    x = (game_screen.display_width / 2 - game_screen.block_size * 2) + board_x * game_screen.block_size
    y = (game_screen.display_height / 2 - game_screen.block_size * 1.65) + board_y * game_screen.block_size
    return x, y


def _identity_label(state: LobbyState, identity: str) -> str:
    name = state.display_name(identity)
    if name:
        return name
    seat = state.host_seat if identity == "host" else state.peer_seat()
    return {"player1": "P1", "player2": "P2"}.get(seat, seat)


def _bans_of(state: LobbyState, identity: str) -> list[str]:
    return [card for card, banner in state.bans.items() if banner == identity]


class _SpectatorBoardCache:
    def __init__(self) -> None:
        self._signature: tuple = ()
        self._cards: list = []

    def get(self, state: LobbyState) -> list:
        signature = (tuple(state.bans.items()), state.host_seat)
        if signature != self._signature:
            self._signature = signature
            self._cards = []
            for row, identity in enumerate(_BAN_IDENTITIES):
                for col, name in enumerate(_bans_of(state, identity)[:MAX_BANS_PER_PLAYER]):
                    try:
                        self._cards.append(CardFactory.create(name, "display", col, row))
                    except ValueError:
                        pass
        return self._cards


def _render_lock(game_screen: GameScreen, board_x: int, board_y: int) -> None:
    locked = SpriteRegistry.get_instance().get("locked")
    if locked is None:
        return
    x, y = _cell_origin(game_screen, board_x, board_y)
    game_screen.surface.blit(locked, (int(x), int(y)))


def _render_spectator_labels(game_screen: GameScreen, state: LobbyState) -> None:
    bs = game_screen.block_size
    for row, identity in enumerate(_BAN_IDENTITIES):
        _x, y = _cell_origin(game_screen, 0, row)
        label = _identity_label(state, identity)
        draw_text(label, game_screen.mid_text_font, WHITE,
                  game_screen.display_width / 2 - bs * 3.7, y + bs * 0.3,
                  game_screen.surface)


def _render_player_ban_rows(game_screen: GameScreen, state: LobbyState,
                            controls: str, my_identity: Optional[str]) -> None:
    bs = game_screen.block_size
    x = game_screen.display_width // 16 * 2
    base_y = game_screen.display_height / 2 + bs * 1.5

    if my_identity is not None:
        rows = [my_identity, "peer" if my_identity == "host" else "host"]
    else:
        rows = list(_BAN_IDENTITIES)

    step = bs * 0.3
    for i, identity in enumerate(rows):
        cards = _bans_of(state, identity)
        label = _identity_label(state, identity)
        line = f"{label} ({len(cards)}/{MAX_BANS_PER_PLAYER}): {' '.join(cards) if cards else '-'}"
        draw_text(line, game_screen.text_font, WHITE, x, base_y + i * step,
                  game_screen.surface)

    all_line = f"all bans ({len(state.bans)}/{MAX_BANS_PER_PLAYER * 2}): " \
               f"{' '.join(state.bans) if state.bans else '-'}"
    draw_text(all_line, game_screen.text_font, WHITE, x, base_y + 2 * step,
              game_screen.surface)


def _render_header(game_screen: GameScreen, state: LobbyState, controls: Optional[str],
                   local_role: str, my_seat: str, my_identity: Optional[str]) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    draw_text("BAN DRAFT", game_screen.title_text_font, WHITE,
              cx - bs * 1.1, bs * 0.25, game_screen.surface)

    seat_labels = {"player1": "P1", "player2": "P2"}
    if controls == "both":
        identity = "You: local (both sides)"
        help_text = "click / S / B: ban   C / U: unban   |   ESC: back to lobby"
    elif controls == "host":
        my_name = state.display_name("host")
        identity = f"You: {my_name or seat_labels.get(my_seat, my_seat)} (host)"
        help_text = "click / S / B: ban   C / U: unban   |   ESC: back to lobby"
    elif controls == "peer":
        my_name = state.display_name("peer")
        identity = f"You: {my_name or seat_labels.get(my_seat, my_seat)}"
        help_text = "click / S / B: ban   C / U: unban   |   ESC: leave game"
    else:
        identity = "God View" if local_role == "god" else "Spectator"
        help_text = "watching ban draft   |   ESC: leave game"
    draw_text(identity, game_screen.text_font, WHITE,
              bs * 0.2, bs * 0.2, game_screen.surface)
    draw_text(help_text, game_screen.mid_text_font, WHITE,
              bs * 0.2, game_screen.display_height - bs * 0.45, game_screen.surface)


def _render_leave_confirm(game_screen: GameScreen) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    overlay = pygame.Surface((game_screen.display_width, game_screen.display_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    game_screen.surface.blit(overlay, (0, 0))
    lines = [
        "Leave the game?",
        "[Y] yes        [N] no",
    ]
    offsets = (-bs * 0.4, bs * 0.4)
    for line, dy in zip(lines, offsets):
        w = game_screen.mid_text_font.size(line)[0]
        draw_text(line, game_screen.mid_text_font, WHITE, cx - w / 2, cy + dy, game_screen.surface)


def main(game_screen: GameScreen, state: LobbyState, dispatcher: LobbyDispatcher,
         mode: str, server: Optional[LANServer] = None,
         client: Optional[LANClient] = None) -> str:
    registry = ExhibitRegistry(game_screen)
    card_renderer = CardRenderer(game_screen)
    board_renderer = BoardRenderer(game_screen)
    board_player = initialize_board(game_screen, BoardConfig(4, 3))
    board_spectator = initialize_board(game_screen, BoardConfig(4, 2))
    spectator_board = _SpectatorBoardCache()
    clock = pygame.time.Clock()
    page = 0
    index = 0

    ruleset_locked = TOURNAMENT_BANS if state.settings.ruleset == "tournament" else frozenset()
    back_button = make_back_button(game_screen, text="back", corner="top_right")
    confirming_leave = False

    def actor_for(banner: str) -> str:
        return "host" if banner == "host" else state.peer_seat()

    while True:
        if not state.in_ban_draft:
            return "done"

        if mode == "lan_server" and server is not None:
            server.pulse()
            dispatcher.tick()
        if mode == "lan_client" and client is not None:
            if client.is_disconnected:
                return "disconnected"
            if client.pending_scene is not None:
                return "done"

        local_role = state.local_role
        if mode == "local":
            controls: Optional[str] = "both"
            my_seat = ""
        elif local_role == "host":
            controls = "host"
            my_seat = state.host_seat
        elif local_role in ("player1", "player2"):
            controls = "peer"
            my_seat = local_role
        else:
            controls = None
            my_seat = ""
        my_identity = controls if controls in ("host", "peer") else None
        is_controller = controls in ("host", "both")

        mouse_x, mouse_y = pygame.mouse.get_pos()
        board_x = _to_board_x(mouse_x, game_screen)
        board_y = _to_board_y(mouse_y, game_screen)

        def hovered_card() -> str:
            return registry.card_name_at(page, index, board_x, board_y)

        def try_ban(card: str) -> None:
            if controls is None or card == "None" or not is_bannable_card(card):
                return
            if card in ruleset_locked or card in state.bans:
                return
            if controls == "both":
                banner = "host" if len(_bans_of(state, "host")) < MAX_BANS_PER_PLAYER else "peer"
            else:
                banner = controls
            dispatcher.dispatch(LobbyAction(actor_for(banner), "ban_card", str_value=card))

        def try_unban(card: str) -> None:
            owner = state.bans.get(card)
            if owner is None:
                return
            if controls == "both" or owner == controls:
                dispatcher.dispatch(LobbyAction(actor_for(owner), "unban_card", str_value=card))

        def unban_last() -> None:
            if controls == "both":
                mine = list(state.bans)
            elif my_identity is not None:
                mine = _bans_of(state, my_identity)
            else:
                mine = []
            if mine:
                try_unban(mine[-1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEWHEEL:
                page = (page + (1 if event.y > 0 else -1)) % registry.page_count()
                index = registry.index_count(page) - 1

            if event.type == pygame.KEYDOWN:
                if confirming_leave:
                    if event.key in (pygame.K_y, pygame.K_RETURN):
                        return "quit"
                    if event.key in (pygame.K_n, pygame.K_ESCAPE):
                        confirming_leave = False
                    continue
                if event.key == pygame.K_ESCAPE:
                    if is_controller:
                        dispatcher.dispatch(LobbyAction("host", "set_ban_draft", bool_value=False))
                    else:
                        confirming_leave = True
                elif event.key in (pygame.K_d, pygame.K_RIGHT, pygame.K_SPACE):
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        index = (index + 1) % max(1, registry.index_count(page))
                    else:
                        page = (page + 1) % registry.page_count()
                        index = registry.index_count(page) - 1
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        index = (index - 1) % max(1, registry.index_count(page))
                    else:
                        page = (page - 1) % registry.page_count()
                        index = registry.index_count(page) - 1
                elif event.key in (pygame.K_s, pygame.K_b):
                    try_ban(hovered_card())
                elif event.key in (pygame.K_c, pygame.K_u):
                    card = hovered_card()
                    if card != "None" and state.bans.get(card) is not None:
                        try_unban(card)
                    else:
                        unban_last()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not confirming_leave:
                if is_controller and back_button.touch(*event.pos):
                    dispatcher.dispatch(LobbyAction("host", "set_ban_draft", bool_value=False))
                    continue

                if controls is not None:
                    for i in range(len(registry.get_page_colors(page))):
                        if registry.switch_rects[i].collidepoint(event.pos):
                            index = i
                            break
                    else:
                        card = hovered_card()
                        if state.bans.get(card) is not None:
                            try_unban(card)
                        else:
                            try_ban(card)

        game_screen.render()

        if controls is not None:
            for i, color in enumerate(registry.get_page_colors(page)):
                pygame.draw.rect(game_screen.surface, color, registry.switch_rects[i])
            exhibit_cards = registry.get_page(page, index) + registry.get_magic_row()
            for card in exhibit_cards:
                for render_object in card.get_render_data():
                    card_renderer.render(render_object)
            for card in exhibit_cards:
                if card.job_and_color in state.bans or card.job_and_color in ruleset_locked:
                    _render_lock(game_screen, card.board_x, card.board_y)
            for board in board_player.values():
                board_renderer.render(board)
            _render_player_ban_rows(game_screen, state, controls, my_identity)
        else:
            for card in spectator_board.get(state):
                for render_object in card.get_render_data():
                    card_renderer.render(render_object)
                _render_lock(game_screen, card.board_x, card.board_y)
            for board in board_spectator.values():
                board_renderer.render(board)
            _render_spectator_labels(game_screen, state)

        _render_header(game_screen, state, controls, local_role, my_seat, my_identity)
        if is_controller:
            back_button.update(game_screen)
        if confirming_leave:
            _render_leave_confirm(game_screen)

        pygame.display.update()
        clock.tick(60)
