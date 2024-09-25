from typing import TypedDict


class JobDictionary(TypedDict):
    colors_dict: dict[str, str]
    RGB_colors: dict[str, str]
    attack_type_tags: dict[str, str]
    
class AutoUpdateSetting(TypedDict):
    no_zip_files: dict[str, list[str]]
    zip_file_save_to: dict[str, str]