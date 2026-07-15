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

import json

from core.replay_source import ReplaySource


def _write_jsonl(path, entries):
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def test_metadata_found_when_logged_after_actions(tmp_path):
    entries = [
        {"message": "timer mode timer"},
        {"message": "version 1.0", "version": "1.0"},
        {"message": "action", "is_action": True, "action_player": "player1",
         "action_type": "end_turn"},
        {"message": "action", "is_action": True, "action_player": "player2",
         "action_type": "end_turn"},
        {"message": "player1 deck ADCW-TANKW"},
        {"message": "player2 deck APW-HFW"},
        {"message": "rng_seed 12345", "rng_seed": 12345},
    ]
    path = tmp_path / "replay.jsonl"
    _write_jsonl(path, entries)

    source = ReplaySource(path)
    assert source.metadata["player1_deck"] == ["ADCW", "TANKW"]
    assert source.metadata["player2_deck"] == ["APW", "HFW"]
    assert source.metadata["rng_seed"] == 12345
    assert source.metadata["timer_mode"] == "timer"
    assert source.total_actions == 2


def test_metadata_found_when_logged_before_actions(tmp_path):
    entries = [
        {"message": "player1 deck ADCW"},
        {"message": "player2 deck APW"},
        {"message": "rng_seed 7", "rng_seed": 7},
        {"message": "action", "is_action": True, "action_player": "player1",
         "action_type": "end_turn"},
    ]
    path = tmp_path / "replay.jsonl"
    _write_jsonl(path, entries)

    source = ReplaySource(path)
    assert source.metadata["player1_deck"] == ["ADCW"]
    assert source.metadata["player2_deck"] == ["APW"]
    assert source.metadata["rng_seed"] == 7
