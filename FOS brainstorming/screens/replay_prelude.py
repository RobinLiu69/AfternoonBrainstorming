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

from shared.setting import WHITE, RED, VERSION, JOB_DICTIONARY, JOB_ORDER
from cards.factory import CardFactory
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.game_screen import GameScreen, cell_origin, draw_text, QuitGame
from core.lobby_state import MAX_BANS_PER_PLAYER
from rendering import style
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


def ruleset_bans(metadata: dict) -> list[str]:
    return list(metadata.get("bans", {}).get("judge", []))


def ruleset_ban_summary(metadata: dict) -> tuple[list[str], list[str]]:
    cards = ruleset_bans(metadata)
    tags = sorted(JOB_DICTIONARY["colors_dict"], key=len, reverse=True)
    jobs_by_tag: dict[str, set[str]] = {}
    loose: list[str] = []

    for card in cards:
        for tag in tags:
            job = card[:-len(tag)]
            if card.endswith(tag) and job in JOB_ORDER:
                jobs_by_tag.setdefault(tag, set()).add(job)
                break
        else:
            loose.append(card)

    factions: list[str] = []
    for tag, jobs in jobs_by_tag.items():
        if len(jobs) >= len(JOB_ORDER):
            factions.append(JOB_DICTIONARY["colors_dict"][tag])
        else:
            loose.extend(f"{job}{tag}" for job in sorted(jobs))
    return factions, loose


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


def version_notice(metadata: dict) -> tuple[str, tuple, bool]:
    recorded = metadata.get("version")
    if recorded is None:
        return "version unknown - older replay", style.INK_MUTED, False
    if recorded == VERSION:
        return f"recorded on {recorded}", style.INK_MUTED, False
    return f"recorded on {recorded} - running {VERSION}", style.INK, True


def _render_version(gs: GameScreen, metadata: dict, cx: float, y: float) -> None:
    line, color, mismatch = version_notice(metadata)
    font = gs.mid_text_font if mismatch else gs.text_font
    w = font.size(line)[0]
    draw_text(line, font, color, cx - w / 2, y, gs.surface)


PANEL_W = 7.4
PANEL_LEFT = 3.7
BAND_GAP = 0.20


def deck_layout(gs: GameScreen, metadata: dict) -> tuple[float, float, float]:
    bs = gs.block_size
    label_x = gs.display_width / 2 - bs * PANEL_LEFT
    name_w = max(gs.text_font.size(f"{_seat_label(metadata, s)}:")[0] for s in SEATS)
    deck_x = label_x + name_w + bs * 0.4
    max_cards = max((len(metadata.get(f"{s}_deck", [])) for s in SEATS), default=0)
    widest = max((gs.text_font.size(card)[0]
                  for s in SEATS for card in metadata.get(f"{s}_deck", [])), default=0)
    right_limit = label_x + bs * PANEL_W - bs * style.PANEL_PAD - widest
    step = min(bs * 0.62, (right_limit - deck_x) / max(1, max_cards - 1))
    return label_x, deck_x, max(0.0, step)


def _render_row(gs: GameScreen, label: str, cards: list[str],
                y: float, label_x: float, deck_x: float, step: float) -> None:
    draw_text(label, gs.text_font, WHITE, label_x, y, gs.surface)
    for i, card in enumerate(cards):
        draw_text(card, gs.text_font, WHITE, deck_x + i * step, y, gs.surface)


def render(game_screen: GameScreen, metadata: dict, card_renderer, board_renderer,
           board, cards, rows, settings_line, labels,
           label_x, deck_x, deck_step) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    style.title(game_screen, "REPLAY")

    left = cx - bs * PANEL_LEFT
    pad = bs * style.PANEL_PAD
    factions, loose = ruleset_ban_summary(metadata)

    board_rows = max(1, len(rows))
    _bx, board_top = cell_origin(game_screen, 0, 0)
    panel_top = board_top - bs * style.HEADER_HEIGHT - bs * BAND_GAP
    panel_height = (board_top + bs * board_rows + pad) - panel_top
    style.section(game_screen, "BANS", left - pad, panel_top,
                  bs * PANEL_W + pad * 2, panel_height)

    if rows:
        for cell in board.values():
            board_renderer.render(cell)
        _render_bans(game_screen, card_renderer, cards, rows)
        locked_x, locked_y, per_line = cx + bs * 2.25, cy - bs * 1.45, 3
    else:
        locked_x, locked_y, per_line = left, cy - bs * 1.45, 8

    if factions or loose:
        style.muted_text(game_screen, "ruleset locked", locked_x, locked_y,
                         game_screen.text_font)
        line_y = locked_y + bs * 0.26
        if factions:
            style.muted_text(game_screen, ", ".join(sorted(factions)),
                             locked_x, line_y, game_screen.text_font)
            line_y += bs * 0.26
        for i in range(0, len(loose), per_line):
            style.muted_text(game_screen, "  ".join(loose[i:i + per_line]),
                             locked_x, line_y, game_screen.text_font)
            line_y += bs * 0.26
    elif not rows:
        style.muted_text(game_screen, "no bans this match", left, locked_y,
                         game_screen.mid_text_font)

    deck_top = panel_top + panel_height + bs * 0.3
    style.section(game_screen, "DECKS", label_x - pad, deck_top,
                  bs * PANEL_W + pad * 2, bs * 1.35, right=settings_line)
    deck_y = deck_top + bs * style.HEADER_HEIGHT + pad
    for i, seat in enumerate(SEATS):
        _render_row(game_screen, labels[i], metadata.get(f"{seat}_deck", []),
                    deck_y + i * bs * 0.4, label_x, deck_x, deck_step)

    footer_y = game_screen.display_height - bs * 0.45
    style.muted_text(game_screen, "E/ENTER: watch replay    ESC: back",
                     bs * 0.2, footer_y, game_screen.text_font)

    line, colour, _mismatch = version_notice(metadata)
    line_w = game_screen.text_font.size(line)[0]
    draw_text(line, game_screen.text_font, colour,
              game_screen.display_width - line_w - bs * 0.2, footer_y,
              game_screen.surface)


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

    labels = [f"{_seat_label(metadata, seat)}:" for seat in SEATS]
    label_x, deck_x, deck_step = deck_layout(game_screen, metadata)

    while True:
        game_screen.render()
        render(game_screen, metadata, card_renderer, board_renderer, board, cards,
               rows, settings_line, labels, label_x, deck_x, deck_step)
        back_button.update(game_screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_e, pygame.K_RETURN):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.touch(*event.pos):
                    return False

        clock.tick(60)
