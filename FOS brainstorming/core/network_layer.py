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
import secrets
import socket
import struct
import threading
from typing import Callable, Optional


def _recv_exactly(sock: socket.socket, n: int) -> Optional[bytes]:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _send_msg(sock: socket.socket, payload: dict) -> None:
    data = json.dumps(payload).encode()
    sock.sendall(struct.pack(">I", len(data)) + data)


def _recv_msg(sock: socket.socket) -> Optional[dict]:
    raw_len = _recv_exactly(sock, 4)
    if raw_len is None:
        return None
    length = struct.unpack(">I", raw_len)[0]
    raw_data = _recv_exactly(sock, length)
    if raw_data is None:
        return None
    return json.loads(raw_data.decode())


class LANServer:
    def __init__(self, version: str, host: str = "0.0.0.0", port: int = 5555,
                 god_view: bool = False, host_seat: str = "player1"):
        self.version = version
        self.host = host
        self.port = port
        self.god_view = god_view
        self.host_seat = host_seat
        self.scene: str = ""

        self.on_action: Optional[Callable[[dict], None]] = None
        self.on_client_connect: Optional[Callable[[str], dict]] = None
        self.on_peer_disconnect: Optional[Callable[[], None]] = None
        self.on_peer_reconnect: Optional[Callable[[], None]] = None
        self.on_client_dropped: Optional[Callable[[str], None]] = None

        self._clients: list[tuple[socket.socket, str]] = []
        self._peer_token: Optional[str] = None
        self._lock = threading.Lock()
        self._server_sock: Optional[socket.socket] = None
        self._running = False

    def set_scene(self, scene: str) -> None:
        self.scene = scene

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

    def find_role(self, conn: socket.socket) -> str:
        with self._lock:
            return next((r for c, r in self._clients if c is conn), "")

    def reassign_role(self, conn: socket.socket, new_role: str) -> bool:
        """Update the role label for a connected client. Returns True on success."""
        with self._lock:
            for i, (c, _r) in enumerate(self._clients):
                if c is conn:
                    self._clients[i] = (c, new_role)
                    return True
        return False

    def _decide_role(self, intent: str, token: Optional[str]) -> tuple[str, str]:
        """Returns (role, issued_token). issued_token is sent back in welcome."""
        peer_role = self.peer_seat()
        with self._lock:
            has_peer = any(role == peer_role for _conn, role in self._clients)
            valid_reconnect = (
                token is not None
                and self._peer_token is not None
                and token == self._peer_token
                and not has_peer
            )

        if valid_reconnect:
            return peer_role, self._peer_token  # type: ignore[return-value]

        if intent == "play" and not has_peer:
            new_token = secrets.token_urlsafe(16)
            self._peer_token = new_token
            return peer_role, new_token

        return ("god" if self.god_view else "spectator"), ""

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
            except OSError:
                conn.close()
                continue

            if hello is None or hello.get("type") != "hello":
                print(f"[LANServer] Bad hello from {addr}: {hello!r}")
                conn.close()
                continue

            intent = hello.get("intent", "play")
            token = hello.get("token")
            role, issued_token = self._decide_role(intent, token)
            is_reconnect = (role in ("player1", "player2")
                            and token is not None and token == issued_token)
            state = self.on_client_connect(role) if self.on_client_connect is not None else {}

            try:
                _send_msg(conn, {
                    "type": "welcome",
                    "role": role,
                    "state": state,
                    "version": self.version,
                    "scene": self.scene,
                    "token": issued_token,
                })
            except OSError:
                conn.close()
                continue

            with self._lock:
                self._clients.append((conn, role))
            print(f"[LANServer] Assigned role={role} to {addr} (reconnect={is_reconnect})")

            if is_reconnect and self.on_peer_reconnect is not None:
                try:
                    self.on_peer_reconnect()
                except Exception as e:
                    print(f"[LANServer] on_peer_reconnect raised: {e}")

            threading.Thread(
                target=self._client_loop, args=(conn, addr), daemon=True
            ).start()

    def _client_loop(self, conn: socket.socket, addr) -> None:
        while True:
            msg = _recv_msg(conn)
            if msg is None:
                print(f"[LANServer] Client disconnected: {addr}")
                with self._lock:
                    dropped_role = next((r for c, r in self._clients if c is conn), "")
                    self._clients = [c for c in self._clients if c[0] is not conn]
                try:
                    conn.close()
                except OSError:
                    pass
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
            if msg.get("type") == "action" and self.on_action is not None:
                self.on_action(msg)

    def _prune_dead(self, dead_conns: list[socket.socket]) -> list[str]:
        if not dead_conns:
            return []
        with self._lock:
            dropped_roles = [r for c, r in self._clients if c in dead_conns]
            self._clients = [c for c in self._clients if c[0] not in dead_conns]
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

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False

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
            self._accept_thread.join(timeout=0.3)
            self._accept_thread = None
        
class LANClient:
    def __init__(self, version: str, host: str, port: int = 5555):
        self.version = version
        self.host = host
        self.port = port
        self.on_state_update: Optional[Callable[[dict], None]] = None

        self._sock: Optional[socket.socket] = None
        self.role: str = ""
        self.scene: str = ""
        self.initial_state: dict = {}
        self.token: str = ""
        self.is_disconnected: bool = False
        self._intent: str = "play"

        self.pending_scene: Optional[str]  = None
        self.pending_scene_state: Optional[dict] = None
        self.pending_winner: Optional[str]  = None
        self.pending_statistics: Optional[dict] = None

    @property
    def is_connected(self) -> bool:
        return self._sock is not None

    def connect(self, timeout: float = 5.0, intent: str = "play") -> tuple[str, dict]:
        if self._sock is not None:
            return self.role, self.initial_state

        self._intent = intent
        return self._do_handshake(timeout=timeout, intent=intent, token=None)

    def try_reconnect(self, timeout: float = 5.0) -> bool:
        """Returns True if reconnect succeeded with the same role."""
        if self._sock is not None:
            return True
        if not self.token:
            return False
        try:
            role, _ = self._do_handshake(timeout=timeout, intent=self._intent, token=self.token)
        except (OSError, RuntimeError, ConnectionError) as e:
            print(f"[LANClient] reconnect failed: {e}")
            return False
        return role == "player2"

    def _do_handshake(self, timeout: float, intent: str, token: Optional[str]) -> tuple[str, dict]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((self.host, self.port))
        sock.settimeout(None)

        hello = {"type": "hello", "intent": intent, "version": self.version}
        if token:
            hello["token"] = token
        try:
            _send_msg(sock, hello)
        except OSError:
            sock.close()
            raise

        welcome = _recv_msg(sock)

        if not welcome or welcome.get("type") != "welcome":
            sock.close()
            raise RuntimeError(f"Handshake failed: expected welcome, got {welcome!r}")

        if welcome.get("version") != self.version:
            sock.close()
            raise ConnectionError(f"Version mismatch detected"
                                  f"Server requires {welcome.get('version')}, but client is running {self.version}")

        self._sock = sock
        self.role = welcome["role"]
        self.scene = welcome.get("scene", "")
        self.initial_state = welcome.get("state", {})
        new_token = welcome.get("token", "")
        if new_token:
            self.token = new_token
        self.is_disconnected = False

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
                msg = _recv_msg(sock)
            except (OSError, ValueError):
                break
            if msg is None:
                break

            try:
                mtype = msg.get("type")
                if mtype == "state":
                    print(f"[LANClient] received state envelope")
                    if self.on_state_update is not None:
                        self.on_state_update(msg["state"])
                elif mtype == "scene":
                    self.pending_scene = msg["scene"]
                    self.pending_scene_state = msg.get("state", {})
                elif mtype == "game_over":
                    self.pending_winner = msg["winner"]
                    self.pending_statistics = msg.get("statistics", {})
                elif mtype == "log_transfer":
                    self._save_transferred_logs(msg)
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
            try:
                sock.close()
            except OSError:
                pass
            self._sock = None
            print(f"[LANClient] socket disconnected")

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
        out_dir = Path(__file__).resolve().parent.parent / "battle_records"
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

    def send_action(self, action_dict: dict) -> None:
        if self._sock is None:
            return
        _send_msg(self._sock, {"type": "action", **action_dict})

    def disconnect(self) -> None:
        sock = self._sock
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