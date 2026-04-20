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

from typing import Optional

from core.setting import VERSION
from core.game_state import GameState
from core.draft_state import DraftState
from core.game_screen import GameScreen
from core.network_layer import LANClient, LANServer
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral
from core.scene_exit import DraftExitReason

from screens import start_screen, join_screen, replay_select
from screens.draft import draft
from screens.end_game import end_game
from screens.battling import battling, battling_replay

from utils.logger import GameLogger

from cards import (
    base, card_red, card_blue, card_cyan, card_dark_green, card_fuchsia,
    card_green, card_orange, card_purple, card_white,
)


DEFAULT_PORT = 5555


def _build_game_state_from_draft(draft_state: DraftState) -> GameState:
    player1 = Player(name="player1", deck=draft_state.player1_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=draft_state.player2_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    game_state = GameState(player1, player2, neutral, BoardConfig())
    game_state.timer_mode = draft_state.timer_mode
    game_state.file_auto_delete = draft_state.file_auto_delete

    game_state.game_logger.info(f"player1 deck {'-'.join(player1.deck)}")
    game_state.game_logger.info(f"player2 deck {'-'.join(player2.deck)}")
    game_state.game_logger.info(f"timer mode {game_state.timer_mode}")
    game_state.game_logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)
    game_state.game_logger.info(f"version {VERSION}", version=VERSION)
    return game_state


def _build_game_state_for_client() -> GameState:
    player1 = Player(name="player1", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()
    
    silent_logger = GameLogger(enable_file=False, enable_console=True, enable_jsonl=False)

    game_state = GameState(player1, player2, neutral, BoardConfig(), game_logger=silent_logger)
    
    return game_state

def _broadcast_log_backup(game_state: GameState, server: LANServer) -> None:
    import base64
    logger = game_state.game_logger
    log_path = logger.log_file
    jsonl_path = logger._jsonl_path
    if log_path is None or jsonl_path is None:
        return
    
    logger.close()
    try:
        log_b64 = base64.b64encode(log_path.read_bytes()).decode("ascii")
        jsonl_b64 = base64.b64encode(jsonl_path.read_bytes()).decode("ascii")
    except OSError as e:
        print(f"[main] failed to read log files for backup: {e}")
        return
    server.broadcast_log_files(log_path.name, log_b64, jsonl_path.name, jsonl_b64)


def _finalize_battle(game_state: GameState, game_screen: GameScreen, winner: str, server: Optional[LANServer] = None) -> None:
    game_state.player_timer["player1"] = game_state.player1.time_minutes_and_seconds
    game_state.player_timer["player2"] = game_state.player2.time_minutes_and_seconds

    game_state.game_logger.info(f"winner {winner}")
    game_state.game_logger.info(f"player1 timer {game_state.player1.time_minutes_and_seconds}")
    game_state.game_logger.info(f"player2 timer {game_state.player2.time_minutes_and_seconds}")
    game_state.game_logger.info(f"{game_state.game_statistics.export_for_charts()}")
    game_state.game_logger.info(f"{game_state.game_statistics.score_history}")


    if server is not None:
        _broadcast_log_backup(game_state, server)

    end_game.main(winner, game_state, game_screen)


def main() -> None:
    game_screen = GameScreen()

    while True:
        mode = start_screen.main(game_screen)

        if mode in ("quit", None):
            return
        
        server: Optional[LANServer] = None
        client: Optional[LANClient] = None
        match mode:
            case "local":
                exit_reason: DraftExitReason = draft.main(game_screen, mode="local")
                if exit_reason.kind != "finished" or exit_reason.draft_state is None:
                    continue
                game_state = _build_game_state_from_draft(exit_reason.draft_state)
                winner = battling.main(game_state, game_screen, mode="local")

                # for testing
                # game_state.game_statistics._stats = {StatType.CARD_USE: {'player1': 6, 'player2': 7}, StatType.HIT: {'player1_ASSW': 2, 'player2_ADCW': 1, 'player1_ADCW': 1, 'player2_HFW': 1, 'player2_ASSW': 1}, StatType.DAMAGE_DEALT: {'player1_ASSW': 7, 'player2_ADCW': 7, 'player1_ADCW': 1, 'player2_HFW': 4, 'player2_ASSW': 10}, StatType.DAMAGE_TAKEN: {'player2_LFW': 7, 'player1_SPW': 1, 'player1_ASSW': 4, 'player1_TANKW': 11, 'player2_SPW': 1, 'player1_ADCW': 5}, StatType.DAMAGE_TAKEN_COUNT: {'player2_LFW': 4, 'player1_SPW': 2, 'player1_ASSW': 4, 'player1_TANKW': 6, 'player2_SPW': 2, 'player1_ADCW': 2}, StatType.SCORED: {'player1_SPW': 2, 'player2_ADCW': 6, 'player2_LFW': 0, 'player2_APTW': 6, 'player1_ASSW': 4, 'player1_TANKW': 8, 'player2_HFW': 5, 'player2_SPW': 2, 'player1_ADCW': 1, 'player2_ASSW': 4, 'player2_APW': 3}, StatType.ABILITY: {}, StatType.HEALING: {}, StatType.HEAL_USE: {}, StatType.MOVE: {}, StatType.MOVE_USE: {}, StatType.CUBE_USE: {}, StatType.KILLED: {'player1_ASSW': 1, 'player2_ADCW': 2, 'player1_ADCW': 1, 'player2_HFW': 1, 'player2_ASSW': 1}, StatType.DEATH: {'player2_LFW': 1, 'player1_SPW': 1, 'player1_ASSW': 2, 'player2_SPW': 1, 'player1_ADCW': 1}, StatType.TOKEN_USE: {}, StatType.ROUNDS_SURVIVED: {'player1_SPW': 1, 'player2_ADCW': 6, 'player2_APTW': 6, 'player1_ASSW': 2, 'player1_TANKW': 8, 'player2_HFW': 5, 'player2_SPW': 1, 'player1_ADCW': 1, 'player2_ASSW': 3, 'player2_APW': 3}}
                
                if winner not in ("None", ""):
                    _finalize_battle(game_state, game_screen, winner)
            case "host":
                try:
                    server = LANServer(VERSION, port=DEFAULT_PORT)
                    exit_reason = draft.main(game_screen, mode="lan_server", server=server)
                    if exit_reason.kind != "finished" or exit_reason.draft_state is None:
                        server.stop()
                        continue
                    game_state = _build_game_state_from_draft(exit_reason.draft_state)
                    winner = battling.main(
                        game_state, game_screen,
                        mode="lan_server", server=server,
                    )
                    if winner not in ("None", ""):
                        _finalize_battle(game_state, game_screen, winner, server)
                finally:
                    if server is not None:
                        server.stop()
            case "join":
                try:
                    host_ip = join_screen.main(game_screen)
                    if not host_ip:
                        continue
                    client = LANClient(VERSION, host_ip, port=DEFAULT_PORT)
                    try:
                        exit_reason = draft.main(game_screen, mode="lan_client", client=client)
                    except (ConnectionRefusedError, RuntimeError, OSError) as e:
                        print(f"[main] Failed to join {host_ip}: {e}")
                        continue
                    if exit_reason.kind == "scene_handoff":
                        game_state = _build_game_state_for_client()
                        winner = battling.main(
                            game_state, game_screen,
                            mode="lan_client", client=client, initial_state_dict=exit_reason.next_scene_state
                        )
                        if winner not in ("None", ""):
                            _finalize_battle(game_state, game_screen, winner)
                finally:
                    if client is not None:
                        client.disconnect()
            case "playback":
                replay_path = replay_select.main(game_screen)
                if replay_path is None:
                    continue
                game_state = battling_replay.main(game_screen, replay_path)

                if game_state:
                    _finalize_battle(game_state, game_screen, "player1" if game_state.score < 0 else "player2")
                continue
            case _:
                return
    


if __name__ == "__main__":
    main()