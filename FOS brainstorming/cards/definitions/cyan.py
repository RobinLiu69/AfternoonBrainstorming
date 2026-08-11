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

"""Cyan — coins and upgrades.

Every cyan card has an upgraded printing, chosen in hand and paid for on
arrival. The upgrade is a *variant* of one definition rather than a separate
card, so the two printings cannot drift apart, and it lives in ``vars`` which
serialises generically — no bespoke to_dict is needed to keep it across a
network sync.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import Priority, aura, on, replaces
from cards.events import Event, Resource
from cards.stats import DAMAGE, SCORE, Modifier, Op
from cards.statuses import FIRST_STRIKE, SPENT, UNDYING, WARDED
from shared.setting import CARD_SETTING

cyan = color("Cyan", "C")

UPGRADE = "upgrade"
_CYAN = CARD_SETTING["Cyan"]
TEMPORARY = "temporary"


def _variants(job: str) -> dict[str, dict[str, int]]:
    settings = _CYAN[job]
    return {UPGRADE: {"health": settings["upgrade_health"], "damage": settings["upgrade_damage"]}}


def _upgraded(card, _ctx=None) -> bool:
    return card.variant == UPGRADE


def _pay_for_upgrade(card, cost) -> None:
    """Upgraded copies are bought on arrival; friendly upgraded SP discounts them."""
    if card.variant != UPGRADE:
        return
    discount = _CYAN["SP"]["cost_reduction"] * cost.gs.count_cards(
        lambda c: c.job_and_color == "SPC" and c.variant == UPGRADE and c.owner == card.owner
    )
    price = card.definition.settings["cost"] - discount
    if cost.gs.players_coin.get(card.owner, 0) >= price:
        cost.gs.players_coin[card.owner] -= price
    else:
        cost.cancel()


# Attached to every cyan card; the price is read from that card's own settings.
_deploy_cost = replaces(Event.DEPLOY_COST)(_pay_for_upgrade)


@cyan("ADC", variants=_variants("ADC"))
class Adc:
    """Robs on hit; upgraded, it strikes twice."""

    pay = _deploy_cost

    @on(Event.ON_HIT)
    def rob(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))

    @on(Event.ATTACKED, when=_upgraded)
    def double_strike(card, ctx):
        ctx.attack_now()


@cyan("AP", variants=_variants("AP"))
class Ap:
    """Opens fire on arrival; upgraded, an ally fires on its behalf."""

    pay = _deploy_cost

    @on(Event.ON_HIT)
    def rob(card, ctx):
        ctx.numb(ctx.target)
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))

    @on(Event.DEPLOYED)
    def opening_volley(card, ctx):
        for _ in range(ctx.settings("number_of_attack")):
            if card.variant != UPGRADE:
                ctx.attack_now(ignore_numb=True)
                continue
            ready = [
                c for c in ctx.allies()
                if c is not card and not c.numbness
                and any(shape in c.attack_types for shape in ("nearest", "farthest"))
            ]
            if not ready:
                ctx.attack_now(ignore_numb=True)
                continue
            # An ally shoots, but at the targets this card can reach.
            ctx.attack_now(ctx.rng.choice(ready), targets=ctx.targets(card.attack_types))


@cyan("TANK", variants=_variants("TANK"))
class Tank:
    """Upgraded, it shrugs off the first hit entirely."""

    pay = _deploy_cost

    @on(Event.DEPLOYED, when=_upgraded)
    def raise_ward(card, ctx):
        ctx.set_status(card, WARDED)

    @replaces(Event.DAMAGE_PREVENTION, when=lambda card, event: (
        event.victim is card and WARDED in card.statuses
    ))
    def absorb(card, event):
        card.statuses.discard(WARDED)
        event.cancel()

    @on(Event.AFTER_DAMAGE_TAKEN)
    def rob(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))


@cyan("HF", variants=_variants("HF"))
class Hf:
    """Upgraded, it lingers one turn past death — and stops scoring after."""

    pay = _deploy_cost

    @on(Event.ON_HIT)
    def rob(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))

    @on(Event.ON_KILLED, when=_upgraded)
    def refuse_to_die(card, ctx):
        ctx.set_status(card, UNDYING)
        ctx.buff(card, damage=ctx.settings("damage_bonus"))

    @replaces(Event.LETHAL)
    def linger(card, event):
        if UNDYING in card.statuses:
            event.prevent()

    @aura()
    def borrowed_time_scores_nothing(card, game_state):
        if UNDYING in card.statuses or SPENT in card.statuses:
            yield Modifier.aura(SCORE, 0, card=card, op=Op.SET)

    @on(Event.TURN_END)
    def spend_the_reprieve(card, ctx):
        if UNDYING in card.statuses:
            ctx.set_status(card, UNDYING, False)
            ctx.set_status(card, SPENT)


@cyan("LF", variants=_variants("LF"))
class Lf:
    """Upgraded, it re-rolls its attack shape every turn."""

    pay = _deploy_cost

    @on(Event.ON_HIT)
    def rob(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))

    @on(Event.TURN_START, when=_upgraded)
    def reroll_shape(card, ctx):
        card.vars["pattern"] = ctx.rng.choice(
            ["large_cross", "nearest", "small_cross", "small_cross small_x", "farthest"]
        )


@cyan("ASS", variants=_variants("ASS"))
class Ass:
    """Upgraded, its first strike of the game carries bonus damage."""

    pay = _deploy_cost

    @on(Event.DEPLOYED, when=_upgraded)
    def load(card, ctx):
        ctx.set_status(card, FIRST_STRIKE)
        ctx.grant(
            card, DAMAGE, ctx.settings("damage_bonus"),
            tags=(TEMPORARY,), permanent=False,
        )

    @on(Event.AFTER_DAMAGE_DEALT, when=lambda card, ctx: FIRST_STRIKE in card.statuses)
    def spend_the_shot(card, ctx):
        ctx.set_status(card, FIRST_STRIKE, False)
        ctx.strip(card, tags=(TEMPORARY,))

    @on(Event.ON_KILL)
    def bounty(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))


@cyan("APT", variants=_variants("APT"))
class Apt:
    """Upgraded, wealth becomes damage resistance."""

    pay = _deploy_cost

    # EARLY: a resistance on the victim itself, which the old pipeline applied
    # before any board-wide interception such as Fuchsia APT's halving.
    @replaces(Event.DAMAGE_MODIFY, priority=Priority.EARLY, when=lambda card, event: (
        event.victim is card and card.variant == UPGRADE
    ))
    def wealth_as_armour(card, event):
        settings = card.definition.settings
        per = settings["coin_per_damage_resistance"]
        cap = settings["maximum_damage_resistance"]
        coins = event.victim._gs.players_coin.get(card.owner, 0) if event.victim._gs else 0
        event.reduce_by(min(coins // per, cap))

    @on(Event.TURN_START)
    def stipend(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))


@cyan("SP", variants=_variants("SP"))
class Sp:
    """A payday on arrival; upgraded, it discounts every other cyan card."""

    pay = _deploy_cost

    @on(Event.DEPLOYED)
    def payday(card, ctx):
        ctx.gain(Resource.COIN, ctx.settings("coin_gain"))
