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

from shared.setting import CARD_SETTING, JOB_DICTIONARY
from campaign.ai_query import (
    attack_targets_at, attack_targets_from_pos, position_safety, nearest_enemy_distance,
    friendly_cards, cells_threatening_card, incoming_damage_at_position,
    attack_coverage_cells, ASS_THREAT_DAMAGE, enemy_cards, manhattan,
    projected_incoming_damage,
)
from campaign.config_loader import CAMPAIGN_SETTINGS

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.base import Card


COLOR_TAG_LIST: list[str] = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)


def _is_anger_immortal(card: "Card") -> bool:
    return card.job_and_color == "HFR" and getattr(card, "anger", False)


JOBS_ATTACK_ON_DEPLOY: set[str] = {"ASS"}

NON_ATTACKING_CARDS: set[str] = {"APTG"}

PRIORITY_TARGET_JOBS: set[str] = {"ADC", "SP"}


def target_priority_bonus(target: "Card") -> float:
    job, _ = parse_card_name(target.job_and_color)
    return 5.0 if job in PRIORITY_TARGET_JOBS else 0.0


def followup_kill_bonus(
    attacker: "Card", target: "Card", gs: "GameState", chip_damage: int,
) -> float:
    if gs.number_of_attacks.get(attacker.owner, 0) < 2:
        return 0.0
    remaining = target.health - chip_damage
    if remaining <= 0:
        return 0.0
    armor = max(0, target.armor)
    for other in gs.get_player(attacker.owner).on_board:
        if other is attacker or other.numbness or other.health <= 0:
            continue
        if other.job_and_color in NON_ATTACKING_CARDS:
            continue
        if target not in attack_targets_at(gs, other):
            continue
        other_dmg = other.damage + other.extra_damage
        if remaining + armor <= other_dmg:
            return 15.0 + target.damage * 2.0
    return 0.0


WASTED_CHIP_PENALTY: float = 18.0


_SCORING = CAMPAIGN_SETTINGS["scoring"]
_THREAT = CAMPAIGN_SETTINGS["threat_model"]

KILL_BONUS_BASE: float = float(_SCORING["kill_bonus_base"])
KILL_BONUS_PER_THREAT: float = float(_SCORING["kill_bonus_per_threat"])


HAND_THREAT_VALUE: dict[str, float] = {
    k: float(v) for k, v in _SCORING.get("hand_threat_value", {"ASS": 20.0}).items()
}


SCORE_INCOME_MULTIPLIER: float = float(_SCORING["score_income_multiplier"])


def parse_card_name(card_name: str) -> tuple[str, str]:
    for tag in COLOR_TAG_LIST:
        if card_name.endswith(tag):
            job = card_name[: -len(tag)]
            color = JOB_DICTIONARY["colors_dict"][tag]
            return job, color
    return "", ""


def card_base_stats(card_name: str) -> tuple[int, int]:
    job, color = parse_card_name(card_name)
    if not job or not color:
        return 0, 0
    color_table = CARD_SETTING.get(color)
    if not color_table:
        return 0, 0
    stats = color_table.get(job)
    if not stats:
        return 0, 0
    return stats.get("health", 0), stats.get("damage", 0)


def estimate_score_per_turn(card_name: str) -> int:
    job, color = parse_card_name(card_name)
    if not job:
        return 0
    if job in ("CUBE", "CUBES", "HEAL", "MOVE", "MOVEO", "LUCKYBLOCK"):
        return 0
    if job == "SP":
        sp_data = CARD_SETTING.get(color, {}).get("SP", {})
        return 1 + sp_data.get("extra_score", 0)
    return 1


def score_income_bonus(card_name: str) -> float:
    return estimate_score_per_turn(card_name) * SCORE_INCOME_MULTIPLIER


def attack_denial_bonus(target: "Card") -> float:
    return estimate_score_per_turn(target.job_and_color) * SCORE_INCOME_MULTIPLIER


def defensive_placement_bonus(
    card_name: str,
    position: tuple[int, int],
    gs: "GameState",
    owner: str,
) -> float:
    saved: list["Card"] = []
    for friendly in friendly_cards(gs, owner):
        if position in cells_threatening_card(gs, friendly):
            saved.append(friendly)
    if not saved:
        return 0.0
    return sum(f.damage * 6.0 + f.health * 1.5 for f in saved)


def threat_placement_bonus(
    card_name: str,
    position: tuple[int, int],
    gs: "GameState",
    owner: str,
) -> float:
    job, _ = parse_card_name(card_name)
    attack_types = JOB_DICTIONARY.get("attack_type_tags", {}).get(job, "")
    if not attack_types or attack_types == "None":
        return 0.0
    _, damage = card_base_stats(card_name)
    if damage <= 0:
        return 0.0
    targets = attack_targets_from_pos(gs, owner, position[0], position[1], attack_types)
    if not targets:
        return 0.0
    total = sum(min(damage, t.health) * 0.3 + t.damage * 0.5 for t in targets)
    if job not in JOBS_ATTACK_ON_DEPLOY:
        total *= 0.6
    return total


def incoming_damage_penalty(
    card_name: str,
    position: tuple[int, int],
    gs: "GameState",
    owner: str,
) -> float:
    incoming = incoming_damage_at_position(gs, owner, position[0], position[1])
    if incoming <= 0:
        return 0.0
    health, _ = card_base_stats(card_name)
    if health <= 0:
        return 0.0
    if incoming >= health:
        return -float(_THREAT["incoming_kill_penalty"])
    return -incoming * float(_THREAT["incoming_chip_penalty_per_damage"])


def hand_threat_penalty(card_name: str) -> float:
    job, _ = parse_card_name(card_name)
    return -HAND_THREAT_VALUE.get(job, 0.0)


def future_ass_threat_penalty(
    card_name: str, position: tuple[int, int], gs: "GameState",
) -> float:
    health, _ = card_base_stats(card_name)
    if health <= 0 or health > ASS_THREAT_DAMAGE:
        return 0.0
    x, y = position
    vulnerable = 0
    for dx, dy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        nx, ny = x + dx, y + dy
        if gs.board_config.is_valid_position(nx, ny) and not gs.board_dict[nx, ny].occupy:
            vulnerable += 1
    if vulnerable == 0:
        return 0.0
    score_per_turn = estimate_score_per_turn(card_name)
    return -float(vulnerable) * (3.0 + score_per_turn * 1.5)


SQUISHY_DPS_JOBS: set[str] = {"ADC", "AP", "SP"}


def protection_bonus(card_name: str, gs: "GameState", owner: str) -> float:
    job, _ = parse_card_name(card_name)
    if job not in SQUISHY_DPS_JOBS:
        return 0.0
    has_front_line = any(
        c.health > ASS_THREAT_DAMAGE for c in gs.get_player(owner).on_board
    )
    return 4.0 if has_front_line else -12.0


def reach_bonus(card_name: str, position: tuple[int, int], gs: "GameState") -> float:
    job, _ = parse_card_name(card_name)
    if not job:
        return 0.0
    attack_types = JOB_DICTIONARY.get("attack_type_tags", {}).get(job, "")
    if not attack_types or attack_types == "None":
        return 0.0
    cells = attack_coverage_cells(gs, position[0], position[1], attack_types)
    return cells * 0.8


def lethal_placement_bonus(
    card_name: str,
    position: tuple[int, int],
    gs: "GameState",
    owner: str,
) -> float:
    job, _ = parse_card_name(card_name)
    if job not in JOBS_ATTACK_ON_DEPLOY:
        return 0.0

    _, damage = card_base_stats(card_name)
    if damage <= 0:
        return 0.0

    attack_types = JOB_DICTIONARY.get("attack_type_tags", {}).get(job, "")
    if not attack_types:
        return 0.0

    x, y = position
    targets = attack_targets_from_pos(gs, owner, x, y, attack_types)
    best_bonus = 0.0
    for target in targets:
        if _is_anger_immortal(target):
            continue
        effective_damage = damage - max(0, target.armor)
        if effective_damage <= 0:
            continue
        if target.health <= effective_damage:
            bonus = (
                KILL_BONUS_BASE
                + target.damage * KILL_BONUS_PER_THREAT
                + attack_denial_bonus(target)
                + target_priority_bonus(target)
            )
            if bonus > best_bonus:
                best_bonus = bonus
    return best_bonus


def evaluate_placement(
    card_name: str,
    position: tuple[int, int],
    gs: "GameState",
    owner: str,
) -> float:
    x, y = position
    if not gs.board_config.is_valid_position(x, y):
        return -1000.0
    if gs.board_dict[x, y].occupy:
        return -1000.0

    health, damage = card_base_stats(card_name)
    score = 0.0

    score += health * 0.5 + damage * 1.5

    safety = position_safety(gs, x, y)
    job, _ = parse_card_name(card_name)
    if job == "SP":
        score += safety * 4.0
    elif job in ("TANK", "HF"):
        score += safety * 1.0
    elif job == "ASS":
        score += safety * 0.5
    else:
        score += safety * 2.0

    dist = nearest_enemy_distance(gs, owner, x, y)
    if job in ("ASS", "LF"):
        if dist <= 2:
            score += 2.0
    if job in ("TANK", "HF") and dist <= 1:
        score += 3.0

    if job == "SP" and dist <= 2:
        score -= 5.0

    score += lethal_placement_bonus(card_name, position, gs, owner)
    score += defensive_placement_bonus(card_name, position, gs, owner)
    score += threat_placement_bonus(card_name, position, gs, owner)
    score += incoming_damage_penalty(card_name, position, gs, owner)
    score += hand_threat_penalty(card_name)
    score += score_income_bonus(card_name)
    score += reach_bonus(card_name, position, gs)
    score += future_ass_threat_penalty(card_name, position, gs)
    score += protection_bonus(card_name, gs, owner)

    return score


def score_move_destination(card: "Card", dest: tuple[int, int], gs: "GameState") -> float:
    dx, dy = dest
    targets = attack_targets_from_pos(gs, card.owner, dx, dy, card.attack_types)

    if card.job_and_color == "ADCO":
        return float(sum(min(card.damage, t.health) * 2.0 for t in targets))

    if card.job_and_color == "LFO":
        enemies = enemy_cards(gs, card.owner)
        if not enemies:
            return 0.0
        nearest = min(manhattan((dx, dy), (e.board_x, e.board_y)) for e in enemies)
        return 6.0 - nearest

    if card.job_and_color == "HFO":
        projected_damage = card.damage + card.extra_damage + 1
        return position_safety(gs, dx, dy) + len(targets) * projected_damage * 0.6

    if card.job_and_color == "ASSO":
        for t in targets:
            effective = card.damage - max(0, t.armor)
            if effective > 0 and t.health <= effective:
                return 20.0 + t.damage * 2.0
        return float(len(targets) * 2.0)

    return float(len(targets) * 1.5)


def evaluate_attack(attacker: "Card", gs: "GameState") -> tuple[float, "Card | None"]:
    if attacker.numbness:
        return -1.0, None
    if attacker.job_and_color in NON_ATTACKING_CARDS:
        return -1.0, None

    targets = attack_targets_at(gs, attacker)
    if not targets:
        return -1.0, None

    best_score = float("-inf")
    best_target: "Card | None" = None
    attacker_immortal = _is_anger_immortal(attacker)
    projected = projected_incoming_damage(
        gs, attacker.owner, attacker.board_x, attacker.board_y
    )
    attacker_doomed = not attacker_immortal and attacker.health <= projected
    deterministic_aoe = bool(attacker.attack_types) and all(
        at in ("small_cross", "small_x", "large_cross")
        for at in attacker.attack_types.split(" ")
        if at
    )
    aggregate_score: float = 0.0
    for target in targets:
        s = 0.0

        effective_damage = attacker.damage + attacker.extra_damage
        if target.armor >= effective_damage:
            s += 5.0
        elif target.health <= effective_damage - max(0, target.armor) and not _is_anger_immortal(target):
            s += 100.0 + target.damage * 10.0 + attack_denial_bonus(target)
        else:
            s += min(effective_damage, target.health) * 2.0
            followup = followup_kill_bonus(attacker, target, gs, effective_damage)
            s += followup
            if followup == 0.0 and not attacker_doomed:
                s -= WASTED_CHIP_PENALTY

        s += target.damage * 3.0
        s += target_priority_bonus(target)

        if (target.damage >= attacker.health and not target.numbness
                and not attacker_immortal and not attacker_doomed):
            s -= 50.0

        if target.numbness:
            s -= 20.0

        if s > best_score:
            best_score = s
            best_target = target

        if deterministic_aoe:
            aggregate_score += s

    if deterministic_aoe and aggregate_score > best_score:
        best_score = aggregate_score

    return best_score, best_target
