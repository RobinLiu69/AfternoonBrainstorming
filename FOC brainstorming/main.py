import start_screen, menu, battling, end_game, playback
import datetime
from player import Player, GameScreen


def main() -> None:

    player1 = Player(name="player1", deck=[], in_hand=[], on_board=[], draw_pile=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], in_hand=[], on_board=[], draw_pile=[], discard_pile=[])
    game_screen = GameScreen()

    mode = start_screen.main(game_screen)

    match mode:
        case "start":
            game_screen.log = open(f"{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt", "w")
            game_screen.seed_set()
            if menu.main(game_screen, player1, player2) and game_screen.log is not None:
                if player1.deck == [] and player2.deck == []:
                    player1.deck = ['ASSP', 'CUBES', 'ADCW', 'ADCW', 'TANKR', 'TANKR', 'SPW', 'SPW', 'HFP', 'HFP', 'ASSO', 'MOVE']
                    player2.deck = ['LFDKG', 'LFDKG', 'ASSDKG', 'ASSDKG', 'CUBES', 'CUBES', 'CUBES', 'ASSP', 'ASSP', 'SPDKG', 'HFR', 'HFR']

                game_screen.log.write(f"player1 deck {"-".join(player1.deck)}\nplayer2 deck {"-".join(player2.deck)}\n")
                
                game_screen.log.write(f"timer mode {game_screen.timer_mode}\n")

                winner = battling.main(game_screen, player1, player2)

                game_screen.player_timer["player1"] = player1.time_minutes_and_seconds
                game_screen.player_timer["player2"] = player2.time_minutes_and_seconds
                
                game_screen.log.write(f"winner {winner}\n")
            
                game_screen.log.write(f"player1 score {abs(game_screen.score)}\n" if game_screen.score <= 0 else "")
                game_screen.log.write(f"player2 score {game_screen.score}\n" if game_screen.score >= 0 else "")
                
                game_screen.log.write(f"player1 timer {player1.time_minutes_and_seconds}\n")
                game_screen.log.write(f"player2 timer {player2.time_minutes_and_seconds}\n")
                
                game_screen.log.write(f"{game_screen.data.data_dicts}\n")
                game_screen.log.write(f"{game_screen.data.score_records}\n")
            else:
                winner = "quit"

            if game_screen.log is not None: game_screen.log.close()
            
            
            if winner == "None":
                winner = "player1"
                game_screen.score = 10
                
                game_screen.player_timer["player1"] = "05:33"
                game_screen.player_timer["player2"] = "03:38"
                
                game_screen.data.data_dicts = {'card_use_count': {'player1': 15, 'player2': 13}, 'hit_count': {'player1_APF': 1, 'player2_ADCO': 6, 'player2_ASSW': 4, 'player1_TANKG': 4, 'player2_ASSF': 2, 'player2_SHADOW': 3, 'player1_APB': 5}, 'damage_dealt': {'player1_APF': 1, 'player2_ADCO': 37, 'player2_ASSW': 38, 'player1_TANKG': 4, 'player2_ASSF': 13, 'player1_APB': 10}, 'damage_taken_count': {'player2_ADCO': 2, 'player1_APF': 7, 'player1_TANKB': 8, 'player1_TANKR': 6, 'player1_TANKG': 4, 'player2_APTF': 3, 'player2_ASSF': 1, 'player1_APB': 1, 'player2_TANKR': 1, 'player2_TANKG': 1, 'player1_TANKF': 7, 'player2_ASSW': 2}, 'damage_taken': {'player2_ADCO': 3, 'player1_APF': 14, 'player1_TANKB': 24, 'player1_TANKR': 15, 'player1_TANKG': 12, 'player2_APTF': 4, 'player2_ASSF': 2, 'player1_APB': 4, 'player2_TANKR': 2, 'player2_TANKG': 2, 'player1_TANKF': 19, 'player2_ASSW': 2}, 'scored': {'player1_TANKR': 11, 'player1_TANKB': 11, 'player1_APF': 5, 'player2_ADCO': 8, 'player2_APTF': 3, 'player2_TANKR': 13, 'player1_TANKG': 4, 'player1_TANKF': 9, 'player2_ASSF': 2, 'player1_APB': 5, 'player2_ASSW': 3, 'player2_TANKG': 6, 'player2_HFR': 0}, 'ability_count': {'player1_APF': 1, 'player1_APB': 5}, 'healing_amount': {}, 'heal_count': {}, 'move_count': {'player2_ADCO': 2}, 'use_move_count': {}, 'cube_used_count': {}, 'killed_count': {'player2_ADCO': 3, 'player1_TANKG': 2, 'player2_ASSF': 3, 'player1_APB': 2, 'player2_ASSW': 2}, 'death_count': {'player1_APF': 3, 'player2_APTF': 2, 'player1_TANKR': 1, 'player1_TANKG': 1, 'player2_ASSF': 1, 'player1_APB': 1, 'player1_TANKB': 1, 'player2_ASSW': 1, 'player1_TANKF': 1}, 'use_token_count': {'player1': 6}, 'rounds_survived': {'player1_TANKR': 11, 'player1_TANKB': 11, 'player1_APF': 5, 'player2_ADCO': 12, 'player2_APTF': 4, 'player2_TANKR': 17, 'player1_TANKG': 4, 'player1_TANKF': 9, 'player2_ASSF': 1, 'player1_APB': 6, 'player2_ASSW': 2, 'player2_TANKG': 9, 'player2_HFR': 3}}
                game_screen.data.score_records = [0, 0, -3, -2, -5, -2, -6, -3, -5, 0, -3, 1, -3, 1, -4, 1, -6, -1, -8, -3, -10]
            
            if winner != "quit":
                end_game.main(winner, game_screen)

        case "playback":
            try:
                game_screen.playback = open("playback.txt", "r")
            except FileNotFoundError:
                return
            
            seed = int(game_screen.playback.readline().split()[-1])
            player1.deck = game_screen.playback.readline().split()[-1].split("-")
            player2.deck = game_screen.playback.readline().split()[-1].split("-")
            game_screen.seed_set(seed)
            game_screen.timer_mode = game_screen.playback.readline().split()[-1]
            winner = playback.main(game_screen, player1, player2)

            game_screen.playback.close()

            if winner != "quit":
                end_game.main(winner, game_screen)
        case "quit":
            pass
    
if __name__ == "__main__":
    main()