# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright 2024-2026 Robin Liu / FOC Studio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------

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