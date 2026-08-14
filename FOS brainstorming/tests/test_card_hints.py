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

import json
import re
from pathlib import Path

from shared.setting import (CARD_SETTING, CARDS_HINTS_DICTIONARY, FOLDER_PATH,
                            hint_job_and_color)

PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.]*)\}")

# numbers that live in the hint text on purpose: they come from the rules or
# from a literal in the card code, not from card_setting.json
LITERAL_NUMBERS: dict[str, set[str]] = {
    "APTG": {"1"},        # card_green Apt: card.armor += 1
    "ASSG": {"5"},        # card_green Ass: players_luck += 5
    "APTB": {"1"},        # card_blue Apt: after_token armor += 1
    "SPG": {"10"},        # the //10 step, not min_luck_to_spawn
    "APTO": {"1", "2"},   # the 2:1 armor to attack conversion ratio
    "HFDKG": {"4", "1"},  # health <= 4 threshold, heal 1
    "LFDKG": {"4", "1"},  # the 1/4 fraction, whose divisor is a code literal
    "ADCC": {"1", "2"}, "APC": {"1", "2"}, "TANKC": {"2", "0"},
    "HFC": {"2", "1"}, "LFC": {"2"}, "ASSC": {"1"},
    "APTC": {"5", "1"}, "SPC": {"1", "3"},
}


def raw_hints() -> dict[str, str]:
    path = Path(FOLDER_PATH) / "config" / "card_hints.json"
    return json.loads(path.read_text(encoding="utf-8"))


def flatten(settings: dict, prefix: str = "") -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in settings.items():
        if isinstance(value, dict):
            out.update(flatten(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


def test_every_placeholder_resolves() -> None:
    unresolved = {code: text for code, text in CARDS_HINTS_DICTIONARY.items()
                  if PLACEHOLDER.search(text)}

    assert unresolved == {}


def test_placeholders_name_a_real_setting() -> None:
    bad: list[str] = []
    for code, text in raw_hints().items():
        job, color_name = hint_job_and_color(code)
        color_table = CARD_SETTING.get(color_name, {}) if color_name else {}
        known = set(flatten(color_table.get(job, {}))) | set(flatten(color_table))
        for path in PLACEHOLDER.findall(text):
            if path not in known:
                bad.append(f"{code}: {{{path}}}")

    assert bad == []


def test_a_tuned_number_never_stays_hardcoded() -> None:
    """A hint that spells out a value from card_setting.json silently goes stale
    the moment that value is retuned, so it has to be a placeholder instead."""
    stale: list[str] = []
    for code, text in raw_hints().items():
        job, color_name = hint_job_and_color(code)
        settings = CARD_SETTING.get(color_name, {}).get(job, {}) if color_name else {}
        if not settings:
            continue
        allowed = LITERAL_NUMBERS.get(code, set())
        tunables = {key: value for key, value in flatten(settings).items()
                    if key not in ("health", "damage", "upgrade_health", "upgrade_damage", "cost")}
        for number in set(re.findall(r"\d+", PLACEHOLDER.sub("", text))):
            if number in allowed:
                continue
            for key, value in tunables.items():
                if str(value) == number:
                    stale.append(f"{code}: {number} looks like {key}")

    assert stale == []


def test_the_code_to_settings_mapping_handles_every_shape() -> None:
    assert hint_job_and_color("APTGY") == ("APT", "Gray")
    assert hint_job_and_color("ADCDKG") == ("ADC", "DarkGreen")
    assert hint_job_and_color("TANKC (+)") == ("TANK", "Cyan")
    assert hint_job_and_color("ADCBR") == ("ADC", "Brown")
    assert hint_job_and_color("LUCKYBLOCK") == ("LUCKYBLOCK", "")


def test_a_cross_job_placeholder_reaches_its_sibling() -> None:
    assert str(CARD_SETTING["Gray"]["WIGHT"]["health"]) in CARDS_HINTS_DICTIONARY["BARROWGY"]
    assert "{" not in CARDS_HINTS_DICTIONARY["BARROWGY"]
