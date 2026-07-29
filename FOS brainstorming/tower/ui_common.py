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

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from core.UI import Button

from tower.content import ENEMY_LABELS, RELICS, ROOM_LABELS


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
    bs = game_screen.block_size
    return Button(bs * 1.5, bs * 0.6, bs * 0.5, bs * 0.5,
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


def draw_relic_strip(game_screen: GameScreen, run: dict) -> None:
    """One line per relic down the right edge."""
    bs = game_screen.block_size
    x = game_screen.display_width - bs * 3.4
    y = bs * 1.1
    for relic_id in run.get("relics", []):
        draw_text(relic_label(relic_id), game_screen.small_text_font,
                  relic_color(relic_id), x, y, game_screen.surface)
        y += bs * 0.3
