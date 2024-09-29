import menu, battling, end_game
from player_info import Player, GameScreen

def main() -> None:
    player1 = Player(name="player1", deck=[], in_hand=[], on_board=[], draw_deck=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], in_hand=[], on_board=[], draw_deck=[], discard_pile=[])
    game_screen = GameScreen()
    menu.main(game_screen, player1, player2)
    if player1.deck == [] and player2.deck == []:
        player1.deck = ['APTR', 'APTR', 'TANKR', 'TANKR', 'TANKG', 'TANKO', 'ASSR', 'ASSO', 'ADCO', 'ADCO', 'TANKO', 'HEAL']
        player2.deck = ['HFR', 'HFR', 'LFR', 'LFR', 'ADCW', 'ADCW', 'ASSW', 'ASSO', 'MOVE', 'SPW', 'TANKR', 'TANKR']
        
        
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
    
    
#     game_screen.data.data_dicts = {'card_use_count': {'player1': 19, 'player2': 12}, 'hit_count': {'player2_APB': 6, 'player1_LFO': 2}, 'damage_dealt': {'player2_APB': 12, 'player2_TANKP': 8, 'player1_LFO': 17, 'player2_SPB': 12}, 'damage_taken_count': {'player1_LFG': 3, 'player1_TANKO': 15, 'player2_HFP': 3, 'player2_TANKR': 3, 'player1_LFO': 4}, 'damage_taken': {'player1_LFG': 6, 'player1_TANKO': 20, 'player2_HFP': 8, 'player2_TANKR': 9, 
# 'player1_LFO': 6}, 'scored': {'player1_TANKO': 5, 'player2_HFP': 2, 'player2_TANKR': 4, 'player2_APB': 6, 'player1_LFO': 2, 'player2_TANKB': 4, 'player2_TANKP': 3, 'player1_LFG': 0, 'player2_SPB': 2, 'player2_ASSB': 2}, 'ability_count': {'player2_APB': 6}, 'healing_amount': {}, 'heal_count': {}, 'move_count': {'player1_TANKO': 2, 'player1_LFO': 2}, 'use_move_count': {}, 'cube_used_count': {}, 'killed_count': {'player2_APB': 1, 'player1_LFO': 2, 'player2_SPB': 3}, 'death_count': {'player1_LFG': 1, 'player2_TANKR': 1, 'player2_HFP': 1, 'player1_LFO': 1, 'player1_TANKO': 2}, 'use_token_count': {'player2': 4}, 'rounds_survived': {'player1_TANKO': 6, 'player2_HFP': 2, 'player2_TANKR': 4, 'player2_APB': 6, 'player1_LFO': 2, 'player2_TANKB': 4, 'player2_TANKP': 3, 'player2_SPB': 2}}
#     game_screen.data.score_records = [0, 0, -2, 1, -2, 3, 1, 6, 6, 16]
    
    end_game.main(winner, game_screen)
    
    
if __name__ == "__main__":
    main()