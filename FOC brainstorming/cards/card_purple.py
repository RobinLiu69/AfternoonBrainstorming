from typing import TYPE_CHECKING

from core.game_state import GameState
from core.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card


card_settings = CARD_SETTING["Purple"]
color_code = "P"


class PurpleCard(Card):
    pass


class Adc(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ap(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        for target in self.detection(
            "nearest",
            tuple(
                filter(
                    lambda card: card.owner != self.owner and
                    card.health > 0, 
                    game_state.get_opponent_cards(self.owner)
                )
            ), game_state
        ):
            target.armor = 0
            target.damage = target.original_damage
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        target.armor = 0
        target.damage = target.original_damage
        return True


class Tank(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def move_broadcast(self, target: Card, game_state: GameState) -> bool:
        if target.owner != self.owner:
            target.damage_calculate(card_settings["TANK"]["movement_damage"], self, game_state)
            return True
        return False


class Hf(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def start_turn(self, game_state: GameState) -> int:
        if self.attack_types:
            count = len(tuple(self.detection(self.attack_types, game_state.get_opponent_cards(self.owner), game_state)))
            game_state.number_of_attacks[self.owner] += count // 3
        return 0


class Lf(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ass(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSP", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        count: int = min(len(game_state.get_player_cards(victim.owner))-len(game_state.get_player_cards(self.owner))-card_settings["ASS"]["unit_gap"], card_settings["ASS"]["maximum_card_draw_from_killed"])
        for i in range(count):
            game_state.card_to_draw[self.owner] += 1
        return True


class Apt(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["APT"]["health"],
                 damage: int = card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTP", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Sp(PurpleCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPP", health=health, damage=damage, board_x=board_x, board_y=board_y)


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)