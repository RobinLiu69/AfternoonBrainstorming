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
from shared.setting import WHITE, BLUE, RED
from shared import card_code
from core.game_screen import GameScreen, draw_text
from rendering import style, hud_layout
from core.UI import ScoreDisplay, AttackCountDisplay
from core.card_hint import HintBox, draw_card_glyph, get_stat_prefix
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
        self._hint_box = HintBox(
            width=int(game_screen.block_size*3),
            height=int(game_screen.block_size)
        )
    def render_score(self, local_controller: str, controller: str, game_state: GameState) -> None:
        self._score_display.display(local_controller, controller, game_state, self.game_screen)

    TURN_GAP = 0.28

    def _turn_bounds(self, controller: str) -> tuple[float, float]:
        gs = self.game_screen
        width = gs.big_text_font.size(f"Turn: {controller}")[0]
        left = gs.display_width / 2 - width / 2
        return left, left + width

    def render_controller_label(self, controller: str) -> None:
        gs = self.game_screen
        left, _right = self._turn_bounds(controller)
        draw_text(f"Turn: {controller}", gs.big_text_font, WHITE, left,
                  gs.display_height / 2 - gs.block_size * 2.1, gs.surface)

    def render_identity_label(self, local_controller: str) -> None:
        style.identity_label(self.game_screen, local_controller)

    def render_player_panels(self, game_state: GameState, controller: str) -> None:
        for player in (game_state.player1, game_state.player2):
            self._render_panel(player, game_state, controller)

    def _render_panel(self, player: "Player", game_state: GameState,
                      controller: str) -> None:
        gs = self.game_screen
        bs = gs.block_size
        seat = player.name
        panel = hud_layout.panel_rect(gs, seat)
        style.section(gs, f"PLAYER {seat[-1]}", panel.x, panel.y, panel.width,
                      panel.height, player.time_display,
                      style.HEADER_ACTIVE if seat == controller else None)

        left = hud_layout.content_left(gs, seat)
        width = hud_layout.content_width(gs, seat)
        line = gs.text_font.get_linesize()
        top = hud_layout.stats_top(gs, seat)

        meter = self._p1_attack_display if seat == "player1" else self._p2_attack_display
        style.muted_text(gs, "attacks", left, top, gs.text_font)
        meter.display(game_state.number_of_attacks[seat], gs,
                      left + bs * 0.66, top + (line - meter.height) / 2)

        self._stat_row(left, top + line, width, "luck",
                       f"{game_state.players_luck[seat]}%",
                       "coins", str(game_state.players_coin[seat]))
        tokens = game_state.players_token[seat]
        totems = game_state.players_totem[seat]
        if tokens or totems:
            self._stat_row(left, top + line * 2, width, "tokens", str(tokens),
                           "totems" if totems else "", str(totems))

        label_y = hud_layout.hand_label_top(gs, seat)
        draw_text("HAND", gs.mid_text_font, style.INK, left, label_y, gs.surface)
        total = str(len(player.hand))
        draw_text(total, gs.mid_text_font, style.INK_MUTED,
                  left + width - gs.mid_text_font.size(total)[0], label_y, gs.surface)
        self._render_hand_rows(player)

        foot = hud_layout.footer_top(gs, seat)
        self._stat_row(left, foot, width, "draw", str(len(player.draw_pile)),
                       "discard", str(len(player.discard_pile)))
        self._stat_row(left, foot + line, width, "on board",
                       str(len(player.on_board)), "", "")

    def _stat_row(self, x: float, y: float, width: float, label: str, value: str,
                  label_b: str, value_b: str) -> None:
        gs = self.game_screen
        font = gs.text_font
        style.muted_text(gs, label, x, y, font)
        draw_text(value, font, style.INK, x + gs.block_size * 0.66, y, gs.surface)
        if not label_b:
            return
        half = x + width * 0.50
        style.muted_text(gs, label_b, half, y, font)
        draw_text(value_b, font, style.INK, half + gs.block_size * 0.72, y, gs.surface)

    def _render_hand_rows(self, player: "Player") -> None:
        gs = self.game_screen
        bs = gs.block_size
        seat = player.name
        line = gs.text_font.get_linesize()
        shown = hud_layout.shown_rows(gs, seat, len(player.hand))

        for i in range(shown):
            code = player.hand[i]
            rect = hud_layout.row_rect(gs, seat, i)
            if i == player.selected_card_index:
                fill = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                fill.fill(style.CONTROL_FILL)
                gs.surface.blit(fill, rect.topleft)
                pygame.draw.rect(gs.surface, style.INK, rect, style.edge_width(gs))

            glyph = bs * hud_layout.GLYPH
            draw_card_glyph(gs, gs.surface, card_code.plain_code(code),
                            rect.x + bs * 0.06, rect.y + (rect.height - glyph) / 2, glyph)
            text_y = rect.y + (rect.height - line) / 2
            draw_text(card_code.base_code(code), gs.text_font, style.INK,
                      rect.x + bs * 0.44, text_y, gs.surface)
            stats = get_stat_prefix(code)
            if stats:
                draw_text(stats, gs.text_font, style.INK_MUTED,
                          rect.right - gs.text_font.size(stats)[0] - bs * 0.08,
                          text_y, gs.surface)

        hidden = len(player.hand) - shown
        if hidden > 0:
            rect = hud_layout.row_rect(gs, seat, shown)
            style.muted_text(gs, f"+{hidden} more", rect.x,
                             rect.y + (rect.height - line) / 2, gs.text_font)

    def render_hint(self, mouse_x: int, mouse_y: int, card_or_name: "Card | str") -> None:
        self._hint_box.update(mouse_x, mouse_y, card_or_name, self.game_screen)

    def render_spectator_count(self, game_state: GameState) -> None:
        style.spectator_count(self.game_screen,
                              getattr(game_state, "net_spectator_count", 0))

    def render_awaiting_server(self, game_state: GameState) -> None:
        style.awaiting_server(self.game_screen,
                              getattr(game_state, "net_awaiting_ack", False))

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
        pad = bs * style.PANEL_PAD
        line_h = font.get_linesize()
        width = max(font.size(line)[0] for line in lines) + pad * 2
        height = bs * style.HEADER_HEIGHT + line_h * len(lines) + pad * 1.6
        x = gs.display_width / 2 - width / 2
        y = gs.display_height / 2 - height / 2

        style.modal_section(gs, "NET", x, y, width, height)
        top = y + bs * style.HEADER_HEIGHT + pad * 0.7
        for i, line in enumerate(lines):
            draw_text(line, font, style.INK, x + pad, top + i * line_h, gs.surface)

    def render_spectator_decks(self, game_state: GameState, local_controller: str) -> None:
        is_god = local_controller == "god"
        for player in (game_state.player1, game_state.player2):
            total = len(player.deck)
            if is_god:
                body = sorted(c for c in player.draw_pile if c != "?")
                title = f"DRAW PILE {len(player.draw_pile)}"
            else:
                known = sorted(player.revealed_deck)
                body = list(known)
                unknown = max(0, total - len(known))
                if unknown:
                    body.append(f"+ {unknown} unknown")
                title = f"DECK {len(known)}/{total}"
            self._render_deck_block(player, title, body or ["(empty)"])

    def _render_deck_block(self, player: "Player", title: str, body: list[str]) -> None:
        gs = self.game_screen
        seat = player.name
        area = hud_layout.hand_area(gs, seat)
        line_h = gs.text_font.get_linesize()
        label_h = gs.mid_text_font.get_linesize()
        pad = gs.block_size * hud_layout.PAD

        rows = hud_layout.shown_rows(gs, seat, len(player.hand))
        if len(player.hand) > rows:
            rows += 1
        top = area.y + hud_layout.row_height(gs) * rows + pad
        room = area.bottom - top - label_h
        fits = max(0, int(room // line_h))
        if fits <= 0:
            return

        pygame.draw.line(gs.surface, style.DIVIDER, (area.x, top - pad * 0.5),
                         (area.right, top - pad * 0.5), style.edge_width(gs))
        draw_text(title, gs.mid_text_font, style.INK, area.x, top, gs.surface)
        shown = body if len(body) <= fits else body[:max(0, fits - 1)]
        for i, line in enumerate(shown):
            draw_text(line, gs.text_font, style.INK_MUTED, area.x,
                      top + label_h + i * line_h, gs.surface)
        hidden = len(body) - len(shown)
        if hidden > 0:
            draw_text(f"+{hidden} more", gs.text_font, style.INK_DISABLED, area.x,
                      top + label_h + len(shown) * line_h, gs.surface)
