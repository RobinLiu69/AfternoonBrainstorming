from typing import TYPE_CHECKING

from cards.card import Board, Card
from core.game_screen import GameScreen, Orange_setting, ORANGE

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral

card_settings = Orange_setting


class OrangeCard(Card):
    pass


class Adc(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCO", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            self.moving = True
            self.hit_cards.clear()
            return True
        else:
            return False
    
    def moved(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen)
        return True


class Ap(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True
    
    def start_turn(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        match self.owner:
            case "player1":
                player1.hand.append("MOVEO")
            case "player2":
                player2.hand.append("MOVEO")
        return 0


class Tank(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        match self.owner:
            case "player1":
                player1.hand.append("MOVEO")
            case "player2":
                player2.hand.append("MOVEO")
        return True


class Hf(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            self.moving = True
            self.hit_cards.clear()
            return True
        else:
            return False
        
    def moved(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.extra_damage += card_settings["HF"]["extra_damage_from_moving"]
        self.anger = True
        return True
    
    def damage_bonus(self, value: int, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if clear_numbness:
            self.extra_damage = 0
            self.anger = False
        if self.numbness == True:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1
    


class Lf(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            self.moving = True
            self.hit_cards.clear()
            return True
        else:
            return False
        
    def moved(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for card in self.detection("nearest", filter(lambda card: card.owner != self.owner and card != self, neutral.on_board + player1.on_board + player2.on_board)):
            card.damage_calculate(self.damage, self, player1, player2, neutral, board_dict, game_screen)
        return True


class Ass(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def moved(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.anger = True
        return True
    
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.moving = True
        if self.anger:
            game_screen.number_of_attacks[self.owner] += card_settings["ASS"]["number_of_attack_increase_from_killed"]
            self.anger = False
        return True
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if clear_numbness:
            self.anger = False
        if self.numbness == True:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1


class Apt(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTO", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def moved(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += card_settings["APT"]["armor_get_from_moving"]
        value = self.armor // 2
        if value > 0:
            self.damage += value
            self.armor = self.armor % 2
        return True

    def move_broadcast(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner == self.owner and target != self:
            target.armor += card_settings["APT"]["armor_get_from_moving"]
            self.armor += card_settings["APT"]["armor_get_from_moving"]
        return True
    

class Sp(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPO", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def move_broadcast(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner == self.owner:
            for card in self.detection("farthest", filter(lambda card: card.owner != self.owner and card != self, neutral.on_board + player1.on_board + player2.on_board)):
                card.damage_calculate(card_settings["SP"]["movement_damage"], self, player1, player2, neutral, board_dict, game_screen)
        return True