"""
----------------
Thin TCP transport for LAN draft sessions.

Wire format (both directions):
    [4 bytes big-endian length][UTF-8 JSON payload]

Server  → Client : full DraftState dict after every action
Client  → Server : DraftAction dict
"""
import json
import socket
import zlib
import struct
import threading
from typing import Callable, Optional


def _recv_exactly(sock: socket.socket, n: int) -> Optional[bytes]:
    """Read exactly n bytes, or return None on disconnect."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _send_msg(sock: socket.socket, payload: dict) -> None:
    """Send a length-prefixed JSON message."""
    data = json.dumps(payload).encode()
    
    print(data)
    sock.sendall(struct.pack(">I", len(data)) + data)
 
 
def _recv_msg(sock: socket.socket) -> Optional[dict]:
    """Receive a length-prefixed JSON message. Returns None on disconnect."""
    raw_len = _recv_exactly(sock, 4)
    if raw_len is None:
        return None
    length = struct.unpack(">I", raw_len)[0]
    raw_data = _recv_exactly(sock, length)
    if raw_data is None:
        return None
    
    print(json.loads(raw_data.decode()))
    return json.loads(raw_data.decode())


class LANServer:
    """
    Run on the host machine (lan_server mode).

    Usage:
        server = LANServer()
        dispatcher.attach_server(server)
        server.start()          # non-blocking; accepts clients in background
        ...
        server.stop()
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5555):
        self.host = host
        self.port = port
        # Called with a dict whenever a client sends an action.
        self.on_action: Optional[Callable[[dict], None]] = None

        self._clients: list[socket.socket] = []
        self._lock = threading.Lock()
        self._server_sock: Optional[socket.socket] = None

    def start(self) -> None:
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(2)
        threading.Thread(target=self._accept_loop, daemon=True).start()
        print(f"[LANServer] Listening on {self.host}:{self.port}")

    def _accept_loop(self) -> None:
        if not self._server_sock: return
        while True:
            try:
                conn, addr = self._server_sock.accept()
                print(f"[LANServer] Client connected: {addr}")
                with self._lock:
                    self._clients.append(conn)
                threading.Thread(
                    target=self._client_loop, args=(conn, addr), daemon=True
                ).start()
            except OSError:
                break

    def _client_loop(self, conn: socket.socket, addr) -> None:
        while True:
            msg = _recv_msg(conn)
            if msg is None:
                print(f"[LANServer] Client disconnected: {addr}")
                with self._lock:
                    if conn in self._clients:
                        self._clients.remove(conn)
                break
            if self.on_action:
                self.on_action(msg)

    def broadcast(self, state_dict: dict) -> None:
        """Push updated DraftState to all connected clients."""
        with self._lock:
            dead = []
            for conn in self._clients:
                try:
                    _send_msg(conn, state_dict)
                except OSError:
                    dead.append(conn)
            for conn in dead:
                self._clients.remove(conn)

    def stop(self) -> None:
        if self._server_sock:
            self._server_sock.close()


class LANClient:
    """
    Run on the guest machine (lan_client mode).

    Usage:
        client = LANClient("192.168.x.x")
        dispatcher.attach_client(client)
        client.on_state_update = my_render_callback   # optional push handler
        client.connect()
        ...
        client.disconnect()
    """

    def __init__(self, host: str, port: int = 5555):
        self.host = host
        self.port = port
        # Called with a state dict whenever the server pushes an update.
        self.on_state_update: Optional[Callable[[dict], None]] = None

        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        threading.Thread(target=self._recv_loop, daemon=True).start()
        print(f"[LANClient] Connected to {self.host}:{self.port}")

    def _recv_loop(self) -> None:
        if not self._sock: return
        """Background thread: receive pushed state updates from the server."""
        while True:
            msg = _recv_msg(self._sock)
            if msg is None:
                print("[LANClient] Disconnected from server.")
                break
            if self.on_state_update:
                self.on_state_update(msg)

    def send_action(self, action_dict: dict) -> None:
        if self._sock:
            _send_msg(self._sock, action_dict)

    def disconnect(self) -> None:
        if self._sock:
            self._sock.close()