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

"""Act maps: 3 acts, 9 layers each (layer 0 only exists in act 1).

    0  opening blessing        (act 1 only)
    1  weak battle
    2  branch of 2: a room now, and the enemy waiting on layer 3
    3  the enemy chosen on layer 2
    4  branch of 2
    5  the enemy chosen on layer 4
    6  branch of 3: each route holds two rooms
    7  the second room of the route chosen on layer 6
    8  act boss

A layer's content is fixed when the act is generated, so the player can see
the rooms and the enemies ahead (unless a curse relic hides them).
"""

from __future__ import annotations

import random

from tower import enemies
from tower.content import ROOM_KINDS

FIRST_ACT: int = 1
LAST_ACT: int = 3
LAYERS_PER_ACT: int = 9
BLESSING_LAYER: int = 0
BOSS_LAYER: int = 8

ROOM_WEIGHTS: dict[str, float] = {
    "event": 0.40,
    "gold_mine": 0.25,
    "relic_chest": 0.20,
    "shop": 0.15,
}

# rooms whose screen does not exist yet - they are simply not generated
DISABLED_ROOMS: frozenset[str] = frozenset()


def _roll_room(rng: random.Random) -> dict:
    kinds = [k for k in ROOM_KINDS if k not in DISABLED_ROOMS]
    weights = [ROOM_WEIGHTS[k] for k in kinds]
    return {"kind": rng.choices(kinds, weights=weights)[0]}


def _battle_enemy(act: int, factions, rng: random.Random, weak_index: int, kind: str) -> dict:
    if kind == "weak":
        return enemies.weak_enemy(rng, weak_index)
    if kind == "elite":
        return enemies.elite_enemy(act, factions, rng)
    return enemies.normal_enemy(act, factions, rng)


def _branch_enemy_kinds(act: int, rng: random.Random) -> list[str]:
    """Two options: act 1 trains on trash, later acts offer normal vs elite."""
    if act == 1:
        return ["weak", "weak"]
    pair = ["normal", "elite"]
    rng.shuffle(pair)
    return pair


def build_act(act: int, factions, rng: random.Random) -> dict:
    layers: list[dict] = []
    weak_index = 0

    if act == FIRST_ACT:
        layers.append({"index": BLESSING_LAYER, "kind": "blessing"})
    else:
        layers.append({"index": BLESSING_LAYER, "kind": "skip"})

    first_kind = "weak" if act == FIRST_ACT else "normal"
    layers.append({
        "index": 1, "kind": "battle",
        "enemy": _battle_enemy(act, factions, rng, weak_index, first_kind),
    })
    if first_kind == "weak":
        weak_index += 1

    for layer_index in (2, 4):
        options: list[dict] = []
        for enemy_kind in _branch_enemy_kinds(act, rng):
            enemy = _battle_enemy(act, factions, rng, weak_index, enemy_kind)
            if enemy_kind == "weak":
                weak_index += 1
            options.append({"room": _roll_room(rng), "enemy": enemy})
        layers.append({"index": layer_index, "kind": "branch", "options": options})
        layers.append({"index": layer_index + 1, "kind": "battle_linked", "source": layer_index})

    layers.append({
        "index": 6, "kind": "branch",
        "options": [{"rooms": [_roll_room(rng), _roll_room(rng)]} for _ in range(3)],
    })
    layers.append({"index": 7, "kind": "room_linked", "source": 6})
    layers.append({
        "index": BOSS_LAYER, "kind": "battle",
        "enemy": enemies.act_boss(act, factions, rng),
    })

    layers.sort(key=lambda entry: entry["index"])
    _guarantee_shop(layers, rng)
    return {"act": act, "layers": layers}


def _all_rooms(layers: list[dict]):
    for layer in layers:
        for option in layer.get("options", []):
            if "room" in option:
                yield option["room"]
            for room in option.get("rooms", []):
                yield room


def _guarantee_shop(layers: list[dict], rng: random.Random) -> None:
    rooms = list(_all_rooms(layers))
    if any(room["kind"] == "shop" for room in rooms):
        return
    if rooms:
        rng.choice(rooms)["kind"] = "shop"


def layer_at(act_map: dict, index: int) -> dict:
    for layer in act_map["layers"]:
        if layer["index"] == index:
            return layer
    raise KeyError(f"act {act_map.get('act')} has no layer {index}")


def resolve_layer(act_map: dict, index: int, picks: dict) -> dict:
    """Concrete content of a layer, following the branch picks made so far."""
    layer = layer_at(act_map, index)
    kind = layer["kind"]

    if kind in ("blessing", "skip", "branch"):
        return layer

    if kind == "battle":
        return {"index": index, "kind": "battle", "enemy": layer["enemy"]}

    source = layer["source"]
    pick = picks.get(str(source), picks.get(source))
    if pick is None:
        raise ValueError(f"layer {index} needs a pick on layer {source}")
    option = layer_at(act_map, source)["options"][pick]

    if kind == "battle_linked":
        return {"index": index, "kind": "battle", "enemy": option["enemy"]}
    return {"index": index, "kind": "room", "room": option["rooms"][1]}


def branch_choice_room(act_map: dict, index: int, pick: int) -> dict:
    """The room the player enters right away when picking a branch option."""
    option = layer_at(act_map, index)["options"][pick]
    return option["room"] if "room" in option else option["rooms"][0]


def boss_of(act_map: dict) -> dict:
    return layer_at(act_map, BOSS_LAYER)["enemy"]


def act_seed(seed: int, act: int) -> int:
    return (seed * 1000003 + act * 7919) % (2 ** 31 - 1)


def build_run_maps(seed: int, factions) -> list[dict]:
    return [
        build_act(act, factions, random.Random(act_seed(seed, act)))
        for act in range(FIRST_ACT, LAST_ACT + 1)
    ]
