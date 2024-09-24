from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, RED


class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=4, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        self.damage += 1
        for card in on_board_cards:
            if card.owner == self.owner and card.job_and_color == "SPR":
                card.damage += 1
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=3, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        target.numbness = True
        value = target.damage//2
        self.damage += value
        target.damage -= value
        for card in on_board_cards:
            if card.owner == self.owner and card.job_and_color == "SPR":
                card.damage += value
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=9, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def been_attacked(self, attacker: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.armor += 2
        
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.armor += 2
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=9, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HFR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        self.health -= 1
        if self.health == 0:
            self.anger = True
        self.damage += 1
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.damage += 1
        return True

    def can_be_killed(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.anger:
            return False
        else:
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


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=5, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        self.armor += 1
        self.damage += 1
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.armor += 1
            card.damage += 1
        return True


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=2, damage:int=4):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.damage += 2
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.damage += 2
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=6, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.armor += 1
            card.damage += 1
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.armor += 1
            card.damage += 1
        self.armor += 1
        self.damage += 1
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=1, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)