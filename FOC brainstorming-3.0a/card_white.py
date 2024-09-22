from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, WHITE


class Cube(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=4, damage:int=0):
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
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1):
        self.owner = owner if owner == "display" else "neutral"
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HEAL", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def update(self, game_screen: GameScreen) -> None:
        self.display_update(game_screen)

class Move(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1):
        self.owner = owner if owner == "display" else "neutral"
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="MOVE", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def update(self, game_screen: GameScreen) -> None:
        self.display_update(game_screen)

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=5, damage:int=4):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=4, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=15, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=9, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HFW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=7, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=2, damage:int=5):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=8, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.armor += 2
        self.armor += 2
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=1, damage:int=5):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPW", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 2