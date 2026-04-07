from typing import Optional

from core.game_state import GameState
from core.draft_state import DraftState
from core.game_screen import GameScreen
from core.network_layer import LANClient, LANServer
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral
from core.scene_exit import DraftExitReason

from screens import start_screen, join_screen
from screens.draft import draft
from screens.end_game import end_game
from screens.battling import battling

from cards import (
    base, card_red, card_blue, card_cyan, card_dark_green, card_fuchsia,
    card_green, card_orange, card_purple, card_white,
)


DEFAULT_PORT = 5555


def _build_game_state_from_draft(draft_state: DraftState) -> GameState:
    """Host / local path: construct a fresh GameState from completed draft picks."""
    player1 = Player(name="player1", deck=draft_state.player1_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=draft_state.player2_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    game_state = GameState(player1, player2, neutral, BoardConfig())
    game_state.timer_mode = draft_state.timer_mode
    game_state.file_auto_delete = draft_state.file_auto_delete

    game_state.game_logger.info(f"player1 deck {'-'.join(player1.deck)}")
    game_state.game_logger.info(f"player2 deck {'-'.join(player2.deck)}")
    game_state.game_logger.info(f"timer mode {game_state.timer_mode}")
    return game_state


def _build_game_state_for_client() -> GameState:
    """Client path: empty stub. battling.main will overwrite via apply_dict."""
    player1 = Player(name="player1", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()
    return GameState(player1, player2, neutral, BoardConfig())


def _finalize_battle(game_state: GameState, game_screen: GameScreen, winner: str) -> None:
    game_state.player_timer["player1"] = game_state.player1.time_minutes_and_seconds
    game_state.player_timer["player2"] = game_state.player2.time_minutes_and_seconds

    game_state.game_logger.info(f"winner {winner}")
    game_state.game_logger.info(f"player1 timer {game_state.player1.time_minutes_and_seconds}")
    game_state.game_logger.info(f"player2 timer {game_state.player2.time_minutes_and_seconds}")
    game_state.game_logger.info(f"{game_state.game_statistics.export_for_charts()}")
    game_state.game_logger.info(f"{game_state.game_statistics.score_history}")

    end_game.main(winner, game_state, game_screen)


def main() -> None:
    game_screen = GameScreen()
    mode = start_screen.main(game_screen)

    server: Optional[LANServer] = None
    client: Optional[LANClient] = None
    # mode = "local"
    try:
        match mode:
            case "local":
                exit_reason: DraftExitReason = draft.main(game_screen, mode="local")
                if exit_reason.kind != "finished" or exit_reason.draft_state is None:
                    return
                game_state = _build_game_state_from_draft(exit_reason.draft_state)
                winner = battling.main(game_state, game_screen, mode="local")
                if winner not in ("None", ""):
                    _finalize_battle(game_state, game_screen, winner)
            case "host":
                server = LANServer(port=DEFAULT_PORT)
                exit_reason = draft.main(game_screen, mode="lan_server", server=server)
                if exit_reason.kind != "finished" or exit_reason.draft_state is None:
                    return
                game_state = _build_game_state_from_draft(exit_reason.draft_state)
                winner = battling.main(
                    game_state, game_screen,
                    mode="lan_server", server=server,
                )
                if winner not in ("None", ""):
                    _finalize_battle(game_state, game_screen, winner)
            case "join":
                host_ip = join_screen.main(game_screen)
                if not host_ip:
                    return
                client = LANClient(host_ip, port=DEFAULT_PORT)
                try:
                    exit_reason = draft.main(game_screen, mode="lan_client", client=client)
                except (ConnectionRefusedError, RuntimeError, OSError) as e:
                    print(f"[main] Failed to join {host_ip}: {e}")
                    return
                if exit_reason.kind == "scene_handoff":
                    game_state = _build_game_state_for_client()
                    winner = battling.main(
                        game_state, game_screen,
                        mode="lan_client", client=client, initial_state_dict=exit_reason.next_scene_state
                    )
                    if winner not in ("None", ""):
                        _finalize_battle(game_state, game_screen, winner)
            case "quit" | _:
                return
    finally:
        if server is not None:
            server.stop()
        if client is not None:
            client.disconnect()


if __name__ == "__main__":
    main()