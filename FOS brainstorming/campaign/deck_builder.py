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

from __future__ import annotations
from typing import Optional

import pygame

from shared.setting import WHITE, JOB_DICTIONARY
from core.draft_state import DraftState
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.game_screen import GameScreen
from cards.base import Card
from screens.draft.exhibit_registry import ExhibitRegistry
from screens.draft.draft_action import DraftAction
from rendering.draft_renderer import DraftRenderer

from campaign.ai_decks import STAGE_ORDER, STAGE_AI_DECKS, STAGE_PLAYER_DECKS


DECK_SIZE: int = 12
MAX_UNIT: int = 2
MAX_MAGIC: int = 3
MAGIC_CARDS: tuple[str, ...] = ("CUBES", "HEAL", "MOVE", "MOVEO")


STAGE_TO_COLOR_CODE: dict[str, str] = {
    "white": "W", "red": "R", "blue": "B", "green": "G", "orange": "O",
}


def _unlocked_color_codes(stage: str, cleared: set[str]) -> list[str]:
    if stage == "boss":
        return ["W", "R", "B", "G", "O"]
    codes: list[str] = ["W"]
    current_idx = STAGE_ORDER.index(stage)
    own_code = STAGE_TO_COLOR_CODE.get(stage)
    if own_code and own_code not in codes:
        codes.append(own_code)
    for i, s in enumerate(STAGE_ORDER):
        if i >= current_idx or s in ("white", "boss"):
            continue
        code = STAGE_TO_COLOR_CODE.get(s)
        if code and code not in codes and s in cleared:
            codes.append(code)
    return codes


def _color_code_of(job_and_color: str) -> str:
    for tag in sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True):
        if job_and_color.endswith(tag):
            return tag
    return ""


class _CampaignExhibitRegistry:
    """ExhibitRegistry wrapper that only exposes pages whose colour is unlocked."""

    def __init__(self, base: ExhibitRegistry, unlocked_codes: list[str]):
        self._pages: list[list[Card]] = []
        for page in base._pages:
            if not page:
                continue
            if _color_code_of(page[0].job_and_color) in unlocked_codes:
                self._pages.append(page)
        self._magic_row: list[Card] = list(base.get_magic_row())

    def page_count(self) -> int:
        return len(self._pages)

    def get_page(self, page: int) -> list[Card]:
        return self._pages[page] if 0 <= page < len(self._pages) else []

    def get_magic_row(self) -> list[Card]:
        return self._magic_row

    def card_name_at(self, page: int, board_x: Optional[int], board_y: Optional[int]) -> str:
        if board_x is None or board_y is None:
            return "None"
        for card in self.get_page(page):
            if card.board_x == board_x and card.board_y == board_y:
                return card.job_and_color
        for card in self._magic_row:
            if card.board_x == board_x and card.board_y == board_y:
                return card.job_and_color
        return "None"


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


def _collect_actions(page: int, registry: _CampaignExhibitRegistry,
                     mouse_board_x: Optional[int], mouse_board_y: Optional[int]) -> list[DraftAction]:
    actions: list[DraftAction] = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            actions.append(DraftAction("player1", "quit"))
            continue
        if event.type == pygame.MOUSEWHEEL:
            actions.append(DraftAction("player1", "page_next" if event.y > 0 else "page_prev"))
            continue
        if event.type == pygame.MOUSEBUTTONDOWN:
            card = registry.card_name_at(page, mouse_board_x, mouse_board_y)
            if event.button == 1 and card != "None":
                actions.append(DraftAction("player1", "add_card", card))
            elif event.button == 3:
                if card != "None":
                    actions.append(DraftAction("player1", "remove_card", card))
                else:
                    actions.append(DraftAction("player1", "remove_last_card"))
            continue
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_ESCAPE:
                    actions.append(DraftAction("player1", "quit"))
                case pygame.K_SPACE | pygame.K_d | pygame.K_RIGHT:
                    actions.append(DraftAction("player1", "page_next"))
                case pygame.K_a | pygame.K_LEFT:
                    actions.append(DraftAction("player1", "page_prev"))
                case pygame.K_s:
                    card = registry.card_name_at(page, mouse_board_x, mouse_board_y)
                    if card != "None":
                        actions.append(DraftAction("player1", "add_card", card))
                case pygame.K_c:
                    actions.append(DraftAction("player1", "remove_last_card"))
                case pygame.K_e | pygame.K_RETURN | pygame.K_KP_ENTER:
                    actions.append(DraftAction("player1", "confirm_start"))
                case pygame.K_f:
                    actions.append(DraftAction("player1", "toggle_hint"))
    return actions


def _can_add(deck: list[str], card: str) -> bool:
    if len(deck) >= DECK_SIZE:
        return False
    limit = MAX_MAGIC if card in MAGIC_CARDS else MAX_UNIT
    return deck.count(card) < limit


def main(game_screen: GameScreen, stage: str, cleared: set[str]) -> Optional[list[str]]:
    """Draft-style deck builder for campaign. Returns the chosen 12-card deck or None."""
    unlocked = _unlocked_color_codes(stage, cleared)
    base_registry = ExhibitRegistry()
    registry = _CampaignExhibitRegistry(base_registry, unlocked)

    draft_state = DraftState()
    draft_state.board_config = BoardConfig(4, 3)
    draft_state.board_dict = initialize_board(game_screen, draft_state.board_config)
    draft_state.player2_deck = list(STAGE_AI_DECKS[stage])
    draft_state.player1_deck = list(STAGE_PLAYER_DECKS.get(stage, []))[:DECK_SIZE]
    draft_state.phase = "p1_first6"
    draft_state.local_player = "god"

    renderer = DraftRenderer(game_screen, registry)  # type: ignore[arg-type]

    page = 0
    hint_on = False
    clock = pygame.time.Clock()
    confirmed: Optional[list[str]] = None
    running = True

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        bx = _to_board_x(mouse_x, game_screen)
        by = _to_board_y(mouse_y, game_screen)

        actions = _collect_actions(page, registry, bx, by)
        for a in actions:
            if a.action_type == "quit":
                running = False
            elif a.action_type == "page_next" and registry.page_count() > 0:
                page = (page + 1) % registry.page_count()
            elif a.action_type == "page_prev" and registry.page_count() > 0:
                page = (page - 1) % registry.page_count()
            elif a.action_type == "toggle_hint":
                hint_on = not hint_on
            elif a.action_type == "add_card" and a.card_name:
                if _can_add(draft_state.player1_deck, a.card_name):
                    draft_state.player1_deck.append(a.card_name)
            elif a.action_type == "remove_card" and a.card_name:
                if a.card_name in draft_state.player1_deck:
                    draft_state.player1_deck.remove(a.card_name)
            elif a.action_type == "remove_last_card":
                if draft_state.player1_deck:
                    draft_state.player1_deck.pop()
            elif a.action_type == "confirm_start":
                if len(draft_state.player1_deck) == DECK_SIZE:
                    confirmed = list(draft_state.player1_deck)
                    running = False

        renderer.render_frame(page, bx, by, draft_state, hint_on)
        _draw_help(game_screen, draft_state.player1_deck)
        pygame.display.update()
        clock.tick(60)

    return confirmed


def _draw_help(game_screen: GameScreen, p1_deck: list[str]) -> None:
    from core.game_screen import draw_text
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    msg_left = "left-click: add   right-click: remove   wheel/arrows: page"
    msg_right = f"deck: {len(p1_deck)}/{DECK_SIZE}   press ENTER when full"
    draw_text(msg_left, game_screen.mid_text_font, WHITE,
              cx - bs * 4.2, cy + bs * 1.55, game_screen.surface)
    draw_text(msg_right, game_screen.mid_text_font, WHITE,
              cx + bs * 0.6, cy + bs * 1.55, game_screen.surface)
