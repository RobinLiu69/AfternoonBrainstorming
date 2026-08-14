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

from cards.card_white import Tank as WhiteTank
from core.game_state import GameState
from tests.helpers import make_game_state, place_card


def labels(game_state: GameState) -> list[str]:
    return [event.text for event in game_state.pending_combat_events
            if event.kind == "float" and event.text]


def kinds_at(game_state: GameState, x: int, y: int) -> set[str]:
    return {event.kind for event in game_state.pending_combat_events
            if (event.board_x, event.board_y) == (x, y)}


class TestStatAdjustAnimates:
    def test_a_buff_floats_one_green_label_for_every_stat_it_touched(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, armor=3, damage=3)

        assert labels(gs) == ["+3 SHIELD +3 ATK"]
        assert all(event.good for event in gs.pending_combat_events if event.text)
        assert (card.armor, card.damage) == (3, WhiteTank("player1", 0, 0).damage + 3)

    def test_a_debuff_floats_a_red_label(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, damage=-1)

        assert labels(gs) == ["-1 ATK"]
        assert not any(event.good for event in gs.pending_combat_events if event.text)

    def test_losing_health_plays_a_hurt_and_a_damage_number(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        before = card.health
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, health=-2)

        assert card.health == before - 2
        assert kinds_at(gs, 1, 1) == {"hurt", "float"}
        assert [e.damage for e in gs.pending_combat_events if e.kind == "float"] == [2]

    def test_losing_the_last_health_also_plays_a_death(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        card.health = 1
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, health=-3)

        assert card.health == 0
        assert card.pending_death is True
        assert "death" in kinds_at(gs, 1, 1)

    def test_stats_never_go_below_zero(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        card.damage = 0
        card.armor = 1
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, damage=-5, armor=-5, extra_damage=-5)

        assert (card.damage, card.armor, card.extra_damage) == (0, 0, 0)

    def test_touching_nothing_animates_nothing(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs)

        assert gs.pending_combat_events == []

    def test_the_caller_can_hold_the_label_back(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, damage=1, anim_delay=0.5)

        assert [event.delay for event in gs.pending_combat_events] == [0.5]
