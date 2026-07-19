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
import sys
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from utils.type_hint import JobDictionary, CardSetting


def _get_base_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.realpath(os.path.dirname(__file__)).replace("shared", "")



FOLDER_PATH: str = _get_base_path()

with open(f"{FOLDER_PATH}/config/setting.json", "r", encoding="utf-8") as file:
    SETTING: dict[str, Any] = json.loads(file.read())

with open(f"{FOLDER_PATH}/config/card_setting.json", "r", encoding="utf-8") as file:
    CARD_SETTING: CardSetting = json.loads(file.read())

with open(f"{FOLDER_PATH}/config/card_hints.json", "r", encoding="utf-8") as file:
    CARDS_HINTS_DICTIONARY: dict[str, str] = json.loads(file.read())

with open(f"{FOLDER_PATH}/config/job_dictionary.json", "r", encoding="utf-8") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())

JOB_ORDER = ["ADC", "AP", "TANK", "HF", "LF", "ASS", "APT", "SP"]

VERSION = "4.4.2.2"

ANIM_LUNGE_STEP: float = 0.32
COMBAT_ANIMATIONS_ENABLED = True

def _rgb(name: str) -> tuple[int, int, int]:
    r, g, b = JOB_DICTIONARY["RGB_colors"][name]
    return (r, g, b)

BLACK = _rgb("Black")
WHITE = _rgb("White")
BLUE = _rgb("Blue")
RED = _rgb("Red")
GREEN = _rgb("Green")
ORANGE = _rgb("Orange")
PURPLE = _rgb("Purple")
DARKGREEN = _rgb("DarkGreen")
CYAN = _rgb("Cyan")
FUCHSIA = _rgb("Fuchsia")
BROWN = _rgb("Brown")
