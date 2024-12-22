from dataclasses import dataclass, field
import os, json, pygame
import random
from typing import Iterable, Any, cast

from card import Board, Card, GameScreen, Fuchsia_setting, FUCHSIA, BOARD_SIZE, most_frequent_elements

card_settings = Fuchsia_setting


def spawn_shadow(owner: str, self_board_x: int, self_board_y: int, linker: Card, from_sp: bool=False) -> Card:
    return Shadow(owner, BOARD_SIZE[0]-1-self_board_x, BOARD_SIZE[1]-1-self_board_y, linker, from_sp)



class Shadow(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, linker: Card, movable: bool=True) -> None:
        
        super().__init__(owner=owner, job_and_color="SHADOW", health=1, damage=0, board_x=board_x, board_y=board_y)
        if not movable:
            self.anger = True
        self.linker = linker
        self.job = self.linker.job
        
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def heal(self, value: int, game_screen: GameScreen) -> bool:
        return False
    
    def draw_shape(self, game_screen: GameScreen) -> None:
        if self.surface is None: return
        match self.linker.job:
            case "AP":
                self.shape = tuple(map(lambda coordinate: (coordinate + game_screen.block_size*0.05), self.linker.shaped(game_screen.block_size)))
            case _:
                self.shape = tuple(map(lambda coordinate: (coordinate[0]+game_screen.block_size*0.05, coordinate[1]+game_screen.block_size*0.05), self.linker.shaped(game_screen.block_size)))
        self.color = (159, 0, 80, 100)
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.display_update(game_screen)
    
    def ability(self, target: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.linker.hit_cards.append(target)
        return False

    def damage_block(self, value: int, attacker: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.linker.job_and_color == "APTF":
            self.linker.armor += value//2
        return False
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        match self.linker.job_and_color:
            case "ASSF":
                shadow = spawn_shadow(self.owner, BOARD_SIZE[1]-1-victim.board_x, BOARD_SIZE[1]-1-victim.board_y, self.linker)
                self.linker.shadows.append(shadow)
                return False
            case _:
                return False
    
    def die(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        cards = tuple(filter(lambda card: card.health > 0 and self.board_x == card.board_x and self.board_y == card.board_y, on_board_neutral+player1_on_board+player2_on_board))
        if not cards:
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
        return False

    
    def launch_attack(self, attack_types: str | None, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.numbness or attack_types is None: return False
        game_screen.data.data_update("hit_count", f"{self.owner}_{self.job_and_color}", 1)
        enemies: Iterable["Card"] = tuple(filter(lambda card: card.owner != self.owner and card.health > 0 and card.job_and_color != "SHADOW", on_board_neutral+player1_on_board+player2_on_board))
        target_generator = tuple(self.detection(attack_types, enemies))
        
        if target_generator:
            for target in target_generator:
                target.damage_calculate(self.linker.damage, self.linker, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        else:
            return False
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        return 0
        
        
class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        if self.owner != "display":
            self.shadows.append(spawn_shadow(owner, board_x, board_y, self))
        
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in self.shadows:
                    if shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)
    
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for shadow in self.shadows:
                if not shadow.anger:
                    shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                    shadow.board_y = BOARD_SIZE[1] - 1 - board_y
                
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False
    

class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        if self.owner != "display":
            self.shadows.append(spawn_shadow(owner, board_x, board_y, self))
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        return True

    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            enemies = tuple(filter(lambda card: card.owner != self.owner and card.health > 0 and BOARD_SIZE[0]-1-self.board_x == card.board_x and BOARD_SIZE[1]-1-self.board_y == card.board_y, on_board_neutral+player1_on_board+player2_on_board))
            for enemy in enemies:
                self.ability(enemy, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)
    
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for shadow in self.shadows:
                if not shadow.anger:
                    shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                    shadow.board_y = BOARD_SIZE[1] - 1 - board_y
                
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False
    
    

class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        if self.owner != "display":
            self.shadows.append(spawn_shadow(owner, board_x, board_y, self))
            
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            board_dict[str(shadow.board_x)+"-"+str(shadow.board_y)].occupy = True
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)
    
    def die(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for shadow in self.shadows:
            shadow.die(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return False
    
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for shadow in self.shadows:
                if not shadow.anger:
                    shadow.die(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                    shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                    shadow.board_y = BOARD_SIZE[1] - 1 - board_y
                    board_dict[str(BOARD_SIZE[0] - 1 - board_x)+"-"+str(BOARD_SIZE[1] - 1 - board_y)].occupy = True
            
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False
    
    

class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        if self.owner != "display":
            self.shadows.append(spawn_shadow(owner, board_x, board_y, self))
        
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in self.shadows:
                    if shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)
        
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for shadow in self.shadows:
                if not shadow.anger:
                    shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                    shadow.board_y = BOARD_SIZE[1] - 1 - board_y
                
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False
    

class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        if self.owner != "display":
            self.shadows.append(spawn_shadow(owner, board_x, board_y, self))
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.hit_cards.append(target)
        return True

    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.launch_attack("nearest", player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for target in (most_frequent_elements(self.hit_cards)):
                target.damage_calculate(self.damage, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            count = 0
            for shadow in self.shadows:
                if shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                    count += 1
            self.hit_cards.clear()
            if count:
                return True
            return False
    
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for shadow in self.shadows:
                if not shadow.anger:
                    shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                    shadow.board_y = BOARD_SIZE[1] - 1 - board_y
                
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        shadow = spawn_shadow(self.owner, BOARD_SIZE[1]-1-victim.board_x, BOARD_SIZE[1]-1-victim.board_y, self)
        self.shadows.append(shadow)
        return False
    
    def die(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for shadow in self.shadows:
            shadow.die(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return False
    
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            for shadow in self.shadows:
                shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.hit_cards.clear()
            return True
        else:
            if self.numbness == False:
                count = 0
                for shadow in self.shadows:
                    if shadow.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                        count += 1
                self.hit_cards.clear()
                if count:
                    return True
            return False
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.shadows: list[Card] = []
        if self.owner != "display":
            self.shadows.append(spawn_shadow(owner, board_x, board_y, self))
    
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for shadow in self.shadows:
                if not shadow.anger:
                    shadow.board_x = BOARD_SIZE[0] - 1 - board_x
                    shadow.board_y = BOARD_SIZE[1] - 1 - board_y
                
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for shadow in self.shadows:
            shadow.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_update(game_screen)
    


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1_in_hand: list[str], player2_in_hand: list[str], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        targets = tuple(filter(lambda card: card.owner == self.owner and card.health > 0, player1_on_board+player2_on_board))
        if targets:
            for card in self.detection("nearest", targets):
                card.shadows.append(spawn_shadow(self.owner, self.board_x, self.board_y, card, True))
        return self
