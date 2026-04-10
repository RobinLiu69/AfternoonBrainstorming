from __future__ import annotations
import os
import sys
import json
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from utils.type_hint import JobDictionary, CardSetting


def _get_base_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.realpath(os.path.dirname(__file__)).replace("core", "")



FOLDER_PATH: str = _get_base_path()

with open(f"{FOLDER_PATH}/setting/setting.json", "r", encoding="utf-8") as file:
    SETTING: dict[str, str] = json.loads(file.read())

with open(f"{FOLDER_PATH}/setting/card_setting.json", "r", encoding="utf-8") as file:
    CARD_SETTING: CardSetting = json.loads(file.read())

with open(f"{FOLDER_PATH}/setting/card_hints.json", "r", encoding="utf-8") as file:
    CARDS_HINTS_DICTIONARY: dict[str, str] = json.loads(file.read())

with open(f"{FOLDER_PATH}/setting/job_dictionary.json", "r", encoding="utf-8") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())

VERSION = "4.0.0.3"

BLACK: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Black"].split(", "))))
WHITE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["White"].split(", "))))
BLUE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Blue"].split(", "))))
RED: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Red"].split(", "))))
GREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Green"].split(", "))))
ORANGE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Orange"].split(", "))))
PURPLE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Purple"].split(", "))))
DARKGREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["DarkGreen"].split(", "))))
CYAN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Cyan"].split(", "))))
FUCHSIA: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Fuchsia"].split(", "))))
