from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, Purple_setting, PURPLE

card_settings = Purple_setting

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        target.armor = 0
        target.damage = target.original_damage
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def move_signal(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.owner != self.owner:
            target.damage_calculate(card_settings["TANK"]["movement_damage"], self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        return False


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        if self.attack_types is not None:
            count = len(tuple(self.detection(self.attack_types, tuple(filter(lambda card: card.owner != self.owner, player1_on_board+player2_on_board)))))
            game_screen.number_of_attacks[self.owner] += count//2
        return 0
    

class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        count: int = 0
        match self.owner:
            case "player1":
                count = len(player2_on_board)-len(player1_on_board)-card_settings["ASS"]["unit_gap"] if len(player2_on_board)-len(player1_on_board)-card_settings["ASS"]["unit_gap"] < card_settings["ASS"]["maximum_card_draw_from_killed"] else card_settings["ASS"]["maximum_card_draw_from_killed"]
                for i in range(count):
                    game_screen.card_to_draw[self.owner] += 1
            case "player2":
                count = len(player1_on_board)-len(player2_on_board)-card_settings["ASS"]["unit_gap"] if len(player1_on_board)-len(player2_on_board)-card_settings["ASS"]["unit_gap"] < card_settings["ASS"]["maximum_card_draw_from_killed"] else card_settings["ASS"]["maximum_card_draw_from_killed"]
                for i in range(count):
                    game_screen.card_to_draw[self.owner] += 1
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    

class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPP", health=health, damage=damage, board_x=board_x, board_y=board_y)