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

"""Event rooms.

An event is a small screen with a couple of choices.  Each entry declares
which acts it belongs to, whether the run currently qualifies for it, and how
often it should come up; ``pick`` rolls one of the qualifying entries.

Handlers return ``""`` normally, or ``"lose"`` / ``"abandon"`` if the event
turned into a fight that ended the climb.
"""

from __future__ import annotations

import random
from typing import Optional

from shared import card_code
from shared.setting import WHITE
from core.game_screen import GameScreen

from tower import (
    battle_flow, card_picker, card_pool, choice_screen, enemies, grants,
    notice_screen, run_state, ui_common,
)
from tower.content import (
    ARTISAN_ENCHANTS, ENCHANTS, FACTION_NAMES, RELICS,
)

ALTAR_DEALS: tuple[dict, ...] = (
    {"id": "orb", "label": "Sacrifice", "cost": 150,
     "text": "offer 150 gold for a Forgetting Orb"},
    {"id": "relic", "label": "Tribute", "cost": 150,
     "text": "offer 150 gold for a relic"},
    {"id": "unit", "label": "Conscript", "cost": 50,
     "text": "offer 50 gold for a random unit"},
    {"id": "spell", "label": "Incantation", "cost": 50,
     "text": "offer 50 gold for a random spell"},
    {"id": "card_choice", "label": "Petition", "cost": 100,
     "text": "offer 100 gold to choose a card"},
    {"id": "gold_50", "label": "Small Blessing", "cost": 0,
     "text": "the altar gives you 50 gold"},
    {"id": "gold_100", "label": "Blessing", "cost": 0,
     "text": "the altar gives you 100 gold"},
    {"id": "gold_150", "label": "Great Blessing", "cost": 0,
     "text": "the altar gives you 150 gold"},
)

ALTAR_OFFER_COUNT: int = 2

VISITOR_UNIT_PRICE: int = 150
VISITOR_RELIC_PRICE: int = 250
PRISM_GOLD: int = 50
WANDERER_GOLD: int = 75
HAGGLE_WIN: int = 150
HAGGLE_LOSS: int = 25
STATUE_ORBS: int = 1


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _run_faction(run: dict, rng: random.Random) -> str:
    factions = run.get("factions") or ["W"]
    return rng.choice(list(factions))


def _leave(label: str = "leave") -> dict:
    return {"label": label, "lines": [], "color": ui_common.DIM}


def _option(label: str, text: str, color=WHITE, affordable: bool = True) -> dict:
    return {"label": label, "lines": [text],
            "color": color if affordable else ui_common.DIM}


def _enchanted_indices(run: dict, curse_free: bool = False) -> set[tuple[str, int]]:
    picks = set()
    for zone, index in run_state.enchanted_cards(run):
        keys = card_code.enchant_keys(run[zone][index])
        if curse_free and any(ENCHANTS.get(k, {}).get("kind") == "curse" for k in keys):
            continue
        picks.add((zone, index))
    return picks


# --------------------------------------------------------------------------
# events
# --------------------------------------------------------------------------

def _altar(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    """Two of the eight rites are on offer, so there is always a decision."""
    tag = _run_faction(run, rng)
    deals = rng.sample(list(ALTAR_DEALS), ALTAR_OFFER_COUNT)

    options = [_option(deal["label"], deal["text"], ui_common.GOLD,
                       run_state.affordable(run, deal["cost"]))
               for deal in deals]
    options.append(_leave())

    choice = choice_screen.main(
        game_screen, f"{FACTION_NAMES[tag]} Altar", options, run=run,
        subtitle="the stone hums when you step close")
    if choice is None or choice >= len(deals):
        return ""

    deal = deals[choice]
    if not run_state.affordable(run, deal["cost"]):
        return ""
    if deal["cost"] and not run_state.spend_gold(run, deal["cost"]):
        return ""

    if deal["id"] == "orb":
        run["orbs"] += 1
        notice_screen.main(game_screen, "Accepted", ["+1 Forgetting Orb"],
                           run=run, color=ui_common.ORB)
    elif deal["id"] == "relic":
        grants.grant_random_relic(game_screen, run, rng)
    elif deal["id"] == "unit":
        pool = card_pool.faction_units(tag) or card_pool.run_unit_pool(run["factions"])
        grants.grant_card(game_screen, run, rng.choice(pool))
    elif deal["id"] == "spell":
        grants.grant_card(game_screen, run, rng.choice(list(card_pool.MAGIC_POOL)))
    elif deal["id"] == "card_choice":
        grants.offer_cards(game_screen, run, rng, "The altar offers", allow_skip=False)
    else:
        gold = int(deal["id"].split("_")[1])
        run["gold"] += gold
        notice_screen.main(game_screen, "Accepted", [f"+{gold} gold"],
                           run=run, color=ui_common.GOLD)
    return ""


def _altar_available(run: dict) -> bool:
    return True


def _trade_pairs(run: dict, rng: random.Random) -> list[tuple[str, str]]:
    """Always two trades on the table - with one relic, two things to swap it for."""
    mine = rng.sample(list(run["relics"]), min(2, len(run["relics"])))
    pool = run_state.relic_offers(run)
    if not pool:
        return []
    theirs = rng.sample(pool, min(2, len(pool)))

    if len(mine) >= 2 and len(theirs) >= 2:
        return [(mine[0], theirs[0]), (mine[1], theirs[1])]
    if len(theirs) >= 2:
        return [(mine[0], theirs[0]), (mine[0], theirs[1])]
    if len(mine) >= 2:
        return [(mine[0], theirs[0]), (mine[1], theirs[0])]
    return [(mine[0], theirs[0])]


def _relic_trader(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    pairs = _trade_pairs(run, rng)
    if not pairs:
        return ""

    options = [{
        "label": f"{ui_common.relic_label(mine)}  ->  {ui_common.relic_label(theirs)}",
        "lines": [ui_common.relic_text(theirs)],
        "color": ui_common.relic_color(theirs),
    } for mine, theirs in pairs]
    options.append(_leave())

    choice = choice_screen.main(game_screen, "Relic Trader", options, run=run,
                                subtitle="one of yours for one of mine")
    if choice is None or choice >= len(pairs):
        return ""

    mine, theirs = pairs[choice]
    run["relics"].remove(mine)
    grants.grant_relic(game_screen, run, theirs, rng)
    return ""


def _relic_trader_available(run: dict) -> bool:
    if not run.get("relics"):
        return False
    return len(run_state.relic_offers(run)) >= 2 or len(run["relics"]) >= 2


def _tinker(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    grade = rng.choice(list(ARTISAN_ENCHANTS))
    reforgeable = _enchanted_indices(run, curse_free=True)

    options = [
        _option("strip", "remove an enchantment from a card", ui_common.HILITE),
        _option("reforge", f"turn a card's enchantment into {ENCHANTS[grade]['label']}",
                ui_common.HILITE, bool(reforgeable)),
        _leave(),
    ]
    choice = choice_screen.main(game_screen, "Tinker", options, run=run,
                                subtitle=ENCHANTS[grade]["text"])

    if choice == 0:
        enchanted = _enchanted_indices(run)
        picked = card_picker.main(
            game_screen, run, "Strip which card?",
            allowed=lambda zone, index, code: (zone, index) in enchanted)
        if picked is not None:
            zone, index = picked
            run[zone][index] = card_code.remove_enchants(run[zone][index])

    elif choice == 1 and reforgeable:
        picked = card_picker.main(
            game_screen, run, f"Reforge into {ENCHANTS[grade]['label']}?",
            allowed=lambda zone, index, code: (zone, index) in reforgeable)
        if picked is not None:
            zone, index = picked
            run[zone][index] = card_code.with_enchants(run[zone][index], [grade])
    return ""


def _tinker_available(run: dict) -> bool:
    return bool(run_state.enchanted_cards(run))


def _tinker_weight(run: dict) -> float:
    return 0.4 + 0.3 * len(run_state.enchanted_cards(run))


def _visitor(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    tag = _run_faction(run, rng)
    name = FACTION_NAMES[tag]
    bought_unit = False
    bought_relic = False

    while True:
        relic_pool = [r for r in run_state.relic_offers(run)
                      if RELICS[r].get("faction") in (None, tag)]
        options = [
            _option(f"buy a unit  [{VISITOR_UNIT_PRICE}]", f"choose one of three {name} units",
                    ui_common.GOLD, not bought_unit and run_state.affordable(run, VISITOR_UNIT_PRICE)),
            _option(f"buy a relic  [{VISITOR_RELIC_PRICE}]", f"a {name} relic",
                    ui_common.RELIC,
                    not bought_relic and bool(relic_pool)
                    and run_state.affordable(run, VISITOR_RELIC_PRICE)),
            _option("let's have a bout!", "beat them and both are free", ui_common.CURSE),
            _option("take your leave", f"a free random {name} unit", ui_common.DIM),
        ]
        choice = choice_screen.main(game_screen, f"{name} Visitor", options, run=run,
                                    subtitle="they open a case of wares")

        if choice == 0 and not bought_unit and run_state.spend_gold(run, VISITOR_UNIT_PRICE):
            bought_unit = True
            _offer_faction_units(game_screen, run, tag, rng)

        elif choice == 1 and not bought_relic and relic_pool:
            if run_state.spend_gold(run, VISITOR_RELIC_PRICE):
                bought_relic = True
                grants.grant_relic(game_screen, run, rng.choice(relic_pool), rng)

        elif choice == 2:
            result = battle_flow.fight(game_screen, run, _visitor_champion(tag, rng))
            if result in ("lose", "abandon"):
                return result
            _offer_faction_units(game_screen, run, tag, rng)
            if relic_pool:
                grants.grant_relic(game_screen, run, rng.choice(relic_pool), rng)
            return ""

        else:
            pool = card_pool.faction_units(tag)
            if pool:
                grants.grant_card(game_screen, run, rng.choice(pool))
            return ""


def _offer_faction_units(game_screen: GameScreen, run: dict, tag: str,
                         rng: random.Random) -> None:
    pool = card_pool.faction_units(tag)
    if not pool:
        return
    picks = rng.sample(pool, min(3, len(pool)))
    options = [{"label": code, "color": WHITE, "card": code} for code in picks]
    choice = choice_screen.main(game_screen, "Choose a unit", options, run=run,
                                subtitle=grants.slot_hint(run))
    if choice is not None and choice != choice_screen.SKIP:
        grants.grant_card(game_screen, run, picks[choice])


def _visitor_champion(tag: str, rng: random.Random) -> dict:
    """A lord who left two of their relics at home."""
    champion = enemies.faction_lord(tag, rng)
    champion["label"] = f"{FACTION_NAMES[tag]} Champion"
    champion["relics"] = champion["relics"][:1]
    champion["strategy_overrides"] = {"beam_width": 4, "depth_cap": 3}
    champion["gold"] = 0
    return champion


def _beast_statue(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    options = [
        _option("touch its jaw", ENCHANTS["rage"]["text"], ui_common.CURSE),
        _option("pry loose a fang", f"+{STATUE_ORBS} Forgetting Orb", ui_common.ORB),
    ]
    choice = choice_screen.main(game_screen, "Statue of the Raging Beast", options,
                                run=run, subtitle="its jaw is worn smooth by hands")

    if choice == 0:
        picked = card_picker.main(
            game_screen, run, "Enrage which unit?", subtitle=ENCHANTS["rage"]["text"],
            allowed=lambda zone, index, code: not card_pool.is_magic(code))
        if picked is not None:
            run_state.enchant_card(run, picked[0], picked[1], "rage")
    elif choice == 1:
        run["orbs"] += STATUE_ORBS
        notice_screen.main(game_screen, "A fang comes free",
                           [f"+{STATUE_ORBS} Forgetting Orb"], run=run, color=ui_common.ORB)
    return ""


def _beast_statue_available(run: dict) -> bool:
    return any(not card_pool.is_magic(c) for c in run_state.all_cards(run))


def _prism(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    whites = {(zone, index)
              for zone in ("deck", "bench")
              for index, code in enumerate(run[zone])
              if card_pool.color_tag_of(code) == "W"}

    options = [
        _option("hold a card to the light", ENCHANTS["disperse"]["text"], ui_common.HILITE),
        _option("pocket the shard", f"+{PRISM_GOLD} gold", ui_common.GOLD),
    ]
    choice = choice_screen.main(game_screen, "Prism", options, run=run,
                                subtitle="it splits the torchlight into factions")

    if choice == 0 and whites:
        picked = card_picker.main(
            game_screen, run, "Disperse which white card?",
            subtitle=ENCHANTS["disperse"]["text"],
            allowed=lambda zone, index, code: (zone, index) in whites)
        if picked is not None:
            run_state.enchant_card(run, picked[0], picked[1], "disperse")
            return ""
    run["gold"] += PRISM_GOLD
    return ""


def _prism_available(run: dict) -> bool:
    return any(card_pool.color_tag_of(c) == "W" for c in run_state.all_cards(run))


def _wanderer(game_screen: GameScreen, run: dict, rng: random.Random) -> str:
    options = [
        _option("take their price", f"+{WANDERER_GOLD} gold", ui_common.GOLD),
        _option("haggle", f"{HAGGLE_WIN} gold if they bite, {HAGGLE_LOSS} if they walk",
                ui_common.CURSE),
    ]
    choice = choice_screen.main(game_screen, "Wandering Trader", options, run=run,
                               subtitle="they eye the spare kit on your cart")

    if choice == 1:
        won = rng.random() < 0.5
        gold = HAGGLE_WIN if won else HAGGLE_LOSS
        headline = "They bite" if won else "They walk"
    else:
        gold = WANDERER_GOLD
        headline = "Sold"

    run["gold"] += gold
    notice_screen.main(game_screen, headline, [f"+{gold} gold"],
                       run=run, color=ui_common.GOLD)
    return ""


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------

EVENTS: dict[str, dict] = {
    "altar": {"label": "Altar", "acts": (1, 2, 3), "weight": 1.0,
              "handler": _altar, "available": _altar_available},
    "relic_trader": {"label": "Relic Trader", "acts": (1, 2, 3), "weight": 0.8,
                     "handler": _relic_trader, "available": _relic_trader_available},
    "tinker": {"label": "Tinker", "acts": (1, 2, 3), "weight": _tinker_weight,
               "handler": _tinker, "available": _tinker_available},
    "visitor": {"label": "Visitor", "acts": (2,), "weight": 1.2,
                "handler": _visitor, "available": _altar_available},
    "beast_statue": {"label": "Statue of the Raging Beast", "acts": (3,), "weight": 1.0,
                     "handler": _beast_statue, "available": _beast_statue_available},
    "prism": {"label": "Prism", "acts": (3,), "weight": 1.0,
              "handler": _prism, "available": _prism_available},
    "wanderer": {"label": "Wandering Trader", "acts": (1, 2, 3), "weight": 0.3,
                 "handler": _wanderer, "available": _altar_available},
}


def candidates(run: dict) -> list[str]:
    act = run.get("act", 1)
    return [name for name, entry in sorted(EVENTS.items())
            if act in entry["acts"] and entry["available"](run)]


def weight_of(run: dict, name: str) -> float:
    weight = EVENTS[name]["weight"]
    return float(weight(run)) if callable(weight) else float(weight)


def pick(run: dict, rng: random.Random) -> str:
    names = candidates(run)
    if not names:
        return "wanderer"
    return rng.choices(names, weights=[weight_of(run, n) for n in names])[0]


def enter(game_screen: GameScreen, run: dict, rng: random.Random,
          name: Optional[str] = None) -> str:
    name = name or pick(run, rng)
    return EVENTS[name]["handler"](game_screen, run, rng)
