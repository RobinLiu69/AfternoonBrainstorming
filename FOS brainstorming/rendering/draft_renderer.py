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

from core.game_screen import GameScreen, draw_text
from core.draft_state import DraftState
from shared.setting import WHITE, BLUE, RED
from core.card_hint import HintBox
from rendering.board_renderer import BoardRenderer
from rendering.card_renderer import CardRenderer
from screens.draft.exhibit_registry import ExhibitRegistry
from rendering.sprite_registry import SpriteRegistry


class DraftRenderer:
    def __init__(self, game_screen: GameScreen, exhibit_registry: ExhibitRegistry):
        self.game_screen = game_screen
        self.exhibit_registry = exhibit_registry
        self._hint_box = HintBox(width=int(game_screen.block_size*3), height=int(game_screen.block_size))
        self.card_renderer = CardRenderer(game_screen)
        self.board_renderer = BoardRenderer(game_screen)
        self.switch_rects = self.exhibit_registry.switch_rects

    def render_frame(self, page: int, index: int, mouse_board_x: Optional[int], mouse_board_y: Optional[int], draft_state: DraftState, hint_on: bool = False,
                     multiplayer: bool = False) -> None:
        self.game_screen.render()

        self._render_colors(page)
        self._render_cards(page, index)
        self._render_ban(page, index, draft_state)
        self._render_boards(draft_state)
        self._render_deck_displays(draft_state)
        self._render_status_labels(draft_state)
        self._render_spectator_count(draft_state)
        if multiplayer:
            self._render_identity_label(draft_state.local_player)
        self._render_hint(page, index, mouse_board_x, mouse_board_y, hint_on)

        if draft_state.paused:
            self._render_pause_overlay(draft_state)

    def _render_identity_label(self, local_player: str) -> None:
        label_map = {
            "player1": "You: P1",
            "player2": "You: P2",
            "spectator": "Spectator",
            "god": "God View",
        }
        label = label_map.get(local_player, local_player)
        gs = self.game_screen
        draw_text(label, gs.text_font, WHITE,
                  gs.block_size * 0.2, gs.block_size * 0.2, gs.surface)

    def _render_spectator_count(self, draft_state: DraftState) -> None:
        count = getattr(draft_state, "net_spectator_count", 0)
        if not count or count <= 0:
            return
        gs = self.game_screen
        text = f"spectators: {count}"
        width = gs.text_font.size(text)[0]
        draw_text(text, gs.text_font, WHITE,
                  gs.display_width - width - gs.block_size * 0.3,
                  gs.block_size * 0.2, gs.surface)

    def _render_pause_overlay(self, draft_state: DraftState) -> None:
        gs = self.game_screen
        overlay = pygame.Surface((gs.display_width, gs.display_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        gs.surface.blit(overlay, (0, 0))

        bs = gs.block_size
        cx = gs.display_width / 2
        cy = gs.display_height / 2
        remaining = draft_state.pause_seconds_remaining
        reason = draft_state.pause_reason or "opponent disconnected"

        if remaining == float("inf"):
            window_line = "reconnect window: unlimited"
            note_line = "(waiting for opponent)"
        else:
            window_line = f"reconnect window: {max(0, int(remaining))}s"
            note_line = "(match cancels on timeout)"

        lines = [
            reason,
            window_line,
            note_line,
        ]
        offsets = (-bs * 0.6, 0.0, bs * 0.6)
        for line, dy in zip(lines, offsets):
            draw_text(line, gs.big_text_font, WHITE, cx - bs * 2.0, cy + dy, gs.surface)

    def _render_colors(self, page: int) -> None:
        for i, color in enumerate(self.exhibit_registry.get_page_colors(page)):
            pygame.draw.rect(self.game_screen.surface, color, self.switch_rects[i])

    def _render_cards(self, page: int, index: int) -> None:
        for card in self.exhibit_registry.get_page(page, index):
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
        for card in self.exhibit_registry.get_magic_row():
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
    
    def _render_ban(self, page: int, index: int, draft_state: DraftState) -> None:
        locked = SpriteRegistry.get_instance().get("locked")
        if locked is None:
            return
        gs = self.game_screen
        for card in self.exhibit_registry.get_page(page, index) + self.exhibit_registry.get_magic_row():
            if not draft_state.is_banned(card.job_and_color):
                continue
            for data in card.get_render_data():
                x = (gs.display_width  / 2 - gs.block_size * 2) + data.board_x * gs.block_size
                y = (gs.display_height / 2 - gs.block_size * 1.65) + data.board_y * gs.block_size
                gs.surface.blit(locked, (int(x), int(y)))

    def _render_boards(self, draft_state: DraftState) -> None:
        for board in draft_state.board_dict.values():
            self.board_renderer.render(board)
    
    def _render_player_deck(self, owner: str, draft_state: DraftState) -> None:
        offset_y = 1 if owner == "player1" else 1.5
        draw_text(f"{'P1' if owner == 'player1' else 'P2'}Deck:",
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
        editor = draft_state.current_editor()
        editor_label = draft_state.current_editor_label()
        if editor_label:
            local = draft_state.local_player
            if local in ("player1", "player2"):
                color = BLUE if editor == local else RED
            else:
                color = BLUE if editor == "player1" else RED
            text = f"Drafting: {editor_label}"
            font = self.game_screen.big_big_text_font
            width = font.size(text)[0]
            draw_text(
                text, font, color,
                self.game_screen.display_width / 2 - width / 2,
                self.game_screen.block_size * 0.25,
                self.game_screen.surface
            )
        draw_text(
            f"Timer Mode: {draft_state.settings.timer_mode}",
            self.game_screen.text_font, WHITE,
            self.game_screen.display_width / 5,
            self.game_screen.display_height/1.4 + self.game_screen.block_size*0.2,
            self.game_screen.surface
        )
        draw_text(
            "File Mode: Save" if not draft_state.settings.file_auto_delete else "File Mode: Delete",
            self.game_screen.text_font, WHITE,
            self.game_screen.display_width/5 + self.game_screen.block_size*1.5,
            self.game_screen.display_height/1.4 + self.game_screen.block_size*0.2,
            self.game_screen.surface
        )

    def _render_hint(self, page: int, index: int, mouse_board_x: Optional[int], mouse_board_y: Optional[int], hint_on: bool) -> None:
        self._hint_box.turn_on = hint_on
        if not hint_on:
            return
        if mouse_board_x is None or mouse_board_y is None:
            return
        card_name = self.exhibit_registry.card_name_at(page, index, mouse_board_x, mouse_board_y)
        if card_name == "None":
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self._hint_box.update(mouse_x, mouse_y, card_name, self.game_screen)