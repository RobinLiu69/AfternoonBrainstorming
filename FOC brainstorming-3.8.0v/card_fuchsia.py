from dataclasses import dataclass, field
import os, json, pygame
import random
from typing import Iterable, Any, cast

from card import Board, Card, GameScreen, Fuchsia_setting, FUCHSIA, BOARD_SIZE

card_settings = Fuchsia_setting


def spawn_shadow(owner: str, self_board_x: int, self_board_y: int, damage: int, linker: Card) -> Card:
    return Shadow(owner, BOARD_SIZE[0]-1-self_board_x, BOARD_SIZE[1]-1-self_board_y, damage, linker)
    



class Shadow(Card):
    def __init__(self, owner: str, board_x: int, board_y: int,  damage:int, linker: Card) -> None:
        
        super().__init__(owner=owner, job_and_color="SHADOW", health=1, damage=damage, board_x=board_x, board_y=board_y)
        self.linker = linker
        
    
    def draw_shape(self, game_screen: GameScreen) -> None:
        if self.surface is None: return
        self.shape = tuple(map(lambda coordinate: (coordinate[0]+game_screen.block_size*0.05, coordinate[1]+game_screen.block_size*0.05), self.linker.shaped(game_screen.block_size)))
        self.color = (159, 0, 80, 150)
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        return 0
        
        
class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadow: Card | None = None
        if self.owner != "display":
            self.shadow = spawn_shadow(owner, board_x, board_y, self.damage, self)
        else:
            self.shadow = None
        
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            if self.shadow:
                self.shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        else:
            return False
    

class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadow: Card | None = None
        if self.owner != "display":
            self.shadow = spawn_shadow(owner, board_x, board_y, self.damage, self)
        else:
            self.shadow = None
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True

    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1
    
    

class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return True


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
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
