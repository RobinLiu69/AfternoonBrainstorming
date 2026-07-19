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


card_settings = CARD_SETTING["Brown"]
color_code = "BR"


class BrownCard(Card):
    effects_disabled: bool = False

    def is_giant(self, card: Card) -> bool:
        return card.color_name == "Brown"

    def effects_off(self) -> bool:
        return self.effects_disabled
    
    def deploy(self, game_state: GameState) -> None:
        if any(card for card in game_state.get_player_cards(self.owner) if card.job_and_color == "SPBR" and card.anger):
            self.effects_disabled = True
        return


class Adc(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ADCBR", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_attack(self, game_state: GameState) -> bool:
        attacked = self.launch_attack(self.attack_types, game_state)
        self.hit_cards.clear()
        if attacked and not self.effects_off():
            self.numbness = True
        return attacked


class Ap(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APBR", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def ability(self, target: Card, game_state: GameState) -> bool:
        if self.effects_off():
            return False
        game_state.card_to_draw[game_state.get_opponent_name(self.owner)] += card_settings["AP"]["on_attack_enemy_draw"]
        return True

class Tank(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="TANKBR", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.attacked_this_turn = False
    
    def on_attacked_by(self, attacker: Card, value: int, game_state: GameState) -> bool:
        if not self.effects_off():
            for card in self.detection(
                "nearest", filter(
                    lambda card: card != self, game_state.get_player_cards(self.owner)
                ), game_state
            ):
                card.numbness = True
        return True


class Hf(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="HFBR", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.attack_uses = card_settings["HF"]["attack_uses"]

    def on_attack(self, game_state: GameState) -> bool:
        attack_success = super().on_attack(game_state)
        if self.effects_disabled:
            self.attack_uses = 1
        else:
            self.attack_uses = 2
        return attack_success


class Lf(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="LFBR", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_kill(self, victim: Card, game_state: GameState) -> bool:
        if self.effects_off():
            return False
        points = card_settings["LF"]["on_kill_enemy_points"]
        if self.owner == "player1":
            game_state.score += points
        else:
            game_state.score -= points
        return True


class Ass(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ASSBR", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_kill(self, victim: Card, game_state: GameState) -> bool:
        if self.effects_off():
            return False
        
        game_state.skip_turn_draw[self.owner] = True
        return True


class Apt(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["APT"]["health"],
                 damage: int = card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTBR", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
    def deploy(self, game_state: GameState) -> None:
        super().deploy(game_state)
        if self.effects_off():
            return
        shield = card_settings["APT"]["on_play_enemy_shield"]
        for card in game_state.get_opponent_cards(self.owner):
            if card.health > 0:
                card.armor += shield
                
    def on_refresh(self, game_state: GameState) -> int:
        if self.effects_off():
            return 0
        shield = card_settings["APT"]["on_refresh_enemy_shield"]
        for card in game_state.get_opponent_cards(self.owner):
            if card.health > 0:
                card.armor += shield
        return 0

    def ability(self, target: Card, game_state: GameState) -> bool:
        buff = card_settings["APT"]["on_attack_buff_nearest_ally"]
        bonus = card_settings["APT"]["bonus_if_giant"]
        for ally in self.detection(
            "nearest",
            filter(lambda card: card != self and card.health > 0, game_state.get_player_cards(self.owner)),
            game_state
        ):
            ally.damage += buff["atk"]
            ally.armor += buff["armor"]
            if self.is_giant(ally):
                ally.damage += bonus["atk"]
                ally.armor += bonus["armor"]
        return True


class Sp(BrownCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPBR", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def ability(self, target: Card, game_state: GameState) -> bool:
        self.anger = True
        for card in game_state.get_player_cards(self.owner):
            if card is not self and isinstance(card, BrownCard):
                card.effects_disabled = True
        return True
    
    def set_nullify(self, nullify: bool, game_state: GameState) -> None:
        if nullify:
            for card in game_state.get_player_cards(self.owner):
                if card is not self and isinstance(card, BrownCard):
                    card.effects_disabled = False
        return
    
    def on_killed_by(self, attacker: Card, game_state: GameState) -> bool:
        for card in game_state.get_player_cards(self.owner):
            if card is not self and isinstance(card, BrownCard):
                card.effects_disabled = False
        return True


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)
