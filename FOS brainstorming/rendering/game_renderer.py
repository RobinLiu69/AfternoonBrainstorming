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

from typing import TYPE_CHECKING, Generator

from core.setting import COMBAT_ANIMATIONS_ENABLED
from core.game_screen import GameScreen
from core.game_state import GameState
from rendering.card_renderer import CardRenderer
from rendering.board_renderer import BoardRenderer
from rendering.ui_renderer import UIRenderer
from rendering.combat_animator import CombatAnimator, _Anim


if TYPE_CHECKING:
    from cards.base import Card


class GameRenderer:
    def __init__(self, game_screen: GameScreen):
        self.game_screen = game_screen
        self.dying_cards: list[Card] = []

        self.card_renderer = CardRenderer(game_screen)
        self.board_renderer = BoardRenderer(game_screen)
        self.ui_renderer = UIRenderer(game_screen)
        self.combat_animator = CombatAnimator(game_screen, enabled=COMBAT_ANIMATIONS_ENABLED)
    
    def render_frame(self, local_controller: str, controller: str, mouse_x: int, mouse_y: int,
                     mouse_board_x: int | None, mouse_board_y: int | None, game_state: GameState, hint_on: bool = False,
                     dt: float = 0.0) -> None:
        self.game_screen.render()
    
        self._ingest_combat_events(game_state)

        completed = self.combat_animator.update(dt)
        all_groups = [game_state.neutral.on_board,
                    game_state.player1.on_board,
                    game_state.player2.on_board]
        self._apply_completed_health_updates(completed, all_groups)

        anim_positions = self.combat_animator.get_active_positions()
        self._render_dying_cards(anim_positions)
        self._render_live_cards(all_groups, anim_positions)

        self.board_renderer.render_all(game_state)

        self.combat_animator.render_overlays(self.game_screen.surface)

        if mouse_board_x is not None and mouse_board_y is not None:
            self.board_renderer.render_attack_highlight(
                mouse_board_x, mouse_board_y, local_controller, game_state
            )

        self.ui_renderer.render_score(local_controller, controller, game_state)
        self.ui_renderer.render_controller_label(controller)
        self.ui_renderer.render_hands(game_state)
        self.ui_renderer.render_attack_counts(game_state)
        self.ui_renderer.render_tokens(game_state)
        self.ui_renderer.render_luck(game_state)
        self.ui_renderer.render_totems(game_state)
        self.ui_renderer.render_coins(game_state)
        self.ui_renderer.render_deck_info(game_state)
        self.ui_renderer.render_timers(game_state)

        self._render_hint(mouse_x, mouse_y, mouse_board_x, mouse_board_y, game_state, hint_on)

    def _ingest_combat_events(self, game_state: GameState) -> None:
        for ev in game_state.pending_combat_events:
            self.combat_animator.push(ev)
        game_state.pending_combat_events.clear()

    def _apply_completed_health_updates(self, completed: list[_Anim], all_groups: list[list[Card]]) -> None:
        for anim in completed:
            ev = anim.event
            if ev.kind != "hurt" or ev.post_health < 0:
                continue
            pos = (ev.board_x, ev.board_y)
            for card in self._iter_cards_at(pos, all_groups):
                card.display_health = ev.post_health

    def _iter_cards_at(self, pos, all_groups: list[list[Card]]) -> Generator[Card]:
        for group in all_groups:
            for card in group:
                if (card.board_x, card.board_y) == pos:
                    yield card
        for card in self.dying_cards:
            if (card.board_x, card.board_y) == pos:
                yield card
    
    def _render_dying_cards(self, anim_positions: set[tuple[int, int]]) -> None:
        still_dying = []
        for card in self.dying_cards:
            pos = (card.board_x, card.board_y)
            if pos in anim_positions:
                self._render_card_with_offset(card, pos)
                still_dying.append(card)
            else:
                self.card_renderer.release(card.instance_id)
        self.dying_cards = still_dying
    
    def _render_live_cards(self, all_groups: list[list[Card]], anim_positions: set[tuple[int, int]]) -> None:
        for group in all_groups:
            to_remove: list[Card] = []
            for card in group:
                pos = (card.board_x, card.board_y)
                if card.pending_death and pos not in anim_positions:
                    to_remove.append(card)
                    continue
                self._render_card_with_offset(card, pos)
            for card in to_remove:
                self.card_renderer.release(card.instance_id)

    def _render_card_with_offset(self, card: Card, pos: tuple[int, int]) -> None:
        offset = self.combat_animator.get_offset(*pos)
        for render_object in card.get_render_data():
            self.card_renderer.render(render_object, offset=offset)

    def _render_hint(self, mouse_x: int, mouse_y: int,
                     mouse_board_x: int | None, mouse_board_y: int | None, game_state: GameState, hint_on: bool) -> None:
        self.ui_renderer._hint_box.turn_on = hint_on
        if not hint_on:
            return
        
        if mouse_x < self.game_screen.display_width / 2 - self.game_screen.block_size * 2:
            name, _ = game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, self.game_screen)
            if name != "None":
                self.ui_renderer.render_hint(mouse_x, mouse_y, name)

        elif mouse_x > self.game_screen.display_width / 2 + self.game_screen.block_size * 2:
            name, _ = game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, self.game_screen)
            if name != "None":
                self.ui_renderer.render_hint(mouse_x, mouse_y, name)

        if mouse_board_x is not None and mouse_board_y is not None:
            for card in game_state.get_all_cards():
                if card.board_x == mouse_board_x and card.board_y == mouse_board_y:
                    self.ui_renderer.render_hint(mouse_x, mouse_y, card)
                    return
    
    def _render_boards(self, game_state: GameState) -> None:
        for board in game_state.board_dict.values():
            self.board_renderer.render(board)
    
    def _render_neutral_cards(self, game_state: GameState) -> None:
        for card in game_state.neutral.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
    
    def _render_player_cards(self, game_state: GameState) -> None:
        for card in game_state.player1.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
        for card in game_state.player2.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)