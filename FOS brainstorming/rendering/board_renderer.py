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
from typing import TYPE_CHECKING, cast
import pygame

from core.board_block import Board
from core.game_screen import GameScreen, draw_text
from core.game_state import GameState

if TYPE_CHECKING:
    from cards.base import Card
    from cards.card_fuchsia import Shadow


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

        self._render_attack_order_numbers(card, game_state)

    def _render_attack_order_numbers(self, card: Card, game_state: GameState) -> None:
        if not card.attack_types:
            return
        enemies = [c for c in game_state.get_side_cards(card.owner, True) if c.health > 0]
        font = self.game_screen.big_text_font

        labels: list[tuple[int, int, str, tuple[int, int, int]]] = []
        ordinal = self._collect_attack_labels(card, enemies, 1, game_state, labels)
        for shadow in cast(list["Shadow"], getattr(card, "shadows", ())):
            shadow_enemies = [c for c in game_state.get_side_cards(shadow.owner, True)
                              if c.health > 0 and c.job_and_color != "SHADOW"]
            ordinal = self._collect_attack_labels(shadow, shadow_enemies, ordinal, game_state, labels)

        self._render_labels(labels, font)

    def _collect_attack_labels(self, attacker: Card, enemies: list[Card], ordinal: int,
                               game_state: GameState,
                               labels: list[tuple[int, int, str, tuple[int, int, int]]]) -> int:
        if not attacker.attack_types:
            return ordinal
        for attack_type in attacker.attack_types.split(" "):
            if attack_type == "nearest":
                candidates = self._nearest_candidates(attacker, enemies)
                n = len(candidates)
                label = str(ordinal) if n <= 1 else f"1/{n}"
                color: tuple[int, int, int] = (255, 255, 255) if n <= 1 else (255, 220, 120)
                for c in candidates:
                    labels.append((c.board_x, c.board_y, label, color))
                ordinal += 1
            elif attack_type == "farthest":
                candidates = self._farthest_candidates(attacker, enemies)
                n = len(candidates)
                label = str(ordinal) if n <= 1 else f"1/{n}"
                color = (255, 255, 255) if n <= 1 else (255, 220, 120)
                for c in candidates:
                    labels.append((c.board_x, c.board_y, label, color))
                ordinal += 1
            else:
                targets = list(attacker.detection(attack_type, enemies, game_state))
                for t in targets:
                    labels.append((t.board_x, t.board_y, str(ordinal), (255, 255, 255)))
                    ordinal += 1
        return ordinal

    def _render_labels(self, labels: list[tuple[int, int, str, tuple[int, int, int]]],
                       font: pygame.font.Font) -> None:
        pos_entries: dict[tuple[int, int], list[tuple[str, tuple[int, int, int]]]] = {}
        for bx, by, label, color in labels:
            pos_entries.setdefault((bx, by), []).append((label, color))

        small_font = self.game_screen.text_font
        bs = self.game_screen.block_size

        for (bx, by), entries in pos_entries.items():
            x, y = self._board_to_pixel(bx, by)
            if len(entries) == 1:
                label, color = entries[0]
                tw, th = font.size(label)
                cx = x + (bs - tw) / 2
                cy = y + (bs - th) / 2
                self._draw_label_with_bg(label, font, color, cx, cy)
            elif len(entries) == 2:
                label0, color0 = entries[0]
                tw, th = font.size(label0)
                cx0 = x + (bs - tw) / 2
                cy0 = y + (bs - th) / 2
                self._draw_label_with_bg(label0, font, color0, cx0, cy0)
                label1, color1 = entries[1]
                self._draw_label_with_bg(label1, small_font, color1, cx0 + tw, cy0 + th)
            else:
                line_h = font.size("0")[1]
                total_h = line_h * len(entries)
                start_y = y + (bs - total_h) / 2
                for i, (label, color) in enumerate(entries):
                    tw, th = font.size(label)
                    self._draw_label_with_bg(label, font, color,
                                             x + (bs - tw) / 2, start_y + i * line_h)

    def _draw_label_with_bg(self, label: str, font: pygame.font.Font,
                            color: tuple[int, int, int], cx: float, cy: float) -> None:
        tw, th = font.size(label)
        bg = pygame.Surface((tw + 4, th + 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        self.game_screen.surface.blit(bg, (int(cx) - 2, int(cy) - 1))
        draw_text(label, font, color, cx, cy, self.game_screen.surface)

    def _nearest_candidates(self, card: Card, enemies: list[Card]) -> list[Card]:
        alive = [c for c in enemies if c.health > 0]
        if not alive:
            return []
        min_dist = min(abs(c.board_x - card.board_x) + abs(c.board_y - card.board_y) for c in alive)
        return [c for c in alive if abs(c.board_x - card.board_x) + abs(c.board_y - card.board_y) == min_dist]

    def _farthest_candidates(self, card: Card, enemies: list[Card]) -> list[Card]:
        alive = [c for c in enemies if c.health > 0]
        if not alive:
            return []
        max_dist = max(abs(c.board_x - card.board_x) + abs(c.board_y - card.board_y) for c in alive)
        return [c for c in alive if abs(c.board_x - card.board_x) + abs(c.board_y - card.board_y) == max_dist]

    def _render_highlight_tile(self, color: tuple[int, int, int], board_x: int, board_y: int) -> None:
        x, y = self._board_to_pixel(board_x, board_y)
        surface = pygame.Surface((self.game_screen.block_size, self.game_screen.block_size))
        surface.fill(color)
        surface.set_alpha(60)
        self.game_screen.surface.blit(surface, (x, y))