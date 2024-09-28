from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, DARKGREEN

def engraved_totem(target: Card, times: int, player1_on_board: list[Card], player2_on_board: list[Card], game_screen: GameScreen) -> None:
    for i in range(times):
        game_screen.players_totem[target.owner] += (1*(2**len(tuple(filter(lambda card: card.owner == target.owner and card.job_and_color == "SPDKG", player1_on_board+player2_on_board)))))

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=5, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + (game_screen.players_totem[self.owner]//4)


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=3, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        engraved_totem(self, 3, player1_on_board, player2_on_board, game_screen)
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=9, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def been_damageed(self, damageer: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        engraved_totem(self, 1, player1_on_board, player2_on_board, game_screen)
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=8, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        self.extra_damage = 0
        
        super().__init__(owner=self.owner, job_and_color="HFDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.heal(1, game_screen)
        return True
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        self.damage_calculate(2, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, False)
        engraved_totem(self, 2, player1_on_board, player2_on_board, game_screen)
        return 0

    


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=6, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def deploy(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        targets = self.detection("small_cross", list(filter(lambda card: card.owner != self and card.health > 0, on_board_neutral+player1_on_board+player2_on_board)))
        for target in targets:
            target.damage_calculate(game_screen.players_token[self.owner]//4, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return self
    
    def ability(self, target: Card, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        engraved_totem(self, 1, player1_on_board, player2_on_board, game_screen)
        return True
    


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=2, damage:int=4):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.health > 0:
            self.health = 0
            engraved_totem(self, 4, player1_on_board, player2_on_board, game_screen)
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=6, damage:int=0):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += self.armor//2
        return True
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        value += game_screen.players_totem[self.owner]
        engraved_totem(self, self.armor//2, player1_on_board, player2_on_board, game_screen)
        return value
    
    def after_damage_calculated(self, target: Card, value: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += value//2
        return True
    

class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=1, damage:int=5):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPDKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)