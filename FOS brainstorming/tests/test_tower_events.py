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

"""Events: which ones can come up, and what each choice does to the run.

The screens are driven by stubbing ``choice_screen.main`` and
``card_picker.main`` with the answers a player would click.
"""

import random

import pytest

from shared import card_code
from tower import card_pool, events, run_state
from tower.content import ARTISAN_ENCHANTS

FACTIONS = ["R", "B", "C", "BR"]


@pytest.fixture
def run():
    return run_state.new_run(FACTIONS, seed=17)


@pytest.fixture
def answer(monkeypatch):
    """Queue up the choices a player would make on each screen."""
    def _install(choices=(), cards=()):
        choice_queue = list(choices)
        card_queue = list(cards)
        monkeypatch.setattr(events.choice_screen, "main",
                            lambda *a, **k: choice_queue.pop(0) if choice_queue else None)
        monkeypatch.setattr(events.card_picker, "main",
                            lambda *a, **k: card_queue.pop(0) if card_queue else None)
        monkeypatch.setattr(events.notice_screen, "main", lambda *a, **k: None)
        monkeypatch.setattr(events.grants, "offer_cards", lambda *a, **k: None)
        monkeypatch.setattr(events.grants.choice_screen, "main",
                            lambda *a, **k: choice_queue.pop(0) if choice_queue else None)
    return _install


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------

def test_act_one_only_offers_act_one_events(run):
    run["act"] = 1
    assert "visitor" not in events.candidates(run)
    assert "prism" not in events.candidates(run)
    assert "altar" in events.candidates(run)


def test_the_visitor_belongs_to_act_two(run):
    run["act"] = 2
    assert "visitor" in events.candidates(run)


def test_conditional_events_wait_for_their_condition(run):
    run["act"] = 3
    assert "tinker" not in events.candidates(run)
    assert "relic_trader" not in events.candidates(run)

    run_state.enchant_card(run, "deck", 0, "sharp")
    run_state.add_relic(run, "piggy_bank")
    assert "tinker" in events.candidates(run)
    assert "relic_trader" in events.candidates(run)


def test_the_tinker_shows_up_more_as_you_enchant(run):
    base = events.weight_of(run, "tinker")
    run_state.enchant_card(run, "deck", 0, "sharp")
    run_state.enchant_card(run, "deck", 1, "fort")
    assert events.weight_of(run, "tinker") > base


def test_the_prism_needs_a_white_card_left(run):
    run["act"] = 3
    assert "prism" in events.candidates(run)
    run["deck"] = ["TANKR", "ADCB"]
    assert "prism" not in events.candidates(run)


def test_pick_always_returns_something_playable(run):
    for act in (1, 2, 3):
        run["act"] = act
        for seed in range(10):
            name = events.pick(run, random.Random(seed))
            assert name in events.EVENTS
            assert act in events.EVENTS[name]["acts"]


# --------------------------------------------------------------------------
# altar
# --------------------------------------------------------------------------

def rigged_altar(*deal_ids: str) -> random.Random:
    """An rng whose altar always offers exactly these deals, in order."""
    deals = [next(d for d in events.ALTAR_DEALS if d["id"] == i) for i in deal_ids]
    rng = random.Random(1)
    rng.sample = lambda seq, k: deals[:k]
    return rng


def test_altar_gold_deals_pay_out(run, answer):
    answer(choices=[0])
    events._altar(None, run, rigged_altar("gold_150", "orb"))
    assert run["gold"] == 150


def test_altar_purchases_take_the_gold(run, answer):
    answer(choices=[1])
    run["gold"] = 200

    events._altar(None, run, rigged_altar("gold_150", "orb"))
    assert run["orbs"] == 1
    assert run["gold"] == 50


def test_altar_refuses_when_you_are_broke(run, answer):
    answer(choices=[1])
    run["gold"] = 10

    events._altar(None, run, rigged_altar("gold_150", "orb"))
    assert run["orbs"] == 0
    assert run["gold"] == 10


def test_leaving_the_altar_costs_nothing(run, answer):
    answer(choices=[2])
    run["gold"] = 500
    events._altar(None, run, rigged_altar("gold_150", "orb"))
    assert run["gold"] == 500
    assert run["orbs"] == 0


def test_the_altar_always_puts_two_rites_on_the_table(run, answer, monkeypatch):
    seen: list = []
    monkeypatch.setattr(events.choice_screen, "main",
                        lambda screen, title, options, **k: seen.append(options) or None)
    seed = 0
    while events.altar_deals_left(run):
        events._altar(None, run, random.Random(seed))
        seed += 1
    for options in seen[:-1]:
        assert len(options) == events.ALTAR_OFFER_COUNT + 1
        labels = [o["label"] for o in options[:-1]]
        assert len(set(labels)) == events.ALTAR_OFFER_COUNT


def test_the_altar_never_offers_the_same_rite_twice(run, answer, monkeypatch):
    offered: list[str] = []
    monkeypatch.setattr(
        events.choice_screen, "main",
        lambda screen, title, options, **k: offered.extend(
            o["label"] for o in options[:-1]) or None)

    seed = 0
    while events.altar_deals_left(run):
        events._altar(None, run, random.Random(seed))
        seed += 1

    assert len(offered) == len(set(offered))
    assert len(offered) == len(events.ALTAR_DEALS)


def test_a_spent_altar_stops_showing_up(run):
    run["act"] = 1
    assert "altar" in events.candidates(run)
    run["altar_deals_used"] = [deal["id"] for deal in events.ALTAR_DEALS]
    assert "altar" not in events.candidates(run)


def test_the_altar_no_longer_offers_the_smallest_purse():
    assert "gold_50" not in {deal["id"] for deal in events.ALTAR_DEALS}


def test_an_event_you_have_seen_does_not_come_round_again(run):
    run["act"] = 3
    run_state.enchant_card(run, "deck", 0, "sharp")
    assert "tinker" in events.candidates(run)

    run["events_seen"] = ["tinker", "prism"]
    assert "tinker" not in events.candidates(run)
    assert "prism" not in events.candidates(run)
    # the altar and the trader can still come round
    assert "altar" in events.candidates(run)


def test_entering_an_event_records_it(run, answer):
    answer(choices=[1])
    events.enter(None, run, random.Random(1), "prism")
    assert run["events_seen"] == ["prism"]


def test_pick_falls_back_to_repeatables_once_everything_is_seen(run):
    run["act"] = 3
    run["events_seen"] = list(events.EVENTS)
    for seed in range(10):
        assert events.pick(run, random.Random(seed)) in events.REPEATABLE_EVENTS


# --------------------------------------------------------------------------
# relic trader
# --------------------------------------------------------------------------

def test_relic_trader_swaps_one_for_one(run, answer):
    run_state.add_relic(run, "piggy_bank")
    answer(choices=[0])
    events._relic_trader(None, run, random.Random(3))

    assert "piggy_bank" not in run["relics"]
    assert len(run["relics"]) == 1


def test_walking_away_from_the_trader_keeps_your_relic(run, answer):
    run_state.add_relic(run, "piggy_bank")
    answer(choices=[2])
    events._relic_trader(None, run, random.Random(3))
    assert run["relics"] == ["piggy_bank"]


# --------------------------------------------------------------------------
# tinker
# --------------------------------------------------------------------------

def test_tinker_strips_an_enchantment(run, answer):
    run_state.enchant_card(run, "deck", 0, "bleed")
    answer(choices=[0], cards=[("deck", 0)])
    events._tinker(None, run, random.Random(2))
    assert card_code.enchant_keys(run["deck"][0]) == ()


def test_tinker_reforges_into_an_artisan_grade(run, answer):
    run_state.enchant_card(run, "deck", 0, "sharp")
    answer(choices=[1], cards=[("deck", 0)])
    events._tinker(None, run, random.Random(2))

    keys = card_code.enchant_keys(run["deck"][0])
    assert len(keys) == 1
    assert keys[0] in ARTISAN_ENCHANTS


def test_tinker_will_not_reforge_a_cursed_card(run, answer):
    run_state.enchant_card(run, "deck", 0, "burn")
    answer(choices=[1], cards=[("deck", 0)])
    events._tinker(None, run, random.Random(2))
    assert card_code.has_enchant(run["deck"][0], "burn")


# --------------------------------------------------------------------------
# act 3 events
# --------------------------------------------------------------------------

def test_the_statue_enrages_a_unit(run, answer):
    answer(choices=[0], cards=[("deck", 2)])
    events._beast_statue(None, run, random.Random(1))
    assert card_code.has_enchant(run["deck"][2], "rage")


def test_the_statue_offers_an_orb_instead_of_a_dead_end(run, answer):
    answer(choices=[1])
    events._beast_statue(None, run, random.Random(1))
    assert run_state.enchanted_cards(run) == []
    assert run["orbs"] == events.STATUE_ORBS


def test_the_prism_disperses_a_white_card(run, answer):
    answer(choices=[0], cards=[("deck", 0)])
    events._prism(None, run, random.Random(1))
    assert card_code.has_enchant(run["deck"][0], "disperse")
    assert run["gold"] == 0


def test_the_prism_pays_out_if_you_decline(run, answer):
    answer(choices=[1])
    events._prism(None, run, random.Random(1))
    assert run["gold"] == events.PRISM_GOLD


def test_the_prism_pays_out_if_you_pick_no_card(run, answer):
    answer(choices=[0], cards=[])
    events._prism(None, run, random.Random(1))
    assert run["gold"] == events.PRISM_GOLD


# --------------------------------------------------------------------------
# visitor
# --------------------------------------------------------------------------

def test_the_wanderer_pays_a_flat_price_or_a_gamble(run, answer):
    answer(choices=[0])
    events._wanderer(None, run, random.Random(1))
    assert run["gold"] == events.WANDERER_GOLD

    run["gold"] = 0
    answer(choices=[1])
    events._wanderer(None, run, random.Random(1))
    assert run["gold"] in (events.HAGGLE_WIN, events.HAGGLE_LOSS)


def test_every_event_offers_at_least_two_real_choices(run, monkeypatch):
    """No event may be "one reward or leave" - that is just a gold mine."""
    seen: dict[str, list] = {}

    def capture(name):
        def _main(screen, title, options, **kwargs):
            seen.setdefault(name, []).append(options)
            return None
        return _main

    run["gold"] = 1000
    run_state.add_relic(run, "piggy_bank")
    run_state.enchant_card(run, "deck", 0, "sharp")
    monkeypatch.setattr(events.notice_screen, "main", lambda *a, **k: None)
    monkeypatch.setattr(events.card_picker, "main", lambda *a, **k: None)
    monkeypatch.setattr(events.grants, "offer_cards", lambda *a, **k: None)

    for name in sorted(events.EVENTS):
        monkeypatch.setattr(events.choice_screen, "main", capture(name))
        run["act"] = events.EVENTS[name]["acts"][0]
        events.enter(None, run, random.Random(6), name)

        options = seen[name][0]
        rewards = [o for o in options if o["color"] != events.ui_common.DIM]
        assert len(rewards) >= 2, f"{name} only offers {len(rewards)} real choice(s)"


def test_the_visitor_hands_out_a_parting_gift(run, answer):
    answer(choices=[3])
    before = len(run_state.all_cards(run))
    events._visitor(None, run, random.Random(5))
    assert len(run_state.all_cards(run)) == before + 1


def test_the_visitor_sells_a_unit(run, answer):
    run["gold"] = 500
    answer(choices=[0, 0, 3])
    before = len(run_state.all_cards(run))
    events._visitor(None, run, random.Random(5))

    assert run["gold"] == 500 - events.VISITOR_UNIT_PRICE
    assert len(run_state.all_cards(run)) == before + 2


def test_losing_the_visitor_bout_ends_the_climb(run, answer, monkeypatch):
    answer(choices=[2])
    monkeypatch.setattr(events.battle_flow, "fight", lambda *a, **k: "lose")
    assert events._visitor(None, run, random.Random(5)) == "lose"


def test_winning_the_visitor_bout_pays_for_everything(run, answer, monkeypatch):
    answer(choices=[2, 0])
    monkeypatch.setattr(events.battle_flow, "fight", lambda *a, **k: "win")

    before_cards = len(run_state.all_cards(run))
    assert events._visitor(None, run, random.Random(5)) == ""
    assert run["gold"] == 0
    assert len(run_state.all_cards(run)) == before_cards + 1
    assert len(run["relics"]) == 1


def test_the_visitor_champion_is_a_lighter_lord():
    champion = events._visitor_champion("BR", random.Random(2))
    assert champion["kind"] == "boss"
    assert len(champion["relics"]) == 1
    assert champion["deck"]
    assert {card_pool.color_tag_of(c) for c in champion["deck"]} == {"BR"}
