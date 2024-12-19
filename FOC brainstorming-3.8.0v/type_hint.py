from typing import TypedDict


class JobDictionary(TypedDict):
    colors_dict: dict[str, str]
    RGB_colors: dict[str, str]
    attack_type_tags: dict[str, str]
    
class AutoUpdateSetting(TypedDict):
    no_zip_files: dict[str, list[str]]
    zip_file_save_to: dict[str, str]

class CardSetting(TypedDict):
    White: dict[str, dict[str, int]]
    Red: dict[str, dict[str, int]]
    Green: dict[str, dict[str, int]]
    Blue: dict[str, dict[str, int]]
    Orange: dict[str, dict[str, int]]
    DarkGreen: dict[str, dict[str, int]]
    Cyan: dict[str, dict[str, int]]
    Fuchsia: dict[str, dict[str, int]]
    Purple: dict[str, dict[str, int]]