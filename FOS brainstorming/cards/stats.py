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

"""Derived statistics.

A card never stores its current attack power. It stores a *base* value (from
config/card_setting.json) plus a list of :class:`Modifier` objects, and the
current value is folded on demand. This is what makes "remove all buffs",
"remove buffs from this source" and "the buff disappears when its source dies"
expressible at all — none of which were possible when abilities did
``self.damage += 1``.

Two layers exist, and they map onto the two numbers the UI already shows:

``COUNTER``
    Permanent, serialised, earned by resolving an ability (Red's +1 attack).
    Folds into ``card.damage``.
``AURA``
    Recomputed from the board on every read, contributed by a static effect of
    some card that is currently in play (DarkGreen's totem scaling). Folds into
    ``card.extra_damage`` and vanishes on its own when the source leaves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable


# Statistic names. Plain strings rather than an enum so they serialise as-is and
# read naturally at the call site: ctx.grant(card, DAMAGE, +1).
DAMAGE = "damage"
MAX_HEALTH = "max_health"
SCORE = "score"
ATTACK_COST = "attack_cost"

ALL_STATS: tuple[str, ...] = (DAMAGE, MAX_HEALTH, SCORE, ATTACK_COST)


class Layer(IntEnum):
    """Where a modifier's contribution lands."""

    COUNTER = 10
    AURA = 20


class Op(IntEnum):
    """Fold order is SET, then ADD, then MUL — same shape as MtG layer 7."""

    SET = 0
    ADD = 1
    MUL = 2


@dataclass(frozen=True)
class Modifier:
    """One contribution to one statistic.

    ``tags`` is what makes selective removal possible: Purple's silence strips
    modifiers tagged ``buff`` rather than blanket-resetting a card to its
    printed stats (which also destroyed friendly buffs and could not remove a
    debuff at all).
    """

    stat: str
    op: Op
    value: float
    layer: Layer = Layer.COUNTER
    tags: frozenset[str] = frozenset()
    source_iid: str = ""
    seq: int = 0

    @classmethod
    def aura(
        cls,
        stat: str,
        value: float,
        *,
        card=None,
        op: Op = Op.ADD,
        tags: Iterable[str] = (),
    ) -> "Modifier":
        """A modifier contributed by a static effect.

        Never stored or serialised: it is recomputed from the board on every
        read, so it disappears by itself when its source dies or is silenced.
        """
        return cls(
            stat=stat, op=op, value=value, layer=Layer.AURA,
            tags=frozenset(tags),
            source_iid=getattr(card, "instance_id", ""),
        )

    def to_dict(self) -> dict:
        return {
            "stat": self.stat,
            "op": int(self.op),
            "value": self.value,
            "layer": int(self.layer),
            "tags": sorted(self.tags),
            "source_iid": self.source_iid,
            "seq": self.seq,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Modifier":
        return cls(
            stat=data["stat"],
            op=Op(data["op"]),
            value=data["value"],
            layer=Layer(data["layer"]),
            tags=frozenset(data.get("tags", ())),
            source_iid=data.get("source_iid", ""),
            seq=data.get("seq", 0),
        )


def fold(base: int, modifiers: Iterable[Modifier], stat: str) -> int:
    """Apply every modifier for ``stat`` to ``base`` and return the result.

    MUL is applied one factor at a time with truncation, which reproduces the
    old destructive ``damage //= 2`` / ``damage *= 2`` behaviour exactly rather
    than accumulating a single float factor.
    """
    relevant = [m for m in modifiers if m.stat == stat]
    if not relevant:
        return base

    value = float(base)

    sets = [m for m in relevant if m.op is Op.SET]
    if sets:
        value = float(max(sets, key=lambda m: m.seq).value)

    value += sum(m.value for m in relevant if m.op is Op.ADD)

    for mul in sorted((m for m in relevant if m.op is Op.MUL), key=lambda m: m.seq):
        value = float(int(value * mul.value))

    return int(value)


@dataclass
class ModifierBox:
    """The permanent modifiers a card is carrying."""

    items: list[Modifier] = field(default_factory=list)

    def add(self, modifier: Modifier) -> None:
        self.items.append(modifier)

    def remove_where(self, *, tags: Iterable[str] = (), source_iid: str | None = None) -> list[Modifier]:
        """Drop matching modifiers and return them. Empty filters match nothing."""
        wanted = frozenset(tags)
        if not wanted and source_iid is None:
            return []

        def matches(modifier: Modifier) -> bool:
            if wanted and not (modifier.tags & wanted):
                return False
            if source_iid is not None and modifier.source_iid != source_iid:
                return False
            return True

        dropped = [m for m in self.items if matches(m)]
        self.items = [m for m in self.items if not matches(m)]
        return dropped

    def clear(self) -> None:
        self.items.clear()

    def to_list(self) -> list[dict]:
        return [m.to_dict() for m in self.items]

    @classmethod
    def from_list(cls, data: list[dict]) -> "ModifierBox":
        return cls(items=[Modifier.from_dict(d) for d in data])
