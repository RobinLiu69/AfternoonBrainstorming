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

from __future__ import annotations
import json
import os

from shared.setting import FOLDER_PATH


_DEFAULTS: dict = {
    "ai_delay_ms": {
        "turn_start": 900,
        "action": 650,
        "attack": 500,
        "busy_recheck": 120,
    },
    "thresholds": {
        "placement_min_score": 1.0,
        "attack_min_score": 15.0,
        "lethal_score_threshold": 100.0,
    },
    "scoring": {
        "kill_bonus_base": 100.0,
        "kill_bonus_per_threat": 10.0,
        "score_income_multiplier": 8.0,
        "hand_threat_value": {"ASS": 20.0},
    },
    "threat_model": {
        "ass_threat_damage": 5,
        "incoming_kill_penalty": 30.0,
        "incoming_chip_penalty_per_damage": 1.5,
    },
    "faction_overrides": {},
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_campaign_settings() -> dict:
    path = os.path.join(FOLDER_PATH, "config", "campaign_setting.json")
    if not os.path.isfile(path):
        return _DEFAULTS
    try:
        with open(path, "r", encoding="utf-8") as f:
            user = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _DEFAULTS
    return _deep_merge(_DEFAULTS, user)


CAMPAIGN_SETTINGS: dict = load_campaign_settings()
