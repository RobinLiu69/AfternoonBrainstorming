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

"""Card definitions: the printed card, as opposed to the one on the board.

A :class:`CardDef` is immutable, shared by every copy of that card, and holds
the base stats and the effect list. The mutable per-copy state (position,
health, modifiers, statuses) lives on :class:`~cards.base.Card`.

Splitting the two is what removes the per-card ``__init__`` boilerplate: a
definition declares only what is *different* about that card.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from cards.effects import Effect, collect_effects
from shared.setting import CARD_SETTING, CARDS_HINTS_DICTIONARY, JOB_DICTIONARY

if TYPE_CHECKING:
    from cards.runtime import Card


CARD_DEFS: dict[str, "CardDef"] = {}


@dataclass(frozen=True)
class CardDef:
    name: str
    """The job+colour code used everywhere as an identifier, e.g. "ADCR"."""

    job: str
    color_name: str
    base_health: int
    base_damage: int
    pattern: str
    effects: tuple[Effect, ...] = ()
    settings: dict[str, Any] = field(default_factory=dict)
    variants: dict[str, dict[str, int]] = field(default_factory=dict)
    """Alternate printed stats, e.g. Cyan's upgraded copies."""

    starts_numb: bool = True
    scores: bool = True
    """False for neutral props (cubes, lucky blocks) that never earn points."""

    movable: bool = True
    hint: str = ""

    def handles(self, event: str) -> bool:
        """Whether any effect listens to an event. Lets hot paths skip dispatch."""
        return event in self.event_set

    @property
    def event_set(self) -> frozenset[str]:
        cached = self.__dict__.get("_event_set")
        if cached is None:
            cached = frozenset(e.event for e in self.effects if e.event)
            object.__setattr__(self, "_event_set", cached)
        return cached

    def stats_for(self, variant: str = "") -> tuple[int, int]:
        if variant and variant in self.variants:
            override = self.variants[variant]
            return (
                override.get("health", self.base_health),
                override.get("damage", self.base_damage),
            )
        return (self.base_health, self.base_damage)

    def __call__(self, owner: str, board_x: int, board_y: int, **kwargs) -> "Card":
        """Definitions are callable so ``Adc(owner, x, y)`` still builds a card."""
        from cards.runtime import Card
        return Card(self, owner=owner, board_x=board_x, board_y=board_y, **kwargs)

    def __repr__(self) -> str:
        return f"<CardDef {self.name}>"


def _pattern_for(job: str) -> str:
    pattern = JOB_DICTIONARY["attack_type_tags"].get(job, "")
    return "" if pattern in ("", "None") else pattern


def define(
    name: str,
    *,
    job: str,
    color_name: str,
    health: int | None = None,
    damage: int | None = None,
    pattern: str | None = None,
    variants: dict[str, dict[str, int]] | None = None,
    starts_numb: bool | None = None,
    scores: bool = True,
    movable: bool = True,
) -> Callable[[type], CardDef]:
    """Decorate a class body of effect handlers into a registered CardDef.

    Base stats default to config/card_setting.json and the attack pattern to
    the job's entry in job_dictionary.json, so a card only states what is
    special about it.
    """

    def decorate(cls: type) -> CardDef:
        settings: dict[str, Any] = dict(CARD_SETTING.get(color_name, {}).get(job, {}))
        definition = CardDef(
            name=name,
            job=job,
            color_name=color_name,
            base_health=settings.get("health", 1) if health is None else health,
            base_damage=settings.get("damage", 0) if damage is None else damage,
            pattern=_pattern_for(job) if pattern is None else pattern,
            effects=tuple(collect_effects(dict(vars(cls)))),
            settings=settings,
            variants=variants or {},
            # Assassins deploy ready to act; every other job arrives numb. This
            # is a rule of the job, so it is applied once here rather than being
            # re-stated by each of the nine ASS cards.
            starts_numb=(job != "ASS") if starts_numb is None else starts_numb,
            scores=scores,
            movable=movable,
            hint=CARDS_HINTS_DICTIONARY.get(name, ""),
        )
        CARD_DEFS[name] = definition
        return definition

    return decorate


def color(color_name: str, code: str) -> Callable[..., Callable[[type], CardDef]]:
    """Bind a colour once per definition file: ``red = color("Red", "R")``.

    The card name is then derived from the job, so ``@red("ADC")`` registers
    "ADCR" with Red's stats — the naming convention is applied in one place
    instead of being retyped in every constructor.
    """

    def registrar(job: str, **kwargs) -> Callable[[type], CardDef]:
        kwargs.setdefault("job", job)
        kwargs.setdefault("color_name", color_name)
        return define(job + code, **kwargs)

    return registrar


def neutral(name: str, *, job: str | None = None, color_name: str = "White", **kwargs) -> Callable[[type], CardDef]:
    """Register a prop or magic card, which has no job+colour naming."""
    kwargs.setdefault("scores", False)
    return define(name, job=job or name, color_name=color_name, **kwargs)
