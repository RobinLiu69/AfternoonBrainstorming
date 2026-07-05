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

from cards.factory import CardFactory

from campaign.ai_decks import (
    WHITE_DECK, RED_DECK, BLUE_DECK, GREEN_DECK, ORANGE_DECK, BOSS_DECK,
)


MAGIC_POOL: tuple[str, ...] = ("CUBES", "HEAL", "MOVE", "MOVEO")
NON_DECK_CODES: tuple[str, ...] = ("CUBE", "CUBES", "HEAL", "MOVE", "SHADOW", "LUCKYBLOCK")

MAX_UNIT_COPIES: int = 3
MAX_MAGIC_COPIES: int = 4


def unit_pool() -> list[str]:
    CardFactory.register_all()
    return sorted(c for c in CardFactory._registry if c not in NON_DECK_CODES)


def card_pool() -> list[str]:
    return unit_pool() + list(MAGIC_POOL)


def valid_card_codes() -> set[str]:
    CardFactory.register_all()
    return set(CardFactory._registry) | {"MOVEO"}


RELICS: dict[str, dict] = {
    "war_drum":      {"label": "War Drum",      "effects": {"unit_damage_plus": 1},
                      "text": "your units +1 damage"},
    "iron_plate":    {"label": "Iron Plate",    "effects": {"unit_hp_plus": 2},
                      "text": "your units +2 HP"},
    "lucky_charm":   {"label": "Lucky Charm",   "effects": {"luck_plus": 15},
                      "text": "you start battles with +15 luck"},
    "supply_cache":  {"label": "Supply Cache",  "effects": {"hand_plus": 1},
                      "text": "you start battles with +1 card"},
    "field_medic":   {"label": "Field Medic",   "effects": {"free_heal_every_n_turns": 4},
                      "text": "free heal every 4 of your turns"},
    "swift_boots":   {"label": "Swift Boots",   "effects": {"free_moving_every_n_turns": 4},
                      "text": "free move every 4 of your turns"},
    "war_chest":     {"label": "War Chest",     "effects": {"coin_mult": 1.5},
                      "text": "floor coin rewards +50%"},
    "merchant_pass": {"label": "Merchant Pass", "effects": {"shop_discount": 0.8},
                      "text": "shop prices -20%"},
}

CURSES: dict[str, dict] = {
    "berserker_brew": {"label": "Berserker Brew",
                       "player_effects": {"unit_damage_plus": 2, "hand_plus": -1},
                       "ai_effects": {},
                       "text": "your units +2 damage",
                       "curse_text": "you start battles with 1 less card"},
    "golden_greed":   {"label": "Golden Greed",
                       "player_effects": {"coin_mult": 2.0},
                       "ai_effects": {"unit_hp_plus": 2},
                       "text": "floor coin rewards x2",
                       "curse_text": "enemy units +2 HP"},
    "glass_cannon":   {"label": "Glass Cannon",
                       "player_effects": {"unit_damage_plus": 2, "unit_hp_plus": -2},
                       "ai_effects": {},
                       "text": "your units +2 damage",
                       "curse_text": "your units -2 HP"},
    "heavy_purse":    {"label": "Heavy Purse",
                       "player_effects": {"shop_discount": 0.5},
                       "ai_effects": {"hand_plus": 1, "luck_plus": 10},
                       "text": "shop prices -50%",
                       "curse_text": "enemy starts with +1 card and +10 luck"},
}

CONSUMABLES: dict[str, dict] = {
    "battle_ration": {"label": "Battle Ration", "effects": {"free_heal_every_n_turns": 3},
                      "text": "next battle: free heal every 3 turns", "price": 25},
    "adrenaline":    {"label": "Adrenaline",    "effects": {"free_moving_every_n_turns": 3},
                      "text": "next battle: free move every 3 turns", "price": 20},
    "scout_report":  {"label": "Scout Report",  "effects": {"hand_plus": 2},
                      "text": "next battle: start with +2 cards", "price": 25},
}

MUTATIONS: dict[str, dict] = {
    "sharp_world": {"label": "Sharp World", "effects": {"both_unit_damage_plus": 1},
                    "text": "all units +1 damage"},
    "tough_world": {"label": "Tough World", "effects": {"both_unit_hp_plus": 2},
                    "text": "all units +2 HP"},
    "sudden_death": {"label": "Sudden Death", "effects": {"win_threshold": 8},
                     "text": "first to 8 points wins"},
    "marathon":    {"label": "Marathon", "effects": {"win_threshold": 12},
                    "text": "first to 12 points wins"},
    "open_war":    {"label": "Open War", "effects": {"both_hand_plus": 2},
                    "text": "both sides start with +2 cards"},
}

EVENTS: dict[str, dict] = {
    "fountain": {"label": "Mysterious Fountain",
                 "text": "A fountain glimmers in the dark."},
    "gambler":  {"label": "Wandering Gambler",
                 "text": "A gambler offers you a coin flip."},
    "altar":    {"label": "Ancient Altar",
                 "text": "The altar hungers for a card."},
}


TIER0_DECKS: list[list[str]] = [WHITE_DECK, RED_DECK]

TIER1_DECKS: list[list[str]] = [RED_DECK, BLUE_DECK, GREEN_DECK, ORANGE_DECK]

TIER2_DECKS: list[list[str]] = [
    RED_DECK[:9] + ["ASSDKG", "ASSC", "SPF"],
    BLUE_DECK[:9] + ["HFDKG", "APC", "SPC"],
    GREEN_DECK[:9] + ["LFF", "HFF", "APTC"],
    ORANGE_DECK[:9] + ["ADCDKG", "ASSF", "SPDKG"],
]

META_DECK: list[str] = [
    "TANKB", "TANKB", "LFB", "LFB", "APB", "APB",
    "SPB", "SPB", "ASSB", "ASSB", "HFP", "HFP",
]

TIER3_DECKS: list[list[str]] = [
    BOSS_DECK,
    META_DECK,
    ["ADCR", "ADCO", "ASSR", "ASSB", "ASSDKG", "HFR", "HFO", "LFR", "LFO", "SPR", "SPC", "APTB"],
    ["ADCDKG", "ADCC", "ASSF", "ASSO", "HFF", "HFDKG", "LFR", "LFO", "SPB", "SPF", "TANKC", "APTC"],
    ["ASSW", "ASSR", "ASSB", "ASSG", "ASSO", "ASSDKG", "ASSC", "ASSF", "LFR", "LFO", "SPR", "SPB"],
    ["TANKW", "TANKR", "TANKB", "TANKG", "TANKO", "TANKC", "TANKDKG", "TANKF", "APTW", "APTB", "HFR", "ADCR"],
]

STRONG_CARDS: tuple[str, ...] = ("TANKB", "HFP", "LFB", "HFB", "LFR", "SPB", "TANKF")
WEAK_CARDS: tuple[str, ...] = ("SPC", "ASSDKG", "ASSC", "SPO", "APO", "ASSO", "TANKO", "HFR")

DECK_TIERS: list[list[list[str]]] = [TIER0_DECKS, TIER1_DECKS, TIER2_DECKS, TIER3_DECKS]

DECK_TEMPLATES: dict[str, dict[str, int]] = {
    "balanced": {"ADC": 2, "AP": 1, "TANK": 2, "HF": 2, "LF": 1, "ASS": 2, "APT": 1, "SP": 1},
    "aggro":    {"ADC": 2, "AP": 1, "HF": 2, "LF": 2, "ASS": 3, "SP": 2},
    "fortress": {"ADC": 2, "AP": 1, "TANK": 3, "HF": 2, "LF": 1, "APT": 2, "SP": 1},
    "harvest":  {"ADC": 2, "AP": 1, "TANK": 1, "HF": 2, "LF": 1, "ASS": 2, "SP": 3},
    "snipers":  {"ADC": 3, "AP": 2, "TANK": 1, "HF": 1, "LF": 2, "ASS": 2, "SP": 1},
}

TIER_PALETTES: list[list[list[str]]] = [
    [["W"], ["R"]],
    [["R"], ["B"], ["G"], ["O"],
     ["R", "B"], ["G", "O"], ["R", "O"], ["B", "G"], ["R", "G"], ["B", "O"]],
    [["DKG"], ["B", "F"],
     ["R", "DKG"], ["B", "C"], ["G", "F"], ["O", "DKG"], ["B", "O"],
     ["R", "B", "C"], ["G", "O", "DKG"], ["R", "F", "P"]],
    [["R", "O", "DKG"], ["B", "O", "F"], ["B", "DKG", "P"], ["R", "B", "G", "O"],
     ["B", "O", "DKG", "F"], ["W", "R", "B", "G", "O", "DKG", "C", "F", "P"]],
]


EFFECT_TEXT_TEMPLATES: dict[str, str] = {
    "unit_hp_plus":              "{subject} units {value:+d} HP",
    "unit_damage_plus":          "{subject} units {value:+d} damage",
    "hand_plus":                 "{subject} starts with {value:+d} cards",
    "luck_plus":                 "{subject} starts with {value:+d} luck",
    "free_heal_every_n_turns":   "{subject} gains +1 heal every {value} turns",
    "free_moving_every_n_turns": "{subject} gains +1 move every {value} turns",
    "both_unit_hp_plus":         "all units +{value} HP",
    "both_unit_damage_plus":     "all units +{value} damage",
    "both_hand_plus":            "both sides start with +{value} cards",
    "win_threshold":             "first to {value} points wins",
}


def effect_lines(effects: dict, subject: str) -> list[str]:
    lines: list[str] = []
    for key, value in effects.items():
        if key in ("job_damage_plus", "job_hp_plus"):
            stat = "damage" if key == "job_damage_plus" else "HP"
            for job, n in value.items():
                if n:
                    lines.append(f"{subject} {job} {n:+d} {stat}")
            continue
        template = EFFECT_TEXT_TEMPLATES.get(key)
        if template and value:
            lines.append(template.format(subject=subject, value=value))
    return lines
