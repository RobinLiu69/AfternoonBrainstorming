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

from tower import card_pool
from tower.content import RELICS, SELECTABLE_FACTIONS


SAVE_PATH: str = os.path.join(FOLDER_PATH, "data/tower_progress.json")

REQUIRED_KEYS: tuple[str, ...] = (
    "seed", "factions", "act", "layer", "maps", "deck", "bench", "gold",
)


def _default_state() -> dict:
    return {"best_act": 0, "best_layer": 0, "runs_played": 0, "run": None}


def load() -> dict:
    if not os.path.isfile(SAVE_PATH):
        return _default_state()
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _default_state()

    state = _default_state()
    state["best_act"] = int(data.get("best_act", 0))
    state["best_layer"] = int(data.get("best_layer", 0))
    state["runs_played"] = int(data.get("runs_played", 0))
    run = data.get("run")
    if isinstance(run, dict):
        state["run"] = validate_run(run)
    return state


def validate_run(run: dict) -> dict | None:
    if any(key not in run for key in REQUIRED_KEYS):
        return None
    if not isinstance(run.get("maps"), list) or not run["maps"]:
        return None

    run["factions"] = [f for f in run["factions"] if f in SELECTABLE_FACTIONS]
    run["deck"] = [c for c in run["deck"] if card_pool.is_valid_code(c)]
    run["bench"] = [c for c in run["bench"] if card_pool.is_valid_code(c)]
    run["relics"] = [r for r in run.get("relics", []) if r in RELICS]
    run["picks"] = {str(k): int(v) for k, v in (run.get("picks") or {}).items()}
    run.setdefault("bench_bonus", 0)
    run.setdefault("orbs", 0)
    run.setdefault("debt", 0)
    run.setdefault("pending", None)
    run.setdefault("shop_spent", False)
    run.setdefault("shop_rerolls", 0)
    run.setdefault("battles_won", 0)
    run["events_seen"] = [e for e in run.get("events_seen", []) if isinstance(e, str)]
    run["altar_deals_used"] = [d for d in run.get("altar_deals_used", [])
                               if isinstance(d, str)]

    if not run["deck"]:
        return None
    return run


def save(state: dict) -> None:
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass


def record_run_end(state: dict, act: int, layer: int, won: bool) -> bool:
    state["runs_played"] = state.get("runs_played", 0) + 1
    reached = (act, layer)
    best = (state.get("best_act", 0), state.get("best_layer", 0))
    new_best = reached > best
    if new_best:
        state["best_act"], state["best_layer"] = act, layer
    state["run"] = None
    save(state)
    return new_best
