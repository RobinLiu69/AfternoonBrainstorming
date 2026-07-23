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

from dataclasses import dataclass, fields, replace
from typing import TYPE_CHECKING

from shared.setting import SETTING

if TYPE_CHECKING:
    from core.game_state import GameState


RULESET_OPTIONS: tuple[str, ...] = ("free play", "tournament")


def _load_time_control_options() -> dict[str, tuple[int, int]]:
    options: dict[str, tuple[int, int]] = {}
    for label, value in SETTING.get("time_control_options", {}).items():
        try:
            options[str(label)] = (int(value[0]), int(value[1]))
        except (TypeError, ValueError, IndexError):
            print(f"[match_settings] ignoring bad time control option {label!r}: {value!r}")
    if not options:
        options = {"10min": (600, 0)}
    return options


TIME_CONTROL_OPTIONS: dict[str, tuple[int, int]] = _load_time_control_options()
DEFAULT_TIME_CONTROL: str = str(SETTING.get("default_time_control", ""))
if DEFAULT_TIME_CONTROL not in TIME_CONTROL_OPTIONS:
    DEFAULT_TIME_CONTROL = next(iter(TIME_CONTROL_OPTIONS))


@dataclass
class MatchSettings:
    timer_mode: str = "timer"
    time_control: str = DEFAULT_TIME_CONTROL
    ruleset: str = "free play"
    file_auto_delete: bool = False

    def countdown_seconds(self) -> int:
        return TIME_CONTROL_OPTIONS.get(self.time_control, TIME_CONTROL_OPTIONS[DEFAULT_TIME_CONTROL])[0]

    def increment_seconds(self) -> int:
        return TIME_CONTROL_OPTIONS.get(self.time_control, TIME_CONTROL_OPTIONS[DEFAULT_TIME_CONTROL])[1]

    def time_label(self) -> str:
        return "unlimited" if self.timer_mode == "timer" else self.time_control

    def copy(self) -> "MatchSettings":
        return replace(self)

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def apply_dict(self, data: dict) -> None:
        for f in fields(self):
            if f.name in data:
                setattr(self, f.name, data[f.name])

    def apply_to(self, game_state: "GameState") -> None:
        game_state.timer_mode = self.timer_mode
        game_state.file_auto_delete = self.file_auto_delete
        game_state.countdown_time = self.countdown_seconds()
        game_state.turn_increment_seconds = self.increment_seconds()
        settings = self.to_dict()
        game_state.game_logger.info(
            "settings " + " ".join(f"{name}={value}" for name, value in settings.items()),
            **settings)
        game_state.game_logger.info(f"timer mode {self.timer_mode}")
        game_state.game_logger.info(
            f"time control {self.time_label()}",
            countdown_seconds=game_state.countdown_time,
            increment_seconds=game_state.turn_increment_seconds)


MATCH_SETTING_NAMES: frozenset[str] = frozenset(f.name for f in fields(MatchSettings))
