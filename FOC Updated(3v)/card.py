from dataclasses import dataclass, fields
import os, json, pygame, game_screen
import random
from typing import Sequence, Any

from board_block import Board
from game_screen import *

__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))
JOB_DICTIONARY: dict[str, dict[str, str]] = json.loads(open(f"{__FOLDER_PATH}/job_dictionary.json", "r").read())
COLOR_TAG_DICT: list[str] = sorted( JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)


@dataclass(kw_only=True)
class Card:
    owner: str
    job_and_color: str
    job: str | None = None
    color_name: str | None = None
    color: tuple[int, ...] | None = None
    text_color: tuple[int, ...] | None = None
    health: int
    max_health: int = health
    attack: int
    attack_type: str | None = None
    originalAttack: int = attack
    armor: int = 0
    
    can_attack: bool | None = None
    moving: bool = False
    
    x: int
    y: int
    board_position: int = x+(y*4)

    shape: tuple[tuple[float, float], ...]| None = None

    recursion_limit: int = 20

    anger: bool = False
    
    def get_job(self) -> str:
        return [self.job_and_color.replace(tag, "", 1) for tag in COLOR_TAG_DICT if self.job_and_color.endswith(tag)][0]
    
    def get_attack_type(self) -> str:
        if self.job is None: raise ValueError("Job must be string")
        return JOB_DICTIONARY["attack_type_tags"][self.job]
    
    def get_color_name(self) -> str:
        return [tag for tag in COLOR_TAG_DICT if self.job_and_color.endswith(tag)][0]
    
    def get_RGB_color(self) -> tuple[int, ...]:
        if self.color_name is None: raise ValueError("color_name must be string")
        return tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", ")))
    
    def shaped(self, display_width: int, display_height: int, block_size: float) -> int:
        self.job, self.attack_type, self.color_name, self.color = self.get_job(), self.get_attack_type(), self.get_color_name(), self.get_RGB_color()
        match self.job:
            case "ADC":
                self.shape = (((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.7)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.7)))
            case "HF":
                self.shape = (((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.65)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.65)))
            case "LF":
                self.shape = (((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.36), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.42)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.4775), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.55)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.36), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.68)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.8)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.64), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.68)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5225), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.55)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.64), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.42)))
            case "ASS":
                self.shape = (((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.2), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.65)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.5)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.8), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.65)))
            case "APT":
                self.shape = (((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.5)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.7)), 
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.7)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.5)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.3)))
            case "SP":
                self.shape = (((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.375), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.45)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.75)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.45)),
                        ((display_width/2-block_size*2)+(self.x*block_size)+(block_size*0.625), (display_height/2-block_size*1.65)+(self.y*block_size)+(block_size*0.3)))
            case _:
                if self.shape == None: raise AttributeError("Dosen't have valid shape")
        
        self.text_color = self.color
        
        return 0
    
    def start_turn(self) -> None:
        self.moving = False
    
    def end_turn(self) -> None:
        self.moving = False
    
    def move(self, x: int, y: int, Boards: list[Board]) -> bool:
        if Boards[x+(y*4)].card == False:
            if (((abs(self.y-y) == 1 and (abs(self.x-x) == 1 or abs(self.x-x) == 0)) or (abs(self.y-y) == 0 and abs(self.x-x) == 1)) and (self.y != y or self.x != x) and self.moving == True) == False:
                self.moving = False
                return False

            Boards[self.x+(self.y*4)].card = False
            self.x = x
            self.BoardX = x
            self.y = y
            self.BoardY = y
            self.Board = x+(y*4)
            Boards[self.x+(self.y*4)].card = True
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
    
    def draw_texts(self, game_screen: Game_Screen, display_width: int, display_height: int, block_size: float) -> None:
        if game_screen.text_font is None or game_screen.small_text_font is None: raise ValueError("Text font cna't be None")
        if game_screen.surface is None: raise ValueError("Surface cna't be None")
        if self.text_color is None: raise ValueError("Text color cna't be None")
        draw_text("HP:"+str(self.health), game_screen.text_font, self.text_color,
                    ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.1),
                    (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.03), game_screen.surface)
        draw_text("ATK:"+str(self.attack), game_screen.text_font, self.text_color,
                ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.6),
                (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.03), game_screen.surface)
        if self.owner != "display":
            draw_text(str(self.owner), game_screen.text_font, self.text_color,
                    ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.1),
                    (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.8), game_screen.surface)
        else:
            draw_text(str(self.job_and_color), game_screen.text_font, self.text_color,
                    ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.1),
                    (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.8), game_screen.surface)
        if self.can_attack == False:
            draw_text("numbness", game_screen.small_text_font, self.text_color,
                    ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.6),
                    (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.85), game_screen.surface)
        if self.armor > 0:
            draw_text("arm:"+str(self.armor), game_screen.small_text_font, self.text_color,
                ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.1),
                (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.12), game_screen.surface)
        if self.moving == True:
            draw_text("Moving", game_screen.small_text_font, self.text_color,
                ((display_width/2)-(block_size*2))+(self.x*block_size)+(block_size*0.6),
                (display_height/2)-(block_size*1.65)+(self.y*block_size)+(block_size*0.12), game_screen.surface)
                
    def draw_shape(self, game_screen: Game_Screen) -> None:
        if game_screen.block_size is None: raise ValueError("Block size cna't be None")
        self.shaped(game_screen.display_width, game_screen.display_height, game_screen.block_size)
        
    
    def update(self, game_screen: Game_Screen, draw_text: bool = True) -> None:
        if game_screen.block_size is None: raise ValueError("Block size cna't be None")
        if draw_text: self.draw_texts(game_screen, game_screen.display_width, game_screen.display_height, game_screen.block_size)
        if self.attack < 0:
            self.attack = 0
    
    def launch_attack(self, attack_types: list[str], players: list["Card"], neutral: list["Card"]) -> bool:
        if not self.can_attack: return False
        enemies: list["Card"] = list(filter(lambda card: card.owner != self.owner, players + neutral))
        if "cross" in attack_types:
            for card in enemies:
                if ((card.BoardX == self.BoardX-1 and card.BoardY == self.BoardY) or (card.BoardX == self.BoardX+1 and card.BoardY == self.BoardY) or (card.BoardX == self.BoardX and card.BoardY == self.BoardY-1) or (card.BoardX == self.BoardX and card.BoardY == self.BoardY+1)) and card.owner != self.owner:
                    card.damage(self.attack, self)
                    if len(attack_types) == 1: return True
                    break
            else:
                if len(attack_types) == 1: return False
            
            
        if "x" in attack_types:
            for card in enemies:
                if ((card.BoardX == self.BoardX+1 and card.BoardY == self.BoardY+1) or (card.BoardX == self.BoardX-1 and card.BoardY == self.BoardY+1) or (card.BoardX == self.BoardX-1 and card.BoardY == self.BoardY-1) or (card.BoardX == self.BoardX+1 and card.BoardY == self.BoardY-1)) and card.owner != self.owner:
                    card.damage(self.attack, self)
                    if len(attack_types) == 1: return True
                    break
            else:
                if len(attack_types) == 1: return False
                
        if "big_x" in attack_types:
            for card in enemies:
                if ((card.BoardX == self.BoardX or card.BoardY == self.BoardY) and card.Board != self.Board) and card.owner != self.owner:
                    card.damage(self.attack, self)
                    if len(attack_types) == 1: return True
                    break
            else:
                if len(attack_types) == 1: return False
        
        if "nearest" in attack_types:
            nearby_cards: list["Card"] = sorted(enemies, key=lambda card: abs(card.BoardX-self.BoardX)+abs(card.BoardY-self.BoardY))
            if nearby_cards:
                temp_card = nearby_cards[0]
                nearet_cards: list["Card"] = list(filter(lambda card: abs(card.BoardX-self.BoardX)+abs(card.BoardY-self.BoardY) == abs(temp_card.BoardX-self.BoardX)+abs(temp_card.BoardY-self.BoardY), nearby_cards))

                if len(nearet_cards) and len(attack_types) == 1:
                    i = random.randint(0, len(nearet_cards)-1)
                    nearet_cards[i].damage(self.attack, self)
                    return True
            else:
                if len(attack_types) == 1: return False
        
        if "farest" in attack_types:
            faraway_cards: list["Card"] = sorted(enemies, key=lambda card: abs(card.BoardX-self.BoardX)+abs(card.BoardY-self.BoardY))
            if faraway_cards:
                temp_card = faraway_cards[0]
                farest_cards: list["Card"] = list(filter(lambda card: abs(card.BoardX-self.BoardX)+abs(card.BoardY-self.BoardY) == abs(temp_card.BoardX-self.BoardX)+abs(temp_card.BoardY-self.BoardY), faraway_cards))

                if len(farest_cards) and len(attack_types) == 1:
                    i = random.randint(0, len(farest_cards)-1)
                    farest_cards[i].damage(self.attack, self)
                    return True
            else:
                if len(attack_types) == 1: return False
        return False
    
Card()