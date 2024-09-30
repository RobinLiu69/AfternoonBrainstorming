from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, White_setting, WHITE

card_settings = White_setting


class Cube(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["CUBE"]["health"], damage:int=card_settings["CUBE"]["damage"]) -> None:
        self.owner = owner if owner == "display" else "neutral"
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="CUBES" if self.owner == "display" else "CUBE", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 0

class Heal(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1) -> None:
        self.owner = owner if owner == "display" else "neutral"
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HEAL", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def update(self, game_screen: GameScreen) -> None:
        self.display_update(game_screen)

class Move(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1) -> None:
        self.owner = owner if owner == "display" else "neutral"
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="MOVE", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def update(self, game_screen: GameScreen) -> None:
        self.display_update(game_screen)

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HFW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.armor += card_settings["APT"]["armor_increase"]
        self.armor += card_settings["APT"]["armor_increase"]
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True:
            if  clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1 + card_settings["SP"]["extra_score"]