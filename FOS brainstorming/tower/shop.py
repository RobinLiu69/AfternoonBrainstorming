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

"""Shop stock and pricing.  Pure data, no pygame."""

from __future__ import annotations

import random

from tower import card_pool, grants, run_state
from tower.content import RELICS

STOCK_SIZE: int = 8
ORB_PRICE: int = 120
REROLL_PRICE: int = 50
CURSE_REMOVAL_PRICE: int = 100
SELL_RATE: float = 0.33

RELIC_PRICE: dict[str, int] = {
    "common": 150, "rare": 220, "power": 300, "special": 380, "curse": 0,
}


def relic_price(relic_id: str) -> int:
    return RELIC_PRICE.get(RELICS.get(relic_id, {}).get("tier", "common"), 150)


def sell_price(relic_id: str) -> int:
    return int(relic_price(relic_id) * SELL_RATE)


def is_curse(relic_id: str) -> bool:
    return RELICS.get(relic_id, {}).get("tier") == "curse"


def price_of(item: dict, discount: float) -> int:
    return max(1, int(item["price"] * discount))


def generate_stock(run: dict, rng: random.Random) -> dict:
    """Eight slots: exactly one orb, two or three relics, cards for the rest."""
    items: list[dict] = [{"kind": "orb", "price": ORB_PRICE, "sold": False}]

    relic_pool = run_state.relic_offers(run, source="shop")
    wanted = rng.randint(2, 3)
    for relic_id in rng.sample(relic_pool, min(wanted, len(relic_pool))):
        items.append({"kind": "relic", "relic": relic_id,
                      "price": relic_price(relic_id), "sold": False})

    for code in grants.card_options(run, rng, STOCK_SIZE - len(items)):
        items.append({"kind": "card", "card": code,
                      "price": card_pool.card_price(code), "sold": False})

    rng.shuffle(items)
    return {"items": items, "rerolls": 0, "relic_sold": False, "free_rerolls_used": 0}


def free_rerolls(run: dict) -> int:
    return int(run_state.merged_effects(run).get("free_rerolls", 0))


def reroll_allowance(run: dict) -> int:
    return 1 + int(run_state.merged_effects(run).get("extra_rerolls", 0))


def reroll_price(run: dict, stock: dict) -> int:
    if stock["free_rerolls_used"] < free_rerolls(run):
        return 0
    return int(REROLL_PRICE * run_state.shop_discount(run))


def can_reroll(run: dict, stock: dict) -> bool:
    if stock["rerolls"] >= reroll_allowance(run) + free_rerolls(run):
        return False
    return run_state.affordable(run, reroll_price(run, stock))
