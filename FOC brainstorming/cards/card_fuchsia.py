import math
from typing import Callable, Generator, Iterable, TYPE_CHECKING
from itertools import chain

from core.game_state import GameState, CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card, most_frequent_elements

if TYPE_CHECKING:
    from core.game_state import GameState

card_settings = CARD_SETTING["Fuchsia"]
color_code = "F"


class FuchsiaCard(Card):
    def __init__(self, owner: str, job_and_color: str, health: int, damage: int, board_x: int, board_y: int) -> None:

        super().__init__(owner=owner, job_and_color=job_and_color, health=health, damage=damage, board_x=board_x, board_y=board_y)

        self.shadows: list[Shadow] = []
    
    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        for shadow in self.shadows:
            if shadow.movable:
                shadow.board_x, shadow.board_y = game_state.board_config.get_symmetric_pos(board_x, board_y)

    def spawn_shadow(self, owner: str, board_x: int, board_y: int, attack_types: str, movable: bool=True) -> None:
        self.shadows.append(Shadow(owner, board_x, board_y, self, attack_types, movable))


class Shadow(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, linker: FuchsiaCard, attack_types: str, movable: bool) -> None:
        
        super().__init__(owner=owner, job_and_color="SHADOW", health=1, damage=0, board_x=board_x, board_y=board_y)
        self.attack_types = attack_types
        self.movable = movable
        self.linker = linker
        self.job = self.linker.job

    def heal(self, value: int, game_state: GameState) -> bool:
        return False
    
    def draw_shape(self, game_state: GameState) -> None:
        if not self.surface: return
        match self.linker.job:
            case "AP":
                self.shape = tuple(map(lambda coordinate: (coordinate + game_state.game_screen.block_size*0.05), self.linker.shaped(game_state.game_screen.block_size)))
            case _:
                self.shape = tuple(map(lambda coordinate: (coordinate[0]+ game_state.game_screen.block_size*0.05, coordinate[1]+ game_state.game_screen.block_size*0.05), self.linker.shaped(game_state.game_screen.block_size)))
        self.color = (159, 0, 80, 100)
    
    def update(self, game_state: GameState) -> None:
        self.display_update(game_state)
    
    def ability(self, target: "Card", game_state: GameState) -> bool:
        self.linker.hit_cards.append(target)
        return False

    def damage_block(self, value: int, attacker: "Card", game_state: GameState) -> bool:
        if self.linker.job_and_color == "APTF":
            self.linker.armor += value//2
        return False
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        match self.linker.job_and_color:
            case "ASSF":
                self.linker.spawn_shadow(self.owner, victim.board_x, victim.board_y, self.attack_types)
                return False
            case _:
                return False
    
    def die(self, game_state: GameState) -> bool:
        cards = tuple(filter(lambda card: card.health > 0 and self.board_x == card.board_x and self.board_y == card.board_y, game_state.get_all_cards()))
        if not cards:
            game_state.board_dict[self.board_x, self.board_y].occupy = False
        return False

    
    def attack(self, game_state: GameState) -> bool:
        enemies: Iterable["Card"] = list(filter(lambda card: card.health > 0 and card.job_and_color != "SHADOW", game_state.get_side_cards(self.owner, True)))
        if self.linker.launch_attack(self.attack_types, game_state, tuple(self.detection(self.attack_types, enemies))):
            return True
        else:
            return False
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        return 0
        
        
class Adc(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)
        
    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            for shadow in self.shadows:
                shadow.attack(game_state)
            self.hit_cards.clear()
            return True
        else:
            if not self.numbness:
                count = 0
                for shadow in self.shadows:
                    if shadow.attack(game_state):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)
        self.display_update(game_state)
    

class Ap(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APF", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)
        
        for shadow in self.shadows:
            enemies = tuple(filter(lambda card: card.health > 0 and shadow.is_same_location(card), game_state.get_side_cards(self.owner, True)))
            for enemy in enemies:
                enemy.numbness = True
        
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        return True

    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)
        self.display_update(game_state)

    def start_turn(self, game_state: GameState) -> int:
        for shadow in self.shadows:
            enemies = tuple(filter(lambda card: card.health > 0 and shadow.is_same_location(card), game_state.get_side_cards(self.owner, True)))
            for enemy in enemies:
                enemy.numbness = True
        return 0
    

class Tank(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)
            
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            game_state.board_dict[shadow.board_x, shadow.board_y].occupy = True
            shadow.update(game_state)
        self.display_update(game_state)
    
    def die(self, game_state: GameState) -> bool:
        for shadow in self.shadows:
            shadow.die(game_state)
        return False

    
class Hf(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)

    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            for shadow in self.shadows:
                shadow.attack(game_state)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in self.shadows:
                    if shadow.attack(game_state):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)
        self.display_update(game_state)
    

class Lf(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFF", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, "nearest")

    def attack(self, game_state: GameState) -> bool:
        if self.launch_attack(self.attack_types, game_state):
            for shadow in self.shadows:
                shadow.attack(game_state)
            
            for target in (most_frequent_elements(self.hit_cards, 1)):
                target.damage_calculate(self.damage, self, game_state)
            self.hit_cards.clear()
            return True
        return False
    
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)
        self.display_update(game_state)


class Ass(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
    def attack_area_display(self, game_state: GameState) -> Iterable[tuple[int, int]]:
        return self.attack_area_display(game_state)
        for shadow in self.shadows:
            yield from shadow.attack_area_display(game_state)


    def killed(self, victim: Card, game_state: GameState) -> bool:
        self.spawn_shadow(self.owner, victim.board_x, victim.board_y, self.attack_types)
        return False
    
    def die(self, game_state: GameState) -> bool:
        for shadow in self.shadows:
            shadow.die(game_state)
        return False
    
    def attack(self, game_state: GameState) -> bool:
        temp_shadow_list = self.shadows.copy()
        if self.launch_attack(self.attack_types, game_state):
            for shadow in temp_shadow_list:
                shadow.attack(game_state)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in temp_shadow_list:
                    if shadow.attack(game_state):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            del temp_shadow_list
            return False
    
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)
        self.display_update(game_state)


class Apt(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTF", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)
    
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)
        self.display_update(game_state)

    def on_field_effect_trigger(self, victim: Card, value: int, attacker: Card, game_state: GameState) -> tuple[int, int, Callable[[Card, int, Card, GameState], None] | None] | None:
        for shadow in self.shadows:
            if (self.health > 0 and victim.owner == self.owner and shadow.is_same_location(victim) and victim != self):
                self.armor += math.floor(value * 0.5)
                return (20, math.ceil(value * 0.5), None)
        return None


class Sp(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        targets: tuple[FuchsiaCard] = tuple(filter(lambda card: card.health > 0 and isinstance(card, FuchsiaCard), game_state.get_player_cards(self.owner))) # pyright: ignore[reportAssignmentType]
        if targets:
            for card in self.detection("farthest", targets):
                board_x, board_y = game_state.board_config.get_symmetric_pos(card.board_x, card.board_y)
                card.spawn_shadow(self.owner, board_x, board_y, card.attack_types, False)


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)