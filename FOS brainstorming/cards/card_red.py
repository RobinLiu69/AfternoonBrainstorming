# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING

from shared.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card

if TYPE_CHECKING:
    from core.game_state import GameState


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
        increase = card_settings["ADC"]["damage_increase"]
        self.adjust_stats(game_state, damage=increase)
        for card in game_state.get_all_cards():
            if card.owner == self.owner and card.job_and_color == "SPR":
                card.adjust_stats(game_state, damage=increase)
        return True


class Ap(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        value = int(target.damage * (card_settings["AP"]["attack_steal_rate"]/100))
        self.adjust_stats(game_state, damage=value)
        target.adjust_stats(game_state, damage=-value)

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.adjust_stats(game_state, damage=value)
        return True


class Tank(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def on_attacked_by(self, attacker: Card, value: int, game_state: GameState) -> bool:
        for card in self.detection(
            "nearest", filter(
                lambda card: card != self, game_state.get_player_cards(self.owner)
            ), game_state
        ):
            card.adjust_stats(game_state, armor=card_settings["TANK"]["armor_increase"])

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.adjust_stats(game_state, armor=card_settings["TANK"]["armor_increase"])
        return True


class Hf(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        loss = card_settings["HF"]["health_decrease"]
        increase = card_settings["HF"]["damage_increase"]
        if self.health - loss <= 0:
            self.anger = True

        self.adjust_stats(game_state, health=-loss, damage=increase)

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.adjust_stats(game_state, damage=increase)
        return True

    def on_can_be_killed(self, game_state: GameState) -> bool:
        if self.anger:
            return False
        else:
            return True
    
    def on_settle(self, clear_numbness: bool=True) -> int:
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
        armor = card_settings["LF"]["armor_increase"]
        increase = card_settings["LF"]["damage_increase"]
        self.adjust_stats(game_state, armor=armor, damage=increase)

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.adjust_stats(game_state, armor=armor, damage=increase)
        return True


class Ass(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage: int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def on_kill(self, victim: Card, game_state: GameState) -> bool:
        increase = card_settings["ASS"]["damage_increase"]
        for card in self.detection("nearest", filter(lambda card: card != self, game_state.get_player(self.owner).on_board), game_state):
            card.adjust_stats(game_state, damage=increase)

        for card in filter(lambda card: card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.adjust_stats(game_state, damage=increase)
        return True


class Apt(RedCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage: int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTR", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        armor = card_settings["APT"]["armor_increase"]
        increase = card_settings["APT"]["damage_increase"]
        for card in self.detection("nearest", filter(lambda card: card != self, game_state.get_player(self.owner).on_board), game_state):
            card.adjust_stats(game_state, armor=armor, damage=increase)

        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "SPR", game_state.get_player(self.owner).on_board):
            card.adjust_stats(game_state, armor=armor, damage=increase)

        self.adjust_stats(game_state, armor=armor, damage=increase)
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