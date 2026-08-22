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

"""Shared colours and small drawing helpers for the tower screens."""

from __future__ import annotations

import textwrap

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from rendering import style
from core.UI import Button

from tower import language
from tower.content import ENEMY_LABELS, RELICS, ROOM_LABELS

# free text is wrapped to a fixed width so descriptions never overlap
# whatever is drawn beside or below them
DESC_WRAP: int = 40
RELIC_WRAP: int = 30
PANEL_WRAP: int = 52


def is_cjk(char: str) -> bool:
    return any(start <= ord(char) <= end for start, end in (
        (0x3000, 0x303F),    # punctuation
        (0x3400, 0x4DBF),    # ideographs extension A
        (0x4E00, 0x9FFF),    # ideographs
        (0xFF00, 0xFFEF),    # fullwidth forms
    ))


def has_cjk(text: str) -> bool:
    return any(is_cjk(char) for char in text)


def _chunks(text: str) -> list[str]:
    """Split into wrappable pieces.

    Latin text breaks on spaces.  Chinese has none, so it breaks between
    glyphs - but never *before* closing punctuation, which would strand a
    comma at the start of a line, and never inside a run of latin characters,
    so "25%" and "TANK" stay whole.  Spaces the author wrote are kept, riding
    along on the piece that follows them.
    """
    if not has_cjk(text):
        return text.split()

    trailing = "，。、；：）」』？！%"
    pieces: list[str] = []
    pending_space = False
    for char in text:
        if char.isspace():
            pending_space = True
            continue
        glue = pieces and (
            char in trailing
            or (not is_cjk(char) and not pending_space and not is_cjk(pieces[-1][-1]))
        )
        if glue:
            pieces[-1] += char
        else:
            pieces.append((" " if pending_space and pieces else "") + char)
        pending_space = False
    return pieces


def _join(pieces: list[str], spaced: bool) -> str:
    return (" ".join(pieces) if spaced else "".join(pieces)).strip()


def wrap(text: str, width: int = DESC_WRAP) -> list[str]:
    """Wrap to a column count.  A Chinese glyph counts as two."""
    if not text:
        return []
    if not has_cjk(text):
        return textwrap.wrap(text, width) or [text]

    def cost(chunk: str) -> int:
        return sum(2 if is_cjk(c) else 1 for c in chunk)

    lines: list[str] = []
    current: list[str] = []
    used = 0
    for piece in _chunks(text):
        size = cost(piece)
        if current and used + size > width:
            lines.append(_join(current, spaced=False))
            current, used = [], 0
        current.append(piece)
        used += size
    if current:
        lines.append(_join(current, spaced=False))
    return lines or [text]


def wrap_all(lines, width: int = DESC_WRAP) -> list[str]:
    out: list[str] = []
    for line in lines:
        out.extend(wrap(line, width))
    return out


def wrap_to_width(text: str, font, max_width: float) -> list[str]:
    """Wrap by measuring the font, so a line can never run past its column.

    Works for Chinese too: ``_chunks`` hands back single glyphs when there are
    no spaces to break on.  Measure with the face you will draw with - the
    latin font under-reports CJK and the line would overflow anyway.
    """
    if not text:
        return []
    spaced = not has_cjk(text)
    lines: list[str] = []
    current: list[str] = []
    for piece in _chunks(text):
        candidate = _join(current + [piece], spaced)
        if not current or font.size(candidate)[0] <= max_width:
            current.append(piece)
        else:
            lines.append(_join(current, spaced))
            current = [piece]
    if current:
        lines.append(_join(current, spaced))
    return lines


GOLD: tuple[int, int, int] = (255, 215, 0)
ORB: tuple[int, int, int] = (150, 210, 255)
RELIC: tuple[int, int, int] = (255, 215, 0)
POWER: tuple[int, int, int] = (255, 140, 220)
CURSE: tuple[int, int, int] = (255, 90, 90)
DIM: tuple[int, int, int] = (120, 120, 120)
DONE: tuple[int, int, int] = (90, 130, 90)
ENEMY: tuple[int, int, int] = (255, 150, 90)
HILITE: tuple[int, int, int] = (120, 255, 180)

TIER_COLORS: dict[str, tuple[int, int, int]] = {
    "common": WHITE,
    "rare": (120, 200, 255),
    "power": POWER,
    "special": (255, 235, 140),
    "curse": CURSE,
}


def relic_color(relic_id: str) -> tuple[int, int, int]:
    return TIER_COLORS.get(RELICS.get(relic_id, {}).get("tier", "common"), WHITE)


def tier_label(tier: str) -> str:
    if language.is_chinese():
        from tower.content_zh import TIERS_ZH
        return TIERS_ZH.get(tier, tier)
    return tier


def relic_label(relic_id: str) -> str:
    return language.relic_label(relic_id, RELICS.get(relic_id, {}).get("label", relic_id))


def relic_text(relic_id: str) -> str:
    return language.relic_text(relic_id, RELICS.get(relic_id, {}).get("text", ""))


def enemy_color(kind: str) -> tuple[int, int, int]:
    if kind == "boss":
        return CURSE
    if kind == "elite":
        return POWER
    return ENEMY


def room_label(kind: str) -> str:
    return language.room_label(kind, ROOM_LABELS.get(kind, kind))


def blessing_label(entry: dict) -> str:
    return language.blessing_label(entry["id"], entry["label"])


def blessing_text(entry: dict) -> str:
    return language.blessing_text(entry["id"], entry["text"])


def enemy_label(enemy: dict) -> str:
    return enemy.get("label", ENEMY_LABELS.get(enemy.get("kind", ""), "?"))


def auto_font(game_screen: GameScreen, text: str, size: str = "text_font"):
    """The face that can actually draw ``text``.

    Picked from the string itself rather than from the language setting, so
    anywhere a translated name might turn up renders correctly without every
    call site having to know whether its text was translated.  The latin face
    has no CJK glyphs and would draw blanks.
    """
    if has_cjk(text):
        return language.chinese_font(game_screen, size)
    return getattr(game_screen, size)


def draw_auto(game_screen: GameScreen, text: str, size: str, color,
              x: float, y: float) -> None:
    draw_text(text, auto_font(game_screen, text, size), color, x, y, game_screen.surface)


def box_width(game_screen: GameScreen) -> int:
    return max(1, int(game_screen.block_size / 30))


def back_button(game_screen: GameScreen, text: str = "back") -> Button:
    """Bottom-left corner - the top of the screen belongs to the run bar."""
    bs = game_screen.block_size
    height = bs * 0.6
    return Button(bs * 1.5, height, bs * 0.4,
                  game_screen.display_height - height - bs * 0.25,
                  box_width=box_width(game_screen),
                  font=game_screen.big_text_font, text=text)


TITLE_Y: float = 0.62
SUBTITLE_GAP: float = 0.52
CONTENT_TOP: float = 1.55


def title_y(game_screen: GameScreen) -> float:
    """Baseline of a screen title.  The run bar owns everything above it."""
    return game_screen.block_size * TITLE_Y


def subtitle_y(game_screen: GameScreen, title_lines: int = 1) -> float:
    return game_screen.block_size * (TITLE_Y + SUBTITLE_GAP * title_lines)


def content_top(game_screen: GameScreen) -> float:
    """First row below the title block.  Everything a screen lays out itself
    starts here, so a title can never land on top of the content."""
    return game_screen.block_size * CONTENT_TOP


def draw_run_bar(game_screen: GameScreen, run: dict) -> None:
    """Act / layer / gold / orbs / relic count, along the top of the screen."""
    bs = game_screen.block_size
    y = bs * 0.35
    draw_text(f"act {run['act']}   layer {run['layer']}",
              game_screen.mid_text_font, WHITE, bs * 0.5, y, game_screen.surface)
    draw_text(f"gold {run['gold']}", game_screen.mid_text_font, GOLD,
              bs * 3.2, y, game_screen.surface)
    draw_text(f"orbs {run.get('orbs', 0)}", game_screen.mid_text_font, ORB,
              bs * 4.9, y, game_screen.surface)
    draw_text(f"deck {len(run['deck'])}/{len(run['deck']) + len(run['bench'])}",
              game_screen.mid_text_font, WHITE, bs * 6.4, y, game_screen.surface)
    relics = len(run.get("relics", []))
    if relics:
        draw_text(f"relics {relics}  [F]", game_screen.mid_text_font, RELIC,
                  bs * 8.2, y, game_screen.surface)
    if run.get("debt"):
        draw_text(f"debt {run['debt']}", game_screen.mid_text_font, CURSE,
                  bs * 9.9, y, game_screen.surface)


def column_bottom(game_screen: GameScreen) -> float:
    """Last row a column may use before it runs into the button row."""
    return game_screen.display_height - game_screen.block_size * 1.4


def draw_capped_lines(game_screen: GameScreen, lines, size: str, color,
                      x: float, y: float, step: float,
                      bottom: float | None = None) -> float:
    """Draw a list downwards, stopping with a count rather than running off."""
    bs = game_screen.block_size
    limit = column_bottom(game_screen) if bottom is None else bottom
    lines = list(lines)
    for i, line in enumerate(lines):
        if y + bs * step > limit:
            draw_auto(game_screen, f"+{len(lines) - i} more", "small_text_font",
                      DIM, x, y)
            return y + bs * step
        draw_auto(game_screen, line, size, color, x, y)
        y += bs * step
    return y


RELIC_PANEL_W: float = 4.1


def draw_relic_strip(game_screen: GameScreen, run: dict, detailed: bool = False) -> None:
    """Owned relics as a panel over the screen.  Toggled, never docked.

    It used to be a permanent strip down the right edge with no background,
    which meant five different screens drew their own content straight
    through it.  As an overlay it is drawn last and paints its own ground, so
    it cannot collide with anything, and the run bar carries the count for
    when it is closed.
    """
    if not detailed:
        return
    relics = run.get("relics", []) if run else []
    if not relics:
        return

    bs = game_screen.block_size
    pad = bs * style.PANEL_PAD
    name_font = language.chinese_font(game_screen, "text_font")
    body_font = language.chinese_font(game_screen, "small_text_font")
    width = bs * RELIC_PANEL_W
    text_width = width - pad * 2

    blocks: list[tuple[str, tuple[int, int, int], list[str]]] = [
        (relic_label(relic_id), relic_color(relic_id),
         wrap_to_width(relic_text(relic_id), body_font, text_width))
        for relic_id in relics
    ]
    body = sum(name_font.get_linesize() + bs * 0.2 * len(lines) + bs * 0.06
               for _label, _colour, lines in blocks)
    height = bs * style.HEADER_HEIGHT + pad + body + pad * 0.4

    x = game_screen.display_width - width - bs * 0.3
    y = min(content_top(game_screen),
            game_screen.display_height - height - bs * 0.3)
    style.modal_section(game_screen, "RELICS", x, y, width, height,
                        right=str(len(relics)))

    line_y = y + bs * style.HEADER_HEIGHT + pad * 0.8
    for label, colour, lines in blocks:
        draw_text(label, name_font, colour, x + pad, line_y, game_screen.surface)
        line_y += name_font.get_linesize()
        for line in lines:
            draw_text(line, body_font, DIM, x + pad * 1.4, line_y, game_screen.surface)
            line_y += bs * 0.2
        line_y += bs * 0.06
