from dataclasses import dataclass, field
import pygame
import random, math
from typing import TypeVar, cast, Generator, Iterable

from board_block import Board
from game_screen import *


COLOR_TAG_LIST: list[str] = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)

elements = TypeVar("elements")

def most_frequent_elements(lst: list[elements]) -> list[elements]:
    unique_elements: list[elements] = []
    counts: list[int] = []
    
    
    for item in lst:
        try:
            index = unique_elements.index(item)
            counts[index] += 1
        except ValueError:
            unique_elements.append(item)
            counts.append(1)

    max_count = max(counts)

    most_frequent = [unique_elements[i] for i, count in enumerate(counts) if count == max_count]

    return most_frequent


@dataclass(kw_only=True)
class Card:
    owner: str
    job_and_color: str
    job: str | None = field(init=False, default=None)
    color_name: str | None = field(init=False, default=None)
    color: tuple[int, int, int] | tuple[int, int, int, int] = field(init=False, default=BLACK)
    text_color: tuple[int, int, int] | tuple[int, int, int, int] = field(init=False, default=BLACK)
    health: int
    damage: int
    attack_types: str | None = field(init=False, default=None)
    armor: int = 0
    attack_uses: int = 1
    
    numbness: bool = field(init=False, default=True)
    moving: bool = field(init=False, default=False)
    mouse_selected: bool = field(init=False, default=False)
    
    board_x: int
    board_y: int
    surface: pygame.Surface | None = field(init=False, default=None)
    
    extra_damage: int = 0
    upgrade: bool = False
    
    shape: tuple = field(init=False, default=())

    recursion_limit: int = field(init=False, default=20)

    anger: bool = False
    been_targeted: bool = field(init=False, default=False)
    
    def __post_init__(self) -> None:
        self.trigered_by: "Card" | None = None
        self.shadows: list["Card"] = []
        self.hit_cards: list[Card] = []
        self.max_health: int = self.health
        self.original_damage: int = self.damage
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
            case "SHADOW":
                self.job = self.job_and_color
                self.numbness = False
                self.attack_types = None
                self.color_name = "Fuchsia"
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
    
    def shaped(self, block_size: float) -> tuple:
        match self.job:
            case "ADC":
                return (((block_size*0.5), (block_size*0.3)),
                        ((block_size*0.25), (block_size*0.7)),
                        ((block_size*0.75), (block_size*0.7)))
            case "AP":
                return ((block_size*0.5), (block_size*0.5))
            case "HF":
                return (((block_size*0.4), (block_size*0.4)),
                        ((block_size*0.6), (block_size*0.4)),
                        ((block_size*0.75), (block_size*0.65)),
                        ((block_size*0.25), (block_size*0.65)))
            case "LF":
                return (((block_size*0.5), (block_size*0.3)),
                        ((block_size*0.36), (block_size*0.42)),
                        ((block_size*0.4775), (block_size*0.55)),
                        ((block_size*0.36), (block_size*0.68)),
                        ((block_size*0.5), (block_size*0.8)),
                        ((block_size*0.64), (block_size*0.68)),
                        ((block_size*0.5225), (block_size*0.55)),
                        ((block_size*0.64), (block_size*0.42)))
            case "ASS":
                return (((block_size*0.5), (block_size*0.4)),
                        ((block_size*0.2), (block_size*0.65)),
                        ((block_size*0.5), (block_size*0.5)),
                        ((block_size*0.8), (block_size*0.65)))
            case "APT":
                return (((block_size*0.4), (block_size*0.3)),
                        ((block_size*0.25), (block_size*0.5)),
                        ((block_size*0.4), (block_size*0.7)), 
                        ((block_size*0.6), (block_size*0.7)),
                        ((block_size*0.75), (block_size*0.5)),
                        ((block_size*0.6), (block_size*0.3)))
            case "SP":
                return (((block_size*0.375), (block_size*0.3)),
                        ((block_size*0.25), (block_size*0.45)),
                        ((block_size*0.5), (block_size*0.75)),
                        ((block_size*0.75), (block_size*0.45)),
                        ((block_size*0.625), (block_size*0.3)))
            case "TANK":
                return (((block_size*0.25), (block_size*0.25)),
                        ((block_size*0.25), (block_size*0.75)),
                        ((block_size*0.75), (block_size*0.75)),
                        ((block_size*0.75), (block_size*0.25)))
            case "CUBE":
                return (((block_size*0.45), (block_size*0.45)),
                        ((block_size*0.45), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.45)))
            case "CUBES":
                return (((block_size*0.45), (block_size*0.45)),
                        ((block_size*0.45), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.45))) 
            case "LUCKYBLOCK":
                return (((block_size*0.4), (block_size*0.4)),
                        ((block_size*0.4), (block_size*0.6)),
                        ((block_size*0.6), (block_size*0.6)),
                        ((block_size*0.6), (block_size*0.4))) 
            case "MOVE":
                return ((-10, -10), (-10, -10))
            case "HEAL":
                return ((-10, -10), (-10, -10))
            case _:
                if self.shape == None:
                    raise AttributeError("Dosen't have valid shape.")
                return (0,)
    
    def move(self, board_x: int, board_y: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
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
            self.moved(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            for card in ((on_board_neutral+player1_on_board+player2_on_board)):
                card.move_signal(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            
            return True
        self.moving = False
        return False

    def damage_calculate(self, value: int, attacker: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen, ability: bool=True) -> bool:
        game_screen.data.data_update("damage_taken_count", f"{self.owner}_{self.job_and_color}", 1)
        if self.damage_block(value, attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen): return False
        
        if ability:
            if attacker.ability(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                attacker.hit_cards.append(self)
                game_screen.data.data_update("ability_count", f"{attacker.owner}_{attacker.job_and_color}", 1)
                attacker.ability_signal(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        
        
        value = attacker.damage_bonus(value, self, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        
        value = self.damage_reduce(value, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        
        if self.shadow_block(value, attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
            value = math.ceil(value / 2)
        
        if self.armor > 0 and self.armor >= value:
            game_screen.data.data_update("damage_dealt", f"{attacker.owner}_{attacker.job_and_color}", value)
            game_screen.data.data_update("damage_taken", f"{self.owner}_{self.job_and_color}", value)
            self.armor -= value
            self.been_attacked(attacker, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.been_attacked_signal(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            attacker.after_damage_calculated(self, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        elif self.armor > 0 and self.armor < value:
            game_screen.data.data_update("damage_dealt", f"{attacker.owner}_{attacker.job_and_color}", value)
            game_screen.data.data_update("damage_taken", f"{self.owner}_{self.job_and_color}", value)
            if self.health >= value-self.armor:
                pass
            if self.health < value-self.armor:
                pass
            overflow_value = -(self.armor-value)
            self.armor = 0
            self.health -= overflow_value
            self.been_attacked(attacker, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.been_attacked_signal(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            if self.health <= 0:
                value += self.health
                attacker.after_damage_calculated(self, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                attacker.killed(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                attacker.killed_signal(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                self.been_killed(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                self.been_killed_signal(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            else:
                attacker.after_damage_calculated(self, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            return True
        elif self.armor == 0:
            if self.health >= value:
                pass
            if self.health < value:
                value = self.health
            game_screen.data.data_update("damage_dealt", f"{attacker.owner}_{attacker.job_and_color}", value)
            game_screen.data.data_update("damage_taken", f"{self.owner}_{self.job_and_color}", value)
            self.health -= value
            self.been_attacked(attacker, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            self.been_attacked_signal(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            attacker.after_damage_calculated(self, value, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            if self.health == 0:
                game_screen.data.data_update("killed_count", f"{attacker.owner}_{attacker.job_and_color}", 1)
                game_screen.data.data_update("death_count", f"{self.owner}_{self.job_and_color}", 1)
                attacker.killed(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                attacker.killed_signal(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                self.been_killed(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                self.been_killed_signal(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
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
        if game_screen.surface is None or self.surface is None: raise ValueError("Surface cna't be None.")
        if self.text_color is None: raise ValueError("Text color cna't be None.")
        match self.job_and_color:
            case "MOVE":
                draw_text("MOVE", game_screen.big_text_font, self.text_color,
                         (game_screen.block_size*0.2725), (game_screen.block_size*0.3725), self.surface)
            case "HEAL":
                draw_text("HEAL", game_screen.big_text_font, self.text_color,
                         (game_screen.block_size*0.2725), (game_screen.block_size*0.3725), self.surface)
            case "SHADOW":
                return
            case _:
                draw_text(f"HP:{self.health}" if self.job_and_color != "SPG" else "HP: ?", game_screen.info_text_font, self.text_color,
                         (game_screen.block_size*0.1), (game_screen.block_size*0.03), self.surface)
                if not self.extra_damage:
                    draw_text(f"ATK:{self.damage}" if self.job_and_color != "SPG" else "ATK: ?", game_screen.info_text_font, self.text_color,
                             (game_screen.block_size*0.6), (game_screen.block_size*0.03), self.surface)
                else:
                    draw_text(f"ATK:{self.damage}+{self.extra_damage}", game_screen.info_text_font, self.text_color,
                             (game_screen.block_size*0.5), (game_screen.block_size*0.03), self.surface)
                if self.owner != "display":
                    draw_text(self.owner, game_screen.info_text_font, self.text_color,
                             (game_screen.block_size*0.1), (game_screen.block_size*0.8), self.surface)
                else:
                    draw_text(self.job_and_color, game_screen.info_text_font, self.text_color,
                             (game_screen.block_size*0.1), (game_screen.block_size*0.8), self.surface)
                if self.numbness:
                    draw_text("numbness", game_screen.small_text_font, self.text_color,
                             (game_screen.block_size*0.6), (game_screen.block_size*0.85), self.surface)
                if self.armor > 0:
                    draw_text(f"arm:{self.armor}" if self.job_and_color != "SPG" else "arm: ?", game_screen.small_text_font, self.text_color,
                             (game_screen.block_size*0.1), (game_screen.block_size*0.12), self.surface)
                if self.moving:
                    draw_text("Moving" if not self.mouse_selected else "Selected", game_screen.small_text_font, self.text_color,
                             (game_screen.block_size*0.6), (game_screen.block_size*0.12), self.surface)
                if self.anger:
                    draw_text("Anger", game_screen.small_text_font, self.text_color,
                             (game_screen.block_size*0.6), (game_screen.block_size*0.7725), self.surface)
                if self.been_targeted:
                    draw_text("Target", game_screen.small_text_font, RED,
                             (game_screen.block_size*0.1), (game_screen.block_size*0.75), self.surface)

        game_screen.surface.blit(self.surface, ((game_screen.display_width/2-game_screen.block_size*2)+(self.board_x*game_screen.block_size), (game_screen.display_height/2-game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)))
    
                
    def draw_shape(self, game_screen: GameScreen) -> None:
        if self.surface is None: return
        self.shape = self.shaped(game_screen.block_size)
        
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.display_update(game_screen)
    
    def display_update(self, game_screen: GameScreen, draw_text: bool=True, draw_shape: bool=True) -> None:
        if self.surface is None:
            self.surface = pygame.Surface((game_screen.block_size, game_screen.block_size), pygame.SRCALPHA)
        else:
            self.surface.fill((0, 0, 0, 0))
        if game_screen.block_size is None: raise ValueError("Block size cna't be None.")
        if draw_shape:
            self.draw_shape(game_screen)
            match self.job:
                case "AP":
                    pygame.draw.circle(self.surface, self.color, self.shape, game_screen.block_size*0.2, int(game_screen.thickness/1.1))
                case _:
                    pygame.draw.lines(self.surface, self.color, True, self.shape, int(game_screen.thickness/1.1))
        if draw_text: self.draw_basic_info(game_screen)
        if self.damage < 0:
            self.damage = 0
        
        game_screen.surface.blit(self.surface, ((game_screen.display_width/2-game_screen.block_size*2)+(self.board_x*game_screen.block_size), (game_screen.display_height/2-game_screen.block_size*1.65)+(self.board_y*game_screen.block_size)))
    

    def trigger(self, victim: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def damage_block(self, value: int, attacker: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def ability(self, target: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.hit_cards.append(target)
        return False
    
    def ability_signal(self, target: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def shadow_block(self, value: int, attacker: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        match self.owner:
            case "player1":
                for card in player1_on_board:
                    if card.job_and_color == "APTF":
                        for shadow in card.shadows:
                            if shadow.board_x == self.board_x and shadow.board_y == self.board_y:
                                shadow.damage_block(value, attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                                return True
            case "player2":
                for card in player2_on_board:
                    if card.job_and_color == "APTF":
                        for shadow in card.shadows:
                            if shadow.board_x == self.board_x and shadow.board_y == self.board_y:
                                shadow.damage_block(value, attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                                return True
        return False
    
    def after_damage_calculated(self, target: "Card", value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def killed(self, victim: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def killed_signal(self, victim: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def moved(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def move_signal(self, target: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def been_attacked(self, attacker: "Card", value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def been_attacked_signal(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.been_targeted and self.trigered_by is not None:
            self.trigered_by.trigger(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return False
    
    def been_killed(self, attacker: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def been_killed_signal(self, victim: "Card", player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def die(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
        
    def damage_bonus(self, value: int, victim: "Card", on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage

    def damage_reduce(self, value: int, on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value

    def can_be_killed(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return True

    def token_draw(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False
    
    def got_token(self) -> bool:
        return False

    
    def detection(self, attack_types: str, target_card_list: Iterable["Card"]) -> Generator["Card", None, None]:
        target_card_list = tuple(filter(lambda card: card.health > 0, target_card_list))
        for attack_type in attack_types.split(" "):
            match attack_type:
                case "small_cross":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x-1 and card.board_y == self.board_y) or (card.board_x == self.board_x+1 and card.board_y == self.board_y) or (card.board_x == self.board_x and card.board_y == self.board_y-1) or (card.board_x == self.board_x and card.board_y == self.board_y+1)):
                            yield card
                case "large_cross":
                    for card in target_card_list:
                        if (card.board_x == self.board_x or card.board_y == self.board_y) and not (card.board_x == self.board_x and card.board_y == self.board_y):
                            yield card
                case "small_x":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x+1 and card.board_y == self.board_y+1) or (card.board_x == self.board_x-1 and card.board_y == self.board_y+1) or (card.board_x == self.board_x-1 and card.board_y == self.board_y-1) or (card.board_x == self.board_x+1 and card.board_y == self.board_y-1)):
                            yield card
                case "large_x":
                    pass
                case"nearest":
                    for target in target_card_list:
                        if target.been_targeted:
                            yield target
                    
                    nearby_cards: list["Card"] = sorted(target_card_list, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y))
                    if nearby_cards:
                        temp_card = nearby_cards[0]
                        nearet_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), nearby_cards))
                        
                        random_number = random.randint(0, len(nearet_cards)-1)
                        yield nearet_cards[random_number]
                case "farthest":
                    for target in target_card_list:
                        if target.been_targeted:
                            yield target
                    
                    faraway_cards: list["Card"] = sorted(target_card_list, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y), reverse=True)
                    if faraway_cards:
                        temp_card = faraway_cards[0]
                        farthest_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), faraway_cards))

                        random_number = random.randint(0, len(farthest_cards)-1)
                        yield farthest_cards[random_number]
        return None
    
    def attack(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        attack_success = self.launch_attack(self.attack_types, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.hit_cards.clear()
        return attack_success
        
    def launch_attack(self, attack_types: str | None, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if self.numbness or attack_types is None: return False
        game_screen.data.data_update("hit_count", f"{self.owner}_{self.job_and_color}", 1)
        enemies: Iterable["Card"] = list(filter(lambda card: card.owner != self.owner and card.health > 0 and card.job_and_color != "SHADOW", on_board_neutral+player1_on_board+player2_on_board))
        target_generator = tuple(self.detection(attack_types, enemies))
        
        if target_generator:
            for target in target_generator:
                target.damage_calculate(self.damage, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
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