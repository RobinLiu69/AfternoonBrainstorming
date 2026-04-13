# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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