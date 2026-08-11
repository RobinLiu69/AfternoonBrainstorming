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

"""Blue — token economy.

Tokens convert to cards at a fixed rate. That conversion is a rule of the game
rather than an ability of any blue card, so it lives on GameState; the cards
here only produce tokens and react to them.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import aura, on
from cards.events import Event, Resource
from cards.stats import DAMAGE, Modifier

blue = color("Blue", "B")


def _gained_tokens(card, ctx) -> bool:
    return ctx.resource_name == Resource.TOKEN and ctx.amount > 0


@blue("ADC")
class Adc:
    """Turns drawn cards into free attacks."""

    @on(Event.ON_KILL)
    def bounty(card, ctx):
        ctx.gain(Resource.TOKEN, ctx.settings("token_gain"))

    @on(Event.CARD_DRAWN)
    def ride_the_draw(card, ctx):
        # A numb copy spends the draw shaking off the numbness instead.
        if card.numbness:
            ctx.numb(card, False)
        else:
            ctx.attack_with(card)


@blue("AP")
class Ap:
    """Numbs and banks tokens."""

    @on(Event.ON_HIT)
    def numb_and_bank(card, ctx):
        ctx.numb(ctx.target)
        ctx.gain(Resource.TOKEN, ctx.settings("token_gain"))


@blue("TANK")
class Tank:
    """Banks a token every time it is struck."""

    @on(Event.AFTER_DAMAGE_TAKEN)
    def bank(card, ctx):
        ctx.gain(Resource.TOKEN, ctx.settings("token_gain"))


@blue("HF")
class Hf:
    """Hits for as much as the bank is holding."""

    @aura()
    def token_power(card, game_state):
        yield Modifier.aura(DAMAGE, game_state.players_token.get(card.owner, 0), card=card)


@blue("LF")
class Lf:
    """Banks a token on every hit."""

    @on(Event.ON_HIT)
    def bank(card, ctx):
        ctx.gain(Resource.TOKEN, ctx.settings("token_gain"))


@blue("ASS")
class Ass:
    """Banks tokens on kills."""

    @on(Event.ON_KILL)
    def bounty(card, ctx):
        ctx.gain(Resource.TOKEN, ctx.settings("token_gain"))


@blue("APT")
class Apt:
    """Converts armour into damage and damage back into tokens."""

    @aura()
    def armour_power(card, game_state):
        divisor = card.definition.settings.get("token_from_armor_divisor", 3)
        yield Modifier.aura(DAMAGE, card.armor // divisor, card=card)

    @on(Event.AFTER_DAMAGE_DEALT)
    def bank_the_damage(card, ctx):
        ctx.gain(Resource.TOKEN, ctx.amount)

    @on(Event.RESOURCE_GAINED, when=_gained_tokens)
    def plate_up(card, ctx):
        ctx.add_armor(card, 1)


@blue("SP")
class Sp:
    """Sprays the enemy board on arrival, once per card already committed."""

    @on(Event.DEPLOYED)
    def opening_barrage(card, ctx):
        player = ctx.gs.get_player(card.owner)
        shots = len(player.on_board) + len(player.discard_pile)
        damage = ctx.settings("spawn_damage")
        for _ in range(shots):
            living = ctx.enemies()
            if not living:
                break
            ctx.deal_damage(living[ctx.rng.randrange(len(living))], damage)
        # The barrage must not also set off a chain of retaliatory attacks.
        ctx.cancel_queued_attacks()
