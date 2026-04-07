from typing import TYPE_CHECKING

from core.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card


if TYPE_CHECKING:
    from core.game_state import GameState


card_settings = CARD_SETTING["DarkGreen"]
color_code = "DKG"


class DarkGreenCard(Card):
    def engraved_totem(self, times: int, game_state: GameState) -> None:
        for i in range(times):
            game_state.players_totem[self.owner] += 1 * (card_settings["SP"]["engraved_totem_coefficient"]**len(tuple(filter(lambda card: card.job_and_color == "SPDKG", game_state.get_player_cards(self.owner)))))


class Adc(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ADCDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def update(self, game_state: GameState) -> None:
        self.extra_damage = game_state.players_totem[self.owner] // card_settings["ADC"]["damage_divisor"]
    
    def damage_bonus(self, value: int, victim: Card, game_state: GameState) -> int:
        return value + self.extra_damage


class Ap(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        self.engraved_totem(card_settings["AP"]["engraved_totem"], game_state)
        return True


class Tank(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: "Card", value: int, game_state: GameState) -> bool:
        self.engraved_totem(card_settings["TANK"]["engraved_totem"], game_state)
        return True


class Hf(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:

        self.extra_damage = 0
        
        super().__init__(owner=owner, job_and_color="HFDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        self.heal(1, game_state)
        return True
    
    def start_turn(self, game_state: GameState) -> int:
        self.damage_calculate(2, self, game_state, False)
        self.engraved_totem(card_settings["HF"]["engraved_totem"], game_state)
        return 0


class Lf(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        for target in self.detection("small_cross", tuple(filter(lambda card: card.health > 0, game_state.get_side_cards(self.owner, True)))):
            target.damage_calculate(game_state.players_totem[self.owner]//4, self, game_state)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        self.engraved_totem(card_settings["LF"]["engraved_totem"], game_state)
        return True
    

class Ass(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        self.health = 0
        self.engraved_totem(card_settings["ASS"]["engraved_totem"], game_state)
        return True


class Apt(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["APT"]["health"],
                 damage: int = card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def update(self, game_state: GameState) -> None:
        self.extra_damage = game_state.players_totem[self.owner] // 2
    
    def damage_bonus(self, value: int, victim: Card, game_state: GameState) -> int:
        self.engraved_totem(self.armor//2, game_state)
        return value + self.extra_damage
    
    def after_damage_calculated(self, target: Card, value: int, game_state: GameState) -> bool:
        self.armor += value//2
        return True
    

class Sp(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)