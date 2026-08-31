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

"""Every relic you carry, with what it does spelled out.

Nothing here can overlap: each relic is measured before it is drawn.  Its
text is wrapped against the real pixel width of the column, the block's
height is the sum of the lines it actually needs, and blocks are packed one
after another down a column - so a long effect pushes the next relic down
instead of landing on top of it.  When the columns are full the rest go on
the next page.
"""

from dataclasses import dataclass
from typing import Sequence

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from utils.controls import key_pressed

from rendering import style
from tower import language, ui_common
from tower.content import RELICS

COLUMNS: int = 2
TIER_ORDER: tuple[str, ...] = ("special", "power", "rare", "common", "curse")


def _sort_key(relic_id: str) -> tuple[int, str]:
    tier = RELICS.get(relic_id, {}).get("tier", "common")
    rank = TIER_ORDER.index(tier) if tier in TIER_ORDER else len(TIER_ORDER)
    return rank, ui_common.relic_label(relic_id)


@dataclass
class _Block:
    relic_id: str
    x: float
    y: float
    heading: str
    lines: list[str]


class _Layout:
    """Where every relic goes, worked out once from the real font metrics."""

    def __init__(self, game_screen: GameScreen, relics: Sequence[str]):
        bs = game_screen.block_size
        # measured with the face they will be drawn in, so Chinese lines are
        # sized against the Chinese font rather than the latin one
        self.name_font = language.font(game_screen, "mid_text_font")
        self.text_font = language.font(game_screen, "text_font")

        self.top = ui_common.content_top(game_screen)
        self.bottom = game_screen.display_height - bs * 1.15
        self.margin = bs * 0.35
        gap = bs * 0.5
        usable = game_screen.display_width - self.margin * 2
        self.column_width = (usable - gap * (COLUMNS - 1)) / COLUMNS
        self.column_x = [self.margin + i * (self.column_width + gap)
                         for i in range(COLUMNS)]

        self.name_step = bs * 0.30
        self.line_step = bs * 0.24
        self.block_gap = bs * 0.12

        self.pages: list[list[_Block]] = []
        self._build(sorted(relics, key=_sort_key))

    def _measure(self, relic_id: str) -> tuple[str, list[str], float]:
        tier = ui_common.tier_label(RELICS.get(relic_id, {}).get("tier", "common"))
        heading = f"{ui_common.relic_label(relic_id)}  -  {tier}"
        lines = ui_common.wrap_to_width(ui_common.relic_text(relic_id),
                                        self.text_font, self.column_width)
        height = self.name_step + self.line_step * len(lines) + self.block_gap
        return heading, lines, height

    def _build(self, relics: Sequence[str]) -> None:
        page: list[_Block] = []
        column = 0
        y = self.top

        for relic_id in relics:
            heading, lines, height = self._measure(relic_id)
            if y + height > self.bottom and page:
                column += 1
                y = self.top
                if column >= COLUMNS:
                    self.pages.append(page)
                    page, column = [], 0
            page.append(_Block(relic_id, self.column_x[column], y, heading, lines))
            y += height

        if page or not self.pages:
            self.pages.append(page)

    def page_count(self) -> int:
        return max(1, len(self.pages))


def render(game_screen: GameScreen, run: dict, relics: list, layout: "_Layout",
           page: int, back, prev_btn, next_btn) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    paged = layout.page_count() > 1

    ui_common.draw_run_bar(game_screen, run)

    draw_text(f"Relics  ({len(relics)})", game_screen.title_text_font,
              style.INK, layout.margin, ui_common.title_y(game_screen),
              game_screen.surface)

    if not relics:
        draw_text("nothing yet - beat an elite or crack open a chest",
                  game_screen.mid_text_font, ui_common.DIM,
                  layout.margin, layout.top, game_screen.surface)
    else:
        for block in layout.pages[page]:
            draw_text(block.heading, layout.name_font,
                      ui_common.relic_color(block.relic_id),
                      block.x, block.y, game_screen.surface)
            line_y = block.y + layout.name_step
            for line in block.lines:
                draw_text(line, layout.text_font, ui_common.DIM,
                          block.x + bs * 0.14, line_y, game_screen.surface)
                line_y += layout.line_step

    if paged:
        label = f"page {page + 1} / {layout.page_count()}"
        draw_text(label, game_screen.text_font, WHITE,
                  cx - game_screen.text_font.size(label)[0] / 2,
                  game_screen.display_height - bs * 1.12, game_screen.surface)
        prev_btn.update(game_screen)
        next_btn.update(game_screen)

    back.update(game_screen)


def main(game_screen: GameScreen, run: dict) -> None:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2

    relics = list(run.get("relics", []))
    layout = _Layout(game_screen, relics)
    page = 0

    back = ui_common.back_button(game_screen, "back")
    box_width = ui_common.box_width(game_screen)
    prev_btn = Button(bs * 1.4, bs * 0.55, cx - bs * 1.7,
                      game_screen.display_height - bs * 0.82,
                      box_width=box_width, font=game_screen.text_font, text="< prev")
    next_btn = Button(bs * 1.4, bs * 0.55, cx + bs * 0.3,
                      game_screen.display_height - bs * 0.82,
                      box_width=box_width, font=game_screen.text_font, text="next >")

    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        paged = layout.page_count() > 1

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key in (pygame.K_ESCAPE, pygame.K_r):
                    running = False
                if paged and key in (pygame.K_a, pygame.K_LEFT):
                    page = (page - 1) % layout.page_count()
                if paged and key in (pygame.K_d, pygame.K_RIGHT):
                    page = (page + 1) % layout.page_count()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.touch(mouse_x, mouse_y):
                    running = False
                elif paged and prev_btn.touch(mouse_x, mouse_y):
                    page = (page - 1) % layout.page_count()
                elif paged and next_btn.touch(mouse_x, mouse_y):
                    page = (page + 1) % layout.page_count()
            if event.type == pygame.QUIT:
                raise QuitGame

        render(game_screen, run, relics, layout, page,
               back, prev_btn, next_btn)
        pygame.display.update()
        clock.tick(60)
