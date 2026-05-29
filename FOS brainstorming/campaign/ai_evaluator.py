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
    attack_coverage_cells, ASS_THREAT_DAMAGE,
)
from campaign.config_loader import CAMPAIGN_SETTINGS

if TYPE_CHECKING:
    from core.game_state import GameState
    from cards.base import Card


COLOR_TAG_LIST: list[str] = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)


JOBS_ATTACK_ON_DEPLOY: set[str] = {"ASS"}
"""Jobs whose units have numbness=False on deploy and can attack same turn."""


NON_ATTACKING_CARDS: set[str] = {"APTG"}
"""Cards whose `attack()` is hard-coded to always return False (no attack action
ever connects). Letting the AI pick one as an attacker causes an infinite loop:
the dispatcher fires, attack returns False, attack count isn't decremented, so
the AI re-picks the same target every tick."""


PRIORITY_TARGET_JOBS: set[str] = {"ADC", "SP"}
"""Jobs whose units are extra-valuable to weaken or kill:
- ADC: highest standing damage in most factions, removing it slows opponent offense.
- SP: highest score income (1 + extra_score per turn) — every turn alive is a point.

Their `target.damage * 3` term already gives SP a bump (damage 5 → +15), but a
plain ADC chip with a low-damage attacker still scores ~11 — below default thresholds.
This explicit bonus lets the AI commit to chipping ADC/SP even when its current
attacker isn't a heavy hitter."""


def target_priority_bonus(target: "Card") -> float:
    """Flat +5 for chipping or killing a priority-target job."""
    job, _ = parse_card_name(target.job_and_color)
    return 5.0 if job in PRIORITY_TARGET_JOBS else 0.0


def followup_kill_bonus(
    attacker: "Card", target: "Card", gs: "GameState", chip_damage: int,
) -> float:
    """Reward chip damage that another friendly attacker can finish this turn.

    Without a follow-up, chip is "wasted work": the target stays alive and keeps
    scoring 1+/turn for the opponent. We only count chips that chain into a kill
    within the current attack budget.

    Conditions:
    - We need at least 2 attack counts (this chip + the follow-up).
    - The chip must not already be lethal (separate kill bonus handles that).
    - Some other non-numb friendly must be in attack range of `target` and able
      to one-shot the chipped HP (accounting for target armor).
    """
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


WASTED_CHIP_PENALTY: float = 5.0
"""Subtracted from chip-damage scores when there's no follow-up kill chain.
Encodes 'doing nothing this turn beats wasting attacks on chips you can't
finish' — the opponent keeps scoring from the surviving target either way."""


_SCORING = CAMPAIGN_SETTINGS["scoring"]
_THREAT = CAMPAIGN_SETTINGS["threat_model"]

KILL_BONUS_BASE: float = float(_SCORING["kill_bonus_base"])
KILL_BONUS_PER_THREAT: float = float(_SCORING["kill_bonus_per_threat"])


HAND_THREAT_VALUE: dict[str, float] = {
    k: float(v) for k, v in _SCORING.get("hand_threat_value", {"ASS": 20.0}).items()
}
"""Score discount for keeping a card in hand vs. spending it. ASS is a latent kill
threat — opponent has to play around it, so we don't deploy it unless the immediate
value (kill bonus, defensive block, etc.) clearly beats just sitting in hand.

Sized to outweigh `score_income_bonus` for ASS (1 pt/turn × 8 = 8) plus generic
positional bonuses (~12), so a "stat-dump" ASS placement nets a negative score and
is filtered out by `placement_min_score`."""


SCORE_INCOME_MULTIPLIER: float = float(_SCORING["score_income_multiplier"])
"""How many turns of survival to project when valuing a card's score income.
A normal unit (1 pt/turn) gets +8; SP (2 pt/turn for white) gets +16. Same multiplier
applied to attack kills as denial bonus."""


def parse_card_name(card_name: str) -> tuple[str, str]:
    """Split 'ADCW' into ('ADC', 'White'). Returns ('', '') for spells/magic."""
    for tag in COLOR_TAG_LIST:
        if card_name.endswith(tag):
            job = card_name[: -len(tag)]
            color = JOB_DICTIONARY["colors_dict"][tag]
            return job, color
    return "", ""


def card_base_stats(card_name: str) -> tuple[int, int]:
    """Return (health, damage) from CARD_SETTING. Returns (0, 0) if unknown."""
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
    """How many points the card scores per non-numb turn (the value of `on_settle()`).

    Default: 1. SP gets `1 + extra_score`. CUBE / spells score 0.
    """
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
    """Reward placing a card based on the score it'll generate while alive.

    Multiplier doubles as the AI's implicit horizon — 8 turns of expected survival.
    """
    return estimate_score_per_turn(card_name) * SCORE_INCOME_MULTIPLIER


def attack_denial_bonus(target: "Card") -> float:
    """Bonus for killing a target that was scoring points per turn."""
    return estimate_score_per_turn(target.job_and_color) * SCORE_INCOME_MULTIPLIER


def defensive_placement_bonus(
    card_name: str,
    position: tuple[int, int],
    gs: "GameState",
    owner: str,
) -> float:
    """Bonus for occupying a cell where an enemy ASS could be deployed to kill a friendly.

    Once we sit on the cell, the opponent can't drop an ASS there this turn. The bonus
    sums the value of every friendly saved by blocking this single cell (a single block
    can shield multiple cards if they share a threat cell).
    """
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
    """Reward placing a card where it has enemies in its attack range.

    Without this, ASS placements at random empty corners score the same as ASS placements
    where it could actually hit something. Numb-on-deploy units get a discount since
    their threat is only realized next turn.
    """
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
    """Penalty for placing somewhere the opponent could kill or chip with current attacks.

    Uses `number_of_attacks[opponent]` as the cap — opponent can only fire that many
    attacks this turn. If incoming >= our health, we'd just be feeding a kill back.
    """
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
    """Penalty for dropping a one-shot-able unit where opponent can deploy ASS to kill it.

    Symmetric to `defensive_placement_bonus` and `cells_threatening_card`: same
    worst-case assumption (opponent has a hypothetical ASS with damage 5 / small_x).
    Counts the empty small_x-adjacent cells around the proposed position — each
    one is a slot opponent can pay 1 card + 1 attack to one-shot us.

    Only fires for units whose base health is ≤ ASS damage. TANK / HF / LF tank
    a 5-damage swing and don't trigger this.
    """
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
    # Per-cell penalty scaled by how much score income we'd lose if killed.
    score_per_turn = estimate_score_per_turn(card_name)
    return -float(vulnerable) * (3.0 + score_per_turn * 1.5)


SQUISHY_DPS_JOBS: set[str] = {"ADC", "AP", "SP"}
"""Low-HP key scorers / damage dealers (1-5 base HP across factions). Without
a front-line shield they die fast and their score income evaporates."""


def protection_bonus(card_name: str, gs: "GameState", owner: str) -> float:
    """Hold-or-deploy weight for squishy DPS.

    Deploying ADC/SP/AP into open ground without a tank-shaped friendly already
    on the board is a tempo trap — the opponent removes them cheaply (chip
    chain, ASS deploy-kill, large_cross ranged shot). Wait until TANK/HF/LF
    (HP > 5) anchors the front line first, then commit.

    Returns +4 when at least one friendly tank-class unit is on the board,
    −12 otherwise. The magnitude offsets normal positional scoring enough that
    a same-turn TANK placement (no penalty) consistently out-scores an ADC
    placement when neither is on the board yet.
    """
    job, _ = parse_card_name(card_name)
    if job not in SQUISHY_DPS_JOBS:
        return 0.0
    has_front_line = any(
        c.health > ASS_THREAT_DAMAGE for c in gs.get_player(owner).on_board
    )
    return 4.0 if has_front_line else -12.0


def reach_bonus(card_name: str, position: tuple[int, int], gs: "GameState") -> float:
    """Reward placement positions where the attack pattern covers more cells.

    HF (small_cross + small_x) reaches 3 cells from a corner vs 8 from center —
    a corner placement wastes more than half the unit's range. ASS and TANK have
    the same problem to lesser degrees. ADC (large_cross) covers 6 cells from any
    position so its reach bonus is uniform. AP / APT / SP use nearest/farthest
    and get 0 (their range is enemy-dependent, not cell-based).
    """
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
    """If placing `card_name` at `position` would let it kill an enemy SAME TURN, score that.

    Only cards that come off the bench non-numb (currently ASS) can attack the turn
    they're played. For everything else this returns 0 — the card has to wait a turn,
    so it's not a guaranteed kill.
    """
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
            continue  # can't be killed this turn — don't count as a lethal setup
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
    """Score a (card_name, position) candidate placement. Higher = better."""
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
    """Score moving `card` (currently in `moving=True` state) to `dest`.

    Orange units have unique after_movement effects — score them faction-specifically:
    - ADCO: after_movement re-fires attack from destination, so reward number of
      enemies in the destination's large_cross.
    - LFO: after_movement deals damage to nearest enemy from destination.
    - HFO: after_movement adds +damage; placement safety matters more.
    - ASSO: after_movement sets anger; reward landing where small_x has a killable enemy.
    Default: prefer destinations that bring the unit's attack pattern over more enemies.
    """
    dx, dy = dest
    targets = attack_targets_from_pos(gs, card.owner, dx, dy, card.attack_types)

    if card.job_and_color == "ADCO":
        return float(sum(min(card.damage, t.health) * 2.0 for t in targets))

    if card.job_and_color == "LFO":
        from campaign.ai_query import enemy_cards, manhattan
        enemies = enemy_cards(gs, card.owner)
        if not enemies:
            return 0.0
        nearest = min(manhattan((dx, dy), (e.board_x, e.board_y)) for e in enemies)
        return 6.0 - nearest

    if card.job_and_color == "HFO":
        from campaign.ai_query import position_safety
        # HFO's after_movement adds +1 extra_damage. Score the destination by what its
        # *next* swing (base + current + 1) could do across its 8-cell reach.
        projected_damage = card.damage + card.extra_damage + 1
        return position_safety(gs, dx, dy) + len(targets) * projected_damage * 0.6

    if card.job_and_color == "ASSO":
        # Look for a kill-shot from the new position (small_x).
        for t in targets:
            effective = card.damage - max(0, t.armor)
            if effective > 0 and t.health <= effective:
                return 20.0 + t.damage * 2.0
        return float(len(targets) * 2.0)

    # Generic: prefer destinations with more enemies in attack range.
    return float(len(targets) * 1.5)


def evaluate_attack(attacker: "Card", gs: "GameState") -> tuple[float, "Card | None"]:
    """Score 'attacker performs its attack now'. Returns (score, best_inferred_target).

    Score may be negative (e.g. all candidates are numb or suicidal); caller decides
    whether to act via attack_min_score. Returns (-1, None) when the attacker can't
    legally attack at all (numb or no targets in range).
    """
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
    for target in targets:
        s = 0.0

        effective_damage = attacker.damage + attacker.extra_damage
        if target.armor >= effective_damage:
            s += 5.0
        elif target.health <= effective_damage - max(0, target.armor) and not _is_anger_immortal(target):
            s += 100.0 + target.damage * 10.0 + attack_denial_bonus(target)
        else:
            # Either chip damage, or hitting an anger-immortal target (can't be killed this turn).
            s += min(effective_damage, target.health) * 2.0
            followup = followup_kill_bonus(attacker, target, gs, effective_damage)
            s += followup
            if followup == 0.0:
                s -= WASTED_CHIP_PENALTY

        s += target.damage * 3.0
        s += target_priority_bonus(target)

        # Self-suicide penalty: skip if attacker is anger-immortal (HFR @ 0 HP).
        if target.damage >= attacker.health and not target.numbness and not attacker_immortal:
            s -= 50.0

        if target.numbness:
            s -= 20.0

        if s > best_score:
            best_score = s
            best_target = target

    return best_score, best_target


def _is_anger_immortal(card: "Card") -> bool:
    """HFR's ability gives it `anger` when self-damage drops it to 0 HP — at which point
    `can_be_killed` returns False until settle. Treat as effectively un-killable this turn.
    """
    return card.job_and_color == "HFR" and getattr(card, "anger", False)
