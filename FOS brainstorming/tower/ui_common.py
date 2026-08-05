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

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from core.UI import Button

from tower.content import ENEMY_LABELS, RELICS, ROOM_LABELS

# free text is wrapped to a fixed width so descriptions never overlap
# whatever is drawn beside or below them
DESC_WRAP: int = 40
RELIC_WRAP: int = 30
PANEL_WRAP: int = 52


def wrap(text: str, width: int = DESC_WRAP) -> list[str]:
    if not text:
        return []
    return textwrap.wrap(text, width) or [text]


def wrap_all(lines, width: int = DESC_WRAP) -> list[str]:
    out: list[str] = []
    for line in lines:
        out.extend(wrap(line, width))
    return out


def wrap_to_width(text: str, font, max_width: float) -> list[str]:
    """Wrap by measuring the font, so a line can never run past its column."""
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
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


def relic_label(relic_id: str) -> str:
    return RELICS.get(relic_id, {}).get("label", relic_id)


def relic_text(relic_id: str) -> str:
    return RELICS.get(relic_id, {}).get("text", "")


def enemy_color(kind: str) -> tuple[int, int, int]:
    if kind == "boss":
        return CURSE
    if kind == "elite":
        return POWER
    return ENEMY


def room_label(kind: str) -> str:
    return ROOM_LABELS.get(kind, kind)


def enemy_label(enemy: dict) -> str:
    return enemy.get("label", ENEMY_LABELS.get(enemy.get("kind", ""), "?"))


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
    if run.get("debt"):
        draw_text(f"debt {run['debt']}", game_screen.mid_text_font, CURSE,
                  bs * 8.2, y, game_screen.surface)


def draw_relic_strip(game_screen: GameScreen, run: dict, detailed: bool = False) -> None:
    """Relic names down the right edge; [F] adds what each one does."""
    bs = game_screen.block_size
    relics = run.get("relics", [])
    if not relics:
        return

    x = game_screen.display_width - bs * (3.9 if detailed else 2.6)
    y = bs * 1.1
    step = bs * 0.26
    for relic_id in relics:
        draw_text(relic_label(relic_id), game_screen.text_font,
                  relic_color(relic_id), x, y, game_screen.surface)
        y += step
        if detailed:
            for line in wrap(relic_text(relic_id), RELIC_WRAP):
                draw_text(line, game_screen.small_text_font, DIM,
                          x + bs * 0.12, y, game_screen.surface)
                y += bs * 0.2
            y += bs * 0.04
