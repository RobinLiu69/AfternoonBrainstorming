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

"""Everything that reads or writes the tower run dict."""

from __future__ import annotations

import random

from shared import card_code

from tower import card_pool, tower_map
from tower.content import (
    ADDITIVE_EFFECTS, BENCH_LIMIT, BLESSING_POOLS, BLESSING_POOL_ORDER,
    DECK_LIMIT, ENCHANTS, FLAG_EFFECTS, JOB_EFFECTS, MAX_EFFECTS,
    MIN_EFFECTS, MULTIPLIED_EFFECTS, RELICS, STARTER_DECK,
)


def new_run(factions, seed: int | None = None) -> dict:
    seed = random.randint(0, 2 ** 31 - 1) if seed is None else int(seed)
    factions = list(factions)
    return {
        "seed": seed,
        "factions": factions,
        "act": tower_map.FIRST_ACT,
        "layer": tower_map.BLESSING_LAYER,
        "picks": {},
        "maps": tower_map.build_run_maps(seed, factions),
        "deck": list(STARTER_DECK),
        "bench": [],
        "bench_bonus": 0,
        "orbs": 0,
        "gold": 0,
        "debt": 0,
        "relics": [],
        "pending": None,
        "shop_spent": False,
        "shop_rerolls": 0,
        "battles_won": 0,
        "events_seen": [],
        "altar_deals_used": [],
    }


# --------------------------------------------------------------------------
# rng
# --------------------------------------------------------------------------

def layer_rng(run: dict, salt: int = 0) -> random.Random:
    return random.Random(
        run["seed"] * 1000003 + run["act"] * 7919 + run["layer"] * 97 + salt
    )


# --------------------------------------------------------------------------
# effects
# --------------------------------------------------------------------------

def _merge(target: dict, effects: dict) -> None:
    for key, value in effects.items():
        if key in JOB_EFFECTS:
            bucket = target.setdefault(key, {})
            for job, amount in value.items():
                bucket[job] = bucket.get(job, 0) + amount
        elif key in ADDITIVE_EFFECTS:
            target[key] = target.get(key, 0) + value
        elif key in MULTIPLIED_EFFECTS:
            target[key] = target.get(key, 1.0) * value
        elif key in MAX_EFFECTS:
            target[key] = max(target.get(key, 0), value)
        elif key in MIN_EFFECTS:
            current = target.get(key, 0)
            target[key] = value if not current else min(current, value)
        elif key in FLAG_EFFECTS:
            target[key] = 1


def effects_from_relics(relic_ids, extra: dict | None = None) -> dict:
    """Merged effect dict for an arbitrary relic list - used for enemy relics."""
    out: dict = {"gold_mult": 1.0, "shop_discount": 1.0}
    for relic_id in relic_ids:
        relic = RELICS.get(relic_id)
        if relic:
            _merge(out, relic.get("effects", {}))
    if extra:
        _merge(out, extra)
    return out


def merged_effects(run: dict) -> dict:
    out: dict = {"gold_mult": 1.0, "shop_discount": 1.0}
    for relic_id in run.get("relics", []):
        relic = RELICS.get(relic_id)
        if relic:
            _merge(out, relic.get("effects", {}))

    cards = all_cards(run)
    if "demon_emblem" in run.get("relics", []) and card_pool.spell_count(cards) > 6:
        _merge(out, {"unit_hp_plus": 2, "unit_damage_plus": 1})
    if "tank_bloodline" in run.get("relics", []) and card_pool.all_jobs_are(cards, "TANK"):
        _merge(out, {"job_hp_plus": {"TANK": 3}, "double_tank_effects": 1})
    return out


def battle_effects(run: dict) -> dict:
    """Player-side effects that the battle controller needs."""
    return merged_effects(run)


# --------------------------------------------------------------------------
# deck and bench
# --------------------------------------------------------------------------

def all_cards(run: dict) -> list[str]:
    return list(run["deck"]) + list(run["bench"])


def deck_limit(run: dict) -> int:
    return int(merged_effects(run).get("deck_limit_override", DECK_LIMIT) or DECK_LIMIT)


def bench_limit(run: dict) -> int:
    return (BENCH_LIMIT + int(run.get("bench_bonus", 0))
            + int(merged_effects(run).get("bench_plus", 0)))


def free_bench(run: dict) -> bool:
    return bool(merged_effects(run).get("free_bench"))


def deck_is_full(run: dict) -> bool:
    return len(run["deck"]) >= deck_limit(run)


def bench_is_full(run: dict) -> bool:
    return len(run["bench"]) >= bench_limit(run)


def next_slot(run: dict) -> str:
    """Where a new card would land: deck first, then bench."""
    if not deck_is_full(run):
        return "deck"
    if not bench_is_full(run):
        return "bench"
    return "orb" if run.get("orbs", 0) > 0 else "full"


def add_card(run: dict, code: str) -> str:
    """Put a card in the deck or bench.  Returns the slot actually used.

    ``"orb"`` means both are full but the player owns a Forgetting Orb, so the
    caller must ask which card to burn and then call ``consume_orb_for``.
    ``"full"`` means the card cannot be taken at all.
    """
    slot = next_slot(run)
    if slot in ("deck", "bench"):
        run[slot].append(code)
    return slot


def consume_orb_for(run: dict, code: str, zone: str, index: int) -> bool:
    """Spend an orb to remove deck/bench[index], then add ``code`` in its place."""
    if run.get("orbs", 0) <= 0:
        return False
    if not remove_card(run, zone, index):
        return False
    run["orbs"] -= 1
    run[zone].insert(min(index, len(run[zone])), code)
    return True


def remove_card(run: dict, zone: str, index: int) -> bool:
    target = run.get(zone)
    if not isinstance(target, list) or not (0 <= index < len(target)):
        return False
    target.pop(index)
    return True


def spend_orb_to_remove(run: dict, zone: str, index: int) -> bool:
    if run.get("orbs", 0) <= 0:
        return False
    if not remove_card(run, zone, index):
        return False
    run["orbs"] -= 1
    return True


def swap_deck_bench(run: dict, deck_index: int, bench_index: int) -> bool:
    if not (0 <= deck_index < len(run["deck"])):
        return False
    if not (0 <= bench_index < len(run["bench"])):
        return False
    run["deck"][deck_index], run["bench"][bench_index] = (
        run["bench"][bench_index], run["deck"][deck_index],
    )
    return True


def enchant_card(run: dict, zone: str, index: int, key: str) -> bool:
    """A card holds one enchantment - a new one replaces whatever was there."""
    if key not in ENCHANTS:
        return False
    target = run.get(zone)
    if not isinstance(target, list) or not (0 <= index < len(target)):
        return False
    target[index] = card_code.with_enchants(target[index], [key])
    return True


def enchant_random_card(run: dict, key: str, rng: random.Random) -> str:
    zones = [("deck", i) for i in range(len(run["deck"]))]
    zones += [("bench", i) for i in range(len(run["bench"]))]
    if not zones:
        return ""
    zone, index = rng.choice(zones)
    enchant_card(run, zone, index, key)
    return run[zone][index]


def enchanted_cards(run: dict) -> list[tuple[str, int]]:
    out = [("deck", i) for i, c in enumerate(run["deck"]) if card_code.is_enchanted(c)]
    out += [("bench", i) for i, c in enumerate(run["bench"]) if card_code.is_enchanted(c)]
    return out


# --------------------------------------------------------------------------
# relics
# --------------------------------------------------------------------------

def has_relic(run: dict, relic_id: str) -> bool:
    return relic_id in run.get("relics", [])


def curse_immune(run: dict) -> bool:
    return bool(merged_effects(run).get("curse_immune"))


def can_take_relic(run: dict, relic_id: str) -> bool:
    relic = RELICS.get(relic_id)
    if relic is None or has_relic(run, relic_id):
        return False
    if relic["tier"] == "curse" and curse_immune(run):
        return False
    faction = relic.get("faction")
    if faction and faction not in run.get("factions", []):
        return False
    group = relic.get("group")
    if group and any(RELICS.get(r, {}).get("group") == group for r in run["relics"]):
        return False
    return True


def relic_offers(run: dict, tier: str = "", source: str = "",
                 include_special: bool = False) -> list[str]:
    """Relics on offer.  Curses are never offered by name, and the special tier
    only shows up where the caller allows it - which is boss spoils only."""
    out: list[str] = []
    for relic_id, relic in sorted(RELICS.items()):
        if tier and relic["tier"] != tier:
            continue
        if not tier and relic["tier"] == "curse":
            continue
        if not tier and relic["tier"] == "special" and not include_special:
            continue
        relic_source = relic.get("source", "")
        if relic_source and source and relic_source != source:
            continue
        if relic_source == "shop" and source != "shop":
            continue
        if relic_source == "drop" and source == "shop":
            continue
        if can_take_relic(run, relic_id):
            out.append(relic_id)
    return out


def add_relic(run: dict, relic_id: str) -> bool:
    if not can_take_relic(run, relic_id):
        return False
    run["relics"].append(relic_id)
    return True


def relic_pickup_action(relic_id: str) -> dict:
    return dict(RELICS.get(relic_id, {}).get("on_pickup", {}))


# --------------------------------------------------------------------------
# gold
# --------------------------------------------------------------------------

def gold_multiplier(run: dict) -> float:
    return float(merged_effects(run).get("gold_mult", 1.0))


def shop_discount(run: dict) -> float:
    return float(merged_effects(run).get("shop_discount", 1.0))


def award_gold(run: dict, base: int) -> int:
    """Income arrives net of any debt - the Credit Card is paid off first."""
    amount = int(base * gold_multiplier(run))
    repaid = min(run.get("debt", 0), amount)
    if repaid:
        run["debt"] -= repaid
    run["gold"] += amount - repaid
    return amount - repaid


def credit_limit(run: dict) -> int:
    return int(merged_effects(run).get("credit_limit", 0))


def credit_available(run: dict) -> int:
    return max(0, credit_limit(run) - run.get("debt", 0))


def affordable(run: dict, amount: int) -> bool:
    return run["gold"] + credit_available(run) >= amount


def victory_bonus_gold(run: dict) -> int:
    """Ship in a Bottle: a payout per pirate card in the deck after a win."""
    per_pirate = int(merged_effects(run).get("victory_gold_per_pirate", 0))
    if not per_pirate:
        return 0
    pirates = sum(1 for code in run["deck"] if card_pool.color_tag_of(code) == "C")
    return per_pirate * pirates


def spend_gold(run: dict, amount: int) -> bool:
    """Pay in gold, borrowing the shortfall if a Credit Card allows it."""
    if not affordable(run, amount):
        return False
    borrowed = max(0, amount - run["gold"])
    if borrowed:
        run["debt"] = run.get("debt", 0) + borrowed
    run["gold"] -= amount - borrowed
    run["shop_spent"] = True
    return True


def floor_upkeep(run: dict) -> dict:
    """Per-layer economy: wallet leak, index fund interest, credit card debt."""
    effects = merged_effects(run)
    report = {"upkeep": 0, "interest": 0, "debt": 0}

    leak = int(effects.get("gold_per_floor", 0))
    if leak:
        before = run["gold"]
        run["gold"] = max(0, run["gold"] + leak)
        report["upkeep"] = run["gold"] - before

    rate = float(effects.get("interest_rate", 0.0))
    if rate and not run.get("shop_spent") and run["gold"] > 0:
        gain = int(run["gold"] * rate)
        run["gold"] += gain
        report["interest"] = gain

    debt_rate = float(effects.get("debt_rate", 0.0))
    if debt_rate and run.get("debt", 0) > 0:
        growth = int(run["debt"] * debt_rate)
        run["debt"] += growth
        report["debt"] = growth

    return report


# --------------------------------------------------------------------------
# blessings
# --------------------------------------------------------------------------

def blessing_offers(run: dict) -> list[dict]:
    """One offer out of each pool, so the three never rhyme."""
    rng = layer_rng(run, salt=11)
    return [rng.choice(list(BLESSING_POOLS[pool])) for pool in BLESSING_POOL_ORDER]


# --------------------------------------------------------------------------
# map navigation
# --------------------------------------------------------------------------

def current_map(run: dict) -> dict:
    return run["maps"][run["act"] - tower_map.FIRST_ACT]


def current_layer(run: dict) -> dict:
    return tower_map.resolve_layer(current_map(run), run["layer"], run["picks"])


def record_pick(run: dict, pick: int) -> None:
    run["picks"][str(run["layer"])] = pick


def pick_for(run: dict, layer_index: int):
    return run["picks"].get(str(layer_index))


def is_last_layer(run: dict) -> bool:
    return run["layer"] >= tower_map.boss_layer(run["act"])


def is_final_battle(run: dict) -> bool:
    """The last boss of the last act - winning it ends the climb."""
    return run["act"] >= tower_map.LAST_ACT and is_last_layer(run)


def advance_layer(run: dict) -> str:
    """Move to the next layer, or the next act.  Returns "layer"|"act"|"win"."""
    run["pending"] = None
    if run["layer"] < tower_map.boss_layer(run["act"]):
        run["layer"] += 1
        floor_upkeep(run)
        return "layer"
    if run["act"] >= tower_map.LAST_ACT:
        return "win"
    run["act"] += 1
    run["layer"] = 1
    run["picks"] = {}
    floor_upkeep(run)
    return "act"
