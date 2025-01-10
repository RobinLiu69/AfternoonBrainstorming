import random
from card import Board, Card, GameScreen, Blue_setting, BLUE

card_settings = Blue_setting


def got_token(target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    cards = list(filter(lambda card: card.owner == target.owner, player1_on_board+player2_on_board))
    for card in cards:
        card.got_token()
    
    if game_screen.players_token[target.owner] // game_screen.how_many_token_to_draw_a_card >= 1:
        game_screen.players_token[target.owner] -= game_screen.how_many_token_to_draw_a_card
        game_screen.card_to_draw[target.owner] += 1
        game_screen.data.data_update("use_token_count", target.owner, 1)
        draw_card_effect(target, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        
    
    
def draw_card_effect(target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    for card in filter(lambda card: card.owner == target.owner, player1_on_board+player2_on_board):
        card.token_draw(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)


class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["ADC"]["token_gets"]
        got_token(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True
    
    def token_draw(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.numbness:
            self.numbness = False
        else:
            self.attack(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.hit_cards.clear()
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        game_screen.players_token[self.owner] += card_settings["AP"]["token_gets"]
        for i in range(card_settings["AP"]["token_gets"]): got_token(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["TANK"]["token_gets"]
        for i in range(card_settings["TANK"]["token_gets"]): got_token(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.extra_damage = game_screen.players_token[self.owner]
        self.display_update(game_screen)
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["LF"]["token_gets"]
        for i in range(card_settings["LF"]["token_gets"]): got_token(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["ASS"]["token_gets"]
        for i in range(card_settings["ASS"]["token_gets"]): got_token(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += self.armor//card_settings["APT"]["token_from_armor_divisor"]
        for i in range(self.armor//card_settings["APT"]["token_from_armor_divisor"]): got_token(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True

    def got_token(self) -> bool:
        self.armor += 1
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], discard_pile: list[str], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        enemies = list(filter(lambda card: card.owner != self.owner and card.health > 0, on_board_neutral+player1_on_board+player2_on_board))
        if enemies:
            count = 0
            match self.owner:
                case "player1":
                    count = len(player1_on_board+discard_pile)
                case "player2":
                    count = len(player2_on_board+discard_pile)
            for i in range(count):
                if enemies:
                    enemies[random.randrange(len(enemies))].damage_calculate(card_settings["SP"]["spawn_damage"], self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                    enemies = list(filter(lambda card: card.owner != self.owner and card.health > 0, on_board_neutral+player1_on_board+player2_on_board))    
        return self
