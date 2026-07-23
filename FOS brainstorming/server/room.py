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

import base64
import threading
import time
import traceback
from typing import Callable, Optional

from shared.setting import VERSION
from core.lobby_state import LobbyState
from core.lobby_dispatcher import LobbyDispatcher
from core.draft_state import DraftState
from core.draft_dispatcher import DraftDispatcher
from core.battling_dispatcher import BattlingDispatcher
from core.game_state import GameState
from core.match_prelude import log_match_prelude
from core.player import Player
from core.neutral import Neutral
from core.board_config import BoardConfig
from utils.logger import GameLogger

from server.room_channel import RoomChannel
from server.headless import HeadlessRenderer, make_board_dict


TICK_SECONDS = 0.02
EMPTY_ROOM_TIMEOUT = 120.0
OWNER_ABSENT_TIMEOUT = 300.0


class RoomLobbyDispatcher(LobbyDispatcher):
    def __init__(self, lobby_state: LobbyState):
        super().__init__(lobby_state, mode="lan_server")

    def _on_client_connect(self, role: str) -> dict:
        if role in ("player1", "player2"):
            self._state.peer_connected = True
        elif role in ("spectator", "god"):
            self._state.spectator_count += 1
        welcome_state = self._state.to_dict_for(role)
        self._broadcast()
        return welcome_state


class Room:
    def __init__(self, code: str, version: str = VERSION,
                 on_close: Optional[Callable[["Room"], None]] = None):
        self.code = code
        self.on_close = on_close
        self.scene = "lobby"
        self.closed = False

        self.channel = RoomChannel(version, code)
        self.channel.start()

        self.lobby_state = LobbyState()
        self.lobby_state.room_code = code

        self.draft_state: Optional[DraftState] = None
        self.game_state: Optional[GameState] = None
        self.lobby_dispatcher: Optional[RoomLobbyDispatcher] = None
        self.draft_dispatcher: Optional[DraftDispatcher] = None
        self.battle_dispatcher: Optional[BattlingDispatcher] = None

        self.renderer = HeadlessRenderer()
        self._action_lock = threading.RLock()
        self._absent_seats: set[str] = set()
        self._empty_since: Optional[float] = None
        self._owner_absent_since: Optional[float] = None
        self._last_snapshot: Optional[tuple] = None
        self._secrets_logged = False
        self._close_event = threading.Event()

        self._enter_lobby()
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name=f"room-{code}")
        self._thread.start()

    def adopt_connection(self, conn, addr, hello: dict, creator: bool = False) -> None:
        if creator:
            self.channel.adopt_creator(conn, addr, hello)
        else:
            self.channel.handle_connection(conn, addr, hello)

    def close(self) -> None:
        self._close_event.set()

    def _run(self) -> None:
        try:
            while not self._close_event.is_set():
                match self.scene:
                    case "lobby":
                        self._tick_lobby()
                    case "draft":
                        self._tick_draft()
                    case "battling":
                        self._tick_battle()
                if self._room_abandoned():
                    print(f"[Room {self.code}] abandoned, closing")
                    break
                time.sleep(TICK_SECONDS)
        except Exception:
            print(f"[Room {self.code}] crashed:\n{traceback.format_exc()}")
        finally:
            self.closed = True
            if self.game_state is not None:
                self._log_match_secrets()
                self.game_state.game_logger.detach()
            self.channel.stop()
            if self.on_close is not None:
                try:
                    self.on_close(self)
                except Exception as e:
                    print(f"[Room {self.code}] on_close raised: {e}")
            print(f"[Room {self.code}] closed")

    def _room_abandoned(self) -> bool:
        now = time.monotonic()
        if self.channel.client_count() == 0:
            if self._empty_since is None:
                self._empty_since = now
            if now - self._empty_since > EMPTY_ROOM_TIMEOUT:
                return True
        else:
            self._empty_since = None

        if self.scene == "lobby":
            if self.channel.has_role("host"):
                self._owner_absent_since = None
            else:
                if self._owner_absent_since is None:
                    self._owner_absent_since = now
                if now - self._owner_absent_since > OWNER_ABSENT_TIMEOUT:
                    return True
        return False

    def _guard_actions(self) -> None:
        original = self.channel.on_action

        def locked_action(envelope: dict, conn) -> None:
            if original is None:
                return
            sender_role = self.channel.find_role(conn)
            if not sender_role or envelope.get("player") != sender_role:
                print(f"[Room {self.code}] dropped action from {sender_role!r} "
                      f"claiming to be {envelope.get('player')!r}")
                return
            with self._action_lock:
                original(envelope, conn)

        self.channel.on_action = locked_action

    def _wire_absence_tracking(self, dispatcher) -> None:
        original_connect = self.channel.on_client_connect

        def on_connect(role: str) -> dict:
            self._absent_seats.discard(role)
            state = original_connect(role) if original_connect is not None else {}
            if self._absent_seats:
                dispatcher._on_peer_disconnect()
            return state

        def on_dropped(role: str) -> None:
            if role in ("player1", "player2"):
                self._absent_seats.add(role)
                if isinstance(dispatcher, BattlingDispatcher):
                    remaining = "player2" if role == "player1" else "player1"
                    if remaining not in self._absent_seats:
                        dispatcher.host_seat = remaining

        self.channel.on_client_connect = on_connect
        self.channel.on_client_dropped = on_dropped

    def _enter_lobby(self) -> None:
        self.lobby_dispatcher = RoomLobbyDispatcher(self.lobby_state)
        self.lobby_dispatcher.attach_server(self.channel)
        self._guard_actions()

    def _tick_lobby(self) -> None:
        assert self.lobby_dispatcher is not None
        self.lobby_dispatcher.tick()
        if self.lobby_dispatcher.start_signal:
            self._start_draft()

    def _start_draft(self) -> None:
        host_seat = self.lobby_state.host_seat
        with self.channel._lock:
            owner_conn = next(
                (c for c, r in self.channel._clients if r == "host"), None)
        if owner_conn is not None:
            self.channel.reassign_role(owner_conn, host_seat)
        self.channel.move_token("host", host_seat)

        draft_state = DraftState()
        draft_state.settings = self.lobby_state.settings.copy()
        draft_state.init_ban_deck()
        draft_state.add_ban([c for c in self.lobby_state.bans
                             if not draft_state.is_banned(c)])
        draft_state.player_names = self.lobby_state.seat_names()
        self.draft_state = draft_state

        self.draft_dispatcher = DraftDispatcher(
            draft_state, mode="lan_server",
            reconnect_timeout=self.lobby_state.reconnect_timeout,
            host_seat=host_seat)
        self.draft_dispatcher.attach_server(self.channel)
        self._guard_actions()
        self._wire_absence_tracking(self.draft_dispatcher)

        self.scene = "draft"
        print(f"[Room {self.code}] match starting, entering draft")
        self.channel.broadcast_scene_for("draft", draft_state.to_dict_for)

    def _tick_draft(self) -> None:
        assert self.draft_dispatcher is not None and self.draft_state is not None
        self.channel.pulse()
        if self.draft_dispatcher.peer_lost:
            print(f"[Room {self.code}] player left during draft, closing")
            self._close_event.set()
            return
        if self.draft_state.phase == "done":
            self._start_battle()

    def _start_battle(self) -> None:
        assert self.draft_state is not None
        draft_state = self.draft_state

        player1 = Player(name="player1", deck=draft_state.player1_deck.copy(),
                         hand=[], on_board=[], draw_pile=[], discard_pile=[])
        player2 = Player(name="player2", deck=draft_state.player2_deck.copy(),
                         hand=[], on_board=[], draw_pile=[], discard_pile=[])
        neutral = Neutral()

        settings = draft_state.settings
        keep_files = not settings.file_auto_delete
        log_file = None
        if keep_files:
            from datetime import datetime
            from pathlib import Path
            from shared.setting import FOLDER_PATH
            stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file = Path(f"{FOLDER_PATH}/battle_records/{stamp}_room{self.code}.log")
        logger = GameLogger(enable_file=keep_files, enable_console=False,
                            enable_jsonl=keep_files, log_file=log_file)
        game_state = GameState(player1, player2, neutral, BoardConfig(),
                               game_logger=logger)
        game_state.board_dict = make_board_dict(game_state.board_config)
        self.game_state = game_state

        logger.info(f"room {self.code}")
        settings.apply_to(game_state)
        logger.info(f"version {VERSION}", version=VERSION)
        log_match_prelude(logger, self.lobby_state)
        self._log_match_secrets()

        self.battle_dispatcher = BattlingDispatcher(
            game_state=game_state, mode="lan_server",
            reconnect_timeout=self.lobby_state.reconnect_timeout,
            host_seat=self.lobby_state.host_seat)
        self.battle_dispatcher.attach_server(self.channel)
        self._guard_actions()
        self._wire_absence_tracking(self.battle_dispatcher)

        player1.initialize(game_state)
        player2.initialize(game_state)
        player1.timer_start(game_state)
        player2.timer_start(game_state)

        self.scene = "battling"
        self._last_snapshot = None
        print(f"[Room {self.code}] draft finished, battle starting")
        self.channel.broadcast_scene_for("battling", game_state.to_dict_for)
        game_state.game_logger.log_turn_start("player1", game_state.turn_number)

    @staticmethod
    def _snapshot(game_state: GameState) -> tuple:
        return (
            len(game_state.player1.hand),
            len(game_state.player2.hand),
            len(game_state.player1.draw_pile),
            len(game_state.player2.draw_pile),
            dict(game_state.card_to_draw),
            dict(game_state.players_token),
        )

    def _tick_battle(self) -> None:
        assert self.battle_dispatcher is not None and self.game_state is not None
        dispatcher = self.battle_dispatcher
        game_state = self.game_state

        self.channel.pulse()

        if dispatcher.pending_winner is not None:
            self._finish_battle(dispatcher.pending_winner)
            return

        if game_state.paused:
            return

        winner: Optional[str] = None
        with self._action_lock:
            controller = "player1" if game_state.turn_number % 2 == 0 else "player2"
            game_state.get_player(controller).logic_update(game_state, self.renderer, True)
            game_state.get_opponent(controller).logic_update(game_state, self.renderer, False)
            game_state.neutral.update(game_state, self.renderer)
            game_state.update()

            snapshot = self._snapshot(game_state)
            if snapshot != self._last_snapshot:
                self._last_snapshot = snapshot
                dispatcher._broadcast_state(game_state)

            if game_state.player1.time_out:
                winner = "player2"
            elif game_state.player2.time_out:
                winner = "player1"

        if winner is not None:
            dispatcher._broadcast_state(game_state)
            dispatcher._broadcast_game_over(winner, game_state)
            self._finish_battle(winner)

    def _log_match_secrets(self) -> None:
        if self.game_state is None or self._secrets_logged:
            return
        self._secrets_logged = True
        game_state = self.game_state
        logger = game_state.game_logger
        logger.info(f"player1 deck {'-'.join(game_state.player1.deck)}")
        logger.info(f"player2 deck {'-'.join(game_state.player2.deck)}")
        logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)

    def _finish_battle(self, winner: str) -> None:
        assert self.game_state is not None
        game_state = self.game_state
        logger = game_state.game_logger
        logger.info(f"winner {winner}")
        logger.info(f"player1 timer {game_state.player1.time_display}")
        logger.info(f"player2 timer {game_state.player2.time_display}")
        logger.info(f"{game_state.game_statistics.export_for_charts()}")
        logger.info(f"{game_state.game_statistics.score_history}")

        print(f"[Room {self.code}] game over, winner: {winner}")
        self._broadcast_log_backup()
        self._close_event.set()

    def _broadcast_log_backup(self) -> None:
        assert self.game_state is not None
        logger = self.game_state.game_logger
        log_path = logger.log_file
        jsonl_path = logger._jsonl_path
        logger.close()
        if log_path is None or jsonl_path is None:
            return
        try:
            log_b64 = base64.b64encode(log_path.read_bytes()).decode("ascii")
            jsonl_b64 = base64.b64encode(jsonl_path.read_bytes()).decode("ascii")
        except OSError as e:
            print(f"[Room {self.code}] failed to read log files for backup: {e}")
            return
        self.channel.broadcast_log_files(log_path.name, log_b64,
                                         jsonl_path.name, jsonl_b64)
