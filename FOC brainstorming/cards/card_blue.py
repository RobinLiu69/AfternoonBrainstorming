import random
from cards.card import Board, Card
from core.game_screen import GameScreen, Blue_setting, BLUE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral

card_settings = Blue_setting

class BlueCard(Card):
    def get_token(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        cards = list(filter(lambda card: card.owner == self.owner, player1.on_board+player2.on_board))
        for card in cards:
            if isinstance(card, BlueCard):
                card.after_token(player1, player2, neutral, board_dict, game_screen)
        
        if game_screen.players_token[self.owner] // game_screen.how_many_token_to_draw_a_card >= 1:
            game_screen.players_token[self.owner] -= game_screen.how_many_token_to_draw_a_card
            game_screen.card_to_draw[self.owner] += 1
            game_screen.data.data_update("use_token_count", self.owner, 1)
            self.draw_card_effect(player1, player2, neutral, board_dict, game_screen)
        
    def draw_card_effect(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for card in filter(lambda card: card.owner == self.owner, player1.on_board+player2.on_board):
            if isinstance(card, BlueCard):
                card.token_draw(player1, player2, neutral, board_dict, game_screen)

    def token_draw(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def after_token(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False


class Adc(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["ADC"]["token_gets"]
        self.get_token(player1, player2, neutral, board_dict, game_screen)
        return True
    
    def token_draw(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.numbness:
            self.numbness = False
        else:
            self.attack(player1, player2, neutral, board_dict, game_screen)
            self.hit_cards.clear()
        return True


class Ap(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        game_screen.players_token[self.owner] += card_settings["AP"]["token_gets"]
        for i in range(card_settings["AP"]["token_gets"]): self.get_token(player1, player2, neutral, board_dict, game_screen)
        return True


class Tank(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["TANK"]["token_gets"]
        for i in range(card_settings["TANK"]["token_gets"]): self.get_token(player1, player2, neutral, board_dict, game_screen)
        return True


class Hf(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.extra_damage = game_screen.players_token[self.owner]
        self.display_update(game_screen)
    
    def damage_bonus(self, value: int, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage


class Lf(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["LF"]["token_gets"]
        for i in range(card_settings["LF"]["token_gets"]): self.get_token(player1, player2, neutral, board_dict, game_screen)
        return True


class Ass(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += card_settings["ASS"]["token_gets"]
        for i in range(card_settings["ASS"]["token_gets"]): self.get_token(player1, player2, neutral, board_dict, game_screen)
        
        return True


class Apt(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += self.armor//card_settings["APT"]["token_from_armor_divisor"]
        for i in range(self.armor//card_settings["APT"]["token_from_armor_divisor"]): self.get_token(player1, player2, neutral, board_dict, game_screen)
        return True

    def after_token(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += 1
        return True


class Sp(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        discard_pile = player1.discard_pile if self.owner == "player1" else player2.discard_pile
        enemies = list(filter(lambda card: card.owner != self.owner and card.health > 0, neutral.on_board + player1.on_board + player2.on_board))
        if enemies:
            count = 0
            match self.owner:
                case "player1":
                    count = len(player1.on_board+discard_pile)
                case "player2":
                    count = len(player2.on_board+discard_pile)
            for i in range(count):
                if enemies:
                    enemies[random.randrange(len(enemies))].damage_calculate(card_settings["SP"]["spawn_damage"], self, player1, player2, neutral, board_dict, game_screen)
                    enemies = list(filter(lambda card: card.owner != self.owner and card.health > 0, neutral.on_board + player1.on_board + player2.on_board))    
        return self
