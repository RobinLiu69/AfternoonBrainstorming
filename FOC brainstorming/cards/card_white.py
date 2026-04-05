from typing import TYPE_CHECKING

from core.game_state import GameState
from core.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card, CardRenderData

card_settings = CARD_SETTING["White"]
color_code = "W"


class Cube(Card):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["CUBE"]["health"],
                 damage: int = card_settings["CUBE"]["damage"]) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral",
                         job_and_color="CUBE" if owner == "display" else "CUBE",
                         health=health, damage=damage, board_x=board_x, board_y=board_y)

    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 0

class Cubes(Card):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["CUBE"]["health"],
                 damage: int = card_settings["CUBE"]["damage"]) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral",
                         job_and_color="CUBES" if owner == "display" else "CUBE",
                         health=health, damage=damage, board_x=board_x, board_y=board_y)


class Heal(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral",
                         job_and_color="HEAL", health=health, damage=damage,
                         board_x=board_x, board_y=board_y)


class Move(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=-1, damage:int=-1) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral",
                         job_and_color="MOVE", health=health, damage=damage,
                         board_x=board_x, board_y=board_y)


CardFactory.register("CUBE", Cube)
CardFactory.register("CUBES", Cubes)
CardFactory.register("HEAL", Heal)
CardFactory.register("MOVE", Move)


class WhiteCard(Card):
    pass


class Adc(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ap(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APW", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        return True


class Tank(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Hf(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Lf(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Ass(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSW", health=health, damage=damage, board_x=board_x, board_y=board_y)


class Apt(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTW", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        for card in self.detection(
            "nearest", filter(
                lambda card: card.owner == self.owner and
                card != self,
                game_state.get_player(self.owner).on_board
            )
        ):
            card.armor += self.damage
        self.armor += self.damage
        return True


class Sp(WhiteCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPW", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True:
            if  clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1 + card_settings["SP"]["extra_score"]


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)