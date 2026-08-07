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


def test_layers_are_numbered_in_order():
    for act in (1, 2, 3):
        act_map = _act(act)
        assert [layer["index"] for layer in act_map["layers"]] == list(
            range(tower_map.layers_in_act(act)))


def test_later_acts_are_longer():
    lengths = [tower_map.layers_in_act(act) for act in (1, 2, 3)]
    assert lengths == [9, 11, 13]
    for act in (1, 2, 3):
        assert len(_act(act)["layers"]) == tower_map.layers_in_act(act)


def test_the_two_routes_on_a_branch_are_never_the_same_room():
    """left event / right event is not a choice."""
    for act in (1, 2, 3):
        for seed in range(40):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            for pair in range(tower_map.branch_pairs(act)):
                options = tower_map.layer_at(act_map, 2 + 2 * pair)["options"]
                kinds = [option["room"]["kind"] for option in options]
                assert len(kinds) == len(set(kinds))


def test_no_two_final_routes_are_identical():
    for act in (1, 2, 3):
        for seed in range(40):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            routes = tower_map.layer_at(act_map, _final_branch(act))["options"]
            shapes = [tuple(r["kind"] for r in route["rooms"]) for route in routes]
            assert len(shapes) == len(set(shapes))


def test_siblings_stay_distinct_even_when_the_previous_layer_blocks_kinds():
    """The sibling rule is never waived, even if honouring both is impossible."""
    everything = set(tower_map.ROOM_KINDS)
    first = tower_map._roll_room(random.Random(1), soft_avoid=everything,
                                 hard_avoid=set())
    second = tower_map._roll_room(random.Random(1), soft_avoid=everything,
                                  hard_avoid={first["kind"]})
    assert second["kind"] != first["kind"]


def test_back_to_back_rooms_never_repeat_a_kind():
    """Events may repeat; a shop, mine or chest may not follow itself.

    Only checked on the two-way branches.  The final layer needs three
    distinct opening rooms, and with four room kinds that cannot always also
    dodge the layer below - there, sibling distinctness wins.
    """
    for act in (1, 2, 3):
        for seed in range(30):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            previous: set[str] = set()
            for pair in range(tower_map.branch_pairs(act)):
                options = tower_map.layer_at(act_map, 2 + 2 * pair)["options"]
                kinds = {o["room"]["kind"] for o in options}
                assert not (kinds & previous) - tower_map.REPEATABLE_ROOMS
                previous = kinds


def test_a_route_never_walks_the_same_room_twice_running():
    """Except events, which are different content each visit."""
    for act in (1, 2, 3):
        for seed in range(30):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            routes = tower_map.layer_at(act_map, _final_branch(act))["options"]
            for route in routes:
                first, second = (r["kind"] for r in route["rooms"])
                assert first != second or first in tower_map.REPEATABLE_ROOMS


def test_routes_may_share_a_room_kind_as_long_as_the_shape_differs():
    """event->shop against shop->event is a real choice, so it is allowed."""
    shapes = tower_map.route_shapes()
    assert ("event", "shop") in shapes
    assert ("shop", "event") in shapes
    assert ("event", "event") in shapes
    assert ("shop", "shop") not in shapes

    seen_shared_kind = False
    for seed in range(60):
        act_map = tower_map.build_act(3, FACTIONS, random.Random(seed))
        routes = tower_map.layer_at(act_map, _final_branch(3))["options"]
        openers = [route["rooms"][0]["kind"] for route in routes]
        if len(set(openers)) < len(openers):
            seen_shared_kind = True
            break
    assert seen_shared_kind, "routes should be free to share an opening room"


def test_only_act_one_opens_with_a_blessing():
    assert tower_map.layer_at(_act(1), 0)["kind"] == "blessing"
    assert tower_map.layer_at(_act(2), 0)["kind"] == "skip"


def _final_branch(act: int) -> int:
    return tower_map.boss_layer(act) - 2


def test_branch_layers_offer_the_documented_option_counts():
    for act in (1, 2, 3):
        act_map = _act(act)
        for pair in range(tower_map.branch_pairs(act)):
            assert len(tower_map.layer_at(act_map, 2 + 2 * pair)["options"]) == 2
        final = tower_map.layer_at(act_map, _final_branch(act))
        assert len(final["options"]) == 3
        assert all(len(option["rooms"]) == 2 for option in final["options"])


def test_linked_layers_follow_the_branch_pick():
    act_map = _act(2)
    for pick in (0, 1):
        resolved = tower_map.resolve_layer(act_map, 3, {"2": pick})
        expected = tower_map.layer_at(act_map, 2)["options"][pick]["enemy"]
        assert resolved["kind"] == "battle"
        assert resolved["enemy"] is expected

    final = _final_branch(2)
    resolved = tower_map.resolve_layer(act_map, final + 1, {str(final): 2})
    expected_room = tower_map.layer_at(act_map, final)["options"][2]["rooms"][1]
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
        if layer["kind"] == "battle" and layer["index"] != tower_map.boss_layer(1):
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
                if layer["index"] == tower_map.boss_layer(act):
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
