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

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.base import Card


def empty_positions(gs: "GameState") -> list[tuple[int, int]]:
    return [
        (x, y) for (x, y), board in gs.board_dict.items()
        if not board.occupy and gs.board_config.is_valid_position(x, y)
    ]


def is_corner(gs: "GameState", x: int, y: int) -> bool:
    w, h = gs.board_config.width, gs.board_config.height
    return (x in (0, w - 1)) and (y in (0, h - 1))


def is_edge(gs: "GameState", x: int, y: int) -> bool:
    w, h = gs.board_config.width, gs.board_config.height
    on_border = (x in (0, w - 1)) or (y in (0, h - 1))
    return on_border and not is_corner(gs, x, y)


def position_safety(gs: "GameState", x: int, y: int) -> float:
    if is_corner(gs, x, y):
        return 3.0
    if is_edge(gs, x, y):
        return 2.0
    return 1.0


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def enemy_cards(gs: "GameState", owner: str) -> list["Card"]:
    return [c for c in gs.get_opponent_cards(owner) if c.health > 0]


def friendly_cards(gs: "GameState", owner: str) -> list["Card"]:
    return [c for c in gs.get_player_cards(owner) if c.health > 0]


def attack_targets_from_pos(
    gs: "GameState", owner: str, x: int, y: int, attack_types: str,
) -> list["Card"]:
    """Compute what enemy cards a unit with `attack_types` at (x, y) would hit.

    Position-based variant used both for live attackers and for evaluating
    hypothetical placements. Deterministic — does NOT consume `gs.rng`.
    """
    candidates = [c for c in gs.get_side_cards(owner, get_opponent=True) if c.health > 0]
    if not candidates or not attack_types:
        return []

    hits: list["Card"] = []
    for attack_type in attack_types.split(" "):
        match attack_type:
            case "small_cross":
                for c in candidates:
                    if abs(c.board_x - x) + abs(c.board_y - y) == 1:
                        hits.append(c)
            case "large_cross":
                for c in candidates:
                    same_row = c.board_y == y
                    same_col = c.board_x == x
                    same_pos = c.board_x == x and c.board_y == y
                    if (same_row or same_col) and not same_pos:
                        hits.append(c)
            case "small_x":
                for c in candidates:
                    if abs(c.board_x - x) == 1 and abs(c.board_y - y) == 1:
                        hits.append(c)
            case "nearest":
                sorted_c = sorted(candidates, key=lambda c: manhattan((c.board_x, c.board_y), (x, y)))
                if sorted_c:
                    nearest = manhattan((sorted_c[0].board_x, sorted_c[0].board_y), (x, y))
                    hits.extend(c for c in sorted_c if manhattan((c.board_x, c.board_y), (x, y)) == nearest)
            case "farthest":
                sorted_c = sorted(candidates, key=lambda c: manhattan((c.board_x, c.board_y), (x, y)), reverse=True)
                if sorted_c:
                    farthest = manhattan((sorted_c[0].board_x, sorted_c[0].board_y), (x, y))
                    hits.extend(c for c in sorted_c if manhattan((c.board_x, c.board_y), (x, y)) == farthest)

    seen_ids: set[str] = set()
    unique_hits = []
    for c in hits:
        if c.instance_id not in seen_ids:
            seen_ids.add(c.instance_id)
            unique_hits.append(c)
    return unique_hits


def attack_targets_at(gs: "GameState", attacker: "Card") -> list["Card"]:
    return attack_targets_from_pos(
        gs, attacker.owner, attacker.board_x, attacker.board_y, attacker.attack_types
    )


def nearest_enemy_distance(gs: "GameState", owner: str, x: int, y: int) -> int:
    enemies = enemy_cards(gs, owner)
    if not enemies:
        w, h = gs.board_config.width, gs.board_config.height
        return w + h
    return min(manhattan((x, y), (e.board_x, e.board_y)) for e in enemies)


def is_playable_unit_card(card_name: str) -> bool:
    """Returns True if the card represents a unit (placed on the board).

    Magic cards (HEAL/MOVE/MOVEO/CUBES) are handled separately — they generate
    counters when played, not board units.
    """
    return card_name not in ("HEAL", "MOVE", "MOVEO", "CUBES")


def units_with_pending_move(gs: "GameState", owner: str) -> list["Card"]:
    """My units that have `moving=True` (typically just after an orange attack).

    They're waiting for a move command — if we don't drive them now, the move
    opportunity wastes once the next action resolves.
    """
    return [c for c in gs.get_player(owner).on_board if c.moving and c.health > 0]


def move_destinations_for(gs: "GameState", card: "Card") -> list[tuple[int, int]]:
    """Empty board cells reachable from `card` via a single 8-neighbor step."""
    cells: list[tuple[int, int]] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = card.board_x + dx, card.board_y + dy
            if not gs.board_config.is_valid_position(nx, ny):
                continue
            if gs.board_dict[nx, ny].occupy:
                continue
            cells.append((nx, ny))
    return cells


from campaign.config_loader import CAMPAIGN_SETTINGS as _CS
ASS_THREAT_DAMAGE: int = int(_CS["threat_model"]["ass_threat_damage"])
"""Worst-case lethal-on-deploy threat: a hypothetical enemy ASS (white baseline = 5)."""


def attacker_would_hit_position(
    attacker: "Card", tx: int, ty: int, target_owner: str, gs: "GameState",
) -> bool:
    """Would `attacker` hit a hypothetical enemy unit placed at (tx, ty)?

    `target_owner` is the side that would own the hypothetical target (i.e. attacker's
    opposite). Handles all attack_types patterns including nearest/farthest, which
    depend on existing friendly positions.
    """
    ax, ay = attacker.board_x, attacker.board_y
    if not attacker.attack_types:
        return False
    for at in attacker.attack_types.split(" "):
        match at:
            case "small_cross":
                if abs(ax - tx) + abs(ay - ty) == 1:
                    return True
            case "large_cross":
                if (ax == tx or ay == ty) and not (ax == tx and ay == ty):
                    return True
            case "small_x":
                if abs(ax - tx) == 1 and abs(ay - ty) == 1:
                    return True
            case "nearest":
                friendlies = friendly_cards(gs, target_owner)
                d_new = manhattan((ax, ay), (tx, ty))
                d_others = [manhattan((ax, ay), (f.board_x, f.board_y)) for f in friendlies]
                if not d_others or d_new <= min(d_others):
                    return True
            case "farthest":
                friendlies = friendly_cards(gs, target_owner)
                d_new = manhattan((ax, ay), (tx, ty))
                d_others = [manhattan((ax, ay), (f.board_x, f.board_y)) for f in friendlies]
                if not d_others or d_new >= max(d_others):
                    return True
    return False


def incoming_damage_at_position(
    gs: "GameState", owner: str, x: int, y: int,
) -> int:
    """Damage a unit placed at (x, y) would soak this turn from opponent attacks.

    Opponent can only fire `number_of_attacks[opponent]` of its non-numb units this
    turn; pick the highest-damage candidates as worst case. Ignores positional bonuses
    (red increase-damage, anger, etc) — purely a stat readout. Good enough to avoid
    obvious self-suicide placements.
    """
    opp = gs.get_opponent_name(owner)
    available = gs.number_of_attacks.get(opp, 0)
    if available <= 0:
        return 0

    threats: list[int] = []
    for enemy in enemy_cards(gs, owner):
        if enemy.numbness:
            continue
        if attacker_would_hit_position(enemy, x, y, owner, gs):
            threats.append(enemy.damage + enemy.extra_damage)

    threats.sort(reverse=True)
    return sum(threats[:available])


def cells_threatening_card(gs: "GameState", card: "Card") -> list[tuple[int, int]]:
    """Empty cells where an enemy ASS could be deployed this turn to kill `card`.

    Threat model (Phase 1): opponent could place an ASS (small_x, damage 5, deploys
    non-numb) at any empty cell. Anything else they could place is numb-on-deploy and
    can't attack this turn, so it isn't a same-turn lethal threat.
    """
    effective = ASS_THREAT_DAMAGE - max(0, card.armor)
    if card.health > effective:
        return []
    spots: list[tuple[int, int]] = []
    for (x, y) in empty_positions(gs):
        if abs(card.board_x - x) == 1 and abs(card.board_y - y) == 1:
            spots.append((x, y))
    return spots
