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

"""Static content tables for tower mode.  Pure data, no pygame."""

from __future__ import annotations


JOBS: tuple[str, ...] = ("ADC", "AP", "TANK", "HF", "LF", "ASS", "APT", "SP")

FACTION_NAMES: dict[str, str] = {
    "W": "White",
    "R": "Red",
    "G": "Green",
    "B": "Blue",
    "O": "Orange",
    "DKG": "DarkGreen",
    "C": "Cyan",
    "F": "Fuchsia",
    "BR": "Brown",
    "P": "Purple",
}

FACTION_BLURBS: dict[str, str] = {
    "R": "damage snowball",
    "G": "lucky chaos",
    "B": "mana tempo",
    "O": "mobile counter",
    "DKG": "totem burn",
    "C": "pirate economy",
    "F": "shadow mirror",
    "BR": "giant bruisers",
}

# Purple only has 4 implemented cards, so it is boss-only content.
SELECTABLE_FACTIONS: tuple[str, ...] = ("R", "G", "B", "O", "DKG", "C", "F", "BR")
FACTION_PICK_COUNT: int = 4

MAGIC_POOL: tuple[str, ...] = ("CUBES", "HEAL", "MOVE")

STARTER_DECK: tuple[str, ...] = ("ADCW", "APW", "TANKW", "HFW", "LFW", "ASSW")

DECK_LIMIT: int = 12
BENCH_LIMIT: int = 2
UNLIMITED_DECK_LIMIT: int = 999


# --------------------------------------------------------------------------
# enchantments
# --------------------------------------------------------------------------
# kind:   "normal" | "curse" | "artisan"
# hp / damage:  flat stat change applied when the unit is deployed
# behavior:     handled case by case by tower/enchant_runtime.py

ENCHANTS: dict[str, dict] = {
    "disperse": {"label": "Dispersed", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "on deploy, becomes a random other faction (stats keep)"},
    "sharp":    {"label": "Sharp", "kind": "normal", "hp": 0, "damage": 1,
                 "text": "+1 damage"},
    "fort":     {"label": "Fortified", "kind": "normal", "hp": 2, "damage": 0,
                 "text": "+2 HP"},
    "rage":     {"label": "Berserk", "kind": "normal", "hp": -2, "damage": 2,
                 "text": "+2 damage, -2 HP"},
    "mana":     {"label": "Mana", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "when played, gain 1 mana orb"},
    "radiant":  {"label": "Radiant", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "scores 1 extra point"},
    "steady":   {"label": "Steady", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "immune to numbness"},
    "plated":   {"label": "Plated", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "takes 1 less damage"},
    "ghost":    {"label": "Ghostly", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "vanishes at end of turn, never returns to the discard pile"},
    "chimera":  {"label": "Chimera", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "this is a chimera"},
    "borrowed": {"label": "Borrowed", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "belongs to someone else - never joins the discard pile"},
    "sword":    {"label": "Flying Sword", "kind": "normal", "hp": 0, "damage": 0,
                 "text": "with no enemy in range, attacks the nearest enemy instead"},

    "art_hero":  {"label": "Artisan: Hero", "kind": "artisan", "hp": 1, "damage": 1,
                  "text": "+1 damage, +1 HP"},
    "art_guard": {"label": "Artisan: Guard", "kind": "artisan", "hp": 3, "damage": 0,
                  "text": "+3 HP"},
    "art_mend":  {"label": "Artisan: Mend", "kind": "artisan", "hp": 0, "damage": 0,
                  "text": "heals 1 HP at the start of each of your turns"},

    "burn":  {"label": "Burning", "kind": "curse", "hp": 0, "damage": 0,
              "text": "the first time it is played, the enemy scores 2"},
    "bleed": {"label": "Bleeding", "kind": "curse", "hp": 0, "damage": 0,
              "text": "takes 1 damage at the start of each of your turns"},
    "rust":  {"label": "Rusted", "kind": "curse", "hp": 0, "damage": 0,
              "text": "cannot gain shields"},
}

ARTISAN_ENCHANTS: tuple[str, ...] = ("art_hero", "art_guard", "art_mend")
CURSE_ENCHANTS: tuple[str, ...] = ("burn", "bleed", "rust")
BLESSING_ENCHANTS: tuple[str, ...] = ("sharp", "fort")


# --------------------------------------------------------------------------
# relics
# --------------------------------------------------------------------------
# tier:    "common" | "rare" | "power" | "special" | "curse"
# group:   relics sharing a group are mutually exclusive
# source:  "shop" = shop only, "drop" = never sold, "" = both
# faction: only offered when that faction is in the run
# effects: numeric keys merged by run_state.merged_effects()
# on_pickup: one-shot run action performed the moment it is acquired

RELICS: dict[str, dict] = {}


def _amulets_and_emblems() -> None:
    for job in JOBS:
        RELICS[f"amulet_{job}"] = {
            "label": f"{job} Amulet", "tier": "common", "group": "amulet",
            "text": f"your {job} cards gain +1 HP",
            "effects": {"job_hp_plus": {job: 1}},
        }
        RELICS[f"emblem_{job}"] = {
            "label": f"{job} Emblem", "tier": "rare", "group": "emblem",
            "text": f"your {job} cards gain +1 damage",
            "effects": {"job_damage_plus": {job: 1}},
        }


_amulets_and_emblems()

RELICS.update({
    # ---------------- common ----------------
    "courier": {
        "label": "Courier", "tier": "common",
        "text": "one free shop reroll, and one extra reroll allowed",
        "effects": {"free_rerolls": 1, "extra_rerolls": 1},
    },
    "first_aid_kit": {
        "label": "First Aid Kit", "tier": "common",
        "text": "your healing spells restore 2 extra HP",
        "effects": {"heal_bonus": 2},
    },
    "dorans_shield": {
        "label": "Doran's Shield", "tier": "common",
        "text": "the first unit you deploy each battle gains +2 HP",
        "effects": {"first_unit_hp_plus": 2},
    },
    "dorans_blade": {
        "label": "Doran's Blade", "tier": "common",
        "text": "the first unit you deploy each battle gains +1 damage",
        "effects": {"first_unit_damage_plus": 1},
    },
    "seal_of_radiance": {
        "label": "Seal of Radiance", "tier": "common",
        "text": "on pickup, enchant a card with Radiant",
        "effects": {}, "on_pickup": {"enchant": "radiant"},
    },
    "piggy_bank": {
        "label": "Piggy Bank", "tier": "common",
        "text": "gold rewards +25%",
        "effects": {"gold_mult": 1.25},
    },
    "index_fund": {
        "label": "Index Fund", "tier": "common",
        "text": "each floor, gain 10% of your gold until you spend in a shop",
        "effects": {"interest_rate": 0.10},
    },
    "cuckoo_clock": {
        "label": "Cuckoo Clock", "tier": "common",
        "text": "when your deck reshuffles, draw a card",
        "effects": {"draw_on_reshuffle": 1},
    },
    "pocket_watch": {
        "label": "Pocket Watch", "tier": "common",
        "text": "when your deck reshuffles, gain an attack",
        "effects": {"attack_on_reshuffle": 1},
    },
    "credit_card": {
        "label": "Credit Card", "tier": "common", "source": "shop",
        "text": "shops let you borrow up to 200 gold; debt grows 10% per floor",
        "effects": {"credit_limit": 200, "debt_rate": 0.10},
    },
    "blue_crystal_ball": {
        "label": "Blue Crystal Ball", "tier": "common", "faction": "B",
        "text": "when a mana orb triggers, deal 1 damage to a random enemy",
        "effects": {"orb_trigger_damage": 1},
    },
    "ship_in_a_bottle": {
        "label": "Ship in a Bottle", "tier": "common", "faction": "C",
        "text": "after a victory, gain 20 gold for each pirate in your deck",
        "effects": {"victory_gold_per_pirate": 20},
    },

    # ---------------- rare ----------------
    "prepared_pack": {
        "label": "Prepared Pack", "tier": "rare",
        "text": "start battles with +1 card",
        "effects": {"hand_plus": 1},
    },
    "coupon": {
        "label": "Coupon", "tier": "rare", "source": "drop",
        "text": "shop prices are halved",
        "effects": {"shop_discount": 0.5},
    },
    "ring_of_healing": {
        "label": "Ring of Healing", "tier": "rare",
        "text": "shields from overhealing are doubled",
        "effects": {"overheal_shield_mult": 2},
    },
    "dorans_ring": {
        "label": "Doran's Ring", "tier": "rare",
        "text": "the first spell you cast each battle draws a card",
        "effects": {"first_spell_draw": 1},
    },
    "message_in_a_bottle": {
        "label": "Message in a Bottle", "tier": "rare",
        "text": "every 3 turns, gain a random ghostly spell",
        "effects": {"ghost_spell_every_n_turns": 3},
    },
    "blasting_wand": {
        "label": "Blasting Wand", "tier": "rare",
        "text": "your AP units gain +2 damage but no longer numb their targets",
        "effects": {"job_damage_plus": {"AP": 2}, "ap_no_numb": 1},
    },
    "blue_sigil": {
        "label": "Blue Sigil", "tier": "rare", "faction": "B",
        "text": "on pickup, enchant a card with Mana",
        "effects": {}, "on_pickup": {"enchant": "mana"},
    },
    "mages_blood": {
        "label": "Mage's Blood", "tier": "rare", "faction": "B",
        "text": "you no longer draw at the start of your turn; gain 3 mana orbs instead",
        "effects": {"turn_start_tokens": 3, "no_turn_start_draw": 1},
    },
    "treasure_chest": {
        "label": "Treasure Chest", "tier": "rare", "faction": "C",
        "text": "gain 2 coins at the start of your turn",
        "effects": {"turn_start_coins": 2},
    },

    # ---------------- power ----------------
    "sewing_kit": {
        "label": "Sewing Kit", "tier": "power",
        "text": "damage you deal below 2 is raised to 2",
        "effects": {"min_damage": 2},
    },
    "layered_armor": {
        "label": "Layered Armor", "tier": "power",
        "text": "on pickup, enchant a card with Plated",
        "effects": {}, "on_pickup": {"enchant": "plated"},
    },
    "sword_boomerang": {
        "label": "Sword Boomerang", "tier": "power",
        "text": "on pickup, enchant a card with Flying Sword",
        "effects": {}, "on_pickup": {"enchant": "sword"},
    },
    "unchanging_stone": {
        "label": "Unchanging Stone", "tier": "power", "source": "shop",
        "text": "on pickup, enchant a card with Steady",
        "effects": {}, "on_pickup": {"enchant": "steady"},
    },
    "wax_furnace": {
        "label": "Wax Furnace", "tier": "power", "source": "shop",
        "text": "enchanted units gain +1 damage",
        "effects": {"enchanted_damage_plus": 1},
    },

    # ---------------- special ----------------
    "limit_break": {
        "label": "Limit Break", "tier": "special",
        "text": "your deck has no size limit and the bench is free to arrange",
        "effects": {"deck_limit_override": UNLIMITED_DECK_LIMIT, "free_bench": 1},
    },
    "demon_emblem": {
        "label": "Demon Emblem", "tier": "special",
        "text": "with more than 6 spells in your deck, all your units gain +2 HP and +1 damage",
        "effects": {}, "conditional": "demon_emblem",
    },
    "mana_spring": {
        "label": "Mana Spring", "tier": "special",
        "text": "gain 1 mana orb at the start of your turn",
        "effects": {"turn_start_tokens": 1},
    },
    "battle_focus": {
        "label": "Battle Focus", "tier": "special",
        "text": "gain +1 attack each turn, but your attacks reset at end of turn",
        "effects": {"attacks_plus": 1, "attacks_reset": 1},
    },
    "pacifism": {
        "label": "Pacifism", "tier": "special",
        "text": "you never gain attacks; draw an extra card at the start of your turn",
        "effects": {"no_attack_gain": 1, "turn_start_draw_plus": 1},
    },
    "tank_bloodline": {
        "label": "Tank Bloodline", "tier": "special",
        "text": "if every unit in your deck is a TANK, they gain +3 HP and double effects",
        "effects": {}, "conditional": "tank_bloodline",
    },
    "current_emblem": {
        "label": "Current Emblem", "tier": "special",
        "text": "at the start of your turn, cast Tidal Surge",
        "effects": {"turn_start_tidal": 1},
    },

    # ---------------- curses ----------------
    "worn_pack": {
        "label": "Worn Pack", "tier": "curse",
        "text": "start battles with 1 less card",
        "effects": {"hand_plus": -1},
    },
    "torn_wallet": {
        "label": "Torn Wallet", "tier": "curse",
        "text": "lose 20 gold each floor",
        "effects": {"gold_per_floor": -20},
    },
    "feeble_charm": {
        "label": "Feeble Charm", "tier": "curse",
        "text": "the first unit you deploy each battle has -2 damage",
        "effects": {"first_unit_damage_plus": -2},
    },
    "hot_potato": {
        "label": "Hot Potato", "tier": "curse",
        "text": "on pickup, a random card is enchanted with Burning",
        "effects": {}, "on_pickup": {"enchant": "burn", "random": True},
    },
    "bloodied_needle": {
        "label": "Bloodied Needle", "tier": "curse",
        "text": "on pickup, enchant a card of your choice with Bleeding",
        "effects": {}, "on_pickup": {"enchant": "bleed"},
    },
    "rusted_statue": {
        "label": "Rusted Statue", "tier": "curse",
        "text": "on pickup, a random card is enchanted with Rusted",
        "effects": {}, "on_pickup": {"enchant": "rust", "random": True},
    },
    "fog_of_war": {
        "label": "Fog of War", "tier": "curse",
        "text": "you cannot see the room types on branch floors",
        "effects": {"hide_rooms": 1},
    },
    "sunglasses": {
        "label": "Sunglasses", "tier": "curse",
        "text": "enemies are hidden until you fight them",
        "effects": {"hide_enemies": 1},
    },
})


RELIC_TIERS: tuple[str, ...] = ("common", "rare", "power", "special", "curse")

# numeric effect keys that merge additively / multiplicatively
ADDITIVE_EFFECTS: frozenset[str] = frozenset({
    "unit_hp_plus", "unit_damage_plus", "hand_plus",
    "first_unit_hp_plus", "first_unit_damage_plus",
    "heal_bonus", "min_damage", "enchanted_damage_plus",
    "free_rerolls", "extra_rerolls", "credit_limit",
    "draw_on_reshuffle", "attack_on_reshuffle",
    "turn_start_tokens", "turn_start_coins", "turn_start_draw_plus",
    "attacks_plus", "gold_per_floor", "victory_gold_per_pirate",
    "orb_trigger_damage", "first_spell_draw",
})
FLAG_EFFECTS: frozenset[str] = frozenset({
    "ap_no_numb", "no_turn_start_draw", "attacks_reset", "no_attack_gain",
    "free_bench", "hide_rooms", "hide_enemies", "turn_start_tidal",
    "double_tank_effects",
})
MULTIPLIED_EFFECTS: frozenset[str] = frozenset({"gold_mult", "shop_discount"})
JOB_EFFECTS: frozenset[str] = frozenset({"job_hp_plus", "job_damage_plus"})
MIN_EFFECTS: frozenset[str] = frozenset({"ghost_spell_every_n_turns"})
MAX_EFFECTS: frozenset[str] = frozenset({
    "interest_rate", "debt_rate", "deck_limit_override", "overheal_shield_mult",
})


def relics_of_tier(tier: str) -> list[str]:
    return sorted(rid for rid, r in RELICS.items() if r["tier"] == tier)


def relic_group(relic_id: str) -> str:
    return RELICS.get(relic_id, {}).get("group", "")


# --------------------------------------------------------------------------
# opening blessings - three are offered, the player keeps one
# --------------------------------------------------------------------------

BLESSINGS: tuple[dict, ...] = (
    {"id": "two_cards", "label": "Recruitment Drive",
     "text": "pick a card to add, twice"},
    {"id": "one_orb", "label": "Clear Mind",
     "text": "gain 1 Forgetting Orb"},
    {"id": "one_relic", "label": "Lucky Find",
     "text": "gain 1 random relic"},
    {"id": "bench_plus", "label": "Wider Camp",
     "text": "+2 bench slots"},
    {"id": "enchant_unit", "label": "Blessed Steel",
     "text": "enchant one of your units (Sharp or Fortified)"},
    {"id": "orbs_and_curse", "label": "Devil's Bargain",
     "text": "gain 3 Forgetting Orbs, then take one curse relic of your choice"},
    {"id": "power_and_curse", "label": "Cursed Power",
     "text": "gain 1 power relic and 1 random curse relic"},
)

BLESSING_OFFER_COUNT: int = 3


# --------------------------------------------------------------------------
# rooms and floors
# --------------------------------------------------------------------------

ROOM_LABELS: dict[str, str] = {
    "event": "Event",
    "shop": "Shop",
    "gold_mine": "Gold Mine",
    "relic_chest": "Relic Chest",
}

ROOM_KINDS: tuple[str, ...] = tuple(ROOM_LABELS)

ENEMY_LABELS: dict[str, str] = {
    "weak": "Recruit",
    "normal": "Warband",
    "elite": "Elite",
    "boss": "Boss",
}

GOLD_MINE_REWARD: int = 120
ORB_DROP_CHANCE: float = 0.22
RELIC_DROP_CHANCE: float = 0.25

BATTLE_GOLD: dict[str, int] = {"weak": 60, "normal": 80, "elite": 140, "boss": 220}
