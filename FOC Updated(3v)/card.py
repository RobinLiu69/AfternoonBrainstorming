from dataclasses import dataclass, field
import os, json, pygame
import random
from typing import Sequence, Any, cast

from board_block import Board
from game_screen import *
from type_hint import *

__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))

with open(f"{__FOLDER_PATH}/job_dictionary.json", "r") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())

COLOR_TAG_DICT: list[str] = sorted( JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)


@dataclass(kw_only=True)
class Card:
    owner: str
    job_and_color: str
    job: str | None = field(init=False, default=None)
    color_name: str | None = field(init=False, default=None)
    color: tuple[int, int, int] | None = field(init=False, default=None)
    text_color: tuple[int, int, int] | None = field(init=False, default=None)
    health: int
    attack: int
    attack_type: str | None = field(init=False, default=None)
    armor: int = 0
    
    can_attack: bool | None = field(init=False, default=None)
    moving: bool = False
    
    board_x: int
    board_y: int

    shape: tuple[tuple[float, float], ...]| None = field(init=False, default=None)

    recursion_limit: int = 20

    anger: bool = False
    
    
    def __post_init__(self) -> None:
        self.max_health: int = self.health
        self.originalAttack: int = self.attack
        self.board_position: int = self.board_x+(self.board_y*4)
        self.job, self.attack_type, self.color_name, self.color = self.get_job(), self.get_attack_type(), self.get_color_name(), self.get_RGB_color()

    
    def get_job(self) -> str:
        return [self.job_and_color.replace(tag, "", 1) for tag in COLOR_TAG_DICT if self.job_and_color.endswith(tag)][0]
    
    def get_attack_type(self) -> str:
        if self.job is None: raise ValueError("Job must be string")
        return JOB_DICTIONARY["attack_type_tags"][self.job]
    
    def get_color_name(self) -> str:
        return [tag for tag in COLOR_TAG_DICT if self.job_and_color.endswith(tag)][0]
    
    def get_RGB_color(self) -> tuple[int, int, int]:
        if self.color_name is None: raise ValueError("color_name must be string")
        return cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
    
    def shaped(self, display_width: int, display_height: int, block_size: float) -> int:
        match self.job:
            case "ADC":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.7)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.7)))
            case "HF":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.65)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.65)))
            case "LF":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.36), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.42)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4775), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.55)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.36), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.68)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.8)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.64), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.68)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5225), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.55)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.64), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.42)))
            case "ASS":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.2), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.65)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.5)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.8), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.65)))
            case "APT":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.5)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.7)), 
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.7)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.5)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)))
            case "SP":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.375), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.45)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.75)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.45)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.625), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)))
            case _:
                if self.shape == None: raise AttributeError("Dosen't have valid shape")
        
        self.text_color = self.color
        
        return 0
    
    def start_turn(self) -> None:
        self.moving = False
    
    def end_turn(self) -> None:
        self.moving = False
    
    def move(self, board_x: int, board_y: int, boards: list[Board]) -> bool:
        if boards[board_x+(board_y*4)].card == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False

            boards[self.board_x+(self.board_y*4)].card = False
            self.board_x = board_x
            self.board_y = board_y
            self.board_position = board_x+(board_y*4)
            boards[self.board_x+(self.board_y*4)].card = True
            self.moving = False
            
            return True
        self.moving = False
        return False
    
    def kill(self, dead: "Card") -> bool:
        return True
    
    def die(self, atker: "Card") -> bool:
        return True

    def been_attacked(self, atker: "Card") -> bool:
        return True

    def damage(self, value: int, atker: "Card") -> bool:
        if self.armor > 0 and self.armor >= value:
            self.armor -= value
            self.been_attacked(atker)      
            return True
        elif self.armor > 0 and self.armor < value:
            if self.health >= value-self.armor:
                pass
            if self.health < value-self.armor:
                pass
            value = self.armor-value
            self.armor = 0
            self.health += value
            self.been_attacked(atker)
            if self.health <= 0:
                atker.kill(self)
                self.die(atker)
            return True
        elif self.armor == 0:
            if self.health >= value:
                pass
            if self.health < value:
                pass
            self.health -= value
            self.been_attacked(atker)
            if self.health <= 0:
                atker.kill(self)
                self.die(atker)
            return True
        return False
    
    def heal(self, value: int):
        if self.health+value <= self.max_health:
            # if self.canATK == False:
            #     self.canATK = True
            self.health += value
            return True
        elif self.health+value > self.max_health:
            # if self.canATK == False:
            #     self.canATK = True
            self.health += value
            self.armor += (self.health - self.max_health)//2
            self.health = self.max_health
            return True
        # elif self.canATK == False:
        #     self.canATK = True
        #     return True
        return False
    
    def draw_texts(self, game_screen: GameScreen) -> None:
        if game_screen.text_font is None or game_screen.small_text_font is None: raise ValueError("Text font cna't be None")
        if game_screen.surface is None: raise ValueError("Surface cna't be None")
        if self.text_color is None: raise ValueError("Text color cna't be None")
        draw_text("HP:"+str(self.health), game_screen.text_font, self.text_color,
                    ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                    (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.03), game_screen.surface)
        draw_text("ATK:"+str(self.attack), game_screen.text_font, self.text_color,
                ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.03), game_screen.surface)
        if self.owner != "display":
            draw_text(str(self.owner), game_screen.text_font, self.text_color,
                    ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                    (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.8), game_screen.surface)
        else:
            draw_text(str(self.job_and_color), game_screen.text_font, self.text_color,
                    ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                    (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.8), game_screen.surface)
        if self.can_attack == False:
            draw_text("numbness", game_screen.small_text_font, self.text_color,
                    ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                    (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.85), game_screen.surface)
        if self.armor > 0:
            draw_text("arm:"+str(self.armor), game_screen.small_text_font, self.text_color,
                ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.12), game_screen.surface)
        if self.moving == True:
            draw_text("Moving", game_screen.small_text_font, self.text_color,
                ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.12), game_screen.surface)
                
    def draw_shape(self, game_screen: GameScreen) -> None:
        if game_screen.block_size is None: raise ValueError("Block size cna't be None")
        self.shaped(game_screen.display_width, game_screen.display_height, game_screen.block_size)
        
    
    def update(self, game_screen: GameScreen, draw_text: bool = True, draw_shape: bool = True) -> None:
        if game_screen.block_size is None: raise ValueError("Block size cna't be None")
        if draw_text: self.draw_texts(game_screen)
        if draw_shape: self.draw_shape(game_screen)
        if self.attack < 0:
            self.attack = 0
    
    def launch_attack(self, attack_types: list[str], players: list["Card"], neutral: list["Card"]) -> bool:
        if not self.can_attack: return False
        enemies: list["Card"] = list(filter(lambda card: card.owner != self.owner, players + neutral))
        if "cross" in attack_types:
            for card in enemies:
                if ((card.board_x == self.board_x-1 and card.board_y == self.board_y) or (card.board_x == self.board_x+1 and card.board_y == self.board_y) or (card.board_x == self.board_x and card.board_y == self.board_y-1) or (card.board_x == self.board_x and card.board_y == self.board_y+1)) and card.owner != self.owner:
                    card.damage(self.attack, self)
                    if len(attack_types) == 1: return True
                    break
            else:
                if len(attack_types) == 1: return False
            
            
        if "board_x" in attack_types:
            for card in enemies:
                if ((card.board_x == self.board_x+1 and card.board_y == self.board_y+1) or (card.board_x == self.board_x-1 and card.board_y == self.board_y+1) or (card.board_x == self.board_x-1 and card.board_y == self.board_y-1) or (card.board_x == self.board_x+1 and card.board_y == self.board_y-1)) and card.owner != self.owner:
                    card.damage(self.attack, self)
                    if len(attack_types) == 1: return True
                    break
            else:
                if len(attack_types) == 1: return False
                
        if "big_x" in attack_types:
            for card in enemies:
                if ((card.board_x == self.board_x or card.board_y == self.board_y) and card.board_position != self.board_position) and card.owner != self.owner:
                    card.damage(self.attack, self)
                    if len(attack_types) == 1: return True
                    break
            else:
                if len(attack_types) == 1: return False
        
        if "nearest" in attack_types:
            nearby_cards: list["Card"] = sorted(enemies, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y))
            if nearby_cards:
                temp_card = nearby_cards[0]
                nearet_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), nearby_cards))

                if len(nearet_cards) and len(attack_types) == 1:
                    i = random.randint(0, len(nearet_cards)-1)
                    nearet_cards[i].damage(self.attack, self)
                    return True
            else:
                if len(attack_types) == 1: return False
        
        if "farest" in attack_types:
            faraway_cards: list["Card"] = sorted(enemies, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y))
            if faraway_cards:
                temp_card = faraway_cards[0]
                farest_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), faraway_cards))

                if len(farest_cards) and len(attack_types) == 1:
                    i = random.randint(0, len(farest_cards)-1)
                    farest_cards[i].damage(self.attack, self)
                    return True
            else:
                if len(attack_types) == 1: return False
        return False
