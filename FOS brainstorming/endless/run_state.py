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

import random

from campaign.ai_decks import WHITE_DECK

from endless import scaling
from endless.content import (
    RELICS, CURSES, CONSUMABLES, MAGIC_POOL,
    MAX_UNIT_COPIES, MAX_MAGIC_COPIES, card_pool,
    STRONG_CARDS, WEAK_CARDS,
)


_ADDITIVE_KEYS = ("unit_hp_plus", "unit_damage_plus", "hand_plus", "luck_plus")
_JOB_KEYS = ("job_damage_plus", "job_hp_plus")
_PERIODIC_KEYS = ("free_heal_every_n_turns", "free_moving_every_n_turns")


def new_run() -> dict:
    return {
        "seed": random.randint(0, 2**31 - 1),
        "floor": 1,
        "phase": "battle",
        "deck": list(WHITE_DECK),
        "temp_deck": [],
        "coins": 0,
        "relics": [],
        "curses": [],
        "perm_buffs": {},
        "armed_consumables": [],
        "pending": None,
        "shop_counters": {"remove_card": 0, "reroll": 0, "dmg_all": 0, "hp_all": 0},
        "floor_spec": None,
        "prev_kind": "",
    }


def _floor_rng(run: dict, salt: int) -> random.Random:
    return random.Random(run["seed"] * 1000003 + run["floor"] * 97 + salt)


def ensure_floor_spec(run: dict) -> dict:
    if not run.get("floor_spec"):
        run["floor_spec"] = scaling.floor_spec(run["floor"], _floor_rng(run, 0), run.get("prev_kind", ""))
    return run["floor_spec"]


def advance_floor(run: dict) -> None:
    spec = run.get("floor_spec") or {}
    run["prev_kind"] = spec.get("kind", "")
    run["floor"] += 1
    run["phase"] = "battle"
    run["pending"] = None
    run["floor_spec"] = None


def _merge_effect(target: dict, key, value) -> None:
    if key in _JOB_KEYS:
        bucket = target.setdefault(key, {})
        for job, n in value.items():
            bucket[job] = bucket.get(job, 0) + n
    elif key in _PERIODIC_KEYS:
        current = target.get(key, 0)
        target[key] = value if not current else min(current, value)
    elif key in _ADDITIVE_KEYS:
        target[key] = target.get(key, 0) + value


def merged_player_effects(run: dict) -> tuple[dict, dict, dict]:
    player_fx: dict = {}
    curse_ai_fx: dict = {}
    run_fx = {"coin_mult": 1.0, "shop_discount": 1.0}

    sources = [dict(run.get("perm_buffs", {}))]
    sources += [RELICS[r]["effects"] for r in run.get("relics", []) if r in RELICS]
    sources += [CURSES[c]["player_effects"] for c in run.get("curses", []) if c in CURSES]
    sources += [CONSUMABLES[c]["effects"] for c in run.get("armed_consumables", []) if c in CONSUMABLES]

    for effects in sources:
        for key, value in effects.items():
            if key == "coin_mult":
                run_fx["coin_mult"] *= value
            elif key == "shop_discount":
                run_fx["shop_discount"] *= value
            else:
                _merge_effect(player_fx, key, value)

    for c in run.get("curses", []):
        for key, value in CURSES.get(c, {}).get("ai_effects", {}).items():
            _merge_effect(curse_ai_fx, key, value)

    return player_fx, curse_ai_fx, run_fx


def battle_effects(run: dict, spec: dict) -> tuple[dict, dict]:
    player_fx, curse_ai_fx, _run_fx = merged_player_effects(run)
    ai_fx: dict = {}
    for key, value in spec.get("ai_effects", {}).items():
        _merge_effect(ai_fx, key, value)
    for key, value in curse_ai_fx.items():
        _merge_effect(ai_fx, key, value)
    mutation = spec.get("mutation", {})
    for key, value in mutation.items():
        if key.startswith("both_"):
            _merge_effect(player_fx, key[5:], value)
            _merge_effect(ai_fx, key[5:], value)
    return player_fx, ai_fx


def coin_multiplier(run: dict) -> float:
    _p, _a, run_fx = merged_player_effects(run)
    return run_fx["coin_mult"]


def shop_discount(run: dict) -> float:
    _p, _a, run_fx = merged_player_effects(run)
    return run_fx["shop_discount"]


def award_floor_coins(run: dict, spec: dict) -> int:
    coins = int(spec.get("coin_reward", 0) * coin_multiplier(run))
    run["coins"] += coins
    return coins


def card_copies(run: dict, code: str) -> int:
    return run["deck"].count(code) + run["temp_deck"].count(code)


def can_add_card(run: dict, code: str) -> bool:
    limit = MAX_MAGIC_COPIES if code in MAGIC_POOL else MAX_UNIT_COPIES
    return card_copies(run, code) < limit


def generate_reward_options(run: dict, kind: str) -> list[dict]:
    rng = _floor_rng(run, 1)
    options: list[dict] = []
    unowned = [r for r in sorted(RELICS) if r not in run["relics"]]
    if unowned and (kind == "boss" or (run["floor"] >= 3 and rng.random() < 0.25)):
        options.append({"type": "relic", "relic": rng.choice(unowned)})
    pool = [c for c in card_pool() if can_add_card(run, c)]
    rng.shuffle(pool)
    for code in pool:
        if len(options) >= 3:
            break
        options.append({"type": "card", "card": code})
    return options


def _card_price(code: str) -> int:
    if code in MAGIC_POOL:
        return 25
    price = 35 if code.startswith("TANK") or code.startswith("HF") else 30
    if code in STRONG_CARDS:
        price += 10
    elif code in WEAK_CARDS:
        price -= 10
    return price


def generate_shop_stock(run: dict, reroll: int = 0) -> dict:
    rng = _floor_rng(run, 3 + reroll)
    counters = run["shop_counters"]
    items: list[dict] = [
        {"kind": "perm", "stat": "dmg_all", "label": "all units +1 damage",
         "price": 90 + 30 * counters["dmg_all"], "sold": False},
        {"kind": "perm", "stat": "hp_all", "label": "all units +2 HP",
         "price": 70 + 20 * counters["hp_all"], "sold": False},
    ]
    job = rng.choice(["ADC", "AP", "TANK", "HF", "LF", "ASS", "APT", "SP"])
    items.append({"kind": "perm", "stat": "job_dmg", "job": job,
                  "label": f"{job} +1 damage", "price": 45, "sold": False})
    for name in rng.sample(sorted(CONSUMABLES), 2):
        items.append({"kind": "consumable", "item": name,
                      "label": f"{CONSUMABLES[name]['label']} - {CONSUMABLES[name]['text']}",
                      "price": CONSUMABLES[name]["price"], "sold": False})
    unowned_curses = [c for c in sorted(CURSES) if c not in run["curses"]]
    if unowned_curses:
        curse = rng.choice(unowned_curses)
        items.append({"kind": "curse", "item": curse,
                      "label": f"{CURSES[curse]['label']} - {CURSES[curse]['text']}",
                      "curse_text": CURSES[curse]["curse_text"],
                      "price": 40, "sold": False})
    pool = [c for c in card_pool() if can_add_card(run, c)]
    rng.shuffle(pool)
    for code in pool[:3]:
        items.append({"kind": "card", "card": code, "label": code,
                      "price": _card_price(code), "sold": False})
    return {"items": items, "reroll": reroll}


def apply_perm_buff(run: dict, stat: str, job: str = "") -> None:
    perm = run["perm_buffs"]
    if stat == "dmg_all":
        perm["unit_damage_plus"] = perm.get("unit_damage_plus", 0) + 1
        run["shop_counters"]["dmg_all"] += 1
    elif stat == "hp_all":
        perm["unit_hp_plus"] = perm.get("unit_hp_plus", 0) + 2
        run["shop_counters"]["hp_all"] += 1
    elif stat == "job_dmg":
        bucket = perm.setdefault("job_damage_plus", {})
        bucket[job] = bucket.get(job, 0) + 1


def settle_temp_deck(run: dict, consumption: dict[str, int]) -> list[str]:
    lost: list[str] = []
    temp = run["temp_deck"]
    for code, count in consumption.items():
        for _ in range(count):
            if code in temp:
                temp.remove(code)
                lost.append(code)
    return lost
