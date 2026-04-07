import random
from typing import TYPE_CHECKING, Optional

from core.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card


if TYPE_CHECKING:
    from core.game_state import GameState


card_settings = CARD_SETTING["Cyan"]
color_code = "C"


class CyanCard(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, job_and_color: str,
                 health: int, damage:int) -> None:
        
        super().__init__(owner=owner, job_and_color=job_and_color,
                         health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.upgrade: bool = False
        
    def get_coins(self, value: int, game_state: GameState) -> None:
        game_state.players_coin[self.owner] = game_state.players_coin[self.owner] + value if game_state.players_coin[self.owner] + value <= 50 else 50

    @staticmethod
    def price_check(owner: str, job: str, game_state: GameState) -> bool:
        cyan_cards: filter[CyanCard] = filter(lambda card: isinstance(card, CyanCard), game_state.get_both_player_cards()) # pyright: ignore[reportAssignmentType]
        price = card_settings[job]["cost"]- (card_settings["SP"]["coin_reduced"]*len(tuple(filter(lambda card: card.job_and_color == "SPC" and card.upgrade and card.owner == owner, cyan_cards))))
        if game_state.players_coin[owner] >= price:
            game_state.players_coin[owner] -= price
            return True
        else:
            return False
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["upgrade"] = self.upgrade
        return data
 
    def apply_dict(self, data: dict) -> None:
        super().apply_dict(data)
        self.upgrade = data["upgrade"]


class Adc(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCC",
                         health=health if not upgrade else card_settings["ADC"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["ADC"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)
        self.upgrade = upgrade
        
    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)
    
    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            if self.upgrade:
                self.launch_attack(self.attack_types, game_state)
            self.hit_cards.clear()
            return True
        else:
            return False
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        self.get_coins(card_settings["ADC"]["coin_gets"], game_state)
        return True


class Ap(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
    
        super().__init__(owner=owner, job_and_color="APC",
                         health=health if not upgrade else card_settings["AP"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["AP"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)

        self.upgrade = upgrade
        self.target: Optional[Card] = None
    
    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)
    
    def deploy(self, game_state: GameState) -> None:
        for target in self.detection("nearest", game_state.get_opponent_cards(self.owner)):
            self.target = target

    def after_attack_broadcast(self, attacker: "Card", target: "Card", game_state: GameState) -> bool:
        if attacker.attack_types and attacker.owner == self.owner:
            if any(item in attacker.attack_types for item in ["nearest", "farthest"]):
                if self.target:
                    if self.target.damage_calculate(attacker.damage, attacker, game_state):
                        if self.upgrade: self.get_coins(card_settings["AP"]["coin_gets"], game_state)
        return False
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        return True


class Tank(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKC",
                         health=health if not upgrade else card_settings["TANK"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["TANK"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)
        
        self.upgrade = upgrade

        if upgrade:
            self.anger = True
        
    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)

    def damage_block(self, value: int, attacker: Card, game_state: GameState) -> bool:
        if self.anger:
            self.anger = False
            return True
        else:
            return False
        
    def been_attacked(self, attacker: Card, value: int, game_state: GameState) -> bool:
        self.get_coins(card_settings["TANK"]["coin_gets"], game_state)
        return True


class Hf(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:

        self.count = 1        
        super().__init__(owner=owner, job_and_color="HFC",
                         health=health if not upgrade else card_settings["HF"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["HF"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)
        
        self.upgrade = upgrade
        
    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)

    def ability(self, target: Card, game_state: GameState) -> bool:
        self.get_coins(card_settings["HF"]["coin_gets"], game_state)
        return True

    def been_killed(self, attacker: Card, game_state: GameState) -> bool:
        if self.upgrade == True:
            self.anger = True
            self.damage += card_settings["HF"]["damage_bonus"]
        return True
    
    def can_be_killed(self, game_state: GameState) -> bool:
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


class Lf(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int=card_settings["LF"]["health"],
                 damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFC",
                         health=health if not upgrade else card_settings["LF"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["LF"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)
        
        self.upgrade = upgrade

    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)

    def ability(self, target: Card, game_state: GameState) -> bool:
        self.get_coins(card_settings["LF"]["coin_gets"], game_state)
        return False

    def start_turn(self, game_state: GameState) -> int:
        if self.upgrade:
            self.attack_types = random.choice(["large_cross", "nearest", "small_cross", "small_cross small_x", "farthest"])
        return 0


class Ass(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int=card_settings["ASS"]["health"],
                 damage:int=card_settings["ASS"]["damage"]) -> None:
 
        super().__init__(owner=owner, job_and_color="ASSC",
                         health=health if not upgrade else card_settings["ASS"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["ASS"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)
        
        self.upgrade = upgrade

        if self.upgrade:
            self.anger = True
            self.extra_damage = card_settings["ASS"]["damage_bonus"]
    
    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)

    def damage_bonus(self, value: int, victim: Card, game_state: GameState) -> int:
        self.anger = False
        value += self.extra_damage
        self.extra_damage = 0
        return value
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        self.get_coins(card_settings["ASS"]["coin_gets"], game_state)
        return True


class Apt(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int = card_settings["APT"]["health"],
                 damage: int = card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTC", health=health if not upgrade else card_settings["APT"]["upgrade_health"], damage=damage if not upgrade else card_settings["APT"]["upgrade_damage"], board_x=board_x, board_y=board_y)
        
        self.upgrade = upgrade

    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)

    def damage_reduce(self, value: int, game_state: GameState) -> int:
        value -= game_state.players_coin[self.owner]//card_settings["APT"]["coin_per_damage_resistance"] if game_state.players_coin[self.owner]//card_settings["APT"]["coin_per_damage_resistance"] <= card_settings["APT"]["maximum_damage_resistance"] else card_settings["APT"]["maximum_damage_resistance"]
        return value if value > 0 else 0
    
    def start_turn(self, game_state: GameState) -> int:
        self.get_coins(card_settings["APT"]["coin_gets"], game_state)
        return 0


class Sp(CyanCard):
    def __init__(self, owner: str, board_x: int, board_y: int, upgrade: bool=False,
                 health: int=card_settings["SP"]["health"],
                 damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPC",
                         health=health if not upgrade else card_settings["SP"]["upgrade_health"],
                         damage=damage if not upgrade else card_settings["SP"]["upgrade_damage"],
                         board_x=board_x, board_y=board_y)
        
        self.upgrade = upgrade

    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.upgrade:
    #         draw_text("(+)", game_state.game_screen.mid_text_font, self.text_color, (game_state.game_screen.block_size*0.388), (game_state.game_screen.block_size*0.41), self.surface)
        
    def deploy(self, game_state: GameState) -> None:
        self.get_coins(card_settings["SP"]["coin_gets"], game_state)


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)