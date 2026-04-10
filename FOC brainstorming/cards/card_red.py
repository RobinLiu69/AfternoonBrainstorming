# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright 2024-2026 Robin Liu / FOC Studio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------

from typing import TYPE_CHECKING

from core.game_state import GameState
from core.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card


card_settings = CARD_SETTING["Red"]
color_code = "R"


class RedCard(Card):
    pass


class Adc(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        self.damage += card_settings["ADC"]["damage_increase"]
        for card in game_state.get_all_cards():
            if card.owner == self.owner and card.job_and_color == "SPR":
                card.damage += card_settings["ADC"]["damage_increase"]
        return True


class Ap(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        value = int(target.damage * (card_settings["AP"]["attack_steal_rate"]/100))
        self.damage += value
        target.damage -= value
        
        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.damage += value
        return True


class Tank(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, game_state: GameState) -> bool:
        for card in self.detection(
            "nearest", filter(
                lambda card: card != self, game_state.get_player_cards(self.owner)
            ), game_state
        ):
            card.armor += card_settings["TANK"]["armor_increase"]
        
        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.armor += card_settings["TANK"]["armor_increase"]
        return True


class Hf(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        self.health -= card_settings["HF"]["health_decrease"]
        if self.health == 0:
            self.anger = True
        
        self.damage += card_settings["HF"]["damage_increase"]

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.damage += card_settings["HF"]["damage_increase"]
        return True

    def can_be_killed(self, game_state: GameState) -> bool:
        if self.anger:
            return False
        else:
            return True
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness:
            if clear_numbness and self.anger:
                self.anger = False
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            if self.anger:
                if clear_numbness:
                    self.anger = False
                return 0
            return 1


class Lf(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage: int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        self.armor += card_settings["LF"]["armor_increase"]
        self.damage += card_settings["LF"]["damage_increase"]

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.armor += card_settings["LF"]["armor_increase"]
            card.damage += card_settings["LF"]["damage_increase"]
        return True


class Ass(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage: int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        for card in self.detection("nearest", filter(lambda card: card != self, game_state.get_player(self.owner).on_board), game_state):
            card.damage += card_settings["ASS"]["damage_increase"]

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.damage += card_settings["ASS"]["damage_increase"]
        return True


class Apt(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage: int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        for card in self.detection("nearest", filter(lambda card: card != self, game_state.get_player(self.owner).on_board), game_state):
            card.armor += card_settings["APT"]["armor_increase"]
            card.damage += card_settings["APT"]["damage_increase"]
        
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.armor += card_settings["APT"]["armor_increase"]
            card.damage += card_settings["APT"]["damage_increase"]
        
        self.armor += card_settings["APT"]["armor_increase"]
        self.damage += card_settings["APT"]["damage_increase"]
        return True


class Sp(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage: int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPR", health=health, damage=damage, board_x=board_x, board_y=board_y)


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)