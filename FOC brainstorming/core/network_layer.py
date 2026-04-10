import json
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
    def __init__(self, version: str, host: str = "0.0.0.0", port: int = 5555):
        self.version = version
        self.host = host
        self.port = port

        self.on_action: Optional[Callable[[dict], None]] = None
        self.on_client_connect: Optional[Callable[[], tuple[str, dict]]] = None

        self._clients: list[socket.socket] = []
        self._lock = threading.Lock()
        self._server_sock: Optional[socket.socket] = None
        self._running = False

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

            if self.on_client_connect is not None:
                role, state = self.on_client_connect()
            else:
                role, state = "player2", {}
            try:
                _send_msg(conn, {"type": "welcome", "role": role, "state": state, "version": self.version})
            except OSError:
                conn.close()
                continue

            with self._lock:
                self._clients.append(conn)
            threading.Thread(
                target=self._client_loop, args=(conn, addr), daemon=True
            ).start()

    def _client_loop(self, conn: socket.socket, addr) -> None:
        while True:
            msg = _recv_msg(conn)
            if msg is None:
                print(f"[LANServer] Client disconnected: {addr}")
                with self._lock:
                    if conn in self._clients:
                        self._clients.remove(conn)
                try:
                    conn.close()
                except OSError:
                    pass
                break
            if msg.get("type") == "action" and self.on_action is not None:
                self.on_action(msg)

    def _broadcast_envelope(self, envelope: dict) -> None:
        with self._lock:
            dead: list[socket.socket] = []
            for conn in self._clients:
                try:
                    _send_msg(conn, envelope)
                except OSError:
                    dead.append(conn)
            for conn in dead:
                self._clients.remove(conn)

    def broadcast_state(self, state_dict: dict) -> None:
        self._broadcast_envelope({"type": "state", "state": state_dict})

    def broadcast_scene(self, scene: str, state_dict: dict) -> None:
        self._broadcast_envelope({
            "type": "scene",
            "scene": scene,
            "state": state_dict,
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
            for conn in self._clients:
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
        self.initial_state: dict = {}

        self.pending_scene: Optional[str]  = None
        self.pending_scene_state: Optional[dict] = None
        self.pending_winner: Optional[str]  = None
        self.pending_statistics: Optional[dict] = None

    @property
    def is_connected(self) -> bool:
        return self._sock is not None

    def connect(self, timeout: float = 5.0) -> tuple[str, dict]:
        if self._sock is not None:
            return self.role, self.initial_state

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((self.host, self.port))
        sock.settimeout(None)

        welcome = _recv_msg(sock)
        
        
        if not welcome or welcome.get("type") != "welcome":
            sock.close()
            raise RuntimeError(f"Handshake failed: expected welcome, got {welcome!r}")

        if welcome.get("version") != self.version:
            raise ConnectionError(f"Version mismatch detected"
                                  f"Server requires {welcome.get("version")}, but client is running {self.version}")
        
        self._sock = sock
        self.role = welcome["role"]
        self.initial_state = welcome.get("state", {})

        threading.Thread(target=self._recv_loop, daemon=True).start()
        print(f"[LANClient] Connected to {self.host}:{self.port} as {self.role}")
        return self.role, self.initial_state

    def _recv_loop(self) -> None:
        sock = self._sock
        if sock is None:
            return
        while True:
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
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None