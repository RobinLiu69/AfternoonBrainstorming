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
import threading
import time
from typing import TYPE_CHECKING, Optional

from core.game_action import GameAction, ActionResult
from core.game_state import GameState

if TYPE_CHECKING:
    from core.network_layer import LANServer, LANClient
    from rendering.game_renderer import GameRenderer


DEFAULT_PAUSE_TIMEOUT_SECONDS: float = 60.0


class BattlingDispatcher:
    def __init__(self, game_state: GameState, mode: str = "local",
                 reconnect_timeout: float = DEFAULT_PAUSE_TIMEOUT_SECONDS,
                 host_seat: str = "player1"):
        self.mode = mode
        self._network = None
        self._game_state: GameState = game_state
        self._game_renderer: Optional["GameRenderer"] = None
        self.reconnect_timeout = reconnect_timeout
        self.host_seat = host_seat

        self.pending_winner: Optional[str] = None
        self._pause_deadline: Optional[float] = None
        self._pause_timer: Optional[threading.Timer] = None
        self._pause_lock = threading.Lock()
        self.latencies: dict[str, float] = {}

    def attach_renderer(self, renderer: "GameRenderer") -> None:
        self._game_renderer = renderer

    def attach_server(self, server: "LANServer") -> None:
        self._network = server
        server.reset_callbacks()
        server.set_scene("battling")
        server.host_seat = self.host_seat
        server.on_action = self._on_remote_action
        server.on_client_connect = self._on_client_connect
        server.on_peer_disconnect = self._on_peer_disconnect
        server.on_peer_reconnect = self._on_peer_reconnect
        server.on_pulse = self._on_pulse
        server.on_pong = self._on_pong

    def attach_client(self, client: "LANClient") -> None:
        self._network = client
        client.on_state_update = self._client_apply_state

    def _on_pong(self, role: str, rtt_ms: float) -> None:
        if role in ("player1", "player2"):
            self.latencies[role] = round(rtt_ms, 1)

    def _broadcast_net_info(self) -> None:
        from core.network_layer import LANServer
        if not isinstance(self._network, LANServer):
            return
        with self._network._lock:
            roles = [r for _c, r in self._network._clients]
        latencies = {seat: self.latencies[seat] for seat in ("player1", "player2")
                     if seat in roles and seat in self.latencies}
        spectators = sum(1 for r in roles if r in ("spectator", "god"))
        self._network.broadcast_net_info(spectators, latencies)

    def _on_client_connect(self, role: str) -> dict:
        if self._game_state is None:
            return {}
        self._refresh_pause_remaining()
        return self._game_state.to_dict_for(role)

    def _on_pulse(self) -> None:
        if self._game_state is not None and self._game_state.paused:
            self._broadcast_state(self._game_state)
        self._broadcast_net_info()

    def _refresh_pause_remaining(self) -> None:
        if self._game_state is None:
            return
        if self._game_state.paused and self._pause_deadline is not None:
            self._game_state.pause_seconds_remaining = max(0.0, self._pause_deadline - time.monotonic())

    def _on_peer_disconnect(self) -> None:
        if self._game_state is None:
            return
        if self.reconnect_timeout == float("inf"):
            if self._game_state.paused:
                return
            self._game_state.paused = True
            self._game_state.pause_reason = "opponent disconnected"
            self._game_state.pause_seconds_remaining = float("inf")
            print("[BattlingDispatcher] paused; waiting indefinitely for reconnect")
            self._broadcast_state(self._game_state)
            return
        with self._pause_lock:
            if self._pause_timer is not None:
                return
            self._pause_deadline = time.monotonic() + self.reconnect_timeout
            self._pause_timer = threading.Timer(self.reconnect_timeout, self._on_pause_timeout)
            self._pause_timer.daemon = True
            self._pause_timer.start()
        self._game_state.paused = True
        self._game_state.pause_reason = "opponent disconnected"
        self._game_state.pause_seconds_remaining = self.reconnect_timeout
        print(f"[BattlingDispatcher] paused; reconnect window {self.reconnect_timeout}s")
        self._broadcast_state(self._game_state)

    def _on_peer_reconnect(self) -> None:
        if self._game_state is None:
            return
        with self._pause_lock:
            if self._pause_timer is not None:
                self._pause_timer.cancel()
                self._pause_timer = None
            self._pause_deadline = None
        self._game_state.paused = False
        self._game_state.pause_reason = ""
        self._game_state.pause_seconds_remaining = 0.0
        print("[BattlingDispatcher] resumed (peer reconnected)")
        self._broadcast_state(self._game_state)

    def _on_pause_timeout(self) -> None:
        if self._game_state is None or not self._game_state.paused:
            return
        with self._pause_lock:
            self._pause_timer = None
            self._pause_deadline = None
        self._game_state.paused = False
        self._game_state.pause_reason = ""
        self._game_state.pause_seconds_remaining = 0.0
        winner = self.host_seat
        self.pending_winner = winner
        print(f"[BattlingDispatcher] reconnect timeout; declaring {winner} winner")
        self._broadcast_state(self._game_state)
        self._broadcast_game_over(winner, self._game_state)

    def _client_apply_state(self, state_dict: dict) -> None:
        if self._game_renderer is None:
            return
        self._game_state.apply_dict(state_dict, self._game_renderer)

    def dispatch(self, action: GameAction, game_state: GameState) -> ActionResult:
        self._game_state = game_state

        match self.mode:
            case "local" | "campaign":
                return self._execute(action, game_state)

            case "lan_client":
                self._send_to_server(action)
                return ActionResult(True, message="pending")

            case "lan_server":
                result = self._execute(action, game_state)
                if result.success:
                    self._broadcast_state(game_state)
                    if result.quit and result.message:
                        self._broadcast_game_over(result.message, game_state)
                        self.pending_winner = result.message
                return result

        return ActionResult(False, message=f"unknown mode: {self.mode}")

    def _on_remote_action(self, envelope: dict, sender_conn=None) -> None:
        payload = {k: v for k, v in envelope.items() if k != "type"}
        if not self._sender_matches(payload.get("player"), sender_conn):
            return
        try:
            action = GameAction(**payload)
        except TypeError as e:
            print(f"[BattlingDispatcher] Bad remote action payload: {e}")
            return

        result = self._execute(action, self._game_state)
        if result.success:
            self._broadcast_state(self._game_state)
            if result.quit and result.message:
                self._broadcast_game_over(result.message, self._game_state)
                self.pending_winner = result.message

    def _sender_matches(self, claimed_player, sender_conn) -> bool:
        from core.network_layer import LANServer
        if sender_conn is None or not isinstance(self._network, LANServer):
            return True
        sender_role = self._network.find_role(sender_conn)
        if not sender_role or claimed_player != sender_role:
            print(f"[BattlingDispatcher] dropped action from {sender_role!r} "
                  f"claiming to be {claimed_player!r}")
            return False
        return True

    def _send_to_server(self, action: GameAction) -> None:
        from core.network_layer import LANClient
        if not isinstance(self._network, LANClient):
            print("[BattlingDispatcher] No network attached — cannot send action.")
            return
        self._network.send_action({
            "action_type": action.action_type,
            "player": action.player,
            "board_x": action.board_x,
            "board_y": action.board_y,
            "hand_index": action.hand_index,
        })

    def _broadcast_state(self, game_state: GameState) -> None:
        from core.network_layer import LANServer
        if not isinstance(self._network, LANServer):
            return
        self._refresh_pause_remaining()
        print(f"[BattlingDispatcher] broadcast_state turn={game_state.turn_number} score={game_state.score} paused={game_state.paused}")
        self._network.broadcast_state_for(game_state.to_dict_for)

    def _broadcast_game_over(self, winner: str, game_state: GameState) -> None:
        from core.network_layer import LANServer
        if not isinstance(self._network, LANServer):
            return
        stats = {
            "export_for_charts": game_state.game_statistics.export_for_charts(),
            "score_history":     game_state.game_statistics.score_history,
        }
        self._network.broadcast_game_over(winner, stats)

    def _execute(self, action: GameAction, game_state: GameState) -> ActionResult:
        if game_state.paused and action.action_type not in ("toggle_hint", "toggle_animation", "quit"):
            return ActionResult(False, message="paused")
        game_state.game_logger.log_action(action, action.player)
        owned_actions = ("attack", "play_card", "move_to", "heal",
                         "spawn_cube", "toggle_upgrade", "end_turn")
        if action.action_type in owned_actions:
            current = "player1" if (game_state.turn_number % 2 == 0) else "player2"
            if action.player != current:
                return ActionResult(False, message="Not your turn")

        player = game_state.get_player(action.player)

        match action.action_type:
            case "attack":
                if action.board_x is None or action.board_y is None:
                    return ActionResult(False, message="需要棋盤座標")
                if game_state.number_of_attacks[action.player] <= 0:
                    return ActionResult(False, message="攻擊次數不足")
                player.attack(action.board_x, action.board_y, game_state)
                return ActionResult(True)

            case "play_card":
                if action.hand_index is None:
                    return ActionResult(False)
                if action.board_x is None or action.board_y is None:
                    return ActionResult(False)
                player.play_card(action.board_x, action.board_y, action.hand_index, game_state)
                return ActionResult(True)

            case "move_to":
                if action.board_x is not None and action.board_y is not None:
                    player.move_card(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message="action missing: board_x or board_y")

            case "heal":
                if action.board_x is not None and action.board_y is not None:
                    player.heal_card(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message="action missing: board_x or board_y")

            case "spawn_cube":
                if action.board_x is not None and action.board_y is not None:
                    player.spawn_cube(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message="action missing: board_x or board_y")

            case "toggle_upgrade":
                if action.hand_index is None: return ActionResult(False, message="action missing: hand_index")
                player = game_state.get_player(action.player)
                if 0 <= action.hand_index < len(player.hand):
                    name = player.hand[action.hand_index]
                    if name.endswith(" (+)"):
                        player.hand[action.hand_index] = name[:-4]
                    elif name.endswith("C"):
                        player.hand[action.hand_index] = name + " (+)"
                return ActionResult(success=True)
            
            case "toggle_hint":
                return ActionResult(True)
            
            case "toggle_animation":
                return ActionResult(True)

            case "end_turn":
                if game_state.timer_mode == "countdown" and game_state.turn_increment_seconds > 0:
                    ending_player = game_state.get_player(action.player)
                    ending_player.elapsed_time += game_state.turn_increment_seconds
                    ending_player._refresh_time_display()
                game_state.turn_number += 1
                opponent = game_state.get_opponent_name(action.player)
                game_state.get_player(action.player).turn_end(game_state)
                game_state.game_statistics.add_score_record(game_state.score)
                if abs(game_state.score) >= game_state.win_threshold:
                    winner = "player1" if game_state.score < 0 else "player2"
                    return ActionResult(True, message=winner, quit=True)
                game_state.get_player(opponent).turn_start(game_state)
                return ActionResult(True, end_turn=True)

            case "quit":
                return ActionResult(True, quit=True)

        return ActionResult(False, message=f"unknown action: {action.action_type}")