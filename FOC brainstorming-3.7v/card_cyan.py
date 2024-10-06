from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, draw_text, Cyan_setting, CYAN

card_settings = Cyan_setting


def get_coins(target: Card, value: int, game_screen: GameScreen) -> None:
    game_screen.players_coin[target.owner] = game_screen.players_coin[target.owner] + value if game_screen.players_coin[target.owner] + value <= 50 else 50

def price_check(owner: str, job: str, player1_on_board: list[Card], player2_on_board: list[Card], game_screen: GameScreen) -> bool:
    price = card_settings[job]["cost"] - (card_settings["SP"]["coin_reduced"]*len(tuple(filter(lambda card: card.job_and_color == "SPC" and card.owner == owner, player1_on_board+player2_on_board))))
    if game_screen.players_coin[owner] >= price:
        game_screen.players_coin[owner] -= price
        return True
    else:
        return False
    
class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        self.upgrade = upgrade
        
        super().__init__(owner=owner, job_and_color="ADCC", health=health if not upgrade else card_settings["ADC"]["upgrade_health"], damage=damage if not upgrade else card_settings["ADC"]["upgrade_damage"], board_x=board_x, board_y=board_y)

    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)
    
    def attack(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen) and self.upgrade:
            self.launch_attack(self.attack_types, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        else:
            return False
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        get_coins(self, card_settings["ADC"]["coin_gets"], game_screen)
        return True
    
    
    

class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:

        self.upgrade = upgrade
        
        super().__init__(owner=owner, job_and_color="APC", health=health if not upgrade else card_settings["AP"]["upgrade_health"], damage=damage if not upgrade else card_settings["AP"]["upgrade_damage"], board_x=board_x, board_y=board_y)
    
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)
    
    def deploy(self, player1_on_board: list[Card], player2_on_board: list[Card], game_screen: GameScreen) -> Card:
        for target in tuple(filter(lambda card: card.owner != self.owner, player1_on_board+player2_on_board)):
            if target.been_targeted:
                target.been_targeted = False
                target.trigered_by = None
        else:
            for target in self.detection("nearest", tuple(filter(lambda card: card.owner != self.owner, player1_on_board+player2_on_board))):
                target.been_targeted = True
                target.trigered_by = self
        return self

    def trigger(self, victim: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.upgrade:
            get_coins(self, card_settings["AP"]["coin_gets"], game_screen)
        return True
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        self.upgrade = upgrade
        
        super().__init__(owner=owner, job_and_color="TANKC", health=health if not upgrade else card_settings["TANK"]["upgrade_health"], damage=damage if not upgrade else card_settings["TANK"]["upgrade_damage"], board_x=board_x, board_y=board_y)
    
        if upgrade:
            self.anger = True
        
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)

    def damage_block(self, attacker: Card, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.anger:
            self.anger = False
            return True
        else:
            return False
        
    def been_attacked(self, attacker: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        get_coins(self, card_settings["TANK"]["coin_gets"], game_screen)
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:

        self.upgrade = upgrade
        self.count = 1
        
        super().__init__(owner=owner, job_and_color="HFC", health=health if not upgrade else card_settings["HF"]["upgrade_health"], damage=damage if not upgrade else card_settings["HF"]["upgrade_damage"], board_x=board_x, board_y=board_y)
        
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)

    def ability(self, target: Card, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        get_coins(self, card_settings["HF"]["coin_gets"], game_screen)
        return True

    def been_killed(self, attacker: Card, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.upgrade == True:
            self.anger = True
            self.damage += card_settings["HF"]["damage_bonus"]
        return True
    
    def can_be_killed(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.anger:
            return False
        else:
            return True
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if clear_numbness:
            if self.anger:
                self.count -= 1
        if self.numbness == True or self.count == 0:
            if clear_numbness:
                self.anger = False
                self.numbness = False
            return 0
        else:
            return 1


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:

        self.upgrade = upgrade
        
        super().__init__(owner=owner, job_and_color="LFC", health=health if not upgrade else card_settings["LF"]["upgrade_health"], damage=damage if not upgrade else card_settings["LF"]["upgrade_damage"], board_x=board_x, board_y=board_y)
    
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)

    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.upgrade:
            get_coins(self, card_settings["LF"]["coin_gets"], game_screen)
            return True
        return False

    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        self.attack_types = random.choice(["large_cross", "nearest", "small_cross", "small_cross small_x", "farthest"])
        return 0


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:

        self.upgrade = upgrade
            
        super().__init__(owner=owner, job_and_color="ASSC", health=health if not upgrade else card_settings["ASS"]["upgrade_health"], damage=damage if not upgrade else card_settings["ASS"]["upgrade_damage"], board_x=board_x, board_y=board_y)
    
        if self.upgrade:
            self.anger = True
    
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)

    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + card_settings["ASS"]["damage_bonus"]
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        get_coins(self, card_settings["ASS"]["coin_gets"], game_screen)
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        self.upgrade = upgrade
        
        super().__init__(owner=owner, job_and_color="APTC", health=health if not upgrade else card_settings["APT"]["upgrade_health"], damage=damage if not upgrade else card_settings["APT"]["upgrade_damage"], board_x=board_x, board_y=board_y)
    
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)

    def damage_reduce(self, value: int, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        value -= game_screen.players_coin[self.owner]//card_settings["APT"]["coin_per_damage_resistance"] if game_screen.players_coin[self.owner]//card_settings["APT"]["coin_per_damage_resistance"] <= card_settings["APT"]["maximum_damage_resistance"] else card_settings["APT"]["maximum_damage_resistance"]
        return value if value > 0 else 0
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        get_coins(self, card_settings["APT"]["coin_gets"], game_screen)
        return 0


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        self.upgrade = upgrade
        
        super().__init__(owner=owner, job_and_color="SPC", health=health if not upgrade else card_settings["SP"]["upgrade_health"], damage=damage if not upgrade else card_settings["SP"]["upgrade_damage"], board_x=board_x, board_y=board_y)
    
    def update(self, game_screen: GameScreen) -> None:
        if self.text_color is not None and self.upgrade:
            draw_text("(+)", game_screen.mid_text_font, self.text_color,
                            ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.388),
                            (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.41), game_screen.surface)
        self.display_update(game_screen)
        
    def deploy(self, game_screen: GameScreen) -> Card:
        get_coins(self, card_settings["SP"]["coin_gets"], game_screen)
        return self
