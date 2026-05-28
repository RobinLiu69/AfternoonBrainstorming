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
from campaign.ai_decks import STAGE_ORDER


SAVE_PATH: str = os.path.join(FOLDER_PATH, "campaign_progress.json")


def _default_state() -> dict:
    return {"unlocked": [STAGE_ORDER[0]], "cleared": []}


def load() -> dict:
    if not os.path.isfile(SAVE_PATH):
        return _default_state()
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _default_state()
    state = _default_state()
    state["unlocked"] = [s for s in data.get("unlocked", state["unlocked"]) if s in STAGE_ORDER]
    state["cleared"] = [s for s in data.get("cleared", []) if s in STAGE_ORDER]
    if STAGE_ORDER[0] not in state["unlocked"]:
        state["unlocked"].insert(0, STAGE_ORDER[0])
    return state


def save(state: dict) -> None:
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass


def is_unlocked(stage: str, state: dict | None = None) -> bool:
    if state is None:
        state = load()
    return stage in state.get("unlocked", [])


def mark_cleared(stage: str) -> dict:
    state = load()
    if stage not in state["cleared"]:
        state["cleared"].append(stage)
    idx = STAGE_ORDER.index(stage)
    if idx + 1 < len(STAGE_ORDER):
        nxt = STAGE_ORDER[idx + 1]
        if nxt not in state["unlocked"]:
            state["unlocked"].append(nxt)
    save(state)
    return state
