import math
from typing import Callable, Iterable, TYPE_CHECKING

from core.neutral import Neutral
from core.player import Player
from cards.card import Board, Card, most_frequent_elements
from core.game_screen import GameScreen, Fuchsia_setting, FUCHSIA, BOARD_SIZE

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral

card_settings = Fuchsia_setting


class FuchsiaCard(Card):
    def __init__(self, owner: str, job_and_color: str, health: int, damage: int, board_x: int, board_y: int) -> None:

        super().__init__(owner=owner, job_and_color=job_and_color, health=health, damage=damage, board_x=board_x, board_y=board_y)

        self.shadows: list[Shadow] = []
    
    def after_movement(self, board_x: int, board_y: int, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            if shadow.anger:
                shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                shadow.board_y = BOARD_SIZE[1] - 1 - board_y

    def spawn_shadow(self, owner: str, self_board_x: int, self_board_y: int, attack_types: str, movable: bool=True) -> None:
        self.shadows.append(Shadow(owner, BOARD_SIZE[0]-1-self_board_x, BOARD_SIZE[1]-1-self_board_y, self, attack_types, movable))



class Shadow(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, linker: FuchsiaCard, attack_types: str, movable: bool) -> None:
        
        super().__init__(owner=owner, job_and_color="SHADOW", health=1, damage=0, board_x=board_x, board_y=board_y)
        self.attack_types = attack_types
        self.movable = movable
        self.linker = linker
        self.job = self.linker.job

    def heal(self, value: int, game_screen: GameScreen) -> bool:
        return False
    
    def draw_shape(self, game_screen: GameScreen) -> None:
        if not self.surface: return
        match self.linker.job:
            case "AP":
                self.shape = tuple(map(lambda coordinate: (coordinate + game_screen.block_size*0.05), self.linker.shaped(game_screen.block_size)))
            case _:
                self.shape = tuple(map(lambda coordinate: (coordinate[0]+game_screen.block_size*0.05, coordinate[1]+game_screen.block_size*0.05), self.linker.shaped(game_screen.block_size)))
        self.color = (159, 0, 80, 100)
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.display_update(game_screen)
    
    def ability(self, target: "Card", player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.linker.hit_cards.append(target)
        return False

    def damage_block(self, value: int, attacker: "Card", player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.linker.job_and_color == "APTF":
            self.linker.armor += value//2
        return False
    
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        match self.linker.job_and_color:
            case "ASSF":
                self.linker.spawn_shadow(self.owner, BOARD_SIZE[1]-1-victim.board_x, BOARD_SIZE[1]-1-victim.board_y, self.attack_types)
                return False
            case _:
                return False
    
    def die(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        cards = tuple(filter(lambda card: card.health > 0 and self.board_x == card.board_x and self.board_y == card.board_y, neutral.on_board + player1.on_board + player2.on_board))
        if not cards:
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
        return False

    
    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        enemies: Iterable["Card"] = list(filter(lambda card: card.owner != self.owner and card.health > 0 and card.job_and_color != "SHADOW", neutral.on_board + player1.on_board + player2.on_board))
        if self.linker.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen, tuple(self.detection(self.attack_types, enemies))):
            return True
        else:
            return False
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        return 0
        
        
class Adc(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
        if self.owner != "display":
            self.spawn_shadow(owner, board_x, board_y, self.attack_types)
        
    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.attack(player1, player2, neutral, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in self.shadows:
                    if shadow.attack(player1, player2, neutral, board_dict, game_screen):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)
    

class Ap(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        if self.owner != "display":
            self.spawn_shadow(owner, board_x, board_y, self.attack_types)

    def deploy(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        for shadow in self.shadows:
            enemies = tuple(filter(lambda card: card.owner != self.owner and card.health > 0 and shadow.board_x == card.board_x and shadow.board_y == card.board_y, neutral.on_board + player1.on_board + player2.on_board))
            for enemy in enemies:
                enemy.numbness = True
        return self
        
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True

    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)

    def start_turn(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        for shadow in self.shadows:
            enemies = tuple(filter(lambda card: card.owner != self.owner and card.health > 0 and shadow.board_x == card.board_x and shadow.board_y == card.board_y, neutral.on_board + player1.on_board + player2.on_board))
            for enemy in enemies:
                enemy.numbness = True
        return 0
    

class Tank(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        if self.owner != "display":
            self.spawn_shadow(owner, board_x, board_y, self.attack_types)
            
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            board_dict[str(shadow.board_x)+"-"+str(shadow.board_y)].occupy = True
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)
    
    def die(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for shadow in self.shadows:
            shadow.die(player1, player2, neutral, board_dict, game_screen)
        return False

    

class Hf(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        if self.owner != "display":
            self.spawn_shadow(owner, board_x, board_y, self.attack_types)

    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.attack(player1, player2, neutral, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in self.shadows:
                    if shadow.attack(player1, player2, neutral, board_dict, game_screen):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)

    

class Lf(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        if self.owner != "display":
            self.spawn_shadow(owner, board_x, board_y, "nearest")

    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.attack(player1, player2, neutral, board_dict, game_screen)
            
            for target in (most_frequent_elements(self.hit_cards, 1)):
                target.damage_calculate(self.damage, self, player1, player2, neutral, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        return False
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)


class Ass(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.spawn_shadow(self.owner, BOARD_SIZE[1]-1-victim.board_x, BOARD_SIZE[1]-1-victim.board_y, self.attack_types)
        return False
    
    def die(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for shadow in self.shadows:
            shadow.die(player1, player2, neutral, board_dict, game_screen)
        return False
    
    def attack(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        temp_shadow_list = self.shadows.copy()
        if self.launch_attack(self.attack_types, player1, player2, neutral, board_dict, game_screen):
            for shadow in temp_shadow_list:
                shadow.attack(player1, player2, neutral, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in temp_shadow_list:
                    if shadow.attack(player1, player2, neutral, board_dict, game_screen):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            del temp_shadow_list
            return False
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)


class Apt(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        if self.owner != "display":
            self.spawn_shadow(owner, board_x, board_y, self.attack_types)
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1, player2, neutral, board_dict, game_screen)
        self.display_update(game_screen)
    
    def on_field_effect_trigger(self, victim: Card, value: int, attacker: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> tuple[int, int, Callable[[Card, int, Card, Player, Player, Neutral, dict[str, Board], GameScreen], None] | None] | None:
        for shadow in self.shadows:
            if (self.health > 0 and victim.owner == self.owner and shadow.is_same_location(victim) and victim != self):
                self.armor += math.floor(value * 0.5)
                return (20, math.ceil(value * 0.5), None)
        return None


class Sp(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        targets: tuple[FuchsiaCard] = tuple(filter(lambda card: card.owner == self.owner and card.health > 0 and isinstance(card, FuchsiaCard), neutral.on_board + player1.on_board + player2.on_board)) # pyright: ignore[reportAssignmentType]
        if targets:
            for card in self.detection("farthest", targets):
                    card.spawn_shadow(self.owner, self.board_x, self.board_y, card.attack_types, True)
        return self
