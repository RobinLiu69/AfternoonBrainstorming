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
from datetime import datetime, timedelta

from core.replay_source import ReplaySource, ReplayClock
from core.battling_dispatcher import BattlingDispatcher

from tests.helpers import make_game_state


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


def _timed_replay_source(tmp_path):
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    entries = [
        {"timestamp": t0.isoformat(), "message": "timer mode countdown"},
        {"timestamp": t0.isoformat(), "message": "time control 5+5"},
        {"timestamp": (t0 + timedelta(seconds=30)).isoformat(), "message": "action",
         "is_action": True, "action_player": "player1", "action_type": "end_turn"},
        {"timestamp": (t0 + timedelta(seconds=50)).isoformat(), "message": "action",
         "is_action": True, "action_player": "player2", "action_type": "end_turn"},
    ]
    path = tmp_path / "replay.jsonl"
    _write_jsonl(path, entries)
    return ReplaySource(path), t0


def test_time_control_metadata_and_timestamps(tmp_path):
    source, t0 = _timed_replay_source(tmp_path)
    assert source.metadata["time_control"] == "5+5"
    assert source.start_timestamp == t0.timestamp()
    assert source.action_timestamps == [
        t0.timestamp() + 30,
        t0.timestamp() + 50,
    ]


def test_replay_clock_reconstructs_countdown_with_increment(tmp_path):
    source, _t0 = _timed_replay_source(tmp_path)

    game_state = make_game_state()
    game_state.timer_mode = "countdown"
    game_state.turn_increment_seconds = 5
    game_state.player1.elapsed_time = 300
    game_state.player2.elapsed_time = 300
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")

    clock = ReplayClock(source, game_state)
    assert clock.enabled is True
    clock.reset()

    while True:
        action_index = source.current_action_index
        action = source.next_action()
        if action is None:
            break
        clock.before_action(action_index)
        dispatcher._execute(action, game_state)
        clock.after_action()

    assert game_state.player1.elapsed_time == 275
    assert game_state.player2.elapsed_time == 285
    assert game_state.player1.time_display == "04:35"
    assert game_state.player2.time_display == "04:45"


def test_replay_clock_disabled_without_timestamps(tmp_path):
    entries = [
        {"message": "timer mode countdown"},
        {"message": "action", "is_action": True, "action_player": "player1",
         "action_type": "end_turn"},
    ]
    path = tmp_path / "replay.jsonl"
    _write_jsonl(path, entries)
    source = ReplaySource(path)

    game_state = make_game_state()
    clock = ReplayClock(source, game_state)
    assert clock.enabled is False
    clock.reset()
    assert game_state.player1.time_display == "--:--"
    assert game_state.player2.time_display == "--:--"
