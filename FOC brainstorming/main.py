import datetime, os

from core.game_state import GameState
from core.game_screen import GameScreen
from core.board_config import BoardConfig
from core.player import Player
from core.neutral import Neutral

from screens import start_screen, menu, battling, end_game #, playback


def main() -> None:
    player1 = Player(name="player1", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()

    game_screen = GameScreen()

    game_state = GameState(player1, player2, neutral, game_screen, BoardConfig())

    mode = start_screen.main(game_state)

    match mode:
        case "start":
            if menu.main(game_state):
                if player1.deck == [] and player2.deck == []:
                    player1.deck = ['TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG', 'TANKDKG']
                    player2.deck = ['LFDKG', 'LFDKG', 'ASSDKG', 'ASSDKG', 'CUBES', 'CUBES', 'CUBES', 'ASSP', 'ASSP', 'SPDKG', 'HFR', 'HFR']

                game_state.game_logger.info(f"player1 deck {"-".join(player1.deck)}")
                game_state.game_logger.info(f"player2 deck {"-".join(player2.deck)}")
                
                game_state.game_logger.info(f"timer mode {game_state.timer_mode}")

                winner = battling.main(game_state)
                
                game_state.player_timer["player1"] = player1.time_minutes_and_seconds
                game_state.player_timer["player2"] = player2.time_minutes_and_seconds
                
                game_state.game_logger.info(f"winner {winner}")
                
                game_state.game_logger.info(f"player1 timer {player1.time_minutes_and_seconds}")
                game_state.game_logger.info(f"player2 timer {player2.time_minutes_and_seconds}")
                
                game_state.game_logger.info(f"{game_state.game_statistics.export_for_charts()}")
                game_state.game_logger.info(f"{game_state.game_statistics.score_history}")
            else:
                winner = "quit"
            
            if winner != "quit":
                end_game.main(winner, game_state)

        case "playback":
            # try:
            #     game_screen.playback = open("playback.txt", "r")
            # except FileNotFoundError:
            #     return
            
            # seed = int(game_screen.playback.readline().split()[-1])
            # player1.deck = game_screen.playback.readline().split()[-1].split("-")
            # player2.deck = game_screen.playback.readline().split()[-1].split("-")
            # game_screen.seed_set(seed)
            # game_screen.timer_mode = game_screen.playback.readline().split()[-1]
            # winner = playback.main(game_screen, player1, player2)

            # game_screen.playback.close()

            # if winner != "quit":
            #     end_game.main(winner, game_screen)
            pass
        case "quit":
            pass
    
if __name__ == "__main__":
    main()