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

import pygame

from shared.setting import BLACK, WHITE
from core.game_state import GameState
from rendering import style
from core.game_screen import GameScreen, draw_text, KEYS_TO_CHECK, KEYS_TO_DISPLAY
from screens.end_game.data_prep import set_all_invisible, init_datas, making_image, display_chart


class EndGameRenderer:
    def __init__(self, game_screen: GameScreen, game_state: GameState) -> None:
        self.game_screen = game_screen
        self.game_state = game_state

        (self._p1_datas, self._p2_datas,
         self._p1_prof, self._p2_prof,
         self._display_p1_data, self._display_p2_data,
         self._display_p1_name, self._display_p2_name) = init_datas(game_state.game_statistics)

        self._draw_loading(0, 1, "Preparing...")

        plot_path, pie_paths, bar_paths = making_image(
            self._p1_datas, self._p2_datas,
            self._p1_prof, self._p2_prof,
            game_state.game_statistics,
            on_progress=self._draw_loading,
        )
        self._score_chart, self._charts = display_chart(pie_paths, bar_paths, plot_path, game_screen)
        self._score_chart.visible = True

    def _draw_loading(self, done: int, total: int, label: str) -> None:
        pygame.event.pump()

        gs = self.game_screen
        gs.surface.fill(BLACK)

        cx = gs.display_width / 2
        cy = gs.display_height / 2

        # draw_text("Loading...", gs.big_text_font, WHITE,
        #           cx - gs.block_size * 0.6,
        #           cy - gs.block_size * 1.0, gs.surface)

        bar_w = gs.block_size * 5
        bar_h = gs.block_size * 0.3
        bar_x = cx - bar_w / 2
        bar_y = cy - bar_h
        pygame.draw.rect(gs.surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)

        ratio = max(0.0, min(1.0, done / total if total else 1.0))
        inner_pad = 3
        fill_w = max(0, (bar_w - inner_pad * 2) * ratio)
        pygame.draw.rect(
            gs.surface, WHITE,
            (bar_x + inner_pad, bar_y + inner_pad, fill_w, bar_h - inner_pad * 2),
        )

        pct = int(ratio * 100)
        draw_text(f"{pct}%  ({done}/{total})", gs.text_font, WHITE,
                  cx - gs.block_size * 0.3,
                  bar_y + bar_h + gs.block_size * 0.15, gs.surface)
        draw_text(label, gs.text_font, WHITE,
                  cx - gs.block_size * 2.5,
                  bar_y + bar_h + gs.block_size * 0.5, gs.surface)

        pygame.display.update()

    def set_display_state(self, new_state: str) -> None:
        set_all_invisible(self._score_chart, self._charts)
        match new_state:
            case "mid":
                self._score_chart.visible = True
            case "raw":
                pass
            case "player1" | "player2":
                for chart in self._charts[new_state]["pie"]:
                    chart.visible = True
                for chart in self._charts[new_state]["bar"]:
                    chart.visible = True

    def render_frame(self, winner: str, display_state: str) -> None:
        self.game_screen.render()

        for player_charts in self._charts.values():
            for value in player_charts.values():
                for chart in value:
                    chart.display(self.game_screen)

        match display_state:
            case "raw":
                self._render_raw_data()
            case "mid":
                self._render_end_game_data(winner)
            case "player1":
                self._render_player_title("Player1")
            case "player2":
                self._render_player_title("Player2")

        self._score_chart.display(self.game_screen)
        self._render_nav(display_state)

    def _centred(self, text: str, font, colour, y: float) -> None:
        gs = self.game_screen
        draw_text(text, font, colour,
                  gs.display_width / 2 - font.size(text)[0] / 2, y, gs.surface)

    def _render_end_game_data(self, winner: str) -> None:
        gs = self.game_screen
        bs = gs.block_size

        turns = len(self.game_state.game_statistics.score_history)
        summary = (f"{turns} turns"
                   f"    P1 {self.game_state.player1.time_display}"
                   f"    P2 {self.game_state.player2.time_display}")

        self._centred(f"Winner: {winner.capitalize()}!!", gs.title_text_font,
                      style.INK, bs * 0.35)
        self._centred(summary, gs.mid_text_font, style.INK_MUTED, bs * 1.15)

    def _render_nav(self, display_state: str) -> None:
        gs = self.game_screen
        keys = [("TAB", "raw data", display_state == "raw"),
                ("1", "player1", display_state == "player1"),
                ("2", "player2", display_state == "player2"),
                ("ESC", "continue", False)]
        parts = [f"[{key}] {label}" for key, label, _on in keys]
        gap = gs.block_size * 0.35
        widths = [gs.text_font.size(part)[0] for part in parts]
        total = sum(widths) + gap * (len(parts) - 1)
        x = gs.display_width / 2 - total / 2
        y = gs.display_height - gs.block_size * 0.45
        for part, width, (_k, _l, active) in zip(parts, widths, keys):
            draw_text(part, gs.text_font,
                      style.INK if active else style.INK_DISABLED,
                      x, y, gs.surface)
            x += width + gap

    ROW_STEP = 0.22
    NAME_X = -4.55
    COL_X = -3.3
    COL_STEP = 0.75

    def _render_block(self, title: str, rows: list[list[int]], names: list[str],
                      top: float) -> float:
        gs = self.game_screen
        bs = gs.block_size
        cx = gs.display_width / 2
        left = cx + bs * self.NAME_X

        draw_text(title, gs.mid_text_font, style.INK, left, top, gs.surface)
        rule_y = top + bs * 0.22
        pygame.draw.line(gs.surface, style.DIVIDER[:3],
                         (left, rule_y), (cx + bs * 4.15, rule_y), 1)

        header_y = rule_y + bs * 0.08
        for i, label in enumerate(KEYS_TO_DISPLAY):
            draw_text(label, gs.text_font, style.INK_MUTED,
                      cx + bs * (self.COL_X + self.COL_STEP * i), header_y, gs.surface)

        row_y = header_y + bs * self.ROW_STEP
        for i, row in enumerate(rows):
            y = row_y + bs * self.ROW_STEP * i
            draw_text(names[i], gs.mid_text_font, style.INK, left, y, gs.surface)
            for j, value in enumerate(row):
                draw_text(str(value), gs.mid_text_font,
                          style.INK if value else style.INK_DISABLED,
                          cx + bs * (self.COL_X + self.COL_STEP * j), y, gs.surface)
        return row_y + bs * self.ROW_STEP * len(rows)

    def _render_raw_data(self) -> None:
        bs = self.game_screen.block_size
        cy = self.game_screen.display_height / 2
        bottom = self._render_block("PLAYER 1", self._display_p1_data,
                                    self._display_p1_name, cy - bs * 2.45)
        self._render_block("PLAYER 2", self._display_p2_data,
                           self._display_p2_name, bottom + bs * 0.30)

    def _render_player_title(self, title: str) -> None:
        self._centred(title, self.game_screen.title_text_font, style.INK,
                      self.game_screen.block_size * 0.35)