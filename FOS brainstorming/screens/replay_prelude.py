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

import pygame

from shared.setting import WHITE
from cards.factory import CardFactory
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.game_screen import GameScreen, cell_origin, draw_text
from core.lobby_state import MAX_BANS_PER_PLAYER
from rendering.board_renderer import BoardRenderer
from rendering.card_renderer import CardRenderer
from rendering.sprite_registry import SpriteRegistry
from screens.widgets import make_back_button

SEATS = ("player1", "player2")
UNLISTED_SETTINGS = frozenset({"file_auto_delete"})


def _seat_label(metadata: dict, seat: str) -> str:
    return metadata.get(f"{seat}_name") or seat


def _player_bans(metadata: dict) -> list[tuple[str, list[str]]]:
    bans: dict[str, list[str]] = metadata.get("bans", {})
    return [(banner, cards[:MAX_BANS_PER_PLAYER])
            for banner, cards in bans.items() if banner != "judge"]


def _settings_line(metadata: dict) -> str:
    parts = []
    for name, value in metadata.get("settings", {}).items():
        if name in UNLISTED_SETTINGS:
            continue
        if isinstance(value, bool):
            value = "yes" if value else "no"
        parts.append(f"{name.replace('_', ' ')}: {value}")
    return "   ".join(parts)


def _ban_cards(rows: list[tuple[str, list[str]]]) -> list:
    cards = []
    for row, (_banner, names) in enumerate(rows):
        for col, name in enumerate(names):
            try:
                cards.append(CardFactory.create(name, "display", col, row))
            except ValueError:
                pass
    return cards


def _render_bans(gs: GameScreen, card_renderer: CardRenderer, cards: list,
                 rows: list[tuple[str, list[str]]]) -> None:
    locked = SpriteRegistry.get_instance().get("locked")
    for card in cards:
        for render_object in card.get_render_data():
            card_renderer.render(render_object)
        if locked is not None:
            x, y = cell_origin(gs, card.board_x, card.board_y)
            gs.surface.blit(locked, (int(x), int(y)))

    for row, (banner, banned) in enumerate(rows):
        _x, y = cell_origin(gs, 0, row)
        draw_text(banner if banned else f"{banner} (none)",
                  gs.mid_text_font, WHITE,
                  gs.display_width / 2 - gs.block_size * 3.7,
                  y + gs.block_size * 0.3, gs.surface)


def _render_row(gs: GameScreen, label: str, cards: list[str], y: float) -> None:
    draw_text(label, gs.text_font, WHITE, gs.display_width / 16 * 2, y, gs.surface)
    for i, card in enumerate(cards):
        draw_text(card, gs.text_font, WHITE, gs.display_width / 16 * (i + 3), y, gs.surface)


def main(game_screen: GameScreen, metadata: dict) -> bool:
    card_renderer = CardRenderer(game_screen)
    board_renderer = BoardRenderer(game_screen)

    rows = _player_bans(metadata)
    board = initialize_board(game_screen, BoardConfig(MAX_BANS_PER_PLAYER, max(1, len(rows))))
    cards = _ban_cards(rows)
    settings_line = _settings_line(metadata)
    back_button = make_back_button(game_screen, text="back", corner="top_right")

    clock = pygame.time.Clock()
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    while True:
        game_screen.render()

        draw_text("REPLAY", game_screen.title_text_font, WHITE,
                  cx - bs, bs * 0.25, game_screen.surface)
        draw_text("bans", game_screen.text_font, WHITE,
                  cx - bs * 3.7, cy - bs * 2.1, game_screen.surface)

        if rows:
            for cell in board.values():
                board_renderer.render(cell)
            _render_bans(game_screen, card_renderer, cards, rows)
        else:
            draw_text("no bans this match", game_screen.mid_text_font, WHITE,
                      cx - bs * 3.7, cy - bs * 1.4, game_screen.surface)

        deck_y = cy + bs * 1.35
        draw_text(settings_line, game_screen.text_font, WHITE,
                  game_screen.display_width / 16 * 2, deck_y - bs * 0.45,
                  game_screen.surface)
        for i, seat in enumerate(SEATS):
            _render_row(game_screen, f"{_seat_label(metadata, seat)}:",
                        metadata.get(f"{seat}_deck", []), deck_y + i * bs * 0.4)

        draw_text("E/ENTER: watch replay    ESC: back", game_screen.mid_text_font, WHITE,
                  bs * 0.2, game_screen.display_height - bs * 0.45, game_screen.surface)
        back_button.update(game_screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_e, pygame.K_RETURN):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.touch(*event.pos):
                    return False

        clock.tick(60)
