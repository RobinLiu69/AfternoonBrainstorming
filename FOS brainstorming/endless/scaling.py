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

from shared.setting import JOB_DICTIONARY
from cards.factory import CardFactory

from endless.content import DECK_TIERS, DECK_TEMPLATES, TIER_PALETTES, MUTATIONS, EVENTS


COLOR_TO_STRATEGY: dict[str, str] = {
    "W": "white", "R": "red", "B": "blue", "G": "green", "O": "orange",
}

_COLOR_TAGS = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)


def _color_code_of(card: str) -> str:
    for tag in _COLOR_TAGS:
        if card.endswith(tag):
            return tag
    return ""


def _deck_strategy(deck: list[str]) -> str:
    colors = {_color_code_of(c) for c in deck}
    if len(colors) == 1:
        return COLOR_TO_STRATEGY.get(colors.pop(), "boss")
    return "boss"


def _deck_tier(floor: int) -> int:
    if floor <= 3:
        return 0
    if floor <= 9:
        return 1
    if floor <= 14:
        return 2
    return 3


def _generate_deck(floor: int, rng: random.Random) -> list[str]:
    CardFactory.register_all()
    tier = _deck_tier(floor)
    if floor <= 3:
        template = DECK_TEMPLATES["balanced"]
    else:
        template = DECK_TEMPLATES[rng.choice(sorted(DECK_TEMPLATES))]
    palette = rng.choice(TIER_PALETTES[tier])
    fallback = [c for c in ("W", "R", "B", "G", "O")]
    deck: list[str] = []
    for job, count in template.items():
        colors = [c for c in palette if job + c in CardFactory._registry]
        if not colors:
            colors = [c for c in fallback if job + c in CardFactory._registry]
        for _ in range(count):
            deck.append(job + rng.choice(colors))
    return deck


def _pick_ai_deck(floor: int, rng: random.Random) -> list[str]:
    if rng.random() < 0.35:
        return list(rng.choice(DECK_TIERS[_deck_tier(floor)]))
    return _generate_deck(floor, rng)


def _floor_kind(floor: int, rng: random.Random, prev_kind: str) -> str:
    if floor % 10 == 0:
        return "boss"
    roll = rng.random()
    if floor >= 4 and floor % 5 != 0 and prev_kind != "event" and roll < 0.15:
        return "event"
    if floor >= 4 and roll < 0.35:
        return "elite"
    if floor >= 6 and roll < 0.55:
        return "mutation"
    return "normal"


def floor_spec(floor: int, rng: random.Random, prev_kind: str = "") -> dict:
    kind = _floor_kind(floor, rng, prev_kind)

    if kind == "event":
        event = rng.choice(sorted(EVENTS))
        return {"floor": floor, "kind": "event", "event": event,
                "label": EVENTS[event]["label"]}

    deck = _pick_ai_deck(max(floor, 15) if kind == "boss" else floor, rng)

    if kind == "boss":
        strategy = "claude"
        strategy_overrides = {
            "beam_width": min(10, 4 + 2 * (floor // 10)),
            "depth_cap": min(8, 2 + 2 * (floor // 10)),
        }
    else:
        strategy = "white" if floor <= 3 else _deck_strategy(deck)
        if floor >= 15:
            strategy = "boss"
        strategy_overrides = {"attack_min_score": max(6.0, 12.0 - floor * 0.4)}

    ai_effects: dict = {}
    hp_plus = floor // 8 + (1 if kind in ("elite", "boss") else 0)
    if hp_plus:
        ai_effects["unit_hp_plus"] = hp_plus
    hand_plus = min(3, floor // 10) + (1 if kind == "elite" else 0)
    if hand_plus:
        ai_effects["hand_plus"] = hand_plus
    deck_colors = {_color_code_of(c) for c in deck}
    if floor >= 12 and ("G" in deck_colors or len(deck_colors) > 1):
        ai_effects["luck_plus"] = min(25, floor)
    if floor >= 12:
        ai_effects["free_heal_every_n_turns"] = max(4, 8 - floor // 10)
    if floor >= 15:
        ai_effects["free_moving_every_n_turns"] = 3

    mutation: dict = {}
    mutation_name = ""
    if kind == "mutation":
        mutation_name = rng.choice(sorted(MUTATIONS))
        mutation = dict(MUTATIONS[mutation_name]["effects"])

    coin_reward = 12 + 2 * floor
    if kind == "elite":
        coin_reward *= 2
    elif kind == "boss":
        coin_reward *= 3

    label = f"Floor {floor}"
    if kind == "elite":
        label += "  -  ELITE"
    elif kind == "boss":
        label += "  -  BOSS"
    elif kind == "mutation":
        label += f"  -  {MUTATIONS[mutation_name]['label']}"

    return {
        "floor": floor,
        "kind": kind,
        "ai_deck": deck,
        "strategy": strategy,
        "strategy_overrides": strategy_overrides,
        "ai_effects": ai_effects,
        "mutation": mutation,
        "mutation_name": mutation_name,
        "coin_reward": coin_reward,
        "label": label,
    }
