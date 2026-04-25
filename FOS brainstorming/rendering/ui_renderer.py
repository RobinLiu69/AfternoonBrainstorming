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
from typing import TYPE_CHECKING

from core.game_state import GameState
from shared.setting import WHITE, GREEN, DARKGREEN, CYAN, BLUE, RED
from core.game_screen import GameScreen, draw_text
from core.UI import ScoreDisplay, AttackCountDisplay, TokenDisplay, HighLightBox
from core.card_hint import HintBox
from cards.base import Card


if TYPE_CHECKING:
    from core.player import Player


_PLAYER_OFFSETS: dict[str, dict[str, float]] = {
    "player1": {
        "clock": 1.25,
        "deck_info": 2.0,
        "totem": 4.0,
        "luck": 2.0,
        "coin": 4.4,
    },
    "player2": {
        "clock": -0.7,
        "deck_info": -0.7,
        "totem": -3.25,
        "luck": -1.3,
        "coin": -3.75,
    },
}


class UIRenderer:
    def __init__(self, game_screen: GameScreen):
        self.game_screen = game_screen

        self._score_display = ScoreDisplay(
            width=int(game_screen.block_size*0.15),
            height=int(game_screen.block_size*0.15)
        )
        self._p1_attack_display = AttackCountDisplay(
            player_name="player1",
            width=int(game_screen.block_size*0.1),
            height=int(game_screen.block_size*0.1)
        )
        self._p2_attack_display = AttackCountDisplay(
            player_name="player2",
            width=int(game_screen.block_size*0.1),
            height=int(game_screen.block_size*0.1)
        )
        self._p1_token_display = TokenDisplay(
            player_name="player1",
            radius=int(game_screen.block_size*0.1)
        )
        self._p2_token_display = TokenDisplay(
            player_name="player2",
            radius=int(game_screen.block_size*0.1)
        )
        self._hint_box = HintBox(
            width=int(game_screen.block_size*3),
            height=int(game_screen.block_size)
        )
        self._highlights: dict[str, HighLightBox] = {
            name: HighLightBox(
                x=(game_screen.display_width/2 - game_screen.block_size*3.3
                   if name == "player1"
                   else game_screen.display_width/2 + game_screen.block_size*2.025),
                y=0,
                box_color=BLUE if name == "player1" else RED,
                box_height=int(game_screen.block_size/3),
                box_width=int(game_screen.block_size),
                line_width=int(game_screen.block_size//50),
            )
            for name in ("player1", "player2")
        }

    def render_score(self, local_controller: str, controller: str, game_state: GameState) -> None:
        self._score_display.display(local_controller, controller, game_state, self.game_screen)

    def render_controller_label(self, controller: str) -> None:
        draw_text(
            f"Turn: {controller}",
            self.game_screen.big_text_font, WHITE,
            self.game_screen.display_width/2 - self.game_screen.block_size*0.6,
            self.game_screen.display_height/2 - self.game_screen.block_size*2.1,
            self.game_screen.surface
        )

    def render_hands(self, game_state: GameState) -> None:
        self._render_one_hand(game_state.player1, game_state)
        self._render_one_hand(game_state.player2, game_state)

    def _render_one_hand(self, player: Player, game_state: GameState) -> None:
        match player.name:
            case "player1":
                x = self.game_screen.display_width/2 - self.game_screen.block_size*3.2
            case "player2":
                x = self.game_screen.display_width/2 + self.game_screen.block_size*2.1
            case _:
                x = 0

        for i, card_name in enumerate(player.hand):
            draw_text(
                f"{player.short_name}hand {i + 1}: {card_name}",
                self.game_screen.text_font, WHITE, x,
                self.game_screen.display_height / 14 * (i+1),
                self.game_screen.surface
            )

        highlight = self._highlights.get(player.name)
        if highlight is not None:
            if not (player.selected_card_index == -1 or len(player.hand) <= player.selected_card_index):
                highlight.visable = True
                highlight.update(
                    player.selected_card_index,
                    len(player.hand[player.selected_card_index])
                        if 0 <= player.selected_card_index < len(player.hand) else 0,
                    self.game_screen
                )

    def render_attack_counts(self, game_state: GameState) -> None:
        self._p1_attack_display.display(
            game_state.number_of_attacks["player1"], self.game_screen
        )
        self._p2_attack_display.display(
            game_state.number_of_attacks["player2"], self.game_screen
        )

    def render_tokens(self, game_state: GameState) -> None:
        self._p1_token_display.display(
            game_state.players_token["player1"], self.game_screen
        )
        self._p2_token_display.display(
            game_state.players_token["player2"], self.game_screen
        )

    def render_luck(self, game_state: GameState) -> None:
        for player in (game_state.player1, game_state.player2):
            draw_text(
                f"{player.short_name}Luck: {game_state.players_luck[player.name]}%",
                self.game_screen.text_font, GREEN,
                self.game_screen.display_width/2 - self.game_screen.block_size*_PLAYER_OFFSETS[player.name]["luck"],
                self.game_screen.block_size * 1.1,
                self.game_screen.surface
            )

    def render_totems(self, game_state: GameState) -> None:
        for player in (game_state.player1, game_state.player2):
            if game_state.players_totem[player.name]:
                draw_text(
                    f"totems: {game_state.players_totem[player.name]}",
                    self.game_screen.text_font, DARKGREEN,
                    self.game_screen.display_width/2 - self.game_screen.block_size*_PLAYER_OFFSETS[player.name]["totem"],
                    self.game_screen.display_height - self.game_screen.block_size*0.4,
                    self.game_screen.surface
                )

    def render_coins(self, game_state: GameState) -> None:
        for player in (game_state.player1, game_state.player2):
            if game_state.players_coin[player.name]:
                draw_text(
                    f"coins: {game_state.players_coin[player.name]}",
                    self.game_screen.text_font, CYAN,
                    self.game_screen.display_width/2 - self.game_screen.block_size*_PLAYER_OFFSETS[player.name]["coin"],
                    self.game_screen.display_height/2 + self.game_screen.block_size*1.3,
                    self.game_screen.surface
                )

    def render_deck_info(self, game_state: GameState) -> None:
        for player in (game_state.player1, game_state.player2):
            draw_text(
                f"{player.short_name}DrawDeck: {len(player.draw_pile)} cards",
                self.game_screen.text_font, WHITE,
                self.game_screen.display_width/2 - self.game_screen.block_size*_PLAYER_OFFSETS[player.name]["deck_info"],
                self.game_screen.display_height - self.game_screen.block_size*0.5,
                self.game_screen.surface
            )
            draw_text(
                f"{player.short_name}DiscardPile: {len(player.discard_pile)} cards",
                self.game_screen.text_font, WHITE,
                self.game_screen.display_width/2 - self.game_screen.block_size*_PLAYER_OFFSETS[player.name]["deck_info"],
                self.game_screen.display_height - self.game_screen.block_size*0.4,
                self.game_screen.surface
            )

    def render_timers(self, game_state: GameState) -> None:
        for player in (game_state.player1, game_state.player2):
            draw_text(
                f"{player.short_name}Clock: {player.time_minutes_and_seconds}",
                self.game_screen.text_font, WHITE,
                self.game_screen.display_width/2 - (self.game_screen.display_width/6)*_PLAYER_OFFSETS[player.name]["clock"],
                self.game_screen.display_height / 6.4,
                self.game_screen.surface
            )

    def render_hint(self, mouse_x: int, mouse_y: int, card_or_name: "Card | str") -> None:
        self._hint_box.update(mouse_x, mouse_y, card_or_name, self.game_screen)