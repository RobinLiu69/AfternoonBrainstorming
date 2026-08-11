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

"""Named per-card states.

The old system had a single ``anger`` boolean that meant seven different things
depending on which card owned it — "will survive lethal damage" on Red HF,
"next hit is free" on upgraded Cyan TANK, "moved this turn" on Orange ASS, and
so on. Each status now has its own name, and ``highlight`` records which ones
the renderer should draw with the anger marker so the UI is unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StatusDef:
    name: str
    highlight: bool = False
    """Drawn as the ``anger`` marker by CardRenderData."""

    clears_on_turn_end: bool = False


_REGISTRY: dict[str, StatusDef] = {}


def status(name: str, *, highlight: bool = False, clears_on_turn_end: bool = False) -> str:
    definition = StatusDef(name=name, highlight=highlight, clears_on_turn_end=clears_on_turn_end)
    _REGISTRY[name] = definition
    return name


def is_highlight(name: str) -> bool:
    definition = _REGISTRY.get(name)
    return bool(definition and definition.highlight)


def clears_on_turn_end(name: str) -> bool:
    definition = _REGISTRY.get(name)
    return bool(definition and definition.clears_on_turn_end)


# --- engine-level -------------------------------------------------------
NULLIFIED = status("nullified")
"""All of this card's effects are suppressed (Purple AP). See engine.suppression."""

# --- Red ----------------------------------------------------------------
LAST_STAND = status("last_stand", highlight=True, clears_on_turn_end=True)
"""Red HF: reached 0 health but does not die until the turn settles."""

# --- Orange -------------------------------------------------------------
RAMPAGE = status("rampage", highlight=True, clears_on_turn_end=True)
"""Orange HF/ASS: moved this turn, which arms a follow-up bonus."""

# --- Cyan ---------------------------------------------------------------
WARDED = status("warded", highlight=True)
"""Upgraded Cyan TANK: the next incoming hit is ignored entirely."""

FIRST_STRIKE = status("first_strike", highlight=True)
"""Upgraded Cyan ASS: the next hit this card lands carries bonus damage."""

UNDYING = status("undying", highlight=True)
"""Upgraded Cyan HF: survives lethal damage once, at the cost of scoring."""

SPENT = status("spent")
"""Cyan HF: has already used its undying life, so it no longer scores."""

# --- Brown --------------------------------------------------------------
RAGING = status("raging", highlight=True)
"""Brown SP: while raging, friendly Brown cards lose their drawbacks."""
