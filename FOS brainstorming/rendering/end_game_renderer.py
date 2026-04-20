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

from core.setting import BLACK, WHITE
from core.game_state import GameState
from core.game_screen import GameScreen, draw_text, KEYS_TO_CHECK, KETYS_TO_DISPLAY
from screens.end_game.data_prep import set_all_invisible, init_datas, making_image, display_chart


def display_raw_data(display_player1_data: list[list[int]], display_player2_data: list[list[int]],
                     display_player1_name: list[str], display_player2_name: list[str], game_screen: GameScreen) -> None:

    for i in range(len(KEYS_TO_CHECK)):
        draw_text(KETYS_TO_DISPLAY[i], game_screen.mid_text_font, WHITE,
                  game_screen.display_width/2 + game_screen.block_size*(-3.3+0.75*i),
                  game_screen.display_height/2 + game_screen.block_size*(-2.25), game_screen.surface)
    
    draw_text("Player1:", game_screen.mid_text_font, WHITE,
              game_screen.display_width/2 + game_screen.block_size*(-4.7),
              game_screen.display_height/2 + game_screen.block_size*(-2.1+0.2*len(display_player1_data)/2), game_screen.surface)
    
    for i in range(len(display_player1_data)):
        for j in range(len(display_player1_data[i])):
            draw_text(str(display_player1_data[i][j]), game_screen.mid_text_font, WHITE,
                      game_screen.display_width/2 + game_screen.block_size*(-3.2+0.75*j),
                      game_screen.display_height/2 + game_screen.block_size*(-2+0.2*i), game_screen.surface)
    
        draw_text(display_player1_name[i], game_screen.mid_text_font, WHITE,
                  game_screen.display_width/2 - game_screen.block_size*4,
                  game_screen.display_height/2 + game_screen.block_size*(-2+0.2*i), game_screen.surface)
    
    draw_text("Player2:", game_screen.mid_text_font, WHITE,
              game_screen.display_width/2 + game_screen.block_size*(-4.7),
              game_screen.display_height/2 + game_screen.block_size*(0.15+0.2*len(display_player2_data)/2), game_screen.surface)
    
    for i in range(len(display_player2_data)):
        for j in range(len(display_player2_data[i])):
            draw_text(str(display_player2_data[i][j]), game_screen.mid_text_font, WHITE,
                      game_screen.display_width/2 + game_screen.block_size*(-3.3+0.75*j), 
                      game_screen.display_height/2 + game_screen.block_size*(0.25+0.2*i), game_screen.surface)
    
        draw_text(display_player2_name[i], game_screen.mid_text_font, WHITE,
                  game_screen.display_width/2 - game_screen.block_size*4,
                  game_screen.display_height/2 + game_screen.block_size*(0.25+0.2*i), game_screen.surface)


def display_end_game_data(winner: str, game_state: GameState, game_screen: GameScreen):
    draw_text(f"Winner: {winner.capitalize()}!!", game_screen.title_text_font,
              WHITE, game_screen.display_width/2 - game_screen.block_size*1.5,
              game_screen.display_height/2 - game_screen.block_size*2, game_screen.surface)
    draw_text(f"Total Turns: {len(game_state.game_statistics.score_history)}",
              game_screen.big_text_font, WHITE, game_screen.display_width/2 - game_screen.block_size*3.75/1.1,
              game_screen.display_height/2 - game_screen.block_size*0.4, game_screen.surface)
    draw_text("Player1 Timer: "+game_state.player_timer["player1"]+",   Player2 Timer: "+game_state.player_timer["player2"],
              game_screen.text_font, WHITE, game_screen.display_width/2 - game_screen.block_size*3.75/1.1,
              game_screen.display_height/2 - game_screen.block_size*0.2, game_screen.surface)


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

    def _render_end_game_data(self, winner: str) -> None:
        gs = self.game_screen
        draw_text(f"Winner: {winner.capitalize()}!!",
                  gs.title_text_font, WHITE,
                  gs.display_width/2 - gs.block_size*1.5,
                  gs.display_height/2 - gs.block_size*2, gs.surface)
        draw_text(f"Total Turns: {len(self.game_state.game_statistics.score_history)}",
                  gs.big_text_font, WHITE,
                  gs.display_width/2 - gs.block_size*3.75/1.1,
                  gs.display_height/2 - gs.block_size*0.4, gs.surface)
        draw_text("Player1 Timer: " + self.game_state.player_timer["player1"] +
                  ",   Player2 Timer: " + self.game_state.player_timer["player2"],
                  gs.text_font, WHITE,
                  gs.display_width/2 - gs.block_size*3.75/1.1,
                  gs.display_height/2 - gs.block_size*0.2, gs.surface)

    def _render_raw_data(self) -> None:
        gs = self.game_screen
        p1_data, p2_data = self._display_p1_data, self._display_p2_data
        p1_name, p2_name = self._display_p1_name, self._display_p2_name

        for i in range(len(KEYS_TO_CHECK)):
            draw_text(KETYS_TO_DISPLAY[i], gs.mid_text_font, WHITE,
                      gs.display_width/2 + gs.block_size*(-3.3 + 0.75*i),
                      gs.display_height/2 + gs.block_size*(-2.25), gs.surface)

        draw_text("Player1:", gs.mid_text_font, WHITE,
                  gs.display_width/2 + gs.block_size*(-4.7),
                  gs.display_height/2 + gs.block_size*(-2.1 + 0.2*len(p1_data)/2), gs.surface)
        for i in range(len(p1_data)):
            for j in range(len(p1_data[i])):
                draw_text(str(p1_data[i][j]), gs.mid_text_font, WHITE,
                          gs.display_width/2 + gs.block_size*(-3.2 + 0.75*j),
                          gs.display_height/2 + gs.block_size*(-2 + 0.2*i), gs.surface)
            draw_text(p1_name[i], gs.mid_text_font, WHITE,
                      gs.display_width/2 - gs.block_size*4,
                      gs.display_height/2 + gs.block_size*(-2 + 0.2*i), gs.surface)

        draw_text("Player2:", gs.mid_text_font, WHITE,
                  gs.display_width/2 + gs.block_size*(-4.7),
                  gs.display_height/2 + gs.block_size*(0.15 + 0.2*len(p2_data)/2), gs.surface)
        for i in range(len(p2_data)):
            for j in range(len(p2_data[i])):
                draw_text(str(p2_data[i][j]), gs.mid_text_font, WHITE,
                          gs.display_width/2 + gs.block_size*(-3.3 + 0.75*j),
                          gs.display_height/2 + gs.block_size*(0.25 + 0.2*i), gs.surface)
            draw_text(p2_name[i], gs.mid_text_font, WHITE,
                      gs.display_width/2 - gs.block_size*4,
                      gs.display_height/2 + gs.block_size*(0.25 + 0.2*i), gs.surface)

    def _render_player_title(self, title: str) -> None:
        gs = self.game_screen
        draw_text(title, gs.title_text_font, WHITE,
                  gs.display_width/2 - gs.block_size*3.5,
                  gs.display_height/2 - gs.block_size*2.5, gs.surface)