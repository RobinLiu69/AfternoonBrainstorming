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

"""Which cards exist, and which of them a run may offer."""

from __future__ import annotations

from cards.factory import CardFactory
from shared import card_code

from tower.content import (
    ENCHANTS, FACTION_NAMES, JOBS, MAGIC_POOL, UNIVERSAL_FACTIONS,
)


# longest first so "ADCBR" reads as Brown, not Red, and "APDKG" as DarkGreen
COLOR_TAGS: tuple[str, ...] = tuple(sorted(FACTION_NAMES, key=len, reverse=True))

# codes that exist as classes but are never held in a deck
NON_DECK_CODES: frozenset[str] = frozenset({"CUBE", "SHADOW", "LUCKYBLOCK", "MOVE", "HEAL", "CUBES"})


def color_tag_of(code: str) -> str:
    plain = card_code.plain_code(code)
    for tag in COLOR_TAGS:
        if plain.endswith(tag):
            return tag
    return ""


def job_of(code: str) -> str:
    plain = card_code.plain_code(code)
    tag = color_tag_of(plain)
    return plain[: len(plain) - len(tag)] if tag else plain


def is_magic(code: str) -> bool:
    return card_code.plain_code(code) in MAGIC_POOL


def all_unit_codes() -> list[str]:
    CardFactory.register_all()
    return sorted(c for c in CardFactory._registry if c not in NON_DECK_CODES)


def faction_units(tag: str) -> list[str]:
    return [c for c in all_unit_codes() if color_tag_of(c) == tag]


def run_unit_pool(factions) -> list[str]:
    """Every unit this run may offer: the universal factions plus the drafted ones."""
    tags = list(UNIVERSAL_FACTIONS)
    tags += [t for t in factions if t not in UNIVERSAL_FACTIONS]
    pool: list[str] = []
    for tag in tags:
        pool.extend(faction_units(tag))
    return pool


def run_card_pool(factions) -> list[str]:
    return run_unit_pool(factions) + list(MAGIC_POOL)


def valid_codes() -> set[str]:
    CardFactory.register_all()
    return set(CardFactory._registry) | set(MAGIC_POOL)


def is_valid_code(code: str) -> bool:
    plain = card_code.plain_code(code)
    if plain not in valid_codes():
        return False
    return all(key in ENCHANTS for key in card_code.enchant_keys(code))


def display_name(code: str) -> str:
    """`TANKW*sharp` -> `TANKW [Sharp]`."""
    keys = card_code.enchant_keys(code)
    if not keys:
        return code
    labels = ", ".join(ENCHANTS[k]["label"] for k in keys if k in ENCHANTS)
    return f"{card_code.base_code(code)} [{labels}]"


def enchant_lines(code: str) -> list[str]:
    return [ENCHANTS[k]["text"] for k in card_code.enchant_keys(code) if k in ENCHANTS]


MAGIC_PRICE: int = 45
UNIT_PRICE: int = 65
BIG_UNIT_PRICE: int = 75
ENCHANT_SURCHARGE: int = 30

# the universal factions turn up whatever you drafted, so they turn up rarely
UNIVERSAL_REWARD_WEIGHT: float = 0.35


def card_price(code: str) -> int:
    plain = card_code.plain_code(code)
    if plain in MAGIC_POOL:
        return MAGIC_PRICE
    job = job_of(plain)
    price = BIG_UNIT_PRICE if job in ("TANK", "HF") else UNIT_PRICE
    if card_code.enchant_keys(code):
        price += ENCHANT_SURCHARGE
    return price


def is_universal(code: str) -> bool:
    return color_tag_of(code) in UNIVERSAL_FACTIONS


def reward_weight(code: str) -> float:
    return UNIVERSAL_REWARD_WEIGHT if is_universal(code) else 1.0


def weighted_pick(codes: list[str], rng) -> str:
    """Pick one code, weighted so the universal factions stay uncommon."""
    if not codes:
        return ""
    return rng.choices(codes, weights=[reward_weight(c) for c in codes])[0]


def deck_summary(deck) -> dict[str, int]:
    counts: dict[str, int] = {}
    for code in deck:
        name = card_code.base_code(code)
        counts[name] = counts.get(name, 0) + 1
    return counts


def spell_count(deck) -> int:
    return sum(1 for c in deck if is_magic(c))


def all_jobs_are(deck, job: str) -> bool:
    units = [c for c in deck if not is_magic(c)]
    return bool(units) and all(job_of(c) == job for c in units)


def jobs_present(deck) -> set[str]:
    return {job_of(c) for c in deck if not is_magic(c)} & set(JOBS)
