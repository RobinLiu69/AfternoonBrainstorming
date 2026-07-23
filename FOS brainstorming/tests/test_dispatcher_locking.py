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

import threading

from core.battling_dispatcher import BattlingDispatcher
from core.draft_dispatcher import DraftDispatcher
from core.draft_state import DraftState
from core.lobby_dispatcher import LobbyDispatcher
from core.lobby_state import LobbyState
from tests.helpers import make_game_state


def held_by_other_thread(lock) -> bool:
    result: list[bool] = []

    def attempt() -> None:
        got = lock.acquire(blocking=False)
        if got:
            lock.release()
        result.append(not got)

    thread = threading.Thread(target=attempt)
    thread.start()
    thread.join()
    return result[0]


def test_probe_reports_free_lock():
    assert held_by_other_thread(threading.RLock()) is False


def test_battling_remote_action_runs_under_action_lock():
    game_state = make_game_state()
    dispatcher = BattlingDispatcher(game_state=game_state, mode="lan_server")
    observed: list[bool] = []

    original = dispatcher._execute
    dispatcher._execute = lambda action, gs: (
        observed.append(held_by_other_thread(dispatcher.action_lock)),
        original(action, gs),
    )[1]

    dispatcher._on_remote_action({
        "type": "action", "seq": 1,
        "player": "player1", "action_type": "toggle_hint",
    })
    assert observed == [True]


def test_battling_client_state_apply_runs_under_action_lock():
    game_state = make_game_state()
    dispatcher = BattlingDispatcher(game_state=game_state, mode="lan_client")
    dispatcher._game_renderer = object()
    observed: list[bool] = []
    game_state.apply_dict = lambda state, renderer: observed.append(
        held_by_other_thread(dispatcher.action_lock))

    dispatcher._client_apply_state({})
    assert observed == [True]


def test_draft_remote_action_runs_under_action_lock():
    dispatcher = DraftDispatcher(DraftState(), mode="lan_server")
    observed: list[bool] = []

    original = dispatcher._execute
    dispatcher._execute = lambda action, ds: (
        observed.append(held_by_other_thread(dispatcher.action_lock)),
        original(action, ds),
    )[1]

    dispatcher._on_remote_action({
        "type": "action", "seq": 1,
        "player": "player1", "action_type": "add_card", "card_name": "ADCW",
    })
    assert observed == [True]


def test_lobby_remote_action_runs_under_action_lock():
    dispatcher = LobbyDispatcher(LobbyState(), mode="lan_server")
    observed: list[bool] = []

    original = dispatcher._execute
    dispatcher._execute = lambda action, sender_conn=None: (
        observed.append(held_by_other_thread(dispatcher.action_lock)),
        original(action, sender_conn=sender_conn),
    )[1]

    dispatcher._on_remote_action({
        "type": "action", "seq": 1,
        "player": "host", "action_type": "swap_seats",
    })
    assert observed == [True]
