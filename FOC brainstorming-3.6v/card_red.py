from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, Red_setting, RED

card_settings = Red_setting

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage: int=card_settings["ADC"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        self.damage += card_settings["ADC"]["damage_increase"]
        for card in on_board_cards:
            if card.owner == self.owner and card.job_and_color == "SPR":
                card.damage += card_settings["ADC"]["damage_increase"]
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage: int=card_settings["AP"]["damage"]) -> None:
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
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage: int=card_settings["TANK"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def been_attacked(self, attacker: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.armor += card_settings["TANK"]["armor_increase"]
        
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.armor += card_settings["TANK"]["armor_increase"]
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage: int=card_settings["HF"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HFR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        self.health -= card_settings["HF"]["health_decrease"]
        if self.health == 0:
            self.anger = True
        self.damage += card_settings["HF"]["damage_increase"]
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.damage += card_settings["HF"]["damage_increase"]
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
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage: int=card_settings["LF"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        self.armor += card_settings["LF"]["armor_increase"]
        self.damage += card_settings["LF"]["damage_increase"]
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.armor += card_settings["LF"]["armor_increase"]
            card.damage += card_settings["LF"]["damage_increase"]
        return True


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage: int=card_settings["ASS"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)

    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.damage += card_settings["ASS"]["damage_increase"]
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.damage += card_settings["ASS"]["damage_increase"]
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage: int=card_settings["APT"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        on_board_cards = on_board_neutral + player1_on_board + player2_on_board
        for card in self.detection("nearest", filter(lambda card: card.owner == self.owner and card != self, on_board_cards)):
            card.armor += card_settings["APT"]["armor_increase"]
            card.damage += card_settings["APT"]["damage_increase"]
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", on_board_cards):
            card.armor += card_settings["APT"]["armor_increase"]
            card.damage += card_settings["APT"]["damage_increase"]
        self.armor += card_settings["APT"]["armor_increase"]
        self.damage += card_settings["APT"]["damage_increase"]
        return True


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage: int=card_settings["SP"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPR", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)