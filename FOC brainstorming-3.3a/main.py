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

    end_game.main(game_screen)
    
    
if __name__ == "__main__":
    main()