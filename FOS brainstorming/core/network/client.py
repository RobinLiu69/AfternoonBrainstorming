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

import socket
import threading
import time
from typing import Callable, Optional

from core.network.errors import VersionMismatchError
from core.network.messages import _recv_msg, _send_msg
from core.network.token_store import is_primary_instance, load_token, save_token


ACK_TIMEOUT_SECONDS: float = 10.0
IDLE_TIMEOUT_SECONDS: float = 20.0
RECV_POLL_SECONDS: float = 1.0
WAITING_HINT_DELAY_SECONDS: float = 1.0


class LANClient:
    def __init__(self, version: str, host: str, port: int = 5555, room: str = ""):
        self.version = version
        self.host = host
        self.port = port
        self.room = room
        self.on_state_update: Optional[Callable[[dict], None]] = None

        self._sock: Optional[socket.socket] = None
        self.role: str = ""
        self.scene: str = ""
        self.initial_state: dict = {}
        self.token: str = ""
        self.is_disconnected: bool = False
        self.reconnect_refused: bool = False
        self._intent: str = "play"

        self.pending_scene: Optional[str]  = None
        self.pending_scene_state: Optional[dict] = None
        self.pending_winner: Optional[str]  = None
        self.pending_statistics: Optional[dict] = None
        self.latest_state: Optional[dict] = None

        self.net_spectator_count: int = 0
        self.net_latencies: dict = {}
        self.my_latency: Optional[float] = None

        self.ack_timeout: float = ACK_TIMEOUT_SECONDS
        self.idle_timeout: float = IDLE_TIMEOUT_SECONDS
        self.timed_out: bool = False
        self._last_recv: float = 0.0
        self._write_lock = threading.Lock()
        self._ack_lock = threading.Lock()
        self._action_seq: int = 0
        self._pending_seq: Optional[int] = None
        self._pending_since: float = 0.0

    @property
    def is_connected(self) -> bool:
        return self._sock is not None

    @property
    def is_awaiting_ack(self) -> bool:
        with self._ack_lock:
            if self._pending_seq is None:
                return False
            if time.monotonic() - self._pending_since <= self.ack_timeout:
                return True
            stale_seq = self._pending_seq
            self._pending_seq = None
        print(f"[LANClient] no ack for action #{stale_seq} within {self.ack_timeout}s; "
              f"dropping the connection so it can be re-established")
        self.disconnect()
        self.is_disconnected = True
        return False

    @property
    def awaiting_ack_seconds(self) -> float:
        with self._ack_lock:
            if self._pending_seq is None:
                return 0.0
            return time.monotonic() - self._pending_since

    @property
    def show_waiting_hint(self) -> bool:
        return self.awaiting_ack_seconds > WAITING_HINT_DELAY_SECONDS

    def _check_idle(self) -> bool:
        if time.monotonic() - self._last_recv < self.idle_timeout:
            return True
        self.timed_out = True
        print(f"[LANClient] nothing received from the server for {self.idle_timeout}s; "
              f"connection timed out")
        return False

    def clear_pending_action(self) -> None:
        with self._ack_lock:
            self._pending_seq = None

    def _send(self, sock: socket.socket, payload: dict) -> None:
        with self._write_lock:
            _send_msg(sock, payload)

    def connect(self, timeout: float = 5.0, intent: str = "play") -> tuple[str, dict]:
        if self._sock is not None:
            return self.role, self.initial_state

        self._intent = intent
        token = self.token
        if not token and is_primary_instance():
            token = load_token(self.host, self.port, self.room)
        return self._do_handshake(timeout=timeout, intent=intent, token=token or None)

    def try_reconnect(self, timeout: float = 5.0) -> bool:
        if self._sock is not None:
            return True
        if not self.token:
            return False
        try:
            role, _ = self._do_handshake(timeout=timeout, intent=self._intent, token=self.token)
        except ConnectionRefusedError as e:
            print(f"[LANClient] reconnect refused (host gone): {e}")
            self.reconnect_refused = True
            return False
        except (OSError, RuntimeError, ConnectionError) as e:
            print(f"[LANClient] reconnect failed: {e}")
            if isinstance(e, ConnectionError) and "room_not_found" in str(e):
                self.reconnect_refused = True
            return False
        self.reconnect_refused = False
        return role in ("player1", "player2")

    def _do_handshake(self, timeout: float, intent: str, token: Optional[str]) -> tuple[str, dict]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((self.host, self.port))

        hello = {"type": "hello", "intent": intent, "version": self.version,
                 "room": self.room}
        if token:
            hello["token"] = token
        try:
            _send_msg(sock, hello)
        except OSError:
            sock.close()
            raise

        welcome = _recv_msg(sock)

        if not welcome:
            sock.close()
            raise RuntimeError("Handshake failed: no response from server")

        if welcome.get("type") == "rejected":
            sock.close()
            reason = welcome.get("reason", "unknown")
            if reason == "version_mismatch":
                raise VersionMismatchError(
                    server_version=welcome.get("server_version", "unknown"),
                    client_version=welcome.get("client_version", self.version),
                )
            raise ConnectionError(f"Connection rejected by server: {reason}")

        if welcome.get("type") != "welcome":
            sock.close()
            raise RuntimeError(f"Handshake failed: expected welcome, got {welcome!r}")

        if welcome.get("version") != self.version:
            sock.close()
            raise VersionMismatchError(
                server_version=welcome.get("version", "unknown"),
                client_version=self.version,
            )

        sock.settimeout(RECV_POLL_SECONDS)
        self._last_recv = time.monotonic()
        self.timed_out = False
        self._sock = sock
        self.role = welcome["role"]
        self.scene = welcome.get("scene", "")
        self.initial_state = welcome.get("state", {})
        new_token = welcome.get("token", "")
        if new_token:
            self.token = new_token
        new_room = welcome.get("room", "")
        if new_room:
            self.room = new_room
        if new_token and is_primary_instance():
            save_token(self.host, self.port, self.room, new_token)
        self.is_disconnected = False
        self.clear_pending_action()

        threading.Thread(target=self._recv_loop, daemon=True).start()
        print(f"[LANClient] Connected to {self.host}:{self.port} as {self.role} (scene={self.scene!r})")
        return self.role, self.initial_state

    def _recv_loop(self) -> None:
        sock = self._sock
        if sock is None:
            return
        while True:
            if sock is not self._sock:
                return
            try:
                msg = _recv_msg(sock, on_idle=self._check_idle)
            except (OSError, ValueError):
                break
            if msg is None:
                break
            self._last_recv = time.monotonic()

            try:
                mtype = msg.get("type")
                if mtype == "state":
                    print(f"[LANClient] received state envelope")
                    self.latest_state = msg.get("state")
                    if self.on_state_update is not None:
                        self.on_state_update(msg["state"])
                elif mtype == "scene":
                    self.pending_scene_state = msg.get("state", {})
                    self.pending_scene = msg["scene"]
                    new_role = msg.get("role", "")
                    if new_role:
                        self.role = new_role
                elif mtype == "game_over":
                    self.pending_winner = msg["winner"]
                    self.pending_statistics = msg.get("statistics", {})
                elif mtype == "log_transfer":
                    self._save_transferred_logs(msg)
                elif mtype == "ack":
                    self._on_ack(msg.get("seq"))
                elif mtype == "ping":
                    ts = msg.get("ts", 0.0)
                    try:
                        self._send(sock, {"type": "pong", "ts": ts})
                    except OSError:
                        pass
                elif mtype == "token":
                    self.token = msg.get("token", "")
                    if is_primary_instance():
                        save_token(self.host, self.port, self.room, self.token)
                elif mtype == "net_info":
                    self.net_spectator_count = msg.get("spectator_count", 0)
                    self.net_latencies = msg.get("latencies", {})
                elif mtype == "ping_result":
                    self.my_latency = msg.get("ms")
            except Exception:
                import traceback, sys
                try:
                    sys.stderr.write("=== LANClient._recv_loop: message handler error ===\n")
                    sys.stderr.write(traceback.format_exc())
                    sys.stderr.write("====================================================\n")
                    sys.stderr.flush()
                except Exception:
                    pass
                continue

        if sock is self._sock:
            self.is_disconnected = True
            self.clear_pending_action()
            try:
                sock.close()
            except OSError:
                pass
            self._sock = None
            print(f"[LANClient] socket disconnected")

    def _on_ack(self, seq) -> None:
        if seq is None:
            return
        with self._ack_lock:
            if self._pending_seq is not None and seq >= self._pending_seq:
                self._pending_seq = None

    def consume_pending_scene(self) -> Optional[tuple[str, dict]]:
        if self.pending_scene is None:
            return None
        scene = self.pending_scene
        state = self.pending_scene_state or {}
        self.pending_scene = None
        self.pending_scene_state = None
        return scene, state

    def consume_pending_game_over(self) -> Optional[tuple[str, dict]]:
        if self.pending_winner is None:
            return None
        winner = self.pending_winner
        stats  = self.pending_statistics or {}
        self.pending_winner = None
        self.pending_statistics = None
        return winner, stats
    
    def _save_transferred_logs(self, msg: dict) -> None:
        import base64
        from pathlib import Path
        from shared.setting import FOLDER_PATH
        out_dir = Path(FOLDER_PATH) / "battle_records"
        out_dir.mkdir(parents=True, exist_ok=True)
        for key in ("log_file", "jsonl_file"):
            f = msg.get(key)
            if not f:
                continue
            try:
                (out_dir / f["name"]).write_bytes(base64.b64decode(f["data"]))
                print(f"[LANClient] saved backup: {f['name']}")
            except Exception as e:
                print(f"[LANClient] failed to save {key}: {e}")

    def send_action(self, action_dict: dict, await_ack: bool = False) -> bool:
        sock = self._sock
        if sock is None:
            return False
        if await_ack and self.is_awaiting_ack:
            print("[LANClient] action dropped: still waiting for the server to ack the previous one")
            return False

        with self._ack_lock:
            self._action_seq += 1
            seq = self._action_seq
            if await_ack:
                self._pending_seq = seq
                self._pending_since = time.monotonic()
        try:
            self._send(sock, {"type": "action", "seq": seq, **action_dict})
        except OSError as e:
            print(f"[LANClient] send_action failed (connection lost?): {e}")
            self.clear_pending_action()
            return False
        return True

    def disconnect(self) -> None:
        sock = self._sock
        self.clear_pending_action()
        if sock is None:
            return
        self._sock = None
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass
