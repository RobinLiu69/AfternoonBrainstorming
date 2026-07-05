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

from endless.content import RELICS, CURSES, CONSUMABLES, valid_card_codes


SAVE_PATH: str = os.path.join(FOLDER_PATH, "data/endless_progress.json")


def _default_state() -> dict:
    return {"best_floor": 0, "runs_played": 0, "run": None}


def load() -> dict:
    if not os.path.isfile(SAVE_PATH):
        return _default_state()
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _default_state()
    state = _default_state()
    state["best_floor"] = int(data.get("best_floor", 0))
    state["runs_played"] = int(data.get("runs_played", 0))
    run = data.get("run")
    if isinstance(run, dict):
        state["run"] = _validate_run(run)
    return state


def _validate_run(run: dict) -> dict | None:
    required = ("seed", "floor", "phase", "deck", "temp_deck", "coins")
    if any(k not in run for k in required):
        return None
    valid = valid_card_codes()
    run["deck"] = [c for c in run["deck"] if c in valid]
    run["temp_deck"] = [c for c in run["temp_deck"] if c in valid]
    run["relics"] = [r for r in run.get("relics", []) if r in RELICS]
    run["curses"] = [c for c in run.get("curses", []) if c in CURSES]
    run["armed_consumables"] = [c for c in run.get("armed_consumables", []) if c in CONSUMABLES]
    run.setdefault("perm_buffs", {})
    run.setdefault("pending", None)
    run.setdefault("shop_counters", {"remove_card": 0, "reroll": 0, "dmg_all": 0, "hp_all": 0})
    run.setdefault("floor_spec", None)
    run.setdefault("prev_kind", "")
    if not run["deck"]:
        return None
    return run


def save(state: dict) -> None:
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass


def record_run_end(state: dict, floors_cleared: int) -> bool:
    state["runs_played"] = state.get("runs_played", 0) + 1
    new_best = floors_cleared > state.get("best_floor", 0)
    if new_best:
        state["best_floor"] = floors_cleared
    state["run"] = None
    save(state)
    return new_best
