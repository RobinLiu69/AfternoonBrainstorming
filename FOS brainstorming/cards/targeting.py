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

"""Grid targeting.

This is the one part of the card system with no analogue in Magic or
Hearthstone — it is tactics-grid geometry, closer to a strategy game than a
card game — so it stays bespoke. Extracting it as pure functions (rather than
final methods on Card) means it can be tested and reused without a card
instance, and keeps the effect system free of positional logic.

A pattern is a space-separated string of shape names; a card's shapes come from
its job, via JOB_DICTIONARY["attack_type_tags"].
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator, Protocol, Sequence, TypeVar

if TYPE_CHECKING:
    from core.game_state import GameState


class Positioned(Protocol):
    board_x: int
    board_y: int


T = TypeVar("T", bound=Positioned)

Pos = tuple[int, int]


def _manhattan(item: Positioned, origin: Pos) -> int:
    return abs(item.board_x - origin[0]) + abs(item.board_y - origin[1])


def _closest_group(candidates: Sequence[T], origin: Pos, *, farthest: bool) -> list[T]:
    """Every candidate tied for nearest (or farthest) distance from origin."""
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda c: _manhattan(c, origin), reverse=farthest)
    best = _manhattan(ordered[0], origin)
    return [c for c in ordered if _manhattan(c, origin) == best]


def _offsets(shape: str) -> tuple[Pos, ...]:
    match shape:
        case "small_cross":
            return ((-1, 0), (1, 0), (0, -1), (0, 1))
        case "small_x":
            return ((1, 1), (-1, 1), (-1, -1), (1, -1))
        case _:
            return ()


def find_targets(
    pattern: str,
    origin: Pos,
    candidates: Iterable[T],
    game_state: "GameState",
) -> Iterator[T]:
    """Yield the cards a pattern hits, in resolution order.

    Only living candidates are considered. Shapes are applied left to right and
    each yields independently, matching the original Card.detection.
    """
    living = tuple(c for c in candidates if c.health > 0)  # type: ignore[attr-defined]

    for shape in pattern.split(" "):
        match shape:
            case "small_cross" | "small_x":
                cells = {(origin[0] + dx, origin[1] + dy) for dx, dy in _offsets(shape)}
                for card in living:
                    if (card.board_x, card.board_y) in cells:
                        yield card
            case "large_cross":
                for card in living:
                    same_row = card.board_y == origin[1]
                    same_col = card.board_x == origin[0]
                    if (same_row or same_col) and (card.board_x, card.board_y) != origin:
                        yield card
            case "large_x":
                pass
            case "nearest" | "farthest":
                group = _closest_group(living, origin, farthest=(shape == "farthest"))
                if group:
                    yield game_state.rng.choice(group)


def pattern_cells(
    pattern: str,
    origin: Pos,
    owner: str,
    game_state: "GameState",
) -> Iterator[Pos]:
    """Yield the board cells a pattern covers, for the attack-range overlay."""
    board_positions = tuple(game_state.board_dict.keys())

    for shape in pattern.split(" "):
        match shape:
            case "small_cross" | "small_x":
                cells = {(origin[0] + dx, origin[1] + dy) for dx, dy in _offsets(shape)}
                for pos in board_positions:
                    if pos in cells:
                        yield pos
            case "large_cross":
                for pos in board_positions:
                    if (pos[0] == origin[0] or pos[1] == origin[1]) and pos != origin:
                        yield pos
            case "large_x":
                pass
            case "nearest" | "farthest":
                enemies = [c for c in game_state.get_side_cards(owner, True) if c.health > 0]
                for card in _closest_group(enemies, origin, farthest=(shape == "farthest")):
                    yield (card.board_x, card.board_y)
