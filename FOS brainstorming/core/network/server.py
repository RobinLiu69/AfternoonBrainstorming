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

from core.network.messages import _recv_msg, _send_msg
from core.network.roster import Roster, SEATS


SOCKET_TIMEOUT_SECONDS: float = 5.0
LISTEN_BACKLOG: int = 32


def _tune(conn: socket.socket) -> None:
    try:
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except OSError:
        pass
    conn.settimeout(SOCKET_TIMEOUT_SECONDS)


class LANServer:
    def __init__(self, version: str, host: str = "0.0.0.0", port: int = 5555,
                 god_view: bool = False, host_seat: str = "player1",
                 heartbeat_interval: float = 1.0, heartbeat_timeout: float = 10.0):
        self.version = version
        self.host = host
        self.port = port
        self.roster = Roster(host_seat=host_seat, god_view=god_view)
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

        self._lock = threading.Lock()
        self._write_locks: dict[socket.socket, threading.Lock] = {}
        self._server_sock: Optional[socket.socket] = None
        self._accept_thread: Optional[threading.Thread] = None
        self._running = False

    @staticmethod
    def _force_close(conn: socket.socket) -> None:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            conn.close()
        except OSError:
            pass

    def _write_lock_for(self, conn: socket.socket) -> threading.Lock:
        with self._lock:
            lock = self._write_locks.get(conn)
            if lock is None:
                lock = threading.Lock()
                self._write_locks[conn] = lock
            return lock

    def _forget(self, conn: socket.socket) -> None:
        self._last_seen.pop(conn, None)
        self._write_locks.pop(conn, None)

    def _send_locked(self, conn: socket.socket, payload: dict) -> None:
        with self._write_lock_for(conn):
            _send_msg(conn, payload)

    def send_to(self, conn: socket.socket, payload: dict) -> bool:
        try:
            self._send_locked(conn, payload)
        except OSError:
            return False
        return True

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

    def reset_heartbeat(self) -> None:
        now = time.monotonic()
        with self._lock:
            for conn, _role in self.roster.members():
                self._last_seen[conn] = now

    def find_role(self, conn: socket.socket) -> str:
        return self.roster.role_of(conn)

    def _decide_role(self, intent: str, token: Optional[str]) -> tuple[str, str]:
        role, issued_token, evicted = self.roster.claim(
            intent, token, in_lobby=self.scene == "lobby")
        with self._lock:
            for conn in evicted:
                self._forget(conn)
        for conn in evicted:
            self._force_close(conn)
        return role, issued_token

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(LISTEN_BACKLOG)
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
            threading.Thread(target=self._greet, args=(conn, addr), daemon=True).start()

    def _greet(self, conn: socket.socket, addr) -> None:
        try:
            _tune(conn)
            hello = _recv_msg(conn)
        except (OSError, ValueError):
            self._force_close(conn)
            return

        if hello is None or hello.get("type") != "hello":
            print(f"[LANServer] Bad hello from {addr}: {hello!r}")
            self._force_close(conn)
            return

        try:
            self.handle_connection(conn, addr, hello)
        except Exception as e:
            print(f"[LANServer] handshake failed for {addr}: {e}")
            self._force_close(conn)

    def _fire(self, name: str, *args):
        callback = getattr(self, name)
        if callback is None:
            return None
        try:
            return callback(*args)
        except Exception as e:
            print(f"[LANServer] {name} raised: {e}")
            raise

    def _reject_version(self, conn: socket.socket, addr, client_version: str) -> None:
        try:
            self._send_locked(conn, {
                "type": "rejected",
                "reason": "version_mismatch",
                "server_version": self.version,
                "client_version": client_version,
            })
        except OSError:
            pass
        conn.close()
        print(f"[LANServer] Rejected {addr}: version mismatch "
              f"(client={client_version!r}, server={self.version!r})")

    def handle_connection(self, conn: socket.socket, addr, hello: dict) -> None:
        if not self._running:
            self._force_close(conn)
            print(f"[LANServer] Refused {addr}: server is shutting down")
            return

        client_version = hello.get("version", "")
        if client_version != self.version:
            self._reject_version(conn, addr, client_version)
            return

        token = hello.get("token")
        role, issued_token = self._decide_role(hello.get("intent", "play"), token)
        is_reconnect = (role in SEATS and token is not None and token == issued_token)

        try:
            if role in SEATS:
                self._fire("on_peer_reconnect")
            state = self._fire("on_client_connect", role) or {}
        except Exception:
            self.roster.release(role)
            self._force_close(conn)
            return

        try:
            self._send_locked(conn, {
                "type": "welcome",
                "role": role,
                "state": state,
                "version": self.version,
                "scene": self.scene,
                "token": issued_token,
                "room": self.room_code,
            })
        except OSError:
            self.roster.release(role)
            conn.close()
            return

        self.roster.add(conn, role)
        self._touch(conn)
        print(f"[LANServer] Assigned role={role} to {addr} (reconnect={is_reconnect})")

        threading.Thread(
            target=self._client_loop, args=(conn, addr), daemon=True
        ).start()

    def _touch(self, conn: socket.socket) -> None:
        with self._lock:
            self._last_seen[conn] = time.monotonic()

    def _client_gone(self, conn: socket.socket, addr) -> None:
        print(f"[LANServer] Client disconnected: {addr}")
        dropped_role, was_evicted = self.roster.drop(conn)
        with self._lock:
            self._forget(conn)
        try:
            conn.close()
        except OSError:
            pass
        if was_evicted:
            return
        try:
            self._fire("on_client_dropped", dropped_role)
        except Exception:
            pass
        if dropped_role in SEATS:
            try:
                self._fire("on_peer_disconnect")
            except Exception:
                pass

    def _handle_message(self, conn: socket.socket, msg: dict) -> None:
        match msg.get("type"):
            case "pong":
                rtt_ms = (time.monotonic() - msg.get("ts", 0.0)) * 1000.0
                self.send_to(conn, {"type": "ping_result", "ms": round(rtt_ms, 1)})
                try:
                    self._fire("on_pong", self.find_role(conn), rtt_ms)
                except Exception:
                    pass
            case "action":
                try:
                    self._fire("on_action", msg, conn)
                except Exception:
                    pass
                finally:
                    seq = msg.get("seq")
                    if seq is not None:
                        self.send_to(conn, {"type": "ack", "seq": seq})

    def _client_loop(self, conn: socket.socket, addr) -> None:
        while True:
            try:
                msg = _recv_msg(conn, on_idle=lambda: self._running)
            except (OSError, ValueError):
                msg = None
            if msg is None:
                self._client_gone(conn, addr)
                return
            self._touch(conn)
            self._handle_message(conn, msg)

    def _prune_dead(self, dead_conns: list[socket.socket]) -> list[str]:
        if not dead_conns:
            return []
        dropped_roles = self.roster.drop_many(dead_conns)
        with self._lock:
            for c in dead_conns:
                self._forget(c)
        return dropped_roles

    def _fire_disconnect_callbacks(self, dropped_roles: list[str]) -> None:
        if self.on_client_dropped is not None:
            for r in dropped_roles:
                try:
                    self.on_client_dropped(r)
                except Exception as e:
                    print(f"[LANServer] on_client_dropped raised: {e}")
        for r in dropped_roles:
            if r in SEATS and self.on_peer_disconnect is not None:
                try:
                    self.on_peer_disconnect()
                except Exception as e:
                    print(f"[LANServer] on_peer_disconnect raised: {e}")
                return

    def _broadcast_envelope(self, envelope: dict) -> None:
        snapshot = self.roster.members()
        dead: list[socket.socket] = []
        for conn, _role in snapshot:
            try:
                self._send_locked(conn, envelope)
            except OSError as e:
                print(f"[LANServer] client dropped during broadcast: {e}")
                dead.append(conn)
        self._fire_disconnect_callbacks(self._prune_dead(dead))

    def _broadcast_per_client(self, build_envelope: Callable[[str], dict]) -> None:
        snapshot = self.roster.members()
        dead: list[socket.socket] = []
        for conn, role in snapshot:
            try:
                self._send_locked(conn, build_envelope(role))
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
        return self.roster.count_watchers()

    def broadcast_net_info(self, spectator_count: int, latencies: dict) -> None:
        self._broadcast_envelope({
            "type": "net_info",
            "spectator_count": spectator_count,
            "latencies": latencies,
        })

    def broadcast_ping(self) -> None:
        ts = time.monotonic()
        snapshot = self.roster.members()
        dead: list[socket.socket] = []
        for conn, _role in snapshot:
            try:
                self._send_locked(conn, {"type": "ping", "ts": ts})
            except OSError:
                dead.append(conn)
        if dead:
            self._fire_disconnect_callbacks(self._prune_dead(dead))

    def check_heartbeat(self, timeout: float = 10.0) -> None:
        now = time.monotonic()
        snapshot = self.roster.members()
        with self._lock:
            last_seen_snap = dict(self._last_seen)
        for conn, _role in snapshot:
            last = last_seen_snap.get(conn)
            if last is not None and now - last > timeout:
                print(f"[LANServer] heartbeat timeout, closing stale connection")
                self._force_close(conn)

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

        conns = self.roster.clear()
        with self._lock:
            self._last_seen.clear()
            self._write_locks.clear()
        for conn in conns:
            self._force_close(conn)

