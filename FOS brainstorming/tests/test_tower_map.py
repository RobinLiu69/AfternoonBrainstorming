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

import pytest

from cards.factory import CardFactory
from tower import card_pool, tower_map
from tower.content import ROOM_KINDS

FACTIONS = ["R", "B", "C", "BR"]


def _act(act: int, seed: int = 7):
    return tower_map.build_act(act, FACTIONS, random.Random(seed))


def test_act_has_nine_layers_in_order():
    act_map = _act(1)
    assert [layer["index"] for layer in act_map["layers"]] == list(range(9))


def test_only_act_one_opens_with_a_blessing():
    assert tower_map.layer_at(_act(1), 0)["kind"] == "blessing"
    assert tower_map.layer_at(_act(2), 0)["kind"] == "skip"


def test_branch_layers_offer_the_documented_option_counts():
    act_map = _act(1)
    assert len(tower_map.layer_at(act_map, 2)["options"]) == 2
    assert len(tower_map.layer_at(act_map, 4)["options"]) == 2
    layer6 = tower_map.layer_at(act_map, 6)
    assert len(layer6["options"]) == 3
    assert all(len(option["rooms"]) == 2 for option in layer6["options"])


def test_linked_layers_follow_the_branch_pick():
    act_map = _act(2)
    for pick in (0, 1):
        resolved = tower_map.resolve_layer(act_map, 3, {"2": pick})
        expected = tower_map.layer_at(act_map, 2)["options"][pick]["enemy"]
        assert resolved["kind"] == "battle"
        assert resolved["enemy"] is expected

    resolved = tower_map.resolve_layer(act_map, 7, {"6": 2})
    expected_room = tower_map.layer_at(act_map, 6)["options"][2]["rooms"][1]
    assert resolved["kind"] == "room"
    assert resolved["room"] is expected_room


def test_linked_layer_without_a_pick_is_an_error():
    with pytest.raises(ValueError):
        tower_map.resolve_layer(_act(1), 3, {})


def test_every_act_contains_a_shop():
    for seed in range(25):
        for act in (1, 2, 3):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            rooms = list(tower_map._all_rooms(act_map["layers"]))
            assert any(room["kind"] == "shop" for room in rooms)
            assert all(room["kind"] in ROOM_KINDS for room in rooms)


def test_act_one_only_fields_weak_enemies_before_the_boss():
    act_map = _act(1)
    kinds = []
    for layer in act_map["layers"]:
        if layer["kind"] == "battle" and layer["index"] != tower_map.BOSS_LAYER:
            kinds.append(layer["enemy"]["kind"])
        for option in layer.get("options", []):
            if "enemy" in option:
                kinds.append(option["enemy"]["kind"])
    assert kinds and set(kinds) == {"weak"}


def test_later_acts_offer_a_normal_and_an_elite_branch():
    act_map = _act(3)
    for layer_index in (2, 4):
        options = tower_map.layer_at(act_map, layer_index)["options"]
        assert {option["enemy"]["kind"] for option in options} == {"normal", "elite"}


def test_boss_is_known_from_the_start():
    for act in (1, 2, 3):
        boss = tower_map.boss_of(_act(act))
        assert boss["kind"] == "boss"
        assert boss["label"]


def test_generated_enemy_decks_only_use_real_cards():
    CardFactory.register_all()
    registry = set(CardFactory._registry)
    for seed in range(15):
        for act in (1, 2, 3):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            for layer in act_map["layers"]:
                decks = []
                if "enemy" in layer:
                    decks.append(layer["enemy"]["deck"])
                for option in layer.get("options", []):
                    if "enemy" in option:
                        decks.append(option["enemy"]["deck"])
                for deck in decks:
                    assert deck
                    assert all(code in registry for code in deck)


def test_enemy_decks_stay_inside_the_run_factions():
    allowed = set(FACTIONS) | {"W"}
    for seed in range(10):
        for act in (1, 2):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            for layer in act_map["layers"]:
                if layer["index"] == tower_map.BOSS_LAYER:
                    continue
                decks = [layer["enemy"]["deck"]] if "enemy" in layer else []
                decks += [o["enemy"]["deck"] for o in layer.get("options", []) if "enemy" in o]
                for deck in decks:
                    assert {card_pool.color_tag_of(c) for c in deck} <= allowed


def test_run_maps_are_deterministic_for_a_seed():
    first = tower_map.build_run_maps(1234, FACTIONS)
    second = tower_map.build_run_maps(1234, FACTIONS)
    assert first == second
    assert tower_map.build_run_maps(1235, FACTIONS) != first
