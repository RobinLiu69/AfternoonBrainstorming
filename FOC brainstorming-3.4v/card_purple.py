from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, PURPLE


class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=0, damage:int=0):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=3, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        target.armor = 0
        target.damage = target.original_damage
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=9, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def move_signal(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner != self.owner:
            target.damage_calculate(2, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        return False


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=8, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        self.extra_damage = 0
        
        super().__init__(owner=self.owner, job_and_color="HFP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        if self.attack_types is not None:
            count = len(tuple(self.detection(self.attack_types, tuple(filter(lambda card: card.owner != self.owner, player1_on_board+player2_on_board)))))
            game_screen.number_of_attacks[self.owner] += count//2
        return 0
    

class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=0, damage:int=0):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=2, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        count: int = 0
        match self.owner:
            case "player1":
                count = len(player2_on_board)-len(player1_on_board) if len(player2_on_board)-len(player1_on_board) < 2 else 2
                for i in range(count):
                    game_screen.card_to_draw[self.owner] += 1
            case "player2":
                count = len(player1_on_board)-len(player2_on_board) if len(player1_on_board)-len(player2_on_board) < 2 else 2
                for i in range(count):
                    game_screen.card_to_draw[self.owner] += 1
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=0, damage:int=0):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    

class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=0, damage:int=0):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPP", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)