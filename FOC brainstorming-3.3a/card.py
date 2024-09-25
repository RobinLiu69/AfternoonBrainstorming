from dataclasses import dataclass, field
import os, json, pygame
import random
from typing import Sequence, Any, cast, Generator, Iterable

from board_block import Board
from game_screen import *


COLOR_TAG_LIST: list[str] = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)


@dataclass(kw_only=True)
class Card:
    owner: str
    job_and_color: str
    job: str | None = field(init=False, default=None)
    color_name: str | None = field(init=False, default=None)
    color: tuple[int, int, int] = field(init=False, default=BLACK)
    text_color: tuple[int, int, int] | None = field(init=False, default=None)
    health: int
    damage: int
    attack_types: str | None = field(init=False, default=None)
    armor: int = 0
    
    numbness: bool = field(init=False, default=True)
    moving: bool = False
    mouse_selected: bool = False
    
    board_x: int
    board_y: int
    
    shape: tuple = field(init=False, default=())

    recursion_limit: int = 20

    anger: bool = False
    
    
    def __post_init__(self) -> None:
        self.max_health: int = self.health
        self.original_damage: int = self.damage
        self.board_position: int = self.board_x+(self.board_y*4)
        match self.job_and_color:
            case "MOVE":
                self.job = self.job_and_color
                self.attack_types = None
                self.color_name = "White"
                self.color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
                self.text_color = self.color
            case "HEAL":
                self.job = self.job_and_color
                self.attack_types = None
                self.color_name = "White"
                self.color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
                self.text_color = self.color
            case "CUBE":
                self.job = self.job_and_color
                self.attack_types = None
                self.color_name = "White"
                self.color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
                self.text_color = self.color
            case "CUBES":
                self.job = self.job_and_color
                self.attack_types = None
                self.color_name = "White"
                self.color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
                self.text_color = self.color
            case "LUCKYBLOCK":
                self.job = self.job_and_color
                self.attack_types = None
                self.color_name = "Green"
                self.color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
                self.text_color = self.color
            case _:
                self.job = self.get_job()
                self.attack_types = self.get_attack_type()
                self.color_name = self.get_color_name()
                self.color = self.get_RGB_color()
                self.text_color = self.color
        match self.job:
            case "ASS":
                if self.owner != "display":
                    self.numbness = False
                    # self.moving = True
            case _:
                pass
    
    def get_job(self) -> str:
        for tag in COLOR_TAG_LIST:
            if self.job_and_color.endswith(tag):
                if self.job_and_color.count(tag) > 1:
                    return self.job_and_color[::-1].replace(tag, "", 1)[::-1]
                else:
                    return self.job_and_color.replace(tag, "", 1)
        return "None"
    
    def get_attack_type(self) -> str:
        if self.job is None: raise ValueError("Job must be string.")
        return JOB_DICTIONARY["attack_type_tags"][self.job]
    
    def get_color_name(self) -> str:
        return JOB_DICTIONARY["colors_dict"][[tag for tag in COLOR_TAG_LIST if self.job_and_color.endswith(tag)][0]]
    
    def get_RGB_color(self) -> tuple[int, int, int]:
        if self.color_name is None: raise ValueError("color_name must be string.")
        return cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
    
    def shaped(self, display_width: int, display_height: int, block_size: float) -> None:
        match self.job:
            case "ADC":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.3)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.7)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.7)))
            case "AP":
                self.shape = ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.5), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.5))
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
            case "TANK":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.25)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.25), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.75)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.75)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.75), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.25)))
            case "CUBE":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.6)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.6)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)))    
            case "CUBES":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.6)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.6)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)))    
            case "LUCKYBLOCK":
                self.shape = (((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.4), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.6)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.6)),
                        ((display_width/2-block_size*2)+(self.board_x*block_size)+(block_size*0.6), (display_height/2-block_size*1.65)+(self.board_y*block_size)+(block_size*0.4)))    
            case "MOVE":
                self.shape = ((-10, -10), (-10, -10))
            case "HEAL":
                self.shape = ((-10, -10), (-10, -10))
            case _:
                if self.shape == None: raise AttributeError("Dosen't have valid shape.")        
    
    def move(self, board_x: int, board_y: int, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if board_dict[str(board_x)+"-"+str(board_y)].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_screen.data.data_update("move_count", f"{self.owner}_{self.job_and_color}", 1)
            board_dict[str(self.board_x)+"-"+str(self.board_y)].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            self.board_position = self.board_x+(self.board_y*4)
            board_dict[str(board_x)+"-"+str(board_y)].occupy = True
            self.moving = False
            self.moved(plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False

    def damage_calculate(self, value: int, attacker: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen, ability: bool = True) -> bool:
        game_screen.data.data_update("damage_taken_count", f"{self.owner}_{self.job_and_color}", 1)
        if ability:
            if attacker.ability(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):            
                game_screen.data.data_update("ability_count", f"{attacker.owner}_{attacker.job_and_color}", 1)
        value = attacker.damage_bonus(value, self, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        if self.armor > 0 and self.armor >= value:
            game_screen.data.data_update("damage_dealt", f"{attacker.owner}_{attacker.job_and_color}", value)
            game_screen.data.data_update("damage_taken", f"{self.owner}_{self.job_and_color}", value)
            self.armor -= value
            self.been_attacked(attacker, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)   
            return True
        elif self.armor > 0 and self.armor < value:
            game_screen.data.data_update("damage_dealt", f"{attacker.owner}_{attacker.job_and_color}", value)
            game_screen.data.data_update("damage_taken", f"{self.owner}_{self.job_and_color}", value)
            if self.health >= value-self.armor:
                pass
            if self.health < value-self.armor:
                pass
            value = self.armor-value                        
            self.armor = 0
            self.health += value
            self.been_attacked(attacker, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            if self.health <= 0:
                attacker.killed(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                self.been_killed(attacker, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        elif self.armor == 0:
            if self.health >= value:
                pass
            if self.health < value:
                value = self.health
            game_screen.data.data_update("damage_dealt", f"{attacker.owner}_{attacker.job_and_color}", value)
            game_screen.data.data_update("damage_taken", f"{self.owner}_{self.job_and_color}", value)
            self.health -= value
            self.been_attacked(attacker, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            if self.health == 0:
                game_screen.data.data_update("killed_count", f"{attacker.owner}_{attacker.job_and_color}", 1)
                game_screen.data.data_update("death_count", f"{self.owner}_{self.job_and_color}", 1)
                attacker.killed(self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                self.been_killed(attacker, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        return False
    
    def heal(self, value: int, game_screen: GameScreen):
        if self.health+value <= self.max_health:
            # if self.canATK == False:
            #     self.canATK = True
            self.health += value
            game_screen.data.data_update("damage_taken_count", f"{self.owner}_{self.job_and_color}", 1)
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
    
    def draw_basic_info(self, game_screen: GameScreen) -> None:
        if game_screen.info_text_font is None or game_screen.small_text_font is None: raise ValueError("Text font cna't be None.")
        if game_screen.surface is None: raise ValueError("Surface cna't be None.")
        if self.text_color is None: raise ValueError("Text color cna't be None.")
        match self.job_and_color:
            case "MOVE":
                draw_text("MOVE", game_screen.big_text_font, self.text_color,
                         ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.2725),
                         (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.3725), game_screen.surface)
            case "HEAL":
                draw_text("HEAL", game_screen.big_text_font, self.text_color,
                         ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.2725),
                         (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.3725), game_screen.surface)
                
            case _:
                draw_text("HP:"+str(self.health) if self.job_and_color != "SPG" else "HP: ?", game_screen.info_text_font, self.text_color,
                         ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                         (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.03), game_screen.surface)
                draw_text("ATK:"+str(self.damage) if self.job_and_color != "SPG" else "ATK: ?", game_screen.info_text_font, self.text_color,
                         ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                         (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.03), game_screen.surface)
                if self.owner != "display":
                    draw_text(str(self.owner), game_screen.info_text_font, self.text_color,
                             ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                             (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.8), game_screen.surface)
                else:
                    draw_text(str(self.job_and_color), game_screen.info_text_font, self.text_color,
                             ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                             (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.8), game_screen.surface)
                if self.numbness == True:
                    draw_text("numbness", game_screen.small_text_font, self.text_color,
                             ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                             (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.85), game_screen.surface)
                if self.armor > 0:
                    draw_text("arm:"+str(self.armor) if self.job_and_color != "SPG" else "arm: ?", game_screen.small_text_font, self.text_color,
                             ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.1),
                             (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.12), game_screen.surface)
                if self.moving == True:
                    draw_text("Moving" if not self.mouse_selected else "Selected", game_screen.small_text_font, self.text_color,
                             ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                             (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.12), game_screen.surface)
                if self.anger == True:
                    draw_text("Anger", game_screen.small_text_font, self.text_color,
                             ((game_screen.display_width/2)-(game_screen.block_size*2))+(self.board_x*game_screen.block_size)+(game_screen.block_size*0.6),
                             (game_screen.display_height/2)-(game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)+(game_screen.block_size*0.7725), game_screen.surface)
                
    def draw_shape(self, game_screen: GameScreen) -> None:
        if game_screen.block_size is None: raise ValueError("Block size cna't be None.")
        self.shaped(game_screen.display_width, game_screen.display_height, game_screen.block_size)
        match self.job:
            case "AP":
                pygame.draw.circle(game_screen.surface, self.color, self.shape, game_screen.block_size*0.2, int(game_screen.thickness/1.1))
            case _:
                pygame.draw.lines(game_screen.surface, self.color, True, self.shape, int(game_screen.thickness/1.1))
    
    def update(self, game_screen: GameScreen) -> None:
        self.display_update(game_screen)
    
    def display_update(self, game_screen: GameScreen, draw_text: bool = True, draw_shape: bool = True) -> None:
        if game_screen.block_size is None: raise ValueError("Block size cna't be None.")
        if draw_text: self.draw_basic_info(game_screen)
        if draw_shape: self.draw_shape(game_screen)
        if self.damage < 0:
            self.damage = 0

    # def deploy(self, on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> "Card":
    #     return self

    def ability(self, target: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def killed(self, victim: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def moved(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def move_signal(self, target: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def been_attacked(self, attacker: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def been_killed(self, attacker: "Card", plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def damage_bonus(self, value: int, victim: "Card", on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value

    def can_be_killed(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return True

    def token_draw(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def got_token(self) -> bool:
        return False
    
    def spawned_luckyblock(self) -> bool:
        return False
    
    def detection(self, attack_types: str, target_card_list: Iterable["Card"]) -> Generator["Card", None, None]:
        for attack_type in attack_types.split(" "):
            match attack_type:
                case "small_cross":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x-1 and card.board_y == self.board_y) or (card.board_x == self.board_x+1 and card.board_y == self.board_y) or (card.board_x == self.board_x and card.board_y == self.board_y-1) or (card.board_x == self.board_x and card.board_y == self.board_y+1)):
                            yield card
                case "large_cross":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x or card.board_y == self.board_y) and card.board_position != self.board_position):
                            yield card
                case "small_x":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x+1 and card.board_y == self.board_y+1) or (card.board_x == self.board_x-1 and card.board_y == self.board_y+1) or (card.board_x == self.board_x-1 and card.board_y == self.board_y-1) or (card.board_x == self.board_x+1 and card.board_y == self.board_y-1)):
                            yield card
                case "large_x":
                    pass
                case"nearest":
                    nearby_cards: list["Card"] = sorted(target_card_list, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y))
                    if nearby_cards:
                        temp_card = nearby_cards[0]
                        nearet_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), nearby_cards))
                        random_number = random.randint(0, len(nearet_cards)-1)
                        yield nearet_cards[random_number]
                    
                case "farthest":
                    faraway_cards: list["Card"] = sorted(target_card_list, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y), reverse=True)
                    if faraway_cards:
                        temp_card = faraway_cards[0]
                        farthest_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), faraway_cards))

                        random_number = random.randint(0, len(farthest_cards)-1)
                        yield farthest_cards[random_number]
        return None
    
    def attack(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return self.launch_attack(self.attack_types, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
    
    def launch_attack(self, attack_types: str | None, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.numbness or attack_types is None: return False
        game_screen.data.data_update("hit_count", f"{self.owner}_{self.job_and_color}", 1)
        enemies: Iterable["Card"] = list(filter(lambda card: card.owner != self.owner and card.health > 0, on_board_neutral+player1_on_board+player2_on_board))
        target_generator = tuple(self.detection(attack_types, enemies))
        if target_generator:
            for target in target_generator:
                target.damage_calculate(self.damage, self, plsyer1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        else:
            return False

    def start_of_the_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.moving = False
        self.start_turn(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)

    
    def end_of_the_turn(self, game_screen: GameScreen) -> None:
        self.moving = False
        game_screen.data.data_update("scored", f"{self.owner}_{self.job_and_color}", self.end_turn(False))
        match self.owner:
            case "player1":
                game_screen.score -= self.end_turn(True)
            case "player2":
                game_screen.score += self.end_turn(True)
    
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return 0
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1