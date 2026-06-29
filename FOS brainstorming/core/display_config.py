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
import os
import json

from shared.setting import FOLDER_PATH

DISPLAY_SETTING_PATH = os.path.join(FOLDER_PATH, "display_setting.json")
VALID_MODES: tuple[str, ...] = ("60", "80", "100", "fullscreen")
DEFAULT_MODE = "100"


def load_display_mode() -> str:
    try:
        with open(DISPLAY_SETTING_PATH, "r", encoding="utf-8") as file:
            mode = json.loads(file.read()).get("display_mode", DEFAULT_MODE)
    except (OSError, ValueError):
        return DEFAULT_MODE
    return mode if mode in VALID_MODES else DEFAULT_MODE


def save_display_mode(mode: str) -> None:
    if mode not in VALID_MODES:
        mode = DEFAULT_MODE
    try:
        with open(DISPLAY_SETTING_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps({"display_mode": mode}, indent=4))
    except OSError:
        pass
