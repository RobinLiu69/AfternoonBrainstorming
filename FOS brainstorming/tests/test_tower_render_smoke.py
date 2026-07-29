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

"""Every tower screen draws one frame and leaves when told to.

Each screen renders first and handles events afterwards, so feeding it a
single escape keypress still exercises a whole frame of drawing.
"""

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from cards.factory import CardFactory
from core.game_screen import GameScreen

from tower import (
    battle_prep, card_picker, choice_screen, events, faction_select, map_screen,
    menu_screen, notice_screen, rooms, run_state, shop, shop_screen, tower_map,
    ui_common,
)

FACTIONS = ["R", "B", "C", "BR"]


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


@pytest.fixture
def escape(monkeypatch):
    """Make the next event loop iteration see an escape keypress."""
    def _install(module):
        monkeypatch.setattr(module, "key_pressed", lambda keys: pygame.K_ESCAPE)
        monkeypatch.setattr(pygame.event, "get",
                            lambda: [pygame.event.Event(pygame.KEYDOWN)])
    return _install


@pytest.fixture
def run():
    state = run_state.new_run(FACTIONS, seed=42)
    state["gold"] = 500
    state["orbs"] = 2
    state["bench"] = ["SPB"]
    run_state.add_relic(state, "piggy_bank")
    run_state.add_relic(state, "worn_pack")
    run_state.enchant_card(state, "deck", 0, "sharp")
    return state


def test_menu_screen_renders(game_screen, escape, run):
    escape(menu_screen)
    assert menu_screen.main(game_screen, {"run": run, "best_act": 2,
                                          "best_layer": 5, "runs_played": 3}) is None


def test_menu_screen_renders_without_a_run(game_screen, escape):
    escape(menu_screen)
    assert menu_screen.main(game_screen, {"run": None}) is None


def test_faction_select_renders(game_screen, escape):
    escape(faction_select)
    assert faction_select.main(game_screen) is None


def test_choice_screen_renders_cards_and_text_options(game_screen, escape, run):
    escape(choice_screen)
    options = [
        {"label": "TANKW", "color": ui_common.GOLD, "card": "TANKW"},
        {"label": "Piggy Bank", "lines": ["gold rewards +25%"], "color": ui_common.RELIC},
        {"label": "Sharp blade", "lines": ["+1 damage"], "color": ui_common.HILITE,
         "card": "ASSR*sharp"},
    ]
    assert choice_screen.main(game_screen, "Pick one", options, run=run,
                              subtitle="a subtitle", skip_label="skip",
                              cancel_label="cancel") is None


def test_card_picker_renders_deck_and_bench(game_screen, escape, run):
    escape(card_picker)
    assert card_picker.main(game_screen, run, "Burn which card?",
                            subtitle="costs 1 orb") is None


def test_notice_screen_renders(game_screen, escape, run):
    escape(notice_screen)
    notice_screen.main(game_screen, "Victory", ["+80 gold", "+1 orb"], run=run)


@pytest.mark.parametrize("layer", [0, 1, 2, 6, 8])
def test_map_screen_renders_every_layer_shape(game_screen, escape, run, layer):
    escape(map_screen)
    run["layer"] = layer
    assert map_screen.main(game_screen, run) is None


def test_map_screen_renders_a_linked_layer(game_screen, escape, run):
    escape(map_screen)
    run["layer"] = 2
    run_state.record_pick(run, 0)
    run["layer"] = 3
    assert map_screen.main(game_screen, run) is None


def test_map_screen_renders_under_the_blinding_curses(game_screen, escape, run):
    escape(map_screen)
    run_state.add_relic(run, "fog_of_war")
    run_state.add_relic(run, "sunglasses")
    run["layer"] = 2
    assert map_screen.main(game_screen, run) is None


def test_battle_prep_renders(game_screen, escape, run):
    escape(battle_prep)
    enemy = tower_map.boss_of(run_state.current_map(run))
    enemy_effects = run_state.effects_from_relics(enemy["relics"], enemy["effects"])
    assert battle_prep.main(game_screen, run, enemy,
                            run_state.battle_effects(run), enemy_effects) == "back"


def test_shop_screen_renders(game_screen, escape, run):
    escape(shop_screen)
    stock = shop.generate_stock(run, random.Random(1))
    shop_screen.main(game_screen, run, stock, random.Random(1))


@pytest.mark.parametrize("name", sorted(events.EVENTS))
def test_every_event_renders_and_survives_being_dismissed(game_screen, escape, run, name):
    escape(choice_screen)
    escape(notice_screen)
    run["act"] = events.EVENTS[name]["acts"][0]
    run_state.add_relic(run, "prepared_pack")
    assert events.enter(game_screen, run, random.Random(4), name) == ""


@pytest.mark.parametrize("kind", ["gold_mine", "relic_chest", "event"])
def test_rooms_render_and_return_cleanly(game_screen, escape, run, kind):
    escape(choice_screen)
    escape(notice_screen)
    assert rooms.enter(game_screen, run, {"kind": kind}, random.Random(2)) == ""
