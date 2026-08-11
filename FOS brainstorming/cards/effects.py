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

"""Abilities as data.

An ability used to be an override of a base-class method, which meant the set
of a card's behaviours could not be inspected, filtered or switched off at
runtime — the reason ``nullify`` needed a guard clause at every call site and
Brown needed a second, incompatible mechanism for suppressing only its
drawbacks.

Here an ability is an :class:`Effect` object carrying its timing, ordering and
``tags``, so "run every effect except the ones tagged ``drawback``" is a filter
rather than a special case.

Three kinds, borrowed from Magic's taxonomy:

``TRIGGERED``
    Reacts to an event and issues commands. Most abilities.
``REPLACEMENT``
    Intercepts an event *before* it applies and may rewrite or cancel it.
    Damage prevention and damage redirection live here.
``STATIC``
    Contributes modifiers and suppressions continuously while its card is in
    play. Never mutates anything; it is re-evaluated on demand and stops
    applying by itself when its source leaves the board.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Any, Callable, Iterable


class EffectKind(IntEnum):
    STATIC = 0
    REPLACEMENT = 1
    TRIGGERED = 2


class Priority(IntEnum):
    """Ordering within one event.

    Ties break on board position, then declaration order, so resolution is
    total and reproducible.

    The damage windows use these to reproduce the fixed sequence the old
    ``damage_calculate`` hard-coded:

    ``EARLIEST``
        Cancellation (the old ``damage_block``).
    ``EARLY``
        The victim's own resistances (the old ``damage_reduce``).
    ``NORMAL``
        Board-wide interception (the old ``on_field_effect_trigger``).

    Getting this wrong is silent and numeric: halving before a flat reduction
    is not the same as after.
    """

    EARLIEST = 0
    EARLY = 10
    NORMAL = 20
    LATE = 30
    LATEST = 40


@dataclass(frozen=True)
class Suppression:
    """Switches other effects off.

    ``tags`` empty means "every effect on the target". Purple's silence emits
    one of these via a card status; Brown's SP emits one via an aura, so the
    drawbacks come back on their own the moment it stops raging or is silenced.
    """

    target_iid: str
    tags: frozenset[str] = frozenset()
    source_iid: str = ""

    def covers(self, effect: "Effect") -> bool:
        return not self.tags or bool(self.tags & effect.tags)


@dataclass(frozen=True)
class Effect:
    kind: EffectKind
    fn: Callable[..., Any]
    event: str | None = None
    priority: Priority = Priority.NORMAL
    tags: frozenset[str] = frozenset()
    condition: Callable[..., bool] | None = None
    name: str = ""
    order: int = 0
    """Declaration index within the owning card definition."""

    suppressing: bool = False
    """Static effects only: this aura can emit Suppression objects.

    Declared up front so the engine can find every possible suppressor without
    evaluating every aura in the game on each lookup.
    """

    def applies(self, *args) -> bool:
        return self.condition is None or bool(self.condition(*args))


def _attach(fn: Callable, effect: Effect) -> Callable:
    existing: list[Effect] = list(getattr(fn, "__effects__", ()))
    existing.append(effect)
    fn.__effects__ = existing  # type: ignore[attr-defined]
    return fn


def on(
    event: str,
    *,
    priority: Priority = Priority.NORMAL,
    tags: Iterable[str] = (),
    when: Callable[..., bool] | None = None,
) -> Callable[[Callable], Callable]:
    """Declare a triggered ability. Handler signature is ``(card, ctx)``."""

    def decorate(fn: Callable) -> Callable:
        return _attach(fn, Effect(
            kind=EffectKind.TRIGGERED,
            fn=fn,
            event=event,
            priority=priority,
            tags=frozenset(tags),
            condition=when,
            name=fn.__name__,
        ))

    return decorate


def replaces(
    event: str,
    *,
    priority: Priority = Priority.NORMAL,
    tags: Iterable[str] = (),
    when: Callable[..., bool] | None = None,
) -> Callable[[Callable], Callable]:
    """Declare a replacement effect. Handler signature is ``(card, event)``.

    The handler mutates the event in place — reducing ``event.amount``,
    setting ``event.cancelled``, or diverting damage elsewhere.
    """

    def decorate(fn: Callable) -> Callable:
        return _attach(fn, Effect(
            kind=EffectKind.REPLACEMENT,
            fn=fn,
            event=event,
            priority=priority,
            tags=frozenset(tags),
            condition=when,
            name=fn.__name__,
        ))

    return decorate


def aura(
    *,
    priority: Priority = Priority.NORMAL,
    tags: Iterable[str] = (),
    suppresses: bool = False,
) -> Callable[[Callable], Callable]:
    """Declare a static effect. Handler signature is ``(card, game_state)`` and
    it yields :class:`~cards.stats.Modifier` (applying to its own card) and
    :class:`Suppression` objects (targeting any card).

    Must be free of side effects: it is called every time a derived stat is
    read. Pass ``suppresses=True`` if it can emit Suppression.
    """

    def decorate(fn: Callable) -> Callable:
        return _attach(fn, Effect(
            kind=EffectKind.STATIC,
            fn=fn,
            event=None,
            priority=priority,
            tags=frozenset(tags),
            name=fn.__name__,
            suppressing=suppresses,
        ))

    return decorate


def collect_effects(namespace: dict) -> list[Effect]:
    """Pull every decorated handler out of a card definition's class body,
    preserving declaration order so ties resolve deterministically."""
    found: list[Effect] = []
    for value in namespace.values():
        for effect in getattr(value, "__effects__", ()):
            found.append(effect)
    return [replace(effect, order=index) for index, effect in enumerate(found)]
