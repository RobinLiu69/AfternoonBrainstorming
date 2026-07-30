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

"""Walking a whole climb without any screens, plus the battle-side hooks."""

import random

from shared import card_code
from cards.factory import CardFactory
from tower import (
    battle_builder, battle_effects, card_pool, enchant_runtime, grants,
    run_state, shop, tower_map,
)
from tower.tower_ai import TowerAIController

from tests.helpers import make_game_state

FACTIONS = ["R", "B", "C", "BR"]


def make_run(seed: int = 5) -> dict:
    return run_state.new_run(FACTIONS, seed=seed)


def walk_run(run: dict, pick: int = 0) -> list[dict]:
    """Advance through every layer of every act, taking the same branch each time."""
    visited: list[dict] = []
    while True:
        act_map = run_state.current_map(run)
        layer = tower_map.layer_at(act_map, run["layer"])
        if layer.get("options"):
            index = min(pick, len(layer["options"]) - 1)
            run_state.record_pick(run, index)
            visited.append({"kind": "room",
                            "room": tower_map.branch_choice_room(act_map, run["layer"], index)})
        else:
            visited.append(run_state.current_layer(run))
        if run_state.advance_layer(run) == "win":
            return visited


def test_a_whole_climb_resolves_every_layer():
    for seed in (1, 2, 3):
        for pick in (0, 1):
            run = make_run(seed)
            visited = walk_run(run, pick)
            # act 1 opens on the blessing layer, later acts start at layer 1
            assert len(visited) == 9 + 8 + 8
            assert run["act"] == tower_map.LAST_ACT


def test_every_battle_on_the_way_up_has_a_usable_enemy():
    CardFactory.register_all()
    registry = set(CardFactory._registry)
    run = make_run(11)
    battles = [entry for entry in walk_run(run) if entry["kind"] == "battle"]
    assert len(battles) == 3 * 4
    for entry in battles:
        enemy = entry["enemy"]
        assert enemy["deck"] and all(code in registry for code in enemy["deck"])
        assert enemy["strategy"]
        assert enemy["gold"] > 0


def test_each_act_ends_on_its_boss():
    run = make_run(21)
    bosses = [entry["enemy"] for entry in walk_run(run)
              if entry["kind"] == "battle" and entry["enemy"]["kind"] == "boss"]
    assert len(bosses) == 3
    assert bosses[1]["label"].endswith("Lord")
    assert all(boss["relics"] for boss in bosses)


def test_boss_relics_reach_the_enemy_effect_bundle():
    from tower import enemies
    lord = enemies.faction_lord("BR", random.Random(4))
    effects = run_state.effects_from_relics(lord["relics"], lord["effects"])
    assert effects["job_hp_plus"]["TANK"] >= 1
    # all of a boss's difficulty comes from its relics, never a global stat buff
    assert lord["effects"] == {}
    assert "unit_hp_plus" not in effects


def test_shop_stock_matches_the_design():
    for seed in range(20):
        run = make_run(seed)
        run["gold"] = 5000
        stock = shop.generate_stock(run, random.Random(seed))
        items = stock["items"]
        assert len(items) == shop.STOCK_SIZE
        assert sum(1 for i in items if i["kind"] == "orb") == 1
        assert 2 <= sum(1 for i in items if i["kind"] == "relic") <= 3
        assert all(i["price"] > 0 for i in items)


def test_shop_never_stocks_a_relic_you_cannot_take():
    run = make_run(3)
    run_state.add_relic(run, "amulet_ADC")
    for seed in range(10):
        stock = shop.generate_stock(run, random.Random(seed))
        for item in stock["items"]:
            if item["kind"] == "relic":
                assert item["relic"] != "amulet_ADC"
                assert not item["relic"].startswith("amulet_")


def test_courier_pays_for_the_first_reroll():
    run = make_run(7)
    stock = shop.generate_stock(run, random.Random(1))
    assert shop.reroll_price(run, stock) == shop.REROLL_PRICE

    run_state.add_relic(run, "courier")
    assert shop.reroll_price(run, stock) == 0
    stock["free_rerolls_used"] = 1
    assert shop.reroll_price(run, stock) == shop.REROLL_PRICE


def test_card_options_are_distinct_and_from_the_run_pool():
    run = make_run(9)
    pool = set(card_pool.run_card_pool(FACTIONS))
    for seed in range(10):
        options = grants.card_options(run, random.Random(seed), 3)
        assert len(options) == 3
        assert len(set(options)) == 3
        assert set(options) <= pool


def test_spells_and_white_cards_are_the_rare_ones():
    run = make_run(4)
    spells = whites = chosen = 0
    for seed in range(400):
        for code in grants.card_options(run, random.Random(seed), 3):
            if card_pool.is_magic(code):
                spells += 1
            elif card_pool.color_tag_of(code) == "W":
                whites += 1
            else:
                chosen += 1

    total = spells + whites + chosen
    assert spells / total < 0.16
    # White is 1 of 5 factions in the pool, so an even split would be ~20%
    assert whites / total < 0.12
    assert chosen / total > 0.7


def test_card_prices_sit_well_under_relic_prices():
    from tower import shop
    for code in ("HEAL", "ADCR", "TANKB"):
        assert card_pool.card_price(code) <= 60
    assert card_pool.card_price("ADCR*sharp") > card_pool.card_price("ADCR")
    assert max(card_pool.card_price(c) for c in ("HEAL", "ADCR", "TANKB")) < min(
        shop.RELIC_PRICE[tier] for tier in ("common", "rare", "power", "special"))


def test_battle_deck_is_the_deck_only_and_keeps_enchant_codes():
    run = make_run(2)
    run_state.enchant_card(run, "deck", 0, "sharp")
    run["bench"] = ["SPB"]
    enemy = tower_map.boss_of(run_state.current_map(run))

    game_state = battle_builder.build_game_state(run, enemy)
    assert game_state.player1.deck == run["deck"]
    assert "SPB" not in game_state.player1.deck
    assert card_code.is_enchanted(game_state.player1.deck[0])


def test_enchant_hook_adds_stats_when_a_card_is_played():
    enchant_runtime.install()
    try:
        game_state = make_game_state()
        base = CardFactory.create("TANKW", "player1", 0, 0)
        game_state.player1.hand = ["TANKW*sharp.fort"]
        game_state.player1.play_card(1, 1, 0, game_state)

        assert game_state.player1.hand == []
        played = game_state.player1.on_board[-1]
        assert played.job_and_color == "TANKW"
        assert played.damage == base.damage + 1
        assert played.max_health == base.health + 2
        assert played.health == played.max_health
    finally:
        enchant_runtime.uninstall()


def test_enchant_survives_death_and_returns_to_the_discard_pile():
    enchant_runtime.install()
    try:
        game_state = make_game_state()
        game_state.player1.hand = ["ASSW*sharp"]
        game_state.player1.play_card(1, 1, 0, game_state)
        unit = game_state.player1.on_board[-1]
        unit.health = 0

        class _Sink:
            dying_cards: list = []

        game_state.player1.recycle_cards(game_state, _Sink())
        assert game_state.player1.discard_pile == ["ASSW*sharp"]
    finally:
        enchant_runtime.uninstall()


def test_no_enchant_hook_means_plain_cards_are_untouched():
    enchant_runtime.uninstall()
    game_state = make_game_state()
    base = CardFactory.create("TANKW", "player1", 0, 0)
    game_state.player1.hand = ["TANKW"]
    game_state.player1.play_card(1, 1, 0, game_state)
    played = game_state.player1.on_board[-1]
    assert played.damage == base.damage
    assert played.max_health == base.health


def test_controller_pushes_run_relics_onto_the_player_units():
    run = make_run(6)
    run_state.add_relic(run, "amulet_TANK")

    enemy = {"strategy": "white", "strategy_overrides": {}, "relics": [], "effects": {}}
    controller = TowerAIController(enemy, {}, run_state.battle_effects(run))

    game_state = make_game_state()
    base = CardFactory.create("TANKW", "player1", 0, 0)
    game_state.player1.hand = ["TANKW"]
    game_state.player1.play_card(1, 1, 0, game_state)
    controller._maintain_units(game_state)

    unit = game_state.player1.on_board[-1]
    assert unit.max_health == base.health + 1


def test_first_unit_relics_only_touch_the_first_deploy():
    game_state = make_game_state()
    game_state.player1.hand = ["TANKW", "TANKW"]
    base = CardFactory.create("TANKW", "player1", 0, 0)

    side = battle_effects.SideRuntime({"first_unit_damage_plus": 1}, "player1")
    game_state.player1.play_card(1, 1, 0, game_state)
    side.maintain(game_state)
    game_state.player1.play_card(2, 2, 0, game_state)
    side.maintain(game_state)

    first, second = game_state.player1.on_board
    assert first.damage == base.damage + 1
    assert second.damage == base.damage
