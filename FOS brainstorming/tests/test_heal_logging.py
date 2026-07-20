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

from shared.stat_type import StatType
from tests.helpers import make_game_state, place_card


def _heal_entries(entries):
    return [e for e in entries if e.data.get("heal") is not None]


def _heal_plays(entries):
    return [e for e in entries if e.data.get("card") == "HEAL"]


def test_successful_heal_logs_play_and_result():
    gs = make_game_state()
    entries = []
    gs.game_logger.subscribe(entries.append)
    tank = place_card(gs, "TANKG", "player1", 1, 1)
    tank.health -= 4
    gs.number_of_heals["player1"] = 1

    gs.player1.heal_card(1, 1, gs)

    assert tank.health == tank.max_health - 4 + 6 or tank.health == tank.max_health
    assert gs.number_of_heals["player1"] == 0
    assert gs.game_statistics.get(StatType.HEAL_USE, "player1") == 1
    assert len(_heal_plays(entries)) == 1
    heals = _heal_entries(entries)
    assert len(heals) == 1
    assert heals[0].data["heal"] == 6
    assert heals[0].data["post_health"] == tank.health


def test_missed_heal_logs_nothing_and_keeps_charge():
    gs = make_game_state()
    entries = []
    gs.game_logger.subscribe(entries.append)
    place_card(gs, "TANKG", "player1", 1, 1)
    place_card(gs, "TANKG", "player2", 2, 1)
    gs.number_of_heals["player1"] = 1

    gs.player1.heal_card(3, 2, gs)
    gs.player1.heal_card(2, 1, gs)

    assert gs.number_of_heals["player1"] == 1
    assert gs.game_statistics.get(StatType.HEAL_USE, "player1") == 0
    assert _heal_plays(entries) == []
    assert _heal_entries(entries) == []


def test_ability_heal_logs_result():
    gs = make_game_state()
    entries = []
    gs.game_logger.subscribe(entries.append)
    card = place_card(gs, "TANKG", "player1", 1, 1)
    card.health -= 2

    card.heal(1, gs)

    heals = _heal_entries(entries)
    assert len(heals) == 1
    assert heals[0].data["heal"] == 1
    assert heals[0].data["post_health"] == card.health
