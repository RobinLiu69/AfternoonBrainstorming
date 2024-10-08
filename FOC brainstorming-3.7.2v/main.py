import menu, battling, end_game
from player_info import Player, GameScreen

def main() -> None:
    player1 = Player(name="player1", deck=[], in_hand=[], on_board=[], draw_deck=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], in_hand=[], on_board=[], draw_deck=[], discard_pile=[])
    game_screen = GameScreen()
    menu.main(game_screen, player1, player2)
    if player1.deck == [] and player2.deck == []:
        player1.deck = ['ASSP', 'CUBES', 'ADCW', 'ADCW', 'TANKR', 'TANKR', 'SPW', 'SPW', 'HFP', 'HFP', 'ASSO', 'MOVE']
        player2.deck = ['LFDKG', 'LFDKG', 'ASSDKG', 'ASSDKG', 'CUBES', 'CUBES', 'CUBES', 'ASSP', 'ASSP', 'SPDKG', 'HFR', 'HFR']
        
        
    winner = battling.main(game_screen, player1, player2)
    
    game_screen.player_timer["player1"] = player1.time_minutes_and_seconds
    game_screen.player_timer["player2"] = player2.time_minutes_and_seconds
    
    print(f"winner: {winner}\n")
    
    
    print(f"P1 score: {abs(game_screen.score)}" if game_screen.score <= 0 else "")
    print(f"P2 score: {game_screen.score}" if game_screen.score >= 0 else "")
    print(f"P1 Deck: {player1.deck}")
    print(f"P2 Deck: {player2.deck}")
    
    print(f"player1 timer: {player1.time_minutes_and_seconds}")
    print(f"player2 timer: {player2.time_minutes_and_seconds}")
    
    print(game_screen.data.data_dicts)
    print(game_screen.data.score_records)
    
    
    
    if winner == "None":
        winner = "player2"
        game_screen.score = 10
        
        game_screen.player_timer["player1"] = "10:23"
        game_screen.player_timer["player2"] = "17:40"
        
        game_screen.data.data_dicts = {'card_use_count': {'player2': 30, 'player1': 22}, 'hit_count': {'player2_ASSDKG': 3, 'player2_HFR': 4, 'player2_SPDKG': 2, 'player1_ASSO': 11, 'player1_ASSP': 5, 'player2_ASSP': 4, 'player1_TANKR': 5, 'player2_LFDKG': 1, 'player1_HFP': 3}, 'damage_dealt': {'player2_ASSDKG': 12, 'player2_HFR': 56, 'player2_SPDKG': 9, 'player1_ASSO': 35, 'player2_LFDKG': 41, 'player1_ASSP': 17, 'player2_ASSP': 31, 'player1_TANKR': 10, 'player1_HFP': 8}, 'damage_taken_count': {'neutral_CUBE': 30, 'player1_HFP': 8, 'player1_TANKR': 7, 'player1_ADCW': 3, 'player2_HFR': 17, 'player2_SPDKG': 3, 'player1_ASSO': 3, 'player1_SPW': 4, 'player2_ASSP': 3, 'player2_LFDKG': 10, 'player1_ASSP': 1, 'player2_ASSDKG': 2}, 'damage_taken': {'neutral_CUBE': 72, 'player1_HFP': 26, 'player1_TANKR': 27, 'player1_ADCW': 14, 'player2_HFR': 35, 'player2_SPDKG': 3, 'player1_ASSO': 10, 'player1_SPW': 6, 'player2_ASSP': 4, 'player2_LFDKG': 18, 'player1_ASSP': 2, 'player2_ASSDKG': 2}, 'scored': {'player2_HFR': 11, 'player1_TANKR': 7, 'player1_ADCW': 2, 'player2_SPDKG': 3, 'player1_HFP': 7, 'player1_ASSO': 4, 'player1_SPW': 10, 'player2_LFDKG': 10, 'player1_ASSP': 2, 'player2_ASSP': 6, 'player2_ASSDKG': 4}, 'ability_count': {'player2_HFR': 19, 'player2_LFDKG': 12}, 'healing_amount': {}, 'heal_count': {}, 'move_count': {'player1_ASSO': 8, 'player1_TANKR': 1}, 'use_move_count': {}, 'cube_used_count': {'player2': 14, 'player1': 4}, 'killed_count': {'player2_ASSDKG': 5, 'player2_HFR': 11, 'player2_SPDKG': 1, 'player1_ASSO': 8, 'player2_LFDKG': 6, 'player1_ASSP': 3, 'player2_ASSP': 7, 'player1_HFP': 4}, 'death_count': {'neutral_CUBE': 18, 'player1_HFP': 3, 'player1_TANKR': 3, 'player1_ADCW': 2, 'player2_HFR': 4, 'player2_SPDKG': 3, 'player1_ASSO': 2, 'player1_SPW': 3, 'player2_ASSP': 2, 'player2_LFDKG': 3, 'player1_ASSP': 1, 'player2_ASSDKG': 1}, 'use_token_count': {}, 'rounds_survived': {'player2_HFR': 11, 'player1_TANKR': 8, 'player1_ADCW': 3, 'player2_SPDKG': 3, 'player1_ASSO': 1, 'player2_LFDKG': 10, 'player1_HFP': 8, 'player1_SPW': 1, 'player1_ASSP': 1, 'player2_ASSP': 2, 'player2_ASSDKG': 1}}
        game_screen.data.score_records = [0, 0, 0, 0, 0, 1, 1, 2, 0, 2, 1, 1, 0, 0, -1, 0, -4, -2, -5, -2, -6, -4, -5, 2, 1, 5, 3, 6, 5, 8, 5, 10]
    
    
    end_game.main(winner, game_screen)
    
    
if __name__ == "__main__":
    main()