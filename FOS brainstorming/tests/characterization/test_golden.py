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

"""Behaviour goldens for the card/ability system.

To re-record after an *intentional* behaviour change:

    RECORD_GOLDENS=1 python -m pytest tests/characterization -q

Then read the git diff on tests/characterization/goldens/ and confirm every
change is one you meant to make.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.characterization.harness import deck_for_color, play_game


GOLDEN_DIR = Path(__file__).parent / "goldens"
RECORDING = os.environ.get("RECORD_GOLDENS") == "1"

# Every colour plays a mirror match against itself so colour-internal synergies
# (SPR stacking, token sharing, totem doubling, shadow pairing) all fire.
COLORS = [
    "White", "Red", "Green", "Blue", "Orange",
    "DarkGreen", "Cyan", "Fuchsia", "Brown", "Purple",
]

# Cross-colour pairings that specifically stress the interactions that have
# historically been buggy: silence, drawback suppression, damage interception.
MATCHUPS = [
    ("Purple", "Red"),      # silence vs stat stacking
    ("Purple", "Brown"),    # silence vs drawback suppression
    ("Brown", "White"),     # giants vs baseline
    ("Fuchsia", "Red"),     # shadow damage interception vs buffs
    ("Green", "Cyan"),      # luck randomness vs upgrades
    ("DarkGreen", "Blue"),  # totem scaling vs token draw chains
]


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, snapshots: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshots, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")


def _first_difference(expected: list[dict], actual: list[dict]) -> str:
    for i, (want, got) in enumerate(zip(expected, actual)):
        if want != got:
            want_s = json.dumps(want, indent=1, sort_keys=True, ensure_ascii=False).splitlines()
            got_s = json.dumps(got, indent=1, sort_keys=True, ensure_ascii=False).splitlines()
            for line_no, (a, b) in enumerate(zip(want_s, got_s)):
                if a != b:
                    start = max(0, line_no - 6)
                    context = "\n".join(
                        f"  {want_s[j]!s:<60} | {got_s[j] if j < len(got_s) else ''!s}"
                        for j in range(start, line_no + 1)
                    )
                    return (
                        f"snapshot #{i} ({want.get('_label')}) diverged at line {line_no}\n"
                        f"  {'EXPECTED':<60} | ACTUAL\n{context}"
                    )
            return f"snapshot #{i} ({want.get('_label')}) differs in length"
    if len(expected) != len(actual):
        return f"snapshot count differs: expected {len(expected)}, got {len(actual)}"
    return "no difference found"


def _check(name: str, snapshots: list[dict]) -> None:
    path = GOLDEN_DIR / f"{name}.json"
    if RECORDING or not path.exists():
        _dump(path, snapshots)
        if not RECORDING:
            pytest.skip(f"recorded new golden: {path.name}")
        return
    expected = _load(path)
    if expected != snapshots:
        pytest.fail(
            f"behaviour changed for {name}\n{_first_difference(expected, snapshots)}\n\n"
            f"If this change is intentional, re-record with RECORD_GOLDENS=1."
        )


@pytest.mark.parametrize("color", COLORS)
def test_mirror_match_golden(color: str) -> None:
    deck = deck_for_color(color)
    snapshots = play_game(seed=1337, deck1=deck, deck2=deck, turns=16)
    _check(f"mirror_{color.lower()}", snapshots)


@pytest.mark.parametrize("left,right", MATCHUPS, ids=lambda v: v.lower() if isinstance(v, str) else v)
def test_matchup_golden(left: str, right: str) -> None:
    snapshots = play_game(
        seed=2024,
        deck1=deck_for_color(left),
        deck2=deck_for_color(right),
        turns=16,
    )
    _check(f"vs_{left.lower()}_{right.lower()}", snapshots)


def test_harness_is_deterministic() -> None:
    """The goldens are worthless if the driver itself is not reproducible."""
    deck = deck_for_color("Red")
    first = play_game(seed=99, deck1=deck, deck2=deck, turns=8)
    second = play_game(seed=99, deck1=deck, deck2=deck, turns=8)
    assert first == second
