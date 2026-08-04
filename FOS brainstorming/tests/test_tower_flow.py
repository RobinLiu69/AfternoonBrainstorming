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
    battle_builder, battle_effects, card_pool, enchant_runtime, enemies, grants,
    run_state, shop, tower_map,
)
from tower.content import RELICS
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
            expected = tower_map.layers_in_act(1) + sum(
                tower_map.layers_in_act(act) - 1 for act in (2, 3))
            assert len(visited) == expected
            assert run["act"] == tower_map.LAST_ACT


def test_every_battle_on_the_way_up_has_a_usable_enemy():
    CardFactory.register_all()
    registry = set(CardFactory._registry)
    run = make_run(11)
    battles = [entry for entry in walk_run(run) if entry["kind"] == "battle"]
    # one opener plus one per branch pair plus the boss, in each act
    assert len(battles) == sum(2 + tower_map.branch_pairs(act) for act in (1, 2, 3))
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


def test_the_shop_never_buys_a_relic_back():
    run = make_run(3)
    run_state.add_relic(run, "piggy_bank")
    stock = shop.generate_stock(run, random.Random(1))

    assert not hasattr(run_state, "sell_relic")
    assert not hasattr(shop, "sell_price")
    assert stock["curse_scrapped"] is False
    assert shop.curses_held(run) == []


def test_only_curses_can_be_paid_off():
    run = make_run(3)
    run_state.add_relic(run, "piggy_bank")
    run_state.add_relic(run, "worn_pack")
    assert shop.curses_held(run) == ["worn_pack"]
    assert shop.CURSE_REMOVAL_PRICE > 0


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


def test_spells_and_the_universal_factions_are_the_rare_ones():
    run = make_run(4)
    spells = universal = chosen = 0
    purple = 0
    for seed in range(400):
        for code in grants.card_options(run, random.Random(seed), 3):
            if card_pool.is_magic(code):
                spells += 1
            elif card_pool.is_universal(code):
                universal += 1
                purple += card_pool.color_tag_of(code) == "P"
            else:
                chosen += 1

    total = spells + universal + chosen
    assert spells / total < 0.16
    # White and Purple are 2 of 6 factions in the pool but weighted right down
    assert universal / total < 0.15
    assert chosen / total > 0.7
    # Purple is in there, just seldom
    assert 0 < purple / total < 0.08


def test_card_prices_sit_well_under_relic_prices():
    from tower import shop
    for code in ("HEAL", "ADCR", "TANKB"):
        assert card_pool.card_price(code) <= card_pool.BIG_UNIT_PRICE
    assert card_pool.card_price("ADCR*sharp") > card_pool.card_price("ADCR")
    assert max(card_pool.card_price(c) for c in ("HEAL", "ADCR", "TANKB")) < min(
        shop.RELIC_PRICE[tier] for tier in ("common", "rare", "power", "special"))


def answer_screens(monkeypatch, choices):
    """Feed grants' screens the choices a player would click."""
    queue = list(choices)
    monkeypatch.setattr(grants.choice_screen, "main",
                        lambda *a, **k: queue.pop(0) if queue else None)
    monkeypatch.setattr(grants.card_picker, "main", lambda *a, **k: None)


def test_a_relic_is_offered_one_at_a_time(monkeypatch):
    run = make_run(1)
    answer_screens(monkeypatch, [0])
    taken = grants.offer_relic(None, run, random.Random(2), "Spoils")

    assert taken is not None
    assert run["relics"] == [taken]
    assert run["gold"] == 0


def test_declining_a_relic_pays_a_little_gold(monkeypatch):
    run = make_run(1)
    answer_screens(monkeypatch, [1])
    assert grants.offer_relic(None, run, random.Random(2), "Spoils") is None
    assert run["relics"] == []
    assert run["gold"] == grants.DECLINE_RELIC_GOLD


def test_backing_out_of_a_relic_offer_is_a_decline(monkeypatch):
    run = make_run(1)
    answer_screens(monkeypatch, [None])
    assert grants.offer_relic(None, run, random.Random(2), "Spoils") is None
    assert run["relics"] == []


def test_only_boss_spoils_can_roll_a_special_relic(monkeypatch):
    specials = {r for r, v in RELICS.items() if v["tier"] == "special"}
    seen = set()
    for seed in range(60):
        run = make_run(seed)
        answer_screens(monkeypatch, [0])
        taken = grants.offer_relic(None, run, random.Random(seed), "Spoils")
        seen.add(taken)
    assert not (seen & specials)

    boss_seen = set()
    for seed in range(60):
        run = make_run(seed)
        answer_screens(monkeypatch, [0])
        boss_seen.add(grants.offer_relic(None, run, random.Random(seed), "Spoils",
                                         include_special=True))
    assert boss_seen & specials


def test_an_empty_pool_offers_nothing(monkeypatch):
    run = make_run(1)
    answer_screens(monkeypatch, [0])
    assert grants.offer_relic(None, run, random.Random(1), "Spoils",
                              tier="not_a_tier") is None
    assert run["relics"] == []


def count_options(monkeypatch, answer=0):
    """Record how many options each screen showed, and answer with `answer`."""
    seen: list[int] = []
    monkeypatch.setattr(grants.choice_screen, "main",
                        lambda gs, title, options, **k: seen.append(len(options)) or answer)
    monkeypatch.setattr(grants.card_picker, "main", lambda *a, **k: None)
    return seen


def test_curses_are_still_a_choice_of_three(monkeypatch):
    run = make_run(1)
    seen = count_options(monkeypatch)

    taken = grants.choose_relic(None, run, random.Random(3), "Take one curse",
                                tier="curse")
    assert seen == [3]
    assert RELICS[taken]["tier"] == "curse"


def test_a_curse_choice_cannot_be_walked_away_from(monkeypatch):
    run = make_run(1)
    monkeypatch.setattr(grants.choice_screen, "main", lambda *a, **k: None)
    monkeypatch.setattr(grants.card_picker, "main", lambda *a, **k: None)

    taken = grants.choose_relic(None, run, random.Random(3), "Take one curse",
                                tier="curse")
    assert taken is not None
    assert run["relics"] == [taken]


def test_boss_spoils_are_a_choice_of_three(monkeypatch):
    run = make_run(1)
    seen = count_options(monkeypatch)

    taken = grants.choose_relic(None, run, random.Random(3), "Boss spoils",
                                include_special=True,
                                decline_gold=grants.DECLINE_RELIC_GOLD)
    assert seen == [3]
    assert run["relics"] == [taken]


def test_boss_spoils_can_be_turned_down(monkeypatch):
    run = make_run(1)
    monkeypatch.setattr(grants.choice_screen, "main",
                        lambda *a, **k: grants.choice_screen.SKIP)
    monkeypatch.setattr(grants.card_picker, "main", lambda *a, **k: None)

    assert grants.choose_relic(None, run, random.Random(3), "Boss spoils",
                               decline_gold=grants.DECLINE_RELIC_GOLD) is None
    assert run["relics"] == []
    assert run["gold"] == grants.DECLINE_RELIC_GOLD


def test_the_final_boss_is_the_only_battle_with_no_reward():
    run = make_run(1)
    assert run_state.is_final_battle(run) is False

    run["act"] = tower_map.LAST_ACT
    run["layer"] = tower_map.boss_layer(tower_map.LAST_ACT)
    assert run_state.is_final_battle(run) is True

    run["act"] = 2
    run["layer"] = tower_map.boss_layer(2)
    assert run_state.is_final_battle(run) is False


def test_the_devils_bargain_blessing_pays_orbs_for_one_curse(monkeypatch):
    run = make_run(1)
    answer_screens(monkeypatch, [0])
    grants.apply_blessing(None, run, "orbs_and_curse", random.Random(1))

    assert run["orbs"] == 3
    assert len(run["relics"]) == 1
    assert RELICS[run["relics"][0]]["tier"] == "curse"


def test_skipping_a_card_reward_pays_nothing(monkeypatch):
    run = make_run(1)
    monkeypatch.setattr(grants.choice_screen, "main",
                        lambda *a, **k: grants.choice_screen.SKIP)
    monkeypatch.setattr(grants.card_picker, "main", lambda *a, **k: None)

    assert grants.offer_cards(None, run, random.Random(1)) is None
    assert run["gold"] == 0
    assert run_state.all_cards(run) == list(run["deck"])


def test_declining_a_relic_pays_nothing(monkeypatch):
    run = make_run(1)
    answer_screens(monkeypatch, [1])
    assert grants.offer_relic(None, run, random.Random(2), "Spoils") is None
    assert run["gold"] == 0
    assert run["relics"] == []


def test_enemies_never_move_first_in_act_one():
    for seed in range(20):
        for enemy in (enemies.weak_enemy(random.Random(seed), 0),
                      enemies.normal_enemy(1, FACTIONS, random.Random(seed)),
                      enemies.head_instructor(random.Random(seed))):
            assert enemy["enemy_first"] is False


def test_later_acts_sometimes_let_the_enemy_open():
    seen = set()
    for seed in range(60):
        seen.add(enemies.normal_enemy(2, FACTIONS, random.Random(seed))["enemy_first"])
    assert seen == {True, False}


def test_every_enemy_declares_who_moves_first():
    for act in (1, 2, 3):
        for seed in range(10):
            act_map = tower_map.build_act(act, FACTIONS, random.Random(seed))
            for layer in act_map["layers"]:
                found = [layer["enemy"]] if "enemy" in layer else []
                found += [o["enemy"] for o in layer.get("options", []) if "enemy" in o]
                for enemy in found:
                    assert isinstance(enemy["enemy_first"], bool)


def test_an_enemy_first_battle_starts_on_the_enemy_turn():
    run = make_run(4)
    enemy = dict(enemies.normal_enemy(2, FACTIONS, random.Random(1)))

    enemy["enemy_first"] = False
    assert battle_builder.build_game_state(run, enemy).turn_number == 0

    enemy["enemy_first"] = True
    game_state = battle_builder.build_game_state(run, enemy)
    assert game_state.turn_number == 1
    assert game_state.seat_on_turn() == "player2"


def test_the_opening_attack_goes_to_whoever_starts():
    for turn, opener in ((0, "player1"), (1, "player2")):
        game_state = make_game_state()
        game_state.turn_number = turn
        game_state.player1.deck = ["TANKW"] * 6
        game_state.player2.deck = ["TANKW"] * 6
        game_state.player1.initialize(game_state)
        game_state.player2.initialize(game_state)

        assert game_state.number_of_attacks[opener] == 1
        assert game_state.number_of_attacks[
            "player2" if opener == "player1" else "player1"] == 0
        assert len(game_state.player1.hand) == 3
        assert len(game_state.player2.hand) == 3


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
