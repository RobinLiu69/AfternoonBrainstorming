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
import time

from core.battling_dispatcher import BattlingDispatcher
from core.draft_dispatcher import DraftDispatcher
from core.draft_state import DraftState
from tests.helpers import make_game_state


def _race(dispatcher, timeout_call, reconnect_call) -> None:
    with dispatcher.action_lock:
        thread = threading.Thread(target=timeout_call)
        thread.start()
        time.sleep(0.15)
        reconnect_call()
    thread.join(timeout=5.0)


class TestATimeoutThatLostTheRaceStaysQuiet:
    def test_a_battle_is_not_awarded_when_the_peer_beat_the_timer(self) -> None:
        game_state = make_game_state()
        dispatcher = BattlingDispatcher(game_state=game_state, mode="lan_server",
                                        reconnect_timeout=60.0)
        dispatcher._on_peer_disconnect()
        assert game_state.paused is True

        _race(dispatcher, dispatcher._on_pause_timeout, dispatcher._on_peer_reconnect)

        assert dispatcher.pending_winner is None
        assert game_state.paused is False

    def test_a_battle_is_still_awarded_when_nobody_came_back(self) -> None:
        game_state = make_game_state()
        dispatcher = BattlingDispatcher(game_state=game_state, mode="lan_server",
                                        reconnect_timeout=60.0)
        dispatcher._on_peer_disconnect()

        dispatcher._on_pause_timeout()

        assert dispatcher.pending_winner == dispatcher.host_seat
        assert game_state.paused is False

    def test_a_draft_peer_is_not_lost_when_they_beat_the_timer(self) -> None:
        draft_state = DraftState()
        dispatcher = DraftDispatcher(draft_state=draft_state, mode="lan_server",
                                     reconnect_timeout=60.0)
        dispatcher._on_peer_disconnect()
        assert draft_state.paused is True

        _race(dispatcher, dispatcher._on_pause_timeout, dispatcher._on_peer_reconnect)

        assert dispatcher.peer_lost is False
        assert draft_state.paused is False

    def test_a_draft_peer_is_still_lost_when_nobody_came_back(self) -> None:
        draft_state = DraftState()
        dispatcher = DraftDispatcher(draft_state=draft_state, mode="lan_server",
                                     reconnect_timeout=60.0)
        dispatcher._on_peer_disconnect()

        dispatcher._on_pause_timeout()

        assert dispatcher.peer_lost is True

    def test_a_stray_timeout_without_a_pause_does_nothing(self) -> None:
        game_state = make_game_state()
        dispatcher = BattlingDispatcher(game_state=game_state, mode="lan_server",
                                        reconnect_timeout=60.0)

        dispatcher._on_pause_timeout()

        assert dispatcher.pending_winner is None
        assert game_state.paused is False
