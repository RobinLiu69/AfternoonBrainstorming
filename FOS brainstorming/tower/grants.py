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

"""Turning a reward into run state, including the screens that ask the player.

Everything here may open a screen, so it takes a ``GameScreen``.  The pure
bookkeeping lives in ``run_state``.
"""

from __future__ import annotations

import random
from typing import Optional

from shared.setting import WHITE
from core.game_screen import GameScreen

from tower import card_picker, card_pool, choice_screen, run_state, ui_common
from tower.content import BLESSING_ENCHANTS, ENCHANTS, RELICS

MAGIC_REWARD_WEIGHT: float = 0.12

# turning a reward down pays nothing - skipping is for keeping your deck lean,
# not a way to farm gold
SKIP_CARD_GOLD: int = 0
DECLINE_RELIC_GOLD: int = 0


# --------------------------------------------------------------------------
# cards
# --------------------------------------------------------------------------

def card_options(run: dict, rng: random.Random, count: int = 3) -> list[str]:
    """Reward and shop cards: mostly units of the chosen factions.

    Spells are rare, and White units are rarer than the factions the player
    drafted - the starter deck is already all White.
    """
    units = card_pool.run_unit_pool(run["factions"])
    magic = list(card_pool.MAGIC_POOL)
    picks: list[str] = []

    while len(picks) < count and (units or magic):
        if magic and (not units or rng.random() < MAGIC_REWARD_WEIGHT):
            code = magic.pop(rng.randrange(len(magic)))
        else:
            code = card_pool.weighted_pick(units, rng)
            units.remove(code)
        if code not in picks:
            picks.append(code)
    return picks


def grant_card(game_screen: GameScreen, run: dict, code: str) -> bool:
    """Add a card, spending a Forgetting Orb if deck and bench are both full."""
    slot = run_state.add_card(run, code)
    if slot in ("deck", "bench"):
        return True
    if slot == "full":
        return False

    picked = card_picker.main(
        game_screen, run,
        f"deck and bench are full - burn a card for {card_pool.display_name(code)}?",
        subtitle=f"this spends 1 Forgetting Orb  (you have {run['orbs']})",
    )
    if picked is None:
        return False
    zone, index = picked
    return run_state.consume_orb_for(run, code, zone, index)


def offer_cards(game_screen: GameScreen, run: dict, rng: random.Random,
                title: str = "Pick a card", count: int = 3,
                allow_skip: bool = True) -> Optional[str]:
    codes = card_options(run, rng, count)
    if not codes:
        return None
    options = [{"label": card_pool.display_name(c), "color": WHITE, "card": c} for c in codes]
    choice = choice_screen.main(
        game_screen, title, options, run=run,
        subtitle=slot_hint(run),
        skip_label="take none" if allow_skip else "",
    )
    if choice is None:
        return None
    if choice == choice_screen.SKIP:
        run["gold"] += SKIP_CARD_GOLD
        return None
    code = codes[choice]
    return code if grant_card(game_screen, run, code) else None


def slot_hint(run: dict) -> str:
    slot = run_state.next_slot(run)
    if slot == "deck":
        return f"goes to your deck  ({len(run['deck'])}/{run_state.deck_limit(run)})"
    if slot == "bench":
        return f"deck is full - goes to the bench  ({len(run['bench'])}/{run_state.bench_limit(run)})"
    if slot == "orb":
        return "deck and bench are full - costs 1 Forgetting Orb"
    return "deck and bench are full - you cannot take another card"


# --------------------------------------------------------------------------
# relics
# --------------------------------------------------------------------------

def relic_option(relic_id: str) -> dict:
    relic = RELICS[relic_id]
    return {
        "label": relic["label"],
        "lines": [relic["text"]],
        "color": ui_common.relic_color(relic_id),
    }


def grant_relic(game_screen: GameScreen, run: dict, relic_id: str,
                rng: Optional[random.Random] = None) -> bool:
    if not run_state.add_relic(run, relic_id):
        return False
    action = run_state.relic_pickup_action(relic_id)
    if action.get("enchant"):
        _apply_pickup_enchant(game_screen, run, relic_id, action, rng or random.Random())
    return True


def _apply_pickup_enchant(game_screen: GameScreen, run: dict, relic_id: str,
                          action: dict, rng: random.Random) -> None:
    key = action["enchant"]
    label = ENCHANTS[key]["label"]
    if action.get("random"):
        run_state.enchant_random_card(run, key, rng)
        return
    picked = card_picker.main(
        game_screen, run, f"{RELICS[relic_id]['label']}: enchant a card with {label}",
        subtitle=ENCHANTS[key]["text"], cancellable=False,
    )
    if picked is None:
        run_state.enchant_random_card(run, key, rng)
        return
    zone, index = picked
    run_state.enchant_card(run, zone, index, key)


def offer_relic(game_screen: GameScreen, run: dict, rng: random.Random,
                title: str = "A relic", tier: str = "",
                include_special: bool = False,
                decline_gold: int = DECLINE_RELIC_GOLD) -> Optional[str]:
    """One relic, take it or leave it.

    Picking the best of three made every drop an upgrade; a single relic makes
    the run's shape depend on what the tower hands you.
    """
    pool = run_state.relic_offers(run, tier=tier, include_special=include_special)
    if not pool:
        return None

    relic_id = rng.choice(pool)
    decline = {"label": "leave it", "color": ui_common.DIM,
               "lines": [f"+{decline_gold} gold"] if decline_gold else []}
    choice = choice_screen.main(game_screen, title,
                                [relic_option(relic_id), decline], run=run,
                                subtitle="take it or leave it")
    if choice != 0:
        if decline_gold:
            run["gold"] += decline_gold
        return None
    return relic_id if grant_relic(game_screen, run, relic_id, rng) else None


def choose_relic(game_screen: GameScreen, run: dict, rng: random.Random,
                 title: str, tier: str = "", count: int = 3,
                 include_special: bool = False,
                 decline_gold: int = 0, declinable: bool = False) -> Optional[str]:
    """Pick one of several.  Boss spoils earn a real choice; so does deciding
    which curse hurts least.  Everything else gets ``offer_relic`` instead."""
    pool = run_state.relic_offers(run, tier=tier, include_special=include_special)
    if not pool:
        return None

    label = "leave them"
    if decline_gold:
        label = f"leave them  (+{decline_gold} gold)"

    picks = rng.sample(pool, min(count, len(pool)))
    choice = choice_screen.main(
        game_screen, title, [relic_option(r) for r in picks], run=run,
        skip_label=label if (declinable or decline_gold) else "",
    )
    if choice == choice_screen.SKIP:
        if decline_gold:
            run["gold"] += decline_gold
        return None
    if choice is None:
        if declinable or decline_gold:
            return None
        # a choice you have to make - backing out takes the first one
        choice = 0
    relic_id = picks[choice]
    return relic_id if grant_relic(game_screen, run, relic_id, rng) else None


def grant_random_relic(game_screen: GameScreen, run: dict, rng: random.Random,
                       tier: str = "") -> Optional[str]:
    pool = run_state.relic_offers(run, tier=tier)
    if not pool:
        return None
    relic_id = rng.choice(pool)
    return relic_id if grant_relic(game_screen, run, relic_id, rng) else None


# --------------------------------------------------------------------------
# opening blessings
# --------------------------------------------------------------------------

def apply_blessing(game_screen: GameScreen, run: dict, blessing_id: str,
                   rng: random.Random) -> None:
    if blessing_id == "two_cards":
        offer_cards(game_screen, run, rng, "Recruit a card  (1 of 2)", allow_skip=False)
        offer_cards(game_screen, run, rng, "Recruit a card  (2 of 2)", allow_skip=False)

    elif blessing_id == "one_orb":
        run["orbs"] += 1

    elif blessing_id == "one_relic":
        grant_random_relic(game_screen, run, rng)

    elif blessing_id == "bench_plus":
        run["bench_bonus"] += 2

    elif blessing_id == "enchant_unit":
        key = rng.choice(list(BLESSING_ENCHANTS))
        picked = card_picker.main(
            game_screen, run, f"Enchant a unit with {ENCHANTS[key]['label']}",
            subtitle=ENCHANTS[key]["text"], cancellable=False,
            allowed=lambda zone, index, code: not card_pool.is_magic(code),
        )
        if picked is None:
            run_state.enchant_random_card(run, key, rng)
        else:
            run_state.enchant_card(run, picked[0], picked[1], key)

    elif blessing_id == "orbs_and_curse":
        run["orbs"] += 3
        choose_relic(game_screen, run, rng, "Take one curse", tier="curse")

    elif blessing_id == "power_and_curse":
        grant_random_relic(game_screen, run, rng, tier="power")
        grant_random_relic(game_screen, run, rng, tier="curse")
