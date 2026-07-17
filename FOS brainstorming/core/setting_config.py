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
from typing import Literal, overload
import os
import json

from shared.setting import FOLDER_PATH

SETTING_PATH = os.path.join(FOLDER_PATH, "data/user_setting.json")

SETTING_NAMES = Literal["display_mode", "hint_on", "last_join_ip"]

VALID_SETTING: dict[str, tuple[str | bool, ...] | None] = {
    "display_mode" : ("60", "80", "100", "fullscreen"),
    "hint_on" : (False, True),
    "last_join_ip" : None,
}

DEFAULT_SETTING: dict[str, str | bool] = {
    "display_mode" : "100",
    "hint_on" : False,
    "last_join_ip" : "",
}

@overload
def load_setting(request: Literal["hint_on"]) -> bool: ...
@overload
def load_setting(request: Literal["display_mode", "last_join_ip"]) -> str: ...
def load_setting(request: SETTING_NAMES) -> str | bool:
    if request not in VALID_SETTING:
        raise ValueError(f"unknown setting: {request!r}")
    try:
        with open(SETTING_PATH, "r", encoding="utf-8") as file:
            response = json.loads(file.read()).get(request, DEFAULT_SETTING[request])
    except (OSError, ValueError):
        return DEFAULT_SETTING[request]
    allowed = VALID_SETTING[request]
    if allowed is None:
        return response if isinstance(response, str) else DEFAULT_SETTING[request]
    return response if response in allowed else DEFAULT_SETTING[request]


def save_setting(setting_name: SETTING_NAMES, setting_data: str | bool) -> None:
    if setting_name not in VALID_SETTING:
        raise ValueError(f"unknown setting: {setting_name!r}")
    try:
        with open(SETTING_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        data = {}

    data[setting_name] = setting_data

    try:
        os.makedirs(os.path.dirname(SETTING_PATH), exist_ok=True)
        with open(SETTING_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError:
        pass
