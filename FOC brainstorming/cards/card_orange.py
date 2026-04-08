from typing import TYPE_CHECKING
from core.game_state import GameState
from core.setting import CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card


card_settings = CARD_SETTING["Orange"]
color_code = "O"


class OrangeCard(Card):
    pass


class Adc(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCO", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            self.moving = True
            self.hit_cards.clear()
            return True
        else:
            return False
    
    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        self.launch_attack(self.attack_types, game_state)
        

class Ap(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        return True
    
    def start_turn(self, game_state: GameState) -> int:
        game_state.get_player(self.owner).hand.append("MOVEO")
        return 0


class Tank(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, game_state: GameState) -> bool:
        game_state.get_player(self.owner).hand.append("MOVEO")
        return True


class Hf(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            self.moving = True
            self.hit_cards.clear()
            return True
        else:
            return False
        
    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        self.extra_damage += card_settings["HF"]["extra_damage_from_moving"]
        self.anger = True
    
    def damage_bonus(self, value: int, victim: Card, game_state: GameState) -> int:
        return value + self.extra_damage
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if clear_numbness:
            self.extra_damage = 0
            self.anger = False
        if self.numbness:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1


class Lf(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            self.moving = True
            self.hit_cards.clear()
            return True
        else:
            return False
        
    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        for card in self.detection("nearest", filter(lambda card: card != self, game_state.get_opponent_cards(self.owner)), game_state):
            card.damage_calculate(self.damage, self, game_state)


class Ass(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSO", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        self.anger = True
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        self.moving = True
        if self.anger:
            game_state.number_of_attacks[self.owner] += card_settings["ASS"]["number_of_attack_increase_from_killed"]
            self.anger = False
        return True
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if clear_numbness:
            self.anger = False
        if self.numbness:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1


class Apt(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int=card_settings["APT"]["health"],
                 damage:int=card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTO", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        self.armor += card_settings["APT"]["armor_get_from_moving"]
        value = self.armor // 2
        if value > 0:
            self.damage += value
            self.armor = self.armor % 2

    def move_broadcast(self, target: Card, game_state: GameState) -> bool:
        if target.owner == self.owner and target != self:
            target.armor += card_settings["APT"]["armor_get_from_moving"]
            self.armor += card_settings["APT"]["armor_get_from_moving"]
        return True
    

class Sp(OrangeCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPO", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def move_broadcast(self, target: Card, game_state: GameState) -> bool:
        if target.owner == self.owner:
            for card in self.detection("farthest", game_state.get_side_cards(self.owner, True), game_state):
                card.damage_calculate(card_settings["SP"]["movement_damage"], self, game_state)
        return True


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)