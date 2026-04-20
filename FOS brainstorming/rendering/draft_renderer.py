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

from core.game_screen import GameScreen, draw_text
from core.draft_state import DraftState
from core.setting import WHITE
from core.card_hint import HintBox
from rendering.board_renderer import BoardRenderer
from rendering.card_renderer import CardRenderer
from screens.draft.exhibit_registry import ExhibitRegistry


class DraftRenderer:
    def __init__(self, game_screen: GameScreen, exhibit_registry: ExhibitRegistry):
        self.game_screen = game_screen
        self.exhibit_registry = exhibit_registry
        self._hint_box = HintBox(width=int(game_screen.block_size*3), height=int(game_screen.block_size))
        self.card_renderer = CardRenderer(game_screen)
        self.board_renderer = BoardRenderer(game_screen)

    def render_frame(self, page: int, mouse_board_x: Optional[int], mouse_board_y: Optional[int], draft_state: DraftState, hint_on: bool = False) -> None:
        self.game_screen.render()
        
        self._render_cards(page)
        self._render_boards(draft_state)
        self._render_deck_displays(draft_state)
        self._render_status_labels(draft_state)
        self._render_hint(page, mouse_board_x, mouse_board_y, hint_on)

    def _render_cards(self, page: int) -> None:
        for card in self.exhibit_registry.get_page(page):
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
        for card in self.exhibit_registry.get_magic_row():
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)

    def _render_boards(self, draft_state: DraftState) -> None:
        for board in draft_state.board_dict.values():
            self.board_renderer.render(board)
    
    def _render_player_deck(self, owner: str, draft_state: DraftState) -> None:
        offset_y = 1 if owner == "player1" else 1.5
        draw_text(f"{"P1" if owner == "player1" else "P2"}Deck:",
                  self.game_screen.text_font, WHITE, self.game_screen.display_width//16*2,
                  self.game_screen.display_height - (self.game_screen.display_height//5/offset_y),
                  self.game_screen.surface)
        
        for i, card in enumerate(draft_state.get_deck(owner)):
            if i in draft_state.get_visible_deck(draft_state.local_player, owner):
                draw_text(card, self.game_screen.text_font,
                          WHITE, self.game_screen.display_width/16*(i+3),
                          self.game_screen.display_height-(self.game_screen.display_height/5/offset_y),
                          self.game_screen.surface)
            else:
                draw_text("???", self.game_screen.text_font,
                          WHITE, self.game_screen.display_width/16*(i+3),
                          self.game_screen.display_height-(self.game_screen.display_height/5/offset_y),
                          self.game_screen.surface)

        if draft_state.current_editor() == owner and len(draft_state.get_deck(owner)) < 12:
            draw_text("<--", self.game_screen.text_font, WHITE,
                      self.game_screen.display_width/16 * (len(draft_state.get_deck(owner))+3),
                      self.game_screen.display_height-(self.game_screen.display_height/5/offset_y),
                      self.game_screen.surface)

    def _render_deck_displays(self, draft_state: DraftState) -> None:
        self._render_player_deck("player1", draft_state)
        self._render_player_deck("player2", draft_state)

    def _render_status_labels(self, draft_state: DraftState) -> None:
        draw_text(
            f"Timer Mode: {draft_state.timer_mode}",
            self.game_screen.text_font, WHITE,
            self.game_screen.display_width / 5,
            self.game_screen.display_height/1.4 + self.game_screen.block_size*0.2,
            self.game_screen.surface
        )
        draw_text(
            "File Mode: Save" if not draft_state.file_auto_delete else "File Mode: Delete",
            self.game_screen.text_font, WHITE,
            self.game_screen.display_width/5 + self.game_screen.block_size*1.5,
            self.game_screen.display_height/1.4 + self.game_screen.block_size*0.2,
            self.game_screen.surface
        )

    def _render_hint(self, page: int, mouse_board_x: Optional[int], mouse_board_y: Optional[int], hint_on: bool) -> None:
        self._hint_box.turn_on = hint_on
        if not hint_on:
            return
        if mouse_board_x is None or mouse_board_y is None:
            return
        card_name = self.exhibit_registry.card_name_at(page, mouse_board_x, mouse_board_y)
        if card_name == "None":
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self._hint_box.update(mouse_x, mouse_y, card_name, self.game_screen)