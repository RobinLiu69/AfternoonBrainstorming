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

"""Enemy decks: trash mobs, elite formations and act bosses."""

from __future__ import annotations

import random

from cards.factory import CardFactory

from tower.content import BATTLE_GOLD, ENEMY_LABELS, FACTION_NAMES
from tower import card_pool


# strategies that exist in campaign/ai_strategies; everything else falls back
COLOR_STRATEGY: dict[str, str] = {
    "W": "white", "R": "red", "B": "blue", "G": "green", "O": "orange",
}
FALLBACK_STRATEGY: str = "boss"

WEAK_DECKS: tuple[tuple[str, ...], ...] = (
    ("ADCW", "ADCW", "TANKW", "TANKW", "HFW", "HFW",
     "LFW", "LFW", "ASSW", "ASSW", "APW", "SPW"),
    ("TANKW", "TANKW", "TANKW", "HFW", "HFW", "APTW",
     "APTW", "ADCW", "ADCW", "LFW", "APW", "SPW"),
    ("ASSW", "ASSW", "LFW", "LFW", "ADCW", "ADCW",
     "HFW", "HFW", "APW", "APW", "TANKW", "SPW"),
)

# Act 1 trash: small single-shape White squads, so each fight teaches one idea.
WEAK_FORMATIONS: dict[str, dict] = {
    "warriors": {
        "label": "White Warriors",
        "deck": ("ASSW", "ASSW", "LFW", "LFW", "SPW", "TANKW"),
    },
    "mages": {
        "label": "White Mages",
        "deck": ("APW", "APW", "APTW", "APTW", "TANKW", "TANKW"),
    },
    "heavies": {
        "label": "White Heavies",
        "deck": ("ADCW", "ADCW", "HFW", "HFW", "SPW", "TANKW"),
    },
    "legion": {
        "label": "White Legion",
        "deck": ("ADCW", "APW", "LFW", "HFW", "SPW", "TANKW", "APTW"),
    },
    "bulwark": {
        "label": "White Bulwark",
        "deck": ("SPW", "HFW", "APTW", "APTW", "TANKW", "TANKW"),
    },
}

WHITE_LORD_DECK: tuple[str, ...] = (
    "ADCW", "ADCW", "LFW", "HFW", "TANKW", "LFW",
    "HFW", "TANKW", "APW", "ASSW", "APTW", "SPW",
)

DECK_TEMPLATES: dict[str, dict[str, int]] = {
    "balanced": {"ADC": 2, "AP": 1, "TANK": 2, "HF": 2, "LF": 1, "ASS": 2, "APT": 1, "SP": 1},
    "aggro":    {"ADC": 2, "AP": 1, "HF": 2, "LF": 2, "ASS": 3, "SP": 2},
    "fortress": {"ADC": 2, "AP": 1, "TANK": 3, "HF": 2, "LF": 1, "APT": 2, "SP": 1},
    "harvest":  {"ADC": 2, "AP": 1, "TANK": 1, "HF": 2, "LF": 1, "ASS": 2, "SP": 3},
}

LORD_TEMPLATE: dict[str, int] = {
    "ADC": 2, "AP": 1, "TANK": 2, "HF": 2, "LF": 2, "ASS": 2, "SP": 1,
}

ELITE_FORMATIONS: dict[str, dict] = {
    "tank_wall": {
        "label": "Tank Wall",
        "template": {"TANK": 5, "APT": 2, "HF": 2, "AP": 1, "ADC": 1, "SP": 1},
        "relics": ("amulet_TANK", "dorans_shield"),
    },
    "assassins": {
        "label": "Assassin Cell",
        "template": {"ASS": 5, "LF": 2, "ADC": 2, "AP": 1, "SP": 2},
        "relics": ("emblem_ASS", "prepared_pack"),
    },
    "skirmishers": {
        "label": "Skirmisher Line",
        "template": {"LF": 4, "ADC": 3, "HF": 2, "AP": 1, "ASS": 1, "SP": 1},
        "relics": ("emblem_LF", "pocket_watch"),
    },
}

# an elite carries one relic in act 2 and two in act 3 - never a stat buff
ELITE_RELIC_COUNT: dict[int, int] = {1: 0, 2: 1, 3: 2}

# two thematic relics each faction lord always carries
LORD_RELICS: dict[str, tuple[str, str]] = {
    "R":   ("emblem_LF", "sewing_kit"),
    "G":   ("amulet_HF", "cuckoo_clock"),
    "B":   ("mages_blood", "blue_crystal_ball"),
    "O":   ("emblem_ADC", "pocket_watch"),
    "DKG": ("amulet_TANK", "sewing_kit"),
    "C":   ("treasure_chest", "emblem_ADC"),
    "F":   ("emblem_ASS", "prepared_pack"),
    "BR":  ("amulet_TANK", "battle_focus"),
}

LORD_RANDOM_RELIC_POOL: tuple[str, ...] = (
    "prepared_pack", "wax_furnace", "sewing_kit", "dorans_shield",
    "dorans_blade", "first_aid_kit", "ring_of_healing", "battle_focus",
)


def _fill_template(template: dict[str, int], tags, rng: random.Random) -> list[str]:
    CardFactory.register_all()
    registry = CardFactory._registry
    deck: list[str] = []
    for job, count in template.items():
        colors = [t for t in tags if job + t in registry]
        if not colors:
            colors = ["W"] if job + "W" in registry else []
        if not colors:
            continue
        for _ in range(count):
            deck.append(job + rng.choice(colors))
    return deck


def _strategy_for(deck) -> str:
    tags = {card_pool.color_tag_of(c) for c in deck}
    if len(tags) == 1:
        return COLOR_STRATEGY.get(tags.pop(), FALLBACK_STRATEGY)
    return FALLBACK_STRATEGY


def _attack_min(act: int, kind: str) -> float:
    """Difficulty comes from the AI playing better, not from bigger numbers."""
    base = 11.0 if kind == "normal" else 10.0
    return max(6.0, base - act)


# act 1 always lets the player open; after that the tower sometimes moves first
ENEMY_FIRST_CHANCE: float = 0.35


def _enemy_first(act: int, kind: str, rng: random.Random) -> bool:
    if act == 1 or kind == "weak":
        return False
    return rng.random() < ENEMY_FIRST_CHANCE


def weak_formation_order(rng: random.Random) -> list[str]:
    """Every squad an act fields, in a random order and without repeats."""
    return rng.sample(sorted(WEAK_FORMATIONS), len(WEAK_FORMATIONS))


def weak_enemy(formation_key: str, first: bool = False) -> dict:
    """The very first squad fields understrength units, so act 1 opens below par."""
    formation = WEAK_FORMATIONS[formation_key]
    return {
        "kind": "weak",
        "label": f"Raw {formation['label']}" if first else formation["label"],
        "deck": list(formation["deck"]),
        "formation": formation_key,
        "raw": first,
        "strategy": "white",
        "strategy_overrides": {"attack_min_score": 11.0},
        "relics": [],
        "effects": {"unit_hp_plus": -1, "unit_damage_plus": -1} if first else {},
        "enemy_first": False,
        "gold": BATTLE_GOLD["weak"],
    }


def normal_enemy(act: int, factions, rng: random.Random) -> dict:
    template = DECK_TEMPLATES[rng.choice(sorted(DECK_TEMPLATES))]
    tags = rng.sample(list(factions), min(2, len(factions))) if factions else ["W"]
    deck = _fill_template(template, tags, rng)
    names = " / ".join(FACTION_NAMES[t] for t in tags)
    return {
        "kind": "normal",
        "label": f"{names} {ENEMY_LABELS['normal']}",
        "deck": deck,
        "strategy": _strategy_for(deck),
        "strategy_overrides": {"attack_min_score": _attack_min(act, "normal")},
        "relics": [],
        "effects": {},
        "enemy_first": _enemy_first(act, "normal", rng),
        "gold": BATTLE_GOLD["normal"],
    }


def elite_enemy(act: int, factions, rng: random.Random) -> dict:
    key = rng.choice(sorted(ELITE_FORMATIONS))
    formation = ELITE_FORMATIONS[key]
    tags = rng.sample(list(factions), min(2, len(factions))) if factions else ["W"]
    deck = _fill_template(formation["template"], tags, rng)
    count = ELITE_RELIC_COUNT.get(act, 2)
    return {
        "kind": "elite",
        "label": f"{ENEMY_LABELS['elite']}: {formation['label']}",
        "deck": deck,
        "strategy": _strategy_for(deck),
        "strategy_overrides": {"attack_min_score": _attack_min(act, "elite")},
        "relics": list(formation["relics"][:count]),
        "effects": {},
        "enemy_first": _enemy_first(act, "elite", rng),
        "gold": BATTLE_GOLD["elite"],
    }


def faction_lord(tag: str, rng: random.Random) -> dict:
    deck = _fill_template(LORD_TEMPLATE, [tag], rng)
    fixed = list(LORD_RELICS.get(tag, ()))
    extra = [r for r in LORD_RANDOM_RELIC_POOL if r not in fixed]
    relics = fixed + ([rng.choice(extra)] if extra else [])
    return {
        "kind": "boss",
        "label": f"{FACTION_NAMES[tag]} Lord",
        "deck": deck,
        "strategy": "claude",
        "strategy_overrides": {"beam_width": 6, "depth_cap": 4},
        "relics": relics,
        "effects": {},
        "enemy_first": _enemy_first(2, "boss", rng),
        "gold": BATTLE_GOLD["boss"],
    }


# --------------------------------------------------------------------------
# act bosses
# --------------------------------------------------------------------------
# `available` marks bosses whose cards all exist today.  The ones that need
# unimplemented special spells stay out of the rotation until those land.

def white_lord(rng: random.Random) -> dict:
    """Act 1 boss: a full White deck carrying a single relic."""
    return {
        "kind": "boss",
        "label": "White Lord",
        "deck": list(WHITE_LORD_DECK),
        "strategy": "white",
        "strategy_overrides": {"attack_min_score": 8.0},
        "relics": [rng.choice(list(LORD_RANDOM_RELIC_POOL))],
        "effects": {},
        "enemy_first": False,
        "gold": BATTLE_GOLD["boss"],
    }


def traitor_lord(rng: random.Random) -> dict:
    deck = ["TANKP", "TANKP", "TANKP", "HFP", "HFP", "HFP",
            "APP", "APP", "APP", "ASSP", "ASSP", "ASSP"]
    return {
        "kind": "boss",
        "label": "Traitor Lord",
        "deck": deck,
        "strategy": "claude",
        "strategy_overrides": {"beam_width": 8, "depth_cap": 5},
        "relics": ["emblem_HF", "sewing_kit", "prepared_pack", "amulet_TANK"],
        "effects": {},
        "enemy_first": _enemy_first(3, "boss", rng),
        "gold": BATTLE_GOLD["boss"],
    }


def the_forgotten(factions, rng: random.Random) -> dict:
    """Two lords of the factions you did not pick, back to back.

    Beating the first one resets the score instead of ending the battle; the
    second lord inherits the board and hand and brings their own deck.
    """
    from tower.content import SELECTABLE_FACTIONS

    left_behind = [tag for tag in SELECTABLE_FACTIONS if tag not in factions]
    if len(left_behind) < 2:
        left_behind = list(SELECTABLE_FACTIONS)
    first_tag, second_tag = rng.sample(left_behind, 2)

    first = faction_lord(first_tag, rng)
    second = faction_lord(second_tag, rng)
    first.update({
        "label": "The Forgotten",
        "phase_label": f"{FACTION_NAMES[first_tag]} Lord",
        "note": "two lords, one after the other - beating the first only resets the score",
        "effects": {},
        "gold": BATTLE_GOLD["boss"],
        "next_phase": {
            "label": "The Forgotten",
            "phase_label": f"{FACTION_NAMES[second_tag]} Lord",
            "deck": second["deck"],
            "strategy": second["strategy"],
            "strategy_overrides": second["strategy_overrides"],
            "relics": second["relics"],
            "effects": {},
        },
    })
    return first


ACT3_BOSSES: dict[str, dict] = {
    "traitor_lord": {"builder": lambda factions, rng: traitor_lord(rng),
                     "available": True},
    "the_forgotten": {"builder": the_forgotten, "available": True},
    # needs Tidal Surge / Pirate Raid / Maelstrom spells
    "pirate_captain": {"builder": None, "available": False},
    # needs the demon spell and unit set
    "demon": {"builder": None, "available": False},
}


def act_boss(act: int, factions, rng: random.Random) -> dict:
    if act == 1:
        return white_lord(rng)
    if act == 2:
        return faction_lord(rng.choice(list(factions)), rng)
    options = sorted(k for k, v in ACT3_BOSSES.items() if v["available"])
    key = rng.choice(options)
    return ACT3_BOSSES[key]["builder"](factions, rng)
