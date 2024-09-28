from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, ORANGE


class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=4, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            self.moving = True
            return True
        else:
            return False
    
    def moved(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=3, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        match self.owner:
            case "player1":
                player1_in_hand.append("MOVEO")
            case "player2":
                player2_in_hand.append("MOVEO")
        return 0


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=10, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def been_attacked(self, attacker: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        match self.owner:
            case "player1":
                player1_in_hand.append("MOVEO")
            case "player2":
                player2_in_hand.append("MOVEO")
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=9, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        self.extra_damage = 0
        
        super().__init__(owner=self.owner, job_and_color="HFO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            self.moving = True
            return True
        else:
            return False
        
    def moved(self, player1_in_hand: list[str], plaeyr2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.extra_damage += 1
        self.anger = True
        return True
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        self.extra_damage = 0
        self.anger = False
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 1
    


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=6, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            self.moving = True
            return True
        else:
            return False
        
    def moved(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        cards = tuple(self.detection("nearest", filter(lambda card: card.owner != self.owner and card != self, on_board_neutral + player1_on_board + player2_on_board)))
        if cards:
            cards[0].damage_calculate(self.damage, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=2, damage:int=4):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def moved(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.anger = True
        return True
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.moving = True
        if self.anger:
            game_screen.number_of_attacks[self.owner] += 1
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


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=6, damage:int=0):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += self.armor//4
        return True

    def moved(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += 1
        value = self.armor // 2
        if value > 0:
            self.damage += value
            self.armor = self.armor % 2
        return True

    def move_signal(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner == self.owner and target != self:
            target.armor += 1
            self.armor += 1
        return True
    

class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=1, damage:int=5):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPO", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    def move_signal(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner == self.owner:
            cards = tuple(self.detection("farthest", filter(lambda card: card.owner != self.owner and card != self, on_board_neutral + player1_on_board + player2_on_board)))
            if cards:
                cards[0].damage_calculate(3, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True