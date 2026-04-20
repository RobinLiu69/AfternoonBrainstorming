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

from core.board_block import Board
from core.game_screen import GameScreen
from core.game_state import GameState


class BoardRenderer:
    def __init__(self, game_screen: GameScreen):
        self.game_screen = game_screen

    def _board_to_pixel(self, board_x: int, board_y: int) -> tuple[float, float]:
        x = (self.game_screen.display_width/2 - self.game_screen.block_size*2) + board_x*self.game_screen.block_size
        y = (self.game_screen.display_height/2 - self.game_screen.block_size*1.675) + board_y*self.game_screen.block_size
        return x, y

    def render(self, board: Board) -> None:
        x, y = self._board_to_pixel(board.board_x, board.board_y)
        pygame.draw.rect(self.game_screen.surface, board.color, (x, y, board.width, board.height), self.game_screen.thickness)

    def render_all(self, game_state: GameState) -> None:
        for board in game_state.board_dict.values():
            self.render(board)

    def render_attack_highlight(self, board_x: int, board_y: int, controller: str, game_state: GameState) -> None:
        target_cards = tuple(filter(lambda card: card.board_x == board_x and card.board_y == board_y, game_state.get_all_cards()))
        if not target_cards:
            return

        card = target_cards[0]
        color = (200, 200, 200) if card.owner == controller else (200, 0, 0)

        for ax, ay in card.attack_area_display(game_state):
            self._render_highlight_tile(color, ax, ay)

    def _render_highlight_tile(self, color: tuple[int, int, int], board_x: int, board_y: int) -> None:
        x, y = self._board_to_pixel(board_x, board_y)
        surface = pygame.Surface((self.game_screen.block_size, self.game_screen.block_size))
        surface.fill(color)
        surface.set_alpha(60)
        self.game_screen.surface.blit(surface, (x, y))