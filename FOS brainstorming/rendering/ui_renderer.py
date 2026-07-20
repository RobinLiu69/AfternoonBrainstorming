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

import pygame

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

    def render_identity_label(self, local_controller: str) -> None:
        label_map = {
            "player1": "You: P1",
            "player2": "You: P2",
            "spectator": "Spectator",
            "god": "God View",
        }
        label = label_map.get(local_controller, local_controller)
        draw_text(
            label,
            self.game_screen.text_font, WHITE,
            self.game_screen.block_size * 2.0,
            self.game_screen.block_size * 0.25,
            self.game_screen.surface,
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
                f"{player.short_name}Clock: {player.time_display}",
                self.game_screen.text_font, WHITE,
                self.game_screen.display_width/2 - (self.game_screen.display_width/6)*_PLAYER_OFFSETS[player.name]["clock"],
                self.game_screen.display_height / 6.4,
                self.game_screen.surface
            )

    def render_hint(self, mouse_x: int, mouse_y: int, card_or_name: "Card | str") -> None:
        self._hint_box.update(mouse_x, mouse_y, card_or_name, self.game_screen)

    def render_spectator_count(self, game_state: GameState) -> None:
        count = getattr(game_state, "net_spectator_count", 0)
        if not count or count <= 0:
            return
        gs = self.game_screen
        text = f"spectators: {count}"
        width = gs.text_font.size(text)[0]
        draw_text(text, gs.text_font, WHITE,
                  gs.display_width - width - gs.block_size * 0.3,
                  gs.block_size * 0.2, gs.surface)

    def render_netinfo_overlay(self, local_controller: str, game_state: GameState) -> None:
        gs = self.game_screen
        bs = gs.block_size
        latencies = getattr(game_state, "net_latencies", {}) or {}
        count = getattr(game_state, "net_spectator_count", 0)

        my_ping = getattr(game_state, "net_my_ping", None)

        def fmt(seat: str) -> str:
            ms = latencies.get(seat)
            return f"{ms:.0f} ms" if ms is not None else "host"

        you_str = f"{my_ping:.0f} ms (to host)" if my_ping is not None else "local (host)"

        if local_controller in ("player1", "player2"):
            opp_seat = "player2" if local_controller == "player1" else "player1"
            lines = [f"you      : {you_str}", f"opponent : {fmt(opp_seat)}"]
        else:
            lines = [
                f"player1  : {fmt('player1')}",
                f"player2  : {fmt('player2')}",
                f"you      : {you_str}",
            ]
        lines.append(f"spectators: {count}")
        lines.append(f"turn: {game_state.turn_number}")

        font = gs.text_font
        pad = bs * 0.2
        line_h = font.get_linesize()
        width = max(font.size(line)[0] for line in lines) + pad * 2
        height = line_h * len(lines) + pad * 2
        x = gs.display_width - width - bs * 0.3
        y = bs * 0.6

        panel = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 190))
        pygame.draw.rect(panel, WHITE, panel.get_rect(), max(1, int(bs / 60)))
        gs.surface.blit(panel, (int(x), int(y)))
        for i, line in enumerate(lines):
            draw_text(line, font, WHITE, x + pad, y + pad + i * line_h, gs.surface)

    def render_spectator_decks(self, game_state: GameState, local_controller: str) -> None:
        gs = self.game_screen
        bs = gs.block_size
        font = gs.text_font
        title_font = gs.mid_text_font
        line_h = font.get_linesize()
        pad = bs * 0.15
        is_god = local_controller == "god"

        def deck_lines(player: Player) -> tuple[str, list[str]]:
            total = len(player.deck)
            if is_god:
                cards = sorted(c for c in player.draw_pile if c != "?")
                return f"deck ({len(player.draw_pile)} left)", (cards or ["(empty)"])
            known = sorted(player.revealed_deck)
            unknown = max(0, total - len(known))
            body = list(known)
            if unknown:
                body.append(f"+ {unknown} unknown")
            return f"deck (known {len(known)}/{total})", (body or ["(empty)"])

        def panel_width(title: str, body: list[str]) -> float:
            return max([title_font.size(title)[0]] + [font.size(line)[0] for line in body]) + pad * 2

        def draw_panel(title: str, body: list[str], x: float) -> None:
            width = panel_width(title, body)
            height = title_font.get_linesize() + line_h * len(body) + pad * 2
            y = gs.display_height / 2 - height / 2
            panel = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 200))
            pygame.draw.rect(panel, WHITE, panel.get_rect(), max(1, int(bs / 70)))
            gs.surface.blit(panel, (int(x), int(y)))
            draw_text(title, title_font, WHITE, x + pad, y + pad, gs.surface)
            ty = y + pad + title_font.get_linesize()
            for i, line in enumerate(body):
                draw_text(line, font, WHITE, x + pad, ty + i * line_h, gs.surface)

        p1_title, p1_body = deck_lines(game_state.player1)
        p2_title, p2_body = deck_lines(game_state.player2)
        draw_panel(f"P1 {p1_title}", p1_body, bs * 0.3)
        title2 = f"P2 {p2_title}"
        draw_panel(title2, p2_body, gs.display_width - panel_width(title2, p2_body) - bs * 0.3)