import menu, battling
from player_info import Player, GameScreen

def main() -> None:
    player1 = Player(name="player1", deck=[], in_hand=[], on_board=[], draw_deck=[], discard_pile=[])
    player2 = Player(name="player2", deck=[], in_hand=[], on_board=[], draw_deck=[], discard_pile=[])
    game_screen = GameScreen()
    menu.main(game_screen, player1, player2)
    battling.main(game_screen, player1, player2)

if __name__ == "__main__":
    main()