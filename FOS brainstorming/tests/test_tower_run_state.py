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

from shared import card_code
from tower import card_pool, run_state, tower_map, tower_save
from tower.content import (
    BENCH_LIMIT, DECK_LIMIT, RELICS, SELECTABLE_FACTIONS, STARTER_DECK,
)

FACTIONS = ["R", "B", "C", "BR"]


def make_run(**overrides) -> dict:
    run = run_state.new_run(FACTIONS, seed=99)
    run.update(overrides)
    return run


def fill_deck(run: dict) -> None:
    while len(run["deck"]) < run_state.deck_limit(run):
        run["deck"].append("TANKW")


def test_new_run_starts_with_six_white_cards_and_no_bench():
    run = make_run()
    assert run["deck"] == list(STARTER_DECK)
    assert len(run["deck"]) == 6
    assert run["bench"] == []
    assert run_state.deck_limit(run) == DECK_LIMIT
    assert run_state.bench_limit(run) == BENCH_LIMIT


def test_cards_fill_the_deck_before_the_bench():
    run = make_run()
    fill_deck(run)
    assert run_state.next_slot(run) == "bench"
    assert run_state.add_card(run, "ADCR") == "bench"
    assert run_state.add_card(run, "ADCB") == "bench"
    assert run["bench"] == ["ADCR", "ADCB"]


def test_full_deck_and_bench_without_an_orb_rejects_the_card():
    run = make_run()
    fill_deck(run)
    run_state.add_card(run, "ADCR")
    run_state.add_card(run, "ADCB")
    assert run_state.next_slot(run) == "full"
    assert run_state.add_card(run, "ASSR") == "full"
    assert "ASSR" not in run_state.all_cards(run)


def test_an_orb_lets_a_full_run_swap_a_card_in():
    run = make_run(orbs=1)
    fill_deck(run)
    run_state.add_card(run, "ADCR")
    run_state.add_card(run, "ADCB")
    assert run_state.add_card(run, "ASSR") == "orb"

    burned = run["deck"][0]
    assert run_state.consume_orb_for(run, "ASSR", "deck", 0) is True
    assert run["orbs"] == 0
    assert run["deck"][0] == "ASSR"
    assert run["deck"].count(burned) == list(STARTER_DECK).count(burned) - 1


def test_bench_bonus_widens_the_bench():
    run = make_run(bench_bonus=2)
    assert run_state.bench_limit(run) == BENCH_LIMIT + 2


def test_limit_break_removes_the_deck_cap():
    run = make_run()
    run_state.add_relic(run, "limit_break")
    assert run_state.deck_limit(run) == 999
    assert run_state.free_bench(run) is True


def test_swap_deck_and_bench():
    run = make_run()
    fill_deck(run)
    run_state.add_card(run, "SPB")
    top = run["deck"][0]
    assert run_state.swap_deck_bench(run, 0, 0) is True
    assert run["deck"][0] == "SPB"
    assert run["bench"][0] == top


def test_orb_removal_needs_an_orb():
    run = make_run()
    assert run_state.spend_orb_to_remove(run, "deck", 0) is False
    run["orbs"] = 1
    assert run_state.spend_orb_to_remove(run, "deck", 0) is True
    assert len(run["deck"]) == len(STARTER_DECK) - 1
    assert run["orbs"] == 0


def test_enchanting_writes_into_the_card_code():
    run = make_run()
    assert run_state.enchant_card(run, "deck", 0, "sharp") is True
    assert card_code.enchant_keys(run["deck"][0]) == ("sharp",)
    assert run_state.enchanted_cards(run) == [("deck", 0)]
    assert run_state.enchant_card(run, "deck", 0, "not_a_real_enchant") is False


def test_a_card_only_ever_holds_one_enchantment():
    run = make_run()
    run_state.enchant_card(run, "deck", 0, "sharp")
    run_state.enchant_card(run, "deck", 0, "fort")
    assert card_code.enchant_keys(run["deck"][0]) == ("fort",)

    run_state.enchant_random_card(run, "burn", random.Random(1))
    for code in run_state.all_cards(run):
        assert len(card_code.enchant_keys(code)) <= 1


def test_random_enchant_hits_a_card_in_the_run():
    run = make_run()
    touched = run_state.enchant_random_card(run, "burn", random.Random(3))
    assert card_code.has_enchant(touched, "burn")
    assert touched in run_state.all_cards(run)


def test_relics_are_unique_and_groups_are_exclusive():
    run = make_run()
    assert run_state.add_relic(run, "amulet_ADC") is True
    assert run_state.add_relic(run, "amulet_ADC") is False
    assert run_state.can_take_relic(run, "amulet_TANK") is False
    assert run_state.can_take_relic(run, "emblem_TANK") is True


def test_faction_locked_relics_need_that_faction():
    run = make_run(factions=["R", "G", "O", "F"])
    assert run_state.can_take_relic(run, "mages_blood") is False
    assert run_state.can_take_relic(run, "treasure_chest") is False
    assert run_state.can_take_relic(make_run(), "mages_blood") is True


def test_relic_offers_hide_curses_and_respect_the_source_flag():
    run = make_run()
    drops = run_state.relic_offers(run)
    assert all(RELICS[r]["tier"] != "curse" for r in drops)
    assert "unchanging_stone" not in drops
    assert "coupon" in drops

    stock = run_state.relic_offers(run, source="shop")
    assert "coupon" not in stock
    assert "unchanging_stone" in stock


def test_special_relics_are_boss_spoils_only():
    run = make_run()
    specials = {r for r, v in RELICS.items() if v["tier"] == "special"}
    assert specials

    for offers in (run_state.relic_offers(run),
                   run_state.relic_offers(run, source="shop")):
        assert not (set(offers) & specials)

    boss_spoils = set(run_state.relic_offers(run, include_special=True))
    assert boss_spoils & specials
    assert all(RELICS[r]["tier"] != "curse" for r in boss_spoils)


def test_the_current_emblem_is_not_in_the_game_yet():
    assert "current_emblem" not in RELICS


def test_gold_multiplier_and_award():
    run = make_run()
    assert run_state.award_gold(run, 100) == 100
    run_state.add_relic(run, "piggy_bank")
    assert run_state.award_gold(run, 100) == 125
    assert run["gold"] == 225


def test_shop_discounts_multiply():
    run = make_run()
    run_state.add_relic(run, "coupon")
    assert run_state.shop_discount(run) == 0.5


def test_index_fund_pays_until_you_spend_in_a_shop():
    run = make_run(gold=200)
    run_state.add_relic(run, "index_fund")
    assert run_state.floor_upkeep(run)["interest"] == 20
    assert run["gold"] == 220

    run_state.spend_gold(run, 20)
    assert run_state.floor_upkeep(run)["interest"] == 0


def test_torn_wallet_leaks_gold_but_never_below_zero():
    run = make_run(gold=10)
    run_state.add_relic(run, "torn_wallet")
    run_state.floor_upkeep(run)
    assert run["gold"] == 0


def test_demon_emblem_only_fires_past_six_spells():
    run = make_run()
    run_state.add_relic(run, "demon_emblem")
    assert "unit_hp_plus" not in run_state.merged_effects(run)

    run["deck"] = ["HEAL"] * 7
    effects = run_state.merged_effects(run)
    assert effects["unit_hp_plus"] == 2
    assert effects["unit_damage_plus"] == 1


def test_tank_bloodline_needs_an_all_tank_deck():
    run = make_run()
    run_state.add_relic(run, "tank_bloodline")
    assert "job_hp_plus" not in run_state.merged_effects(run)

    run["deck"] = ["TANKW", "TANKR", "HEAL"]
    effects = run_state.merged_effects(run)
    assert effects["job_hp_plus"] == {"TANK": 3}
    assert effects["double_tank_effects"] == 1


def test_job_relic_effects_stack_per_job():
    run = make_run()
    run_state.add_relic(run, "amulet_TANK")
    run_state.add_relic(run, "emblem_ADC")
    effects = run_state.merged_effects(run)
    assert effects["job_hp_plus"] == {"TANK": 1}
    assert effects["job_damage_plus"] == {"ADC": 1}


def test_blasting_wand_buffs_ap_and_sets_its_flag():
    run = make_run()
    run_state.add_relic(run, "blasting_wand")
    effects = run_state.merged_effects(run)
    assert effects["job_damage_plus"] == {"AP": 2}
    assert effects["ap_no_numb"] == 1


def test_blessing_offers_are_three_distinct_and_seed_stable():
    run = make_run()
    offers = run_state.blessing_offers(run)
    assert len(offers) == 3
    assert len({o["id"] for o in offers}) == 3
    assert run_state.blessing_offers(run) == offers


def test_advance_walks_layers_then_acts_then_wins():
    run = make_run()
    run["layer"] = tower_map.boss_layer(1) - 1
    assert run_state.advance_layer(run) == "layer"
    assert run["layer"] == tower_map.boss_layer(1)

    run["picks"] = {"2": 1}
    assert run_state.advance_layer(run) == "act"
    assert (run["act"], run["layer"]) == (2, 1)
    assert run["picks"] == {}

    run["act"] = tower_map.LAST_ACT
    run["layer"] = tower_map.boss_layer(tower_map.LAST_ACT)
    assert run_state.advance_layer(run) == "win"


def test_current_layer_follows_recorded_picks():
    run = make_run()
    run["layer"] = 2
    run_state.record_pick(run, 1)
    assert run_state.pick_for(run, 2) == 1

    run["layer"] = 3
    resolved = run_state.current_layer(run)
    expected = tower_map.layer_at(run_state.current_map(run), 2)["options"][1]["enemy"]
    assert resolved["enemy"] is expected


def test_run_pool_holds_the_universal_factions_and_the_chosen_ones():
    from tower.content import UNIVERSAL_FACTIONS

    pool = card_pool.run_card_pool(FACTIONS)
    tags = {card_pool.color_tag_of(c) for c in pool if not card_pool.is_magic(c)}
    assert tags == set(FACTIONS) | set(UNIVERSAL_FACTIONS)
    # Purple is never draftable but its four cards can still turn up as rewards
    assert "TANKP" in pool
    assert "P" not in SELECTABLE_FACTIONS


def test_a_faction_you_did_not_draft_stays_out_of_the_pool():
    pool = card_pool.run_card_pool(["R", "B", "C", "BR"])
    tags = {card_pool.color_tag_of(c) for c in pool if not card_pool.is_magic(c)}
    assert "G" not in tags
    assert "O" not in tags


def test_save_validation_drops_unknown_content_but_keeps_the_run():
    run = make_run(orbs=2)
    run["deck"].append("NOT_A_CARD")
    run["relics"] = ["piggy_bank", "not_a_relic"]
    run["factions"] = ["R", "B", "C", "BR", "ZZ"]
    run["picks"] = {2: 1}

    validated = tower_save.validate_run(run)
    assert validated is not None
    assert "NOT_A_CARD" not in validated["deck"]
    assert validated["relics"] == ["piggy_bank"]
    assert validated["factions"] == ["R", "B", "C", "BR"]
    assert validated["picks"] == {"2": 1}


def test_save_validation_rejects_a_run_with_no_deck():
    run = make_run()
    run["deck"] = ["NOT_A_CARD"]
    run["bench"] = []
    assert tower_save.validate_run(run) is None


def test_enchanted_codes_survive_save_validation():
    run = make_run()
    run_state.enchant_card(run, "deck", 0, "sharp")
    enchanted = run["deck"][0]
    assert tower_save.validate_run(run)["deck"][0] == enchanted
