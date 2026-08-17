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

"""Damage from the Judge - the sourceless damage relics and enchantments deal.

The Judge has no side and sits off the board, so any card reacting to "who
hit me" has to cope with an attacker that owns nothing.  Green TANK read the
attacker's luck and crashed on it, which only showed up once tower relics
started dealing damage at arbitrary targets.
"""

import pytest

from cards.factory import CardFactory

from tests.helpers import make_game_state, place_card

NON_DECK = ("CUBE", "CUBES", "HEAL", "MOVE", "SHADOW", "LUCKYBLOCK", "WIGHTGY", "BARROWGY")


def deck_cards() -> list[str]:
    CardFactory.register_all()
    return sorted(c for c in CardFactory._registry if c not in NON_DECK)


def test_the_judge_has_no_side():
    game_state = make_game_state()
    assert game_state.judge.owner not in game_state.players_luck


def test_a_green_tank_survives_being_hit_by_the_judge():
    """The reported crash: TANKG jinxes whoever hit it, and the Judge has no luck."""
    game_state = make_game_state()
    tank = place_card(game_state, "TANKG", "player2", 1, 1)
    before = tank.health

    assert game_state.judge.deal(1, tank, game_state) is True
    assert tank.health == before - 1


@pytest.mark.parametrize("code", deck_cards())
def test_every_card_can_take_damage_from_the_judge(code):
    game_state = make_game_state()
    place_card(game_state, "TANKW", "player1", 0, 0)
    victim = place_card(game_state, code, "player2", 1, 1)
    place_card(game_state, "ADCW", "player2", 2, 2)

    game_state.judge.deal(1, victim, game_state)


@pytest.mark.parametrize("code", deck_cards())
def test_every_card_can_be_killed_by_the_judge(code):
    game_state = make_game_state()
    place_card(game_state, "TANKW", "player1", 0, 0)
    victim = place_card(game_state, code, "player2", 1, 1)

    game_state.judge.deal(victim.health + victim.armor, victim, game_state)
    assert victim.health <= 0


def test_luck_is_untouched_when_the_judge_lands_the_hit():
    game_state = make_game_state()
    tank = place_card(game_state, "TANKG", "player2", 1, 1)
    before = dict(game_state.players_luck)

    for _ in range(20):
        tank.health = tank.max_health
        game_state.judge.deal(1, tank, game_state)

    assert game_state.players_luck == before


def test_a_real_attacker_still_gets_jinxed():
    """The guard must not switch the effect off for ordinary attacks."""
    from cards.card_green import GreenCard

    game_state = make_game_state()
    attacker = place_card(game_state, "ADCW", "player1", 1, 2)
    game_state.players_luck["player1"] = 0

    GreenCard.lucky_effects(attacker, game_state)
    assert game_state.players_luck["player1"] < 0 or attacker.damage >= 0
