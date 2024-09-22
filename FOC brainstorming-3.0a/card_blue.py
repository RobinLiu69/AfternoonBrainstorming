from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, BLUE

def got_token(target: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
    cards = list(filter(lambda card: card.owner == target.owner, player1_on_board+player2_on_board))
    for card in cards:
        card.got_token(in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=4, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def killed(self, victim: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += 1
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True
    
    def token_draw(self, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.numbness:
            self.numbness = False
        else:
            self.attack(in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=4, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        game_screen.players_token[self.owner] += 2
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=10, damage:int=1):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def been_attacked(self, attacker: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += 1
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=8, damage:int=2):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HFB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + game_screen.players_token[self.owner]


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=6, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += 1
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=2, damage:int=4):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def killed(self, victim: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += 2
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=5, damage:int=3):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    
    def ability(self, target: Card, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_token[self.owner] += self.armor//4
        for i in range(self.armor//4): got_token(self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True

    def got_token(self, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += 1
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=1, damage:int=5):
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPB", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def delploy(self, in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], discard_pile: list[str], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        enemies = list(filter(lambda card: card.owner != self.owner and card.health > 0, on_board_neutral+player1_on_board+player2_on_board))
        if enemies:
            match self.owner:
                case "Player1":
                    count = len(player1_on_board+discard_pile)
                case "Player2":
                    count = len(player2_on_board+discard_pile)
            for i in range(count):
                enemies[random.randrange(len(enemies))].damage_calculate(1, self, in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                enemies = list(filter(lambda card: card.owner != self.owner and card.health > 0, on_board_neutral+player1_on_board+player2_on_board))
                        
        return self
