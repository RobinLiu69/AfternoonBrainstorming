from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, White_setting, WHITE

card_settings = White_setting


class Cube(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["CUBE"]["health"], damage:int=card_settings["CUBE"]["damage"]) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral", job_and_color="CUBES" if owner == "display" else "CUBE", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 0


class Heal(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral", job_and_color="HEAL", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Move(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral", job_and_color="MOVE", health=health, damage=damage, board_x=board_x, board_y=board_y)



class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:


        super().__init__(owner=owner, job_and_color="APW", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTW", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_neutral+player1_on_board+player2_on_board)):
            card.armor += card_settings["APT"]["armor_increase"]
        self.armor += card_settings["APT"]["armor_increase"]
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPW", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True:
            if  clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1 + card_settings["SP"]["extra_score"]