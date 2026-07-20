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

import secrets
import socket
import threading
import time
from typing import Callable, Optional

from core.network.messages import _recv_msg, _send_msg


class LANServer:
    def __init__(self, version: str, host: str = "0.0.0.0", port: int = 5555,
                 god_view: bool = False, host_seat: str = "player1",
                 heartbeat_interval: float = 1.0, heartbeat_timeout: float = 10.0):
        self.version = version
        self.host = host
        self.port = port
        self.god_view = god_view
        self.host_seat = host_seat
        self.scene: str = ""
        self.room_code: str = ""

        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self._last_pulse: float = 0.0

        self.on_action: Optional[Callable[[dict, socket.socket], None]] = None
        self.on_client_connect: Optional[Callable[[str], dict]] = None
        self.on_peer_disconnect: Optional[Callable[[], None]] = None
        self.on_peer_reconnect: Optional[Callable[[], None]] = None
        self.on_client_dropped: Optional[Callable[[str], None]] = None
        self.on_pong: Optional[Callable[[str, float], None]] = None
        self.on_pulse: Optional[Callable[[], None]] = None
        self._last_seen: dict = {}

        self._clients: list[tuple[socket.socket, str]] = []
        self._peer_token: Optional[str] = None
        self._evicted: set[socket.socket] = set()
        self._lock = threading.Lock()
        self._server_sock: Optional[socket.socket] = None
        self._running = False

    def set_scene(self, scene: str) -> None:
        self.scene = scene

    def reset_callbacks(self) -> None:
        self.on_action = None
        self.on_client_connect = None
        self.on_peer_disconnect = None
        self.on_peer_reconnect = None
        self.on_client_dropped = None
        self.on_pong = None
        self.on_pulse = None

    def pulse(self, now: Optional[float] = None) -> None:
        if not self._running:
            return
        now = now if now is not None else time.monotonic()
        if now - self._last_pulse < self.heartbeat_interval:
            return
        self._last_pulse = now
        self.broadcast_ping()
        self.check_heartbeat(self.heartbeat_timeout)
        if self.on_pulse is not None:
            try:
                self.on_pulse()
            except Exception as e:
                print(f"[LANServer] on_pulse raised: {e}")

    def peer_seat(self) -> str:
        return "player2" if self.host_seat == "player1" else "player1"

    def update_host_seat(self, new_seat: str) -> None:
        if new_seat not in ("player1", "player2") or new_seat == self.host_seat:
            return
        old_peer = self.peer_seat()
        self.host_seat = new_seat
        new_peer = self.peer_seat()
        with self._lock:
            self._clients = [(c, new_peer if r == old_peer else r) for c, r in self._clients]

    def reset_heartbeat(self) -> None:
        now = time.monotonic()
        with self._lock:
            for conn, _role in self._clients:
                self._last_seen[conn] = now

    def update_god_view(self, god_view: bool) -> None:
        self.god_view = god_view
        old_role = "spectator" if god_view else "god"
        new_role = "god" if god_view else "spectator"
        with self._lock:
            self._clients = [(c, new_role if r == old_role else r) for c, r in self._clients]

    def find_role(self, conn: socket.socket) -> str:
        with self._lock:
            return next((r for c, r in self._clients if c is conn), "")

    def reassign_role(self, conn: socket.socket, new_role: str) -> bool:
        with self._lock:
            for i, (c, _r) in enumerate(self._clients):
                if c is conn:
                    self._clients[i] = (c, new_role)
                    return True
        return False

    def _decide_role(self, intent: str, token: Optional[str]) -> tuple[str, str]:
        peer_role = self.peer_seat()
        token_matches = (
            token is not None
            and self._peer_token is not None
            and token == self._peer_token
        )

        evicted: list[socket.socket] = []
        with self._lock:
            if token_matches:
                kept: list[tuple[socket.socket, str]] = []
                for c, r in self._clients:
                    if r == peer_role:
                        evicted.append(c)
                        self._evicted.add(c)
                        self._last_seen.pop(c, None)
                    else:
                        kept.append((c, r))
                self._clients = kept
                chosen_role: str = peer_role
                issued_token: str = self._peer_token  # type: ignore[assignment]
            else:
                has_peer = any(r == peer_role for _conn, r in self._clients)
                if intent == "play" and not has_peer and self.scene == "lobby":
                    new_token = secrets.token_urlsafe(16)
                    self._peer_token = new_token
                    chosen_role = peer_role
                    issued_token = new_token
                else:
                    chosen_role = "god" if self.god_view else "spectator"
                    issued_token = ""

        for c in evicted:
            try:
                c.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                c.close()
            except OSError:
                pass

        return chosen_role, issued_token

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(2)
        self._running = True
        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()
        print(f"[LANServer] Listening on {self.host}:{self.port}")

    def _accept_loop(self) -> None:
        if not self._server_sock:
            return
        while self._running:
            try:
                conn, addr = self._server_sock.accept()
            except OSError:
                break
            print(f"[LANServer] Client connected: {addr}")

            try:
                conn.settimeout(5.0)
                hello = _recv_msg(conn)
                conn.settimeout(None)
            except (OSError, ValueError):
                conn.close()
                continue

            if hello is None or hello.get("type") != "hello":
                print(f"[LANServer] Bad hello from {addr}: {hello!r}")
                conn.close()
                continue

            self.handle_connection(conn, addr, hello)

    def handle_connection(self, conn: socket.socket, addr, hello: dict) -> None:
        client_version = hello.get("version", "")
        if client_version != self.version:
            try:
                _send_msg(conn, {
                    "type": "rejected",
                    "reason": "version_mismatch",
                    "server_version": self.version,
                    "client_version": client_version,
                })
            except OSError:
                pass
            conn.close()
            print(f"[LANServer] Rejected {addr}: version mismatch (client={client_version!r}, server={self.version!r})")
            return

        intent = hello.get("intent", "play")
        token = hello.get("token")
        role, issued_token = self._decide_role(intent, token)
        is_reconnect = (role in ("player1", "player2")
                        and token is not None and token == issued_token)
        peer_joined = role in ("player1", "player2")

        if peer_joined and self.on_peer_reconnect is not None:
            try:
                self.on_peer_reconnect()
            except Exception as e:
                print(f"[LANServer] on_peer_reconnect raised: {e}")

        state = self.on_client_connect(role) if self.on_client_connect is not None else {}

        try:
            _send_msg(conn, {
                "type": "welcome",
                "role": role,
                "state": state,
                "version": self.version,
                "scene": self.scene,
                "token": issued_token,
                "room": self.room_code,
            })
        except OSError:
            conn.close()
            return

        with self._lock:
            self._clients.append((conn, role))
            self._last_seen[conn] = time.monotonic()
        print(f"[LANServer] Assigned role={role} to {addr} (reconnect={is_reconnect})")

        threading.Thread(
            target=self._client_loop, args=(conn, addr), daemon=True
        ).start()

    def _client_loop(self, conn: socket.socket, addr) -> None:
        while True:
            try:
                msg = _recv_msg(conn)
            except (OSError, ValueError):
                msg = None
            if msg is None:
                print(f"[LANServer] Client disconnected: {addr}")
                with self._lock:
                    was_evicted = conn in self._evicted
                    self._evicted.discard(conn)
                    dropped_role = next((r for c, r in self._clients if c is conn), "")
                    self._clients = [c for c in self._clients if c[0] is not conn]
                    self._last_seen.pop(conn, None)
                try:
                    conn.close()
                except OSError:
                    pass
                if was_evicted:
                    break
                if self.on_client_dropped is not None:
                    try:
                        self.on_client_dropped(dropped_role)
                    except Exception as e:
                        print(f"[LANServer] on_client_dropped raised: {e}")
                if dropped_role in ("player1", "player2") and self.on_peer_disconnect is not None:
                    try:
                        self.on_peer_disconnect()
                    except Exception as e:
                        print(f"[LANServer] on_peer_disconnect raised: {e}")
                break
            with self._lock:
                self._last_seen[conn] = time.monotonic()
            if msg.get("type") == "pong":
                sent_ts = msg.get("ts", 0.0)
                rtt_ms = (time.monotonic() - sent_ts) * 1000.0
                try:
                    _send_msg(conn, {"type": "ping_result", "ms": round(rtt_ms, 1)})
                except OSError:
                    pass
                if self.on_pong is not None:
                    role = self.find_role(conn)
                    try:
                        self.on_pong(role, rtt_ms)
                    except Exception as e:
                        print(f"[LANServer] on_pong raised: {e}")
            elif msg.get("type") == "action" and self.on_action is not None:
                self.on_action(msg, conn)

    def _prune_dead(self, dead_conns: list[socket.socket]) -> list[str]:
        if not dead_conns:
            return []
        with self._lock:
            dropped_roles = [r for c, r in self._clients if c in dead_conns]
            self._clients = [c for c in self._clients if c[0] not in dead_conns]
            for c in dead_conns:
                self._last_seen.pop(c, None)
        return dropped_roles

    def _fire_disconnect_callbacks(self, dropped_roles: list[str]) -> None:
        if self.on_client_dropped is not None:
            for r in dropped_roles:
                try:
                    self.on_client_dropped(r)
                except Exception as e:
                    print(f"[LANServer] on_client_dropped raised: {e}")
        for r in dropped_roles:
            if r in ("player1", "player2") and self.on_peer_disconnect is not None:
                try:
                    self.on_peer_disconnect()
                except Exception as e:
                    print(f"[LANServer] on_peer_disconnect raised: {e}")
                return

    def _broadcast_envelope(self, envelope: dict) -> None:
        with self._lock:
            snapshot = list(self._clients)
        dead: list[socket.socket] = []
        for conn, _role in snapshot:
            try:
                _send_msg(conn, envelope)
            except OSError as e:
                print(f"[LANServer] client dropped during broadcast: {e}")
                dead.append(conn)
        self._fire_disconnect_callbacks(self._prune_dead(dead))

    def _broadcast_per_client(self, build_envelope: Callable[[str], dict]) -> None:
        with self._lock:
            snapshot = list(self._clients)
        dead: list[socket.socket] = []
        for conn, role in snapshot:
            try:
                _send_msg(conn, build_envelope(role))
            except OSError as e:
                print(f"[LANServer] client dropped during broadcast: {e}")
                dead.append(conn)
        self._fire_disconnect_callbacks(self._prune_dead(dead))

    def broadcast_state(self, state_dict: dict) -> None:
        self._broadcast_envelope({"type": "state", "state": state_dict})

    def broadcast_state_for(self, state_for: Callable[[str], dict]) -> None:
        self._broadcast_per_client(
            lambda role: {"type": "state", "state": state_for(role)}
        )

    def broadcast_scene(self, scene: str, state_dict: dict) -> None:
        self._broadcast_envelope({
            "type": "scene",
            "scene": scene,
            "state": state_dict,
        })

    def broadcast_scene_for(self, scene: str, state_for: Callable[[str], dict]) -> None:
        self._broadcast_per_client(lambda role: {
            "type": "scene",
            "scene": scene,
            "state": state_for(role),
            "role": role,
        })

    def broadcast_game_over(self, winner: str, statistics: dict) -> None:
        self._broadcast_envelope({
            "type": "game_over",
            "winner": winner,
            "statistics": statistics,
        })
    
    def broadcast_log_files(self, log_name: str, log_b64: str,
                        jsonl_name: str, jsonl_b64: str) -> None:
        self._broadcast_envelope({
            "type": "log_transfer",
            "log_file":   {"name": log_name,   "data": log_b64},
            "jsonl_file": {"name": jsonl_name, "data": jsonl_b64},
        })

    def count_spectators(self) -> int:
        with self._lock:
            return sum(1 for _c, r in self._clients if r in ("spectator", "god"))

    def broadcast_net_info(self, spectator_count: int, latencies: dict) -> None:
        self._broadcast_envelope({
            "type": "net_info",
            "spectator_count": spectator_count,
            "latencies": latencies,
        })

    def broadcast_ping(self) -> None:
        ts = time.monotonic()
        with self._lock:
            snapshot = list(self._clients)
        dead: list[socket.socket] = []
        for conn, _role in snapshot:
            try:
                _send_msg(conn, {"type": "ping", "ts": ts})
            except OSError:
                dead.append(conn)
        if dead:
            self._fire_disconnect_callbacks(self._prune_dead(dead))

    def check_heartbeat(self, timeout: float = 10.0) -> None:
        now = time.monotonic()
        with self._lock:
            snapshot = list(self._clients)
            last_seen_snap = dict(self._last_seen)
        for conn, _role in snapshot:
            last = last_seen_snap.get(conn)
            if last is not None and now - last > timeout:
                print(f"[LANServer] heartbeat timeout, closing stale connection")
                try:
                    conn.close()
                except OSError:
                    pass

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False

        if self._server_sock:
            try:
                self._server_sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self._server_sock.close()
            except OSError:
                pass
            self._server_sock = None

        if self._accept_thread is not None:
            self._accept_thread.join(timeout=2.0)
            self._accept_thread = None

        with self._lock:
            for conn, _role in self._clients:
                try:
                    conn.close()
                except OSError:
                    pass
            self._clients.clear()
            self._last_seen.clear()

