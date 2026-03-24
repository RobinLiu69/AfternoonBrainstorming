from typing import TYPE_CHECKING

from cards.card import Board, Card
from core.game_screen import GameScreen, Purple_setting, PURPLE

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral

card_settings = Purple_setting


class PurpleCard(Card):
    pass


class Adc(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ap(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        for target in self.detection("nearest", tuple(filter(lambda card: card.owner != self.owner and card.health > 0, neutral.on_board + player1.on_board + player2.on_board))):
            target.armor = 0
            target.damage = target.original_damage
        return self
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        target.armor = 0
        target.damage = target.original_damage
        return True


class Tank(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def move_broadcast(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner != self.owner:
            target.damage_calculate(card_settings["TANK"]["movement_damage"], self, player1, player2, neutral, board_dict, game_screen)
            return True
        return False


class Hf(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    
    def start_turn(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        if self.attack_types:
            count = len(tuple(self.detection(self.attack_types, tuple(filter(lambda card: card.owner != self.owner, player1.on_board + player2.on_board)))))
            game_screen.number_of_attacks[self.owner] += count//3
        return 0
    

class Lf(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ass(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        count: int = 0
        match self.owner:
            case "player1":
                count = len(player2.on_board)-len(player1.on_board)-card_settings["ASS"]["unit_gap"] if len(player2.on_board)-len(player1.on_board)-card_settings["ASS"]["unit_gap"] < card_settings["ASS"]["maximum_card_draw_from_killed"] else card_settings["ASS"]["maximum_card_draw_from_killed"]
                for i in range(count):
                    game_screen.card_to_draw[self.owner] += 1
            case "player2":
                count = len(player1.on_board)-len(player2.on_board)-card_settings["ASS"]["unit_gap"] if len(player1.on_board)-len(player2.on_board)-card_settings["ASS"]["unit_gap"] < card_settings["ASS"]["maximum_card_draw_from_killed"] else card_settings["ASS"]["maximum_card_draw_from_killed"]
                for i in range(count):
                    game_screen.card_to_draw[self.owner] += 1
        return True


class Apt(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    

class Sp(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPP", health=health, damage=damage, board_x=board_x, board_y=board_y)