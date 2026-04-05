from core.game_state import GameState
from core.game_screen import GameScreen
from core.network_layer import LANClient, LANServer
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral

from screens import start_screen, battling, end_game
from screens.draft import draft
from screens.end_game import end_game
from screens.battling import battling

from cards import base, card_red, card_blue, card_cyan, card_dark_green, card_fuchsia, card_green, card_orange, card_purple, card_white


def main() -> None:
    game_screen = GameScreen()

    mode = start_screen.main(game_screen)

    match mode:
        case "host":
            draft_state = draft.main(game_screen)
            if draft_state:
                player1 = Player(name="player1", deck=draft_state.player1_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
                player2 = Player(name="player2", deck=draft_state.player2_deck.copy(), hand=[], on_board=[], draw_pile=[], discard_pile=[])
                neutral = Neutral()
                
                game_state = GameState(player1, player2, neutral, BoardConfig())

                game_state.timer_mode = draft_state.timer_mode
                game_state.file_auto_delete = draft_state.file_auto_delete
                
                game_state.game_logger.info(f"player1 deck {"-".join(player1.deck)}")
                game_state.game_logger.info(f"player2 deck {"-".join(player2.deck)}")
                
                game_state.game_logger.info(f"timer mode {game_state.timer_mode}")
                

                winner = battling.main(game_state, game_screen)
                
                game_state.player_timer["player1"] = player1.time_minutes_and_seconds
                game_state.player_timer["player2"] = player2.time_minutes_and_seconds
                
                game_state.game_logger.info(f"winner {winner}")
                
                game_state.game_logger.info(f"player1 timer {player1.time_minutes_and_seconds}")
                game_state.game_logger.info(f"player2 timer {player2.time_minutes_and_seconds}")
                
                game_state.game_logger.info(f"{game_state.game_statistics.export_for_charts()}")
                game_state.game_logger.info(f"{game_state.game_statistics.score_history}")
                if game_state:
                    end_game.main(winner, game_state, game_screen)
            else:
                winner = "quit"


        case "join":
            pass
        case "quit":
            pass
    
if __name__ == "__main__":
    main()