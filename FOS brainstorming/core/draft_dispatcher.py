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
from dataclasses import dataclass

from core.draft_state import DraftState
from core.network_layer import LANServer, LANClient
from screens.draft.draft_action import DraftAction


MAGIC_CARDS = ["CUBES", "MOVE", "MOVEO", "HEAL"]
MAX_DECK  = 12
MAX_UNIT  = 2
MAX_MAGIC = 3
DEFAULT_PAUSE_TIMEOUT_SECONDS: float = 60.0


@dataclass
class DraftResult:
    success: bool
    phase_advanced:  bool = False
    ready_to_start:  bool = False
    message: str = ""


class DraftDispatcher:
    def __init__(self, draft_state: DraftState, mode: str = "local",
                 reconnect_timeout: float = DEFAULT_PAUSE_TIMEOUT_SECONDS,
                 host_seat: str = "player1"):
        self.mode = mode
        self._network = None
        self._draft_state: DraftState = draft_state
        self.reconnect_timeout = reconnect_timeout
        self.host_seat = host_seat

        self.peer_lost: bool = False
        self._pause_deadline: float | None = None
        self._pause_timer: threading.Timer | None = None
        self._pause_lock = threading.Lock()

    def attach_server(self, server: "LANServer") -> None:
        self._network = server
        server.set_scene("draft")
        server.host_seat = self.host_seat
        server.on_action = self._on_remote_action
        server.on_client_connect = self._on_client_connect
        server.on_peer_disconnect = self._on_peer_disconnect
        server.on_peer_reconnect = self._on_peer_reconnect

    def attach_client(self, client: "LANClient") -> None:
        self._network = client
        client.on_state_update = self._draft_state.apply_dict

    def _on_client_connect(self, role: str) -> dict:
        self._refresh_pause_remaining()
        return self._draft_state.to_dict_for(role)

    def _refresh_pause_remaining(self) -> None:
        if self._draft_state.paused and self._pause_deadline is not None:
            self._draft_state.pause_seconds_remaining = max(0.0, self._pause_deadline - time.monotonic())

    def _on_peer_disconnect(self) -> None:
        with self._pause_lock:
            if self._pause_timer is not None:
                return
            self._pause_deadline = time.monotonic() + self.reconnect_timeout
            self._pause_timer = threading.Timer(self.reconnect_timeout, self._on_pause_timeout)
            self._pause_timer.daemon = True
            self._pause_timer.start()
        self._draft_state.paused = True
        self._draft_state.pause_reason = "opponent disconnected"
        self._draft_state.pause_seconds_remaining = self.reconnect_timeout
        print(f"[DraftDispatcher] paused; reconnect window {self.reconnect_timeout}s")
        self._broadcast(self._draft_state)

    def _on_peer_reconnect(self) -> None:
        with self._pause_lock:
            if self._pause_timer is not None:
                self._pause_timer.cancel()
                self._pause_timer = None
            self._pause_deadline = None
        self._draft_state.paused = False
        self._draft_state.pause_reason = ""
        self._draft_state.pause_seconds_remaining = 0.0
        print("[DraftDispatcher] resumed (peer reconnected)")
        self._broadcast(self._draft_state)

    def _on_pause_timeout(self) -> None:
        if not self._draft_state.paused:
            return
        with self._pause_lock:
            self._pause_timer = None
            self._pause_deadline = None
        self._draft_state.paused = False
        self._draft_state.pause_reason = ""
        self._draft_state.pause_seconds_remaining = 0.0
        self.peer_lost = True
        print("[DraftDispatcher] reconnect timeout; peer lost")
        self._broadcast(self._draft_state)

    def dispatch(self, action: DraftAction, draft_state: DraftState) -> DraftResult:
        self._draft_state = draft_state

        match self.mode:
            case "local":
                return self._execute(action, draft_state)

            case "lan_client":
                self._send_to_server(action)
                return DraftResult(True, message="pending")

            case "lan_server":
                result = self._execute(action, draft_state)
                if result.success:
                    self._broadcast(draft_state)
                return result

        return DraftResult(False, message=f"unknown mode: {self.mode}")

    def _on_remote_action(self, envelope: dict) -> None:
        payload = {k: v for k, v in envelope.items() if k != "type"}
        try:
            action = DraftAction(**payload)
        except TypeError as e:
            print(f"[DraftDispatcher] Bad remote action payload: {e}")
            return

        result = self._execute(action, self._draft_state)
        if result.success:
            self._broadcast(self._draft_state)

    def _send_to_server(self, action: DraftAction) -> None:
        if not isinstance(self._network, LANClient):
            print("[DraftDispatcher] No network attached — cannot send action.")
            return
        self._network.send_action({
            "action_type": action.action_type,
            "player":      action.player,
            "card_name":   action.card_name,
        })

    def _broadcast(self, draft_state: DraftState) -> None:
        if not isinstance(self._network, LANServer):
            return
        self._refresh_pause_remaining()
        self._network.broadcast_state_for(draft_state.to_dict_for)

    def _execute(self, action: DraftAction, draft_state: DraftState) -> DraftResult:
        if draft_state.paused:
            return DraftResult(False, message="paused")
        deck = (draft_state.player1_deck if action.player == "player1"
                else draft_state.player2_deck)

        turn_gated = (
            "add_card", "remove_card", "remove_last_card",
            "advance_phase", "confirm_start",
        )
        if action.action_type in turn_gated:
            if draft_state.current_editor() != action.player:
                return DraftResult(False, message="Not your turn")

        match action.action_type:
            case "add_card":
                if not action.card_name or action.card_name == "None":
                    return DraftResult(False)
                if len(deck) >= MAX_DECK:
                    return DraftResult(False, message="Deck is full")
                is_magic = action.card_name in MAGIC_CARDS
                limit = MAX_MAGIC if is_magic else MAX_UNIT
                if deck.count(action.card_name) >= limit:
                    return DraftResult(False, message="Over limit")
                deck.append(action.card_name)
                return DraftResult(True)
            case "remove_card":
                if action.card_name and action.card_name in deck:
                    idx = len(deck) - 1 - deck[::-1].index(action.card_name)
                    deck.pop(idx)
                return DraftResult(True)
            case "remove_last_card":
                if deck:
                    deck.pop()
                return DraftResult(True)
            case "advance_phase":
                if not draft_state.can_advance():
                    return DraftResult(False, message="Phase not ready")
                draft_state.advance_phase()
                return DraftResult(
                    True,
                    phase_advanced=True,
                    ready_to_start=(draft_state.phase == "done"),
                )
            case "confirm_start":
                # if not draft_state.can_advance():
                #     return DraftResult(False, message="Phase not ready")
                draft_state.advance_phase()
                return DraftResult(
                    True,
                    phase_advanced=True,
                    ready_to_start=(draft_state.phase == "done"),
                )
            case "toggle_timer":
                draft_state.timer_mode = (
                    "countdown" if draft_state.timer_mode == "timer" else "timer"
                )
                return DraftResult(True)
            case "toggle_file_save":
                draft_state.file_auto_delete = not draft_state.file_auto_delete
                return DraftResult(True)
        return DraftResult(False, message=f"unknown action: {action.action_type}")