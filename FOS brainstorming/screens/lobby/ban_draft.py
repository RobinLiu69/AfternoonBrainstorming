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


class _BanBoardCache:
    def __init__(self) -> None:
        self._signature: tuple = ()
        self._cards: list = []

    def get(self, bans: dict[str, str]) -> list:
        signature = tuple(bans)
        if signature != self._signature:
            self._signature = signature
            self._cards = []
            for i, name in enumerate(bans):
                if i >= 12:
                    break
                try:
                    self._cards.append(CardFactory.create(name, "display", i % 4, i // 4))
                except ValueError:
                    pass
        return self._cards


def _render_lock(game_screen: GameScreen, board_x: int, board_y: int) -> None:
    locked = SpriteRegistry.get_instance().get("locked")
    if locked is None:
        return
    x, y = _cell_origin(game_screen, board_x, board_y)
    game_screen.surface.blit(locked, (int(x), int(y)))


def _render_ban_lists(game_screen: GameScreen, state: LobbyState, my_identity: str) -> None:
    total = f"banned ({len(state.bans)}/{MAX_BANS_PER_PLAYER * 2}): " \
            f"{' '.join(state.bans) if state.bans else '-'}"
    draw_text(total, game_screen.text_font, WHITE,
              game_screen.display_width // 16 * 2,
              game_screen.display_height - game_screen.display_height // 5,
              game_screen.surface)
    if my_identity:
        mine = [c for c, banner in state.bans.items() if banner == my_identity]
        line = f"your bans ({len(mine)}/{MAX_BANS_PER_PLAYER}): " \
               f"{' '.join(mine) if mine else '-'}"
        draw_text(line, game_screen.text_font, WHITE,
                  game_screen.display_width // 16 * 2,
                  game_screen.display_height - game_screen.display_height // 5 / 1.5,
                  game_screen.surface)


def _render_header(game_screen: GameScreen, state: LobbyState,
                   local_role: str, my_seat: str, my_identity: str) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    draw_text("BAN DRAFT", game_screen.title_text_font, WHITE,
              cx - bs * 1.1, bs * 0.25, game_screen.surface)

    seat_labels = {"player1": "P1", "player2": "P2"}
    my_name = state.display_name(my_identity) if my_identity else ""
    if local_role == "host":
        identity = f"You: {my_name or seat_labels.get(my_seat, my_seat)} (host)"
        help_text = "click / S / B: ban   C / U: unban   |   ESC: back to lobby"
    elif my_seat:
        identity = f"You: {my_name or seat_labels[my_seat]}"
        help_text = "click / S / B: ban   C / U: unban   |   host closes this screen"
    else:
        identity = "God View" if local_role == "god" else "Spectator"
        help_text = "watching ban draft"
    draw_text(identity, game_screen.text_font, WHITE,
              bs * 0.2, bs * 0.2, game_screen.surface)
    draw_text(help_text, game_screen.mid_text_font, WHITE,
              bs * 0.2, game_screen.display_height - bs * 0.45, game_screen.surface)


def main(game_screen: GameScreen, state: LobbyState, dispatcher: LobbyDispatcher,
         mode: str, server: Optional[LANServer] = None,
         client: Optional[LANClient] = None) -> str:
    registry = ExhibitRegistry(game_screen)
    card_renderer = CardRenderer(game_screen)
    board_renderer = BoardRenderer(game_screen)
    board_dict = initialize_board(game_screen, BoardConfig(4, 3))
    ban_board = _BanBoardCache()
    clock = pygame.time.Clock()
    page = 0
    index = 0

    ruleset_locked = TOURNAMENT_BANS if state.settings.ruleset == "tournament" else frozenset()

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

        local_role = "host" if mode == "lan_server" else state.local_role
        if local_role == "host":
            my_identity = "host"
            my_seat = state.host_seat
        elif local_role in ("player1", "player2"):
            my_identity = "peer"
            my_seat = local_role
        else:
            my_identity = ""
            my_seat = ""
        actor = "host" if local_role == "host" else my_seat

        mouse_x, mouse_y = pygame.mouse.get_pos()
        board_x = _to_board_x(mouse_x, game_screen)
        board_y = _to_board_y(mouse_y, game_screen)

        def hovered_card() -> str:
            return registry.card_name_at(page, index, board_x, board_y)

        def try_ban(card: str) -> None:
            if (my_identity and card != "None" and is_bannable_card(card)
                    and card not in ruleset_locked and card not in state.bans):
                dispatcher.dispatch(LobbyAction(actor, "ban_card", str_value=card))

        def try_unban(card: str) -> None:
            if my_identity and state.bans.get(card) == my_identity:
                dispatcher.dispatch(LobbyAction(actor, "unban_card", str_value=card))

        def unban_last() -> None:
            mine = [c for c, banner in state.bans.items() if banner == my_identity]
            if mine:
                try_unban(mine[-1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEWHEEL:
                page = (page + (1 if event.y > 0 else -1)) % registry.page_count()
                index = registry.index_count(page) - 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and local_role == "host":
                    dispatcher.dispatch(LobbyAction("host", "set_ban_draft", bool_value=False))
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
                    if state.bans.get(card) == my_identity:
                        try_unban(card)
                    elif card == "None":
                        unban_last()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and my_identity:
                for i in range(len(registry.get_page_colors(page))):
                    if registry.switch_rects[i].collidepoint(event.pos):
                        index = i
                        break
                else:
                    card = hovered_card()
                    if state.bans.get(card) == my_identity:
                        try_unban(card)
                    else:
                        try_ban(card)

        game_screen.render()
        for board in board_dict.values():
            board_renderer.render(board)

        if my_identity:
            for i, color in enumerate(registry.get_page_colors(page)):
                pygame.draw.rect(game_screen.surface, color, registry.switch_rects[i])
            exhibit_cards = registry.get_page(page, index) + registry.get_magic_row()
            for card in exhibit_cards:
                for render_object in card.get_render_data():
                    card_renderer.render(render_object)
            for card in exhibit_cards:
                if card.job_and_color in state.bans or card.job_and_color in ruleset_locked:
                    _render_lock(game_screen, card.board_x, card.board_y)
        else:
            for card in ban_board.get(state.bans):
                for render_object in card.get_render_data():
                    card_renderer.render(render_object)
                _render_lock(game_screen, card.board_x, card.board_y)

        _render_ban_lists(game_screen, state, my_identity)
        _render_header(game_screen, state, local_role, my_seat, my_identity)

        pygame.display.update()
        clock.tick(60)
