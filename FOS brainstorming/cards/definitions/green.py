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

"""Green — luck.

A luck roll against the target's own luck score decides between a boon and a
jinx table. Three cards roll with restrictions, which the flags on
:func:`roll_luck` name explicitly.
"""

from __future__ import annotations

from cards.defs import color, neutral
from cards.effects import on, replaces
from cards.events import Event, Resource
from cards.stats import DAMAGE, Op
from shared.combat_event import CombatEvent

green = color("Green", "G")

LUCKY_BLOCK = "LUCKYBLOCK"
_DIAGONALS = ((1, 1), (1, -1), (-1, 1), (-1, -1))


def _hurt_event(ctx, card) -> None:
    ctx.gs.pending_combat_events.append(CombatEvent(
        kind="hurt", board_x=card.board_x, board_y=card.board_y, post_health=card.health,
    ))


def roll_luck(ctx, target, *, ap: bool = False, ap_target: bool = False, tank: bool = False) -> None:
    """Roll the boon/jinx tables against the target's luck.

    ``ap_target`` forces the jinx table (Green AP always jinxes its victim),
    ``tank`` takes the jinx table but declines any boon, and ``ap`` takes boons
    but neither loses luck nor spawns blocks.
    """
    lucky = not ap_target and ctx.rng.randint(1, 100) <= ctx.gs.players_luck[target.owner]

    if lucky:
        if tank:
            return
        ctx.gain(Resource.LUCK, 1, seat=target.owner)
        ctx.log(f"{target.get_uid()}{target.get_position()} got lucky:",
                target=target.get_uid(), target_position=target.get_position())

        match ctx.rng.randint(1, 5):
            case 1:
                ctx.add_armor(target, 4)
            case 2:
                ctx.grant(target, DAMAGE, 2, op=Op.MUL, tags=("buff",))
            case 3:
                ctx.attack_with(target)
            case 4:
                ctx.arm_move(target)
            case 5:
                if ap:
                    return
                for dx, dy in _DIAGONALS:
                    ctx.spawn(LUCKY_BLOCK, target.board_x + dx, target.board_y + dy)
        return

    if ap:
        return

    ctx.gain(Resource.LUCK, -1, seat=target.owner)
    ctx.log(f"{target.get_uid()}{target.get_position()} got jinx:",
            target=target.get_uid(), target_position=target.get_position())

    match ctx.rng.randint(1, 5):
        case 1:
            target.armor = 0
        case 2:
            ctx.numb(target)
        case 3:
            target.health //= 2
            _hurt_event(ctx, target)
        case 4:
            ctx.grant(target, DAMAGE, 0.5, op=Op.MUL, tags=("debuff",))
        case 5:
            if target.health >= 2:
                target.health -= 2
                _hurt_event(ctx, target)


@neutral(LUCKY_BLOCK, job=LUCKY_BLOCK, color_name="Green", pattern="")
class LuckyBlock:
    """Breaking one rolls the luck tables on whoever broke it."""

    @on(Event.ON_KILLED)
    def burst(card, ctx):
        roll_luck(ctx, ctx.killer)
        for ally in ctx.gs.get_player_cards(ctx.killer.owner):
            if ally.job_and_color == "APTG":
                ctx.add_armor(ally, 1)


@green("ADC")
class Adc:
    """Seeds its own row and column with blocks."""

    @on(Event.ON_HIT)
    def seed(card, ctx):
        chance = ctx.settings("luckyblock_spawn_chance")
        for x, y in list(ctx.gs.board_dict):
            if (x == card.board_x or y == card.board_y) and not ctx.gs.board_dict[x, y].occupy:
                if ctx.rng.randint(1, 100) <= chance:
                    ctx.spawn(LUCKY_BLOCK, x, y)


@green("AP")
class Ap:
    """Jinxes its victim, and chances a boon for itself."""

    @on(Event.ON_HIT)
    def hex(card, ctx):
        ctx.numb(ctx.target)
        roll_luck(ctx, ctx.target, ap_target=True)
        roll_luck(ctx, card, ap=True)


@green("TANK")
class Tank:
    """Whoever strikes it risks a jinx."""

    @on(Event.AFTER_DAMAGE_TAKEN)
    def curse_attacker(card, ctx):
        roll_luck(ctx, ctx.other, tank=True)


@green("HF")
class Hf:
    """Breaking blocks makes its owner luckier and reseeds the board."""

    @on(Event.ON_HIT, when=lambda card, ctx: ctx.target.job_and_color == LUCKY_BLOCK)
    def harvest(card, ctx):
        ctx.gain(Resource.LUCK, ctx.settings("luck_increase"))
        free = ctx.free_cells()
        if free:
            x, y = free[ctx.rng.randrange(len(free))]
            ctx.spawn(LUCKY_BLOCK, x, y)


@green("LF")
class Lf:
    """Converts a broken block into a strike, and sometimes a refund."""

    @on(Event.ON_KILL, when=lambda card, ctx: ctx.victim.job_and_color == LUCKY_BLOCK)
    def detonate(card, ctx):
        others = ctx.enemies(include_neutral=False)
        ctx.strike(ctx.targets("nearest", others), card.damage, allow_abilities=False)
        if ctx.rng.randint(1, 100) <= ctx.settings("attack_gain_chance"):
            ctx.gain(Resource.ATTACKS, ctx.settings("attack_gain_per_luckyblock_kill"))


@green("ASS")
class Ass:
    """Steals luck on every kill."""

    @on(Event.ON_KILL)
    def steal_luck(card, ctx):
        ctx.gain(Resource.LUCK, 5)
        ctx.gain(
            Resource.LUCK, -ctx.settings("enemy_luck_loss"),
            seat=ctx.gs.get_opponent_name(card.owner),
        )


@green("APT")
class Apt:
    """Never attacks; buries the squares around it in blocks instead."""

    @replaces(Event.ATTACK_DECLARED)
    def cannot_attack(card, event):
        event.cancel()

    @on(Event.TURN_START)
    def bury(card, ctx):
        for x, y in list(ctx.gs.board_dict):
            adjacent = (abs(x - card.board_x), abs(y - card.board_y)) in ((0, 1), (1, 0))
            if adjacent and not ctx.gs.board_dict[x, y].occupy:
                ctx.spawn(LUCKY_BLOCK, x, y)


@green("SP")
class Sp:
    """Arrives with a burst of luck and scatters blocks in proportion."""

    @on(Event.DEPLOYED)
    def scatter(card, ctx):
        ctx.gain(Resource.LUCK, ctx.settings("luck_increase"))
        free = [pos for pos in ctx.free_cells() if pos != card.get_position()]
        if not free:
            return
        ctx.rng.shuffle(free)
        floor = ctx.settings("min_luck_to_spawn")
        luck = ctx.gs.players_luck[card.owner]
        if luck <= floor:
            return
        for x, y in free[:min((luck - floor) // 10, len(free))]:
            ctx.spawn(LUCKY_BLOCK, x, y)
