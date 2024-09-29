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
    print(f"winner: {winner}\n")
    
    print(f"P1 score: {abs(game_screen.score)}" if game_screen.score <= 0 else "")
    print(f"P2 score: {game_screen.score}" if game_screen.score >= 0 else "")
    print(f"P1 Deck: {player1.deck}")
    print(f"P2 Deck: {player2.deck}")
    
    print(game_screen.data.data_dicts)
    print(game_screen.data.score_records)
    
    # game_screen.data.data_dicts = {'card_use_count': {'player1': 16, 'player2': 15}, 'hit_count': {'player1_TANKO': 1, 'player1_APTR': 11, 'player1_ASSR': 1, 'player2_ASSO': 7, 'player1_ASSO': 3, 'player2_HFR': 3, 'player2_ASSW': 1, 'player2_ADCW': 4}, 'damage_dealt': {'player1_TANKO': 3, 'player1_APTR': 51, 'player1_ASSR': 4, 'player2_ASSO': 27, 'player1_ASSO': 5, 'player2_HFR': 33, 'player2_ASSW': 4, 'player2_ADCW': 16}, 'damage_taken_count': {'player2_SPW': 2, 'player2_HFR': 3, 'player2_ADCW': 4, 'player2_LFR': 4, 'player1_ASSR': 1, 'player1_TANKO': 3, 'player1_ADCO': 3, 'player1_TANKR': 6, 'player2_ASSO': 1, 'player2_TANKR': 3, 'player1_TANKG': 3, 'player1_ASSO': 2, 'player2_ASSW': 1, 'player1_APTR': 4}, 'damage_taken': {'player2_SPW': 2, 'player2_HFR': 12, 'player2_ADCW': 17, 'player2_LFR': 10, 'player1_ASSR': 2, 'player1_TANKO': 10, 'player1_ADCO': 10, 'player1_TANKR': 18, 'player2_ASSO': 2, 'player2_TANKR': 18, 'player1_TANKG': 15, 'player1_ASSO': 9, 'player2_ASSW': 2, 'player1_APTR': 16}, 'scored': {'player1_TANKR': 8, 'player1_APTR': 19, 'player2_SPW': 6, 'player2_HFR': 11, 'player1_TANKO': 10, 'player2_ADCW': 7, 'player2_LFR': 1, 'player2_TANKR': 14, 'player1_ADCO': 3, 'player1_ASSR': 1, 'player2_ASSO': 1, 'player1_ASSO': 9, 'player1_TANKG': 2, 'player2_ASSW': 3}, 'ability_count': {'player1_APTR': 11, 'player2_HFR': 8}, 'healing_amount': {}, 'heal_count': {}, 'move_count': {'player2_ASSO': 5, 'player1_ASSO': 4, 'player2_ADCW': 1}, 'use_move_count': {}, 'cube_used_count': {}, 'killed_count': {'player1_TANKO': 1, 'player1_APTR': 6, 'player1_ASSR': 1, 'player2_ASSO': 4, 'player1_ASSO': 3, 'player2_HFR': 1, 'player2_ASSW': 1}, 'death_count': {'player2_SPW': 2, 'player2_LFR': 2, 'player2_ADCW': 2, 'player1_ASSR': 1, 'player1_ADCO': 2, 'player1_TANKR': 2, 'player1_TANKO': 1, 'player2_ASSO': 1, 'player2_ASSW': 1, 'player2_TANKR': 2, 'player2_HFR': 1}, 'use_token_count': {}, 'rounds_survived': {'player1_TANKR': 8, 'player1_APTR': 19, 'player2_SPW': 1, 'player2_HFR': 11, 'player1_TANKO': 10, 'player2_ADCW': 7, 'player2_LFR': 1, 'player2_TANKR': 14, 'player1_ASSO': 7, 'player1_ADCO': 3, 'player2_ASSW': 2, 'player1_TANKG': 3}}
    # game_screen.data.score_records = [i for i in range(35)]
    
    end_game.main(game_screen)
    
    
if __name__ == "__main__":
    main()