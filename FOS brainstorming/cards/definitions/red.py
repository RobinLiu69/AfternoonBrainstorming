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

"""Red — permanent stat growth.

Every red buff is tagged ``RED``, which is the entire interface between the
colour's cards and its SP: SP copies anything carrying that tag. Previously SP
had no code at all and each of the other seven cards carried its own
``for card in ... if job_and_color == "SPR"`` loop, so adding a red card meant
remembering to write loop number eight.
"""

from __future__ import annotations

from cards.defs import color
from cards.effects import aura, on, replaces
from cards.events import Event
from cards.stats import DAMAGE, SCORE, Modifier, Op
from cards.statuses import LAST_STAND
from shared.combat_event import CombatEvent

red = color("Red", "R")

RED = "red"
"""Tag marking a buff that Red's SP mirrors onto itself."""

BUFF = ("buff", RED)


@red("ADC")
class Adc:
    """Gains attack every time it deals damage."""

    @on(Event.ON_HIT)
    def grow(card, ctx):
        ctx.buff(card, damage=ctx.settings("damage_increase"), tags=BUFF)


@red("AP")
class Ap:
    """Numbs its target and steals its attack outright."""

    @on(Event.ON_HIT)
    def steal_attack(card, ctx):
        ctx.numb(ctx.target)
        stolen = int(ctx.target.damage * (ctx.settings("attack_steal_rate") / 100))
        if not stolen:
            return
        # The theft is two separate acts: only the gain is a red buff, so the
        # victim's loss is never mirrored onto a friendly SP.
        ctx.grant(ctx.target, DAMAGE, -stolen, tags=("debuff",))
        ctx.buff(card, damage=stolen, tags=BUFF)


@red("TANK")
class Tank:
    """Shields its nearest ally whenever it is struck."""

    @on(Event.AFTER_DAMAGE_TAKEN)
    def shield_ally(card, ctx):
        for ally in ctx.nearest_ally():
            ctx.buff(ally, armor=ctx.settings("armor_increase"), tags=BUFF)


@red("HF")
class Hf:
    """Burns its own health for attack, and refuses to die until the turn ends."""

    @on(Event.ON_HIT)
    def burn(card, ctx):
        card.health -= ctx.settings("health_decrease")
        if card.health <= 0:
            ctx.set_status(card, LAST_STAND)
        ctx.gs.pending_combat_events.append(CombatEvent(
            kind="hurt", board_x=card.board_x, board_y=card.board_y,
            post_health=card.health,
        ))
        ctx.buff(card, damage=ctx.settings("damage_increase"), tags=BUFF)

    @replaces(Event.LETHAL)
    def survive(card, event):
        if LAST_STAND in card.statuses:
            event.prevent()

    @aura()
    def no_points_while_dying(card, game_state):
        if LAST_STAND in card.statuses:
            yield Modifier.aura(SCORE, 0, card=card, op=Op.SET)


@red("LF")
class Lf:
    """Grows in both directions on every hit."""

    @on(Event.ON_HIT)
    def grow(card, ctx):
        ctx.buff(
            card,
            damage=ctx.settings("damage_increase"),
            armor=ctx.settings("armor_increase"),
            tags=BUFF,
        )


@red("ASS")
class Ass:
    """Feeds its attack to the nearest ally on a kill."""

    @on(Event.ON_KILL)
    def feed_ally(card, ctx):
        for ally in ctx.nearest_ally():
            ctx.buff(ally, damage=ctx.settings("damage_increase"), tags=BUFF)


@red("APT")
class Apt:
    """Buffs itself and its nearest ally on every hit."""

    @on(Event.ON_HIT)
    def rally(card, ctx):
        gain = {
            "damage": ctx.settings("damage_increase"),
            "armor": ctx.settings("armor_increase"),
        }
        for ally in ctx.nearest_ally():
            ctx.buff(ally, tags=BUFF, **gain)
        ctx.buff(card, tags=BUFF, **gain)


@red("SP")
class Sp:
    """Every buff gained by a friendly red card also lands on this one."""

    @on(Event.BUFF_APPLIED, when=lambda card, ctx: (
        RED in ctx.tags
        and ctx.target is not card
        and ctx.source.owner == card.owner
    ))
    def mirror(card, ctx):
        # Re-buffed without the RED tag, so a second SP does not mirror the
        # mirror and the chain terminates.
        ctx.buff(
            card,
            damage=ctx.damage,
            armor=ctx.armor,
            max_health=ctx.max_health,
            tags=("buff",),
        )
