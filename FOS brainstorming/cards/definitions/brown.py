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

"""Brown — giants: oversized bodies paid for with a drawback.

Every downside is tagged ``DRAWBACK``, and SP suppresses that tag on friendly
giants while it rages. That is the whole mechanism.

The old implementation could not express this with ``nullify`` — which is all
or nothing — so it grew a parallel one: an ``effects_disabled`` flag pushed
onto every brown card whenever SP's state changed, re-pushed on deploy, on
silence and on death, and checked by hand at the top of each ability. It was
also a class attribute that never reached ``to_dict``, so it did not survive a
network sync or a replay. As an aura, none of that machinery is needed: it
applies to cards that arrive later, and it lapses on its own when SP stops
raging, is silenced, or dies.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import Suppression, aura, on
from cards.events import Event
from cards.stats import ATTACK_COST, Modifier, Op
from cards.statuses import RAGING

brown = color("Brown", "BR")

DRAWBACK = "drawback"
DRAWBACKS = (DRAWBACK,)


def _is_giant(card) -> bool:
    return card.color_name == "Brown"


@brown("ADC")
class Adc:
    """Hits hard, then has to catch its breath."""

    @on(Event.ATTACKED, tags=DRAWBACKS)
    def exhausted(card, ctx):
        ctx.numb(card)


@brown("AP")
class Ap:
    """Numbs its target, but hands the opponent a card."""

    @on(Event.ON_HIT)
    def numb_target(card, ctx):
        ctx.numb(ctx.target)

    @on(Event.ON_HIT, tags=DRAWBACKS)
    def feed_opponent(card, ctx):
        ctx.draw(
            ctx.settings("on_attack_enemy_draw"),
            seat=ctx.gs.get_opponent_name(card.owner),
        )


@brown("TANK")
class Tank:
    """Absorbs a hit and stuns its nearest ally doing it."""

    @on(Event.AFTER_DAMAGE_TAKEN, tags=DRAWBACKS)
    def stun_ally(card, ctx):
        for ally in ctx.nearest_ally():
            ctx.numb(ally)


@brown("HF")
class Hf:
    """Costs two attack charges instead of one."""

    @aura(tags=DRAWBACKS)
    def heavy(card, game_state):
        yield Modifier.aura(
            ATTACK_COST, card.definition.settings.get("attack_uses", 2),
            card=card, op=Op.SET,
        )


@brown("LF")
class Lf:
    """Kills well, but every kill scores for the opponent."""

    @on(Event.ON_KILL, tags=DRAWBACKS)
    def gift_points(card, ctx):
        ctx.add_score(
            ctx.settings("on_kill_enemy_points"),
            seat=ctx.gs.get_opponent_name(card.owner),
        )


@brown("ASS")
class Ass:
    """Kills cost it next turn's draw."""

    @on(Event.ON_KILL, tags=DRAWBACKS)
    def skip_draw(card, ctx):
        ctx.skip_next_draw()


@brown("APT")
class Apt:
    """Buffs an ally on hit, but keeps shielding the enemy team."""

    @on(Event.DEPLOYED, tags=DRAWBACKS)
    def shield_enemies_on_arrival(card, ctx):
        for enemy in ctx.enemies(include_neutral=False):
            ctx.add_armor(enemy, ctx.settings("on_play_enemy_shield"))

    @on(Event.TURN_START, tags=DRAWBACKS)
    def shield_enemies_each_turn(card, ctx):
        for enemy in ctx.enemies(include_neutral=False):
            ctx.add_armor(enemy, ctx.settings("on_refresh_enemy_shield"))

    @on(Event.ON_HIT)
    def rally_ally(card, ctx):
        base = ctx.settings("on_attack_buff_nearest_ally")
        bonus = ctx.settings("bonus_if_giant")
        for ally in ctx.nearest_ally():
            damage, armor = base["atk"], base["armor"]
            if _is_giant(ally):
                damage += bonus["atk"]
                armor += bonus["armor"]
            ctx.buff(ally, damage=damage, armor=armor)


@brown("SP")
class Sp:
    """Rages on its first hit; while raging, friendly giants shed their drawbacks."""

    @on(Event.ON_HIT)
    def rage(card, ctx):
        ctx.set_status(card, RAGING)

    @aura(suppresses=True)
    def free_the_giants(card, game_state):
        if RAGING not in card.statuses or card.health <= 0:
            return
        for ally in game_state.get_player_cards(card.owner):
            if ally is not card and _is_giant(ally):
                yield Suppression(
                    target_iid=ally.instance_id,
                    tags=frozenset(DRAWBACKS),
                    source_iid=card.instance_id,
                )
