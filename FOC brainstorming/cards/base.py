import pygame
import random, math
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import TypeVar, cast, Generator, Iterable, Optional, Sequence, Callable, TYPE_CHECKING, final

from core.game_screen import draw_text
from core.game_state import GameState, StatType, JOB_DICTIONARY

COLOR_TAG_LIST: list[str] = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)

Elements = TypeVar("Elements")
CardType = TypeVar("CardType", bound="Card")

if TYPE_CHECKING:
    from core.board_block import Board


def most_frequent_elements(lst: list[Elements], min_count: int=0) -> list[Elements]:
    unique_elements: list[Elements] = []
    counts: list[int] = []
    
    for item in lst:
        try:
            index = unique_elements.index(item)
            counts[index] += 1
        except ValueError:
            unique_elements.append(item)
            counts.append(1)

    max_count = max(counts)

    most_frequent = [unique_elements[i] for i, count in enumerate(counts) if count == max_count and count > min_count]

    return most_frequent


@dataclass(kw_only=True)
class Card(ABC):
    owner: str
    job_and_color: str
    health: int
    damage: int
    board_x: int
    board_y: int
    
    job: str | None = field(init=False, default=None)
    color_name: str | None = field(init=False, default=None)
    color: tuple[int, ...] = field(init=False, default=(0, 0, 0))
    text_color: tuple[int, ...] = field(init=False, default=(0, 0, 0))
    attack_types: str = field(init=False, default="")
    
    numbness: bool = field(init=False, default=True)
    moving: bool = field(init=False, default=False)
    mouse_selected: bool = field(init=False, default=False)
    been_targeted: bool = field(init=False, default=False)
    
    armor: int = 0
    attack_uses: int = 1
    extra_damage: int = 0
    movable: bool = True
    anger: bool = False
    
    max_health: int = field(init=False)
    original_damage: int = field(init=False)
    hit_cards: list["Card"] = field(init=False, default_factory=list)
    
    surface: pygame.Surface | None = field(init=False, default=None)
    shape: tuple = field(init=False, default=())
    recursion_limit: int = field(init=False, default=20)

    def __post_init__(self) -> None:
        self.max_health = self.health
        self.original_damage = self.damage
        
        match self.job_and_color:
            case "MOVE" | "HEAL" | "CUBE" | "CUBES":
                self.job = self.job_and_color
                self.color_name = "White"
            case "LUCKYBLOCK":
                self.job = self.job_and_color
                self.color_name = "Green"
            case "SHADOW":
                self.job = self.job_and_color
                self.color_name = "Fuchsia"
                self.numbness = False
            case _:
                self.job = self.get_job()
                self.color_name = self.get_color_name()
                self.attack_types = self.get_attack_type()

        if self.color_name:
            rgb_str = JOB_DICTIONARY["RGB_colors"][self.color_name]
            self.color = tuple(map(int, rgb_str.split(", ")))
            self.text_color = self.color
        
        if self.job == "ASS" and self.owner != "display":
            self.numbness = False
    
    @final
    def is_same_location(self, card: Card) -> bool:
        return self.board_x == card.board_x and self.board_y == card.board_y
    
    @final
    def get_job(self) -> str:
        for tag in COLOR_TAG_LIST:
            if self.job_and_color.endswith(tag):
                if self.job_and_color.count(tag) > 1:
                    return self.job_and_color[::-1].replace(tag, "", 1)[::-1]
                else:
                    return self.job_and_color.replace(tag, "", 1)
        return "None"
    
    @final
    def get_attack_type(self) -> str:
        if not self.job: raise ValueError("Job must be string.")
        return JOB_DICTIONARY["attack_type_tags"][self.job]
    
    @final
    def get_color_name(self) -> str:
        return JOB_DICTIONARY["colors_dict"][[tag for tag in COLOR_TAG_LIST if self.job_and_color.endswith(tag)][0]]
    
    @final
    def get_RGB_color(self) -> tuple[int, int, int]:
        if not self.color_name: raise ValueError("color_name must be string.")
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
    
    @final
    def move(self, board_x: int, board_y: int, game_state: GameState) -> bool:
        if not self.movable: return False
        if game_state.board_dict[board_x, board_y].occupy == False:
            if (((abs(self.board_y-board_y) == 1 and (abs(self.board_x-board_x) == 1 or abs(self.board_x-board_x) == 0)) or (abs(self.board_y-board_y) == 0 and abs(self.board_x-board_x) == 1)) and (self.board_y != board_y or self.board_x != board_x) and self.moving == True) == False:
                self.moving = False
                return False
            game_state.game_statistics.increment(StatType.MOVE, f"{self.owner}_{self.job_and_color}", 1)
            game_state.board_dict[self.board_x, self.board_y].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            game_state.board_dict[board_x, board_y].occupy = True
            self.moving = False
            self.moved(game_state)
            
            for card in game_state.get_all_cards():
                card.move_broadcast(self, game_state)
            
            return True
        self.moving = False
        return False

    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        pass

    def special_damage_interceptor(self, value: int, attacker: "Card", game_state: GameState) -> int:
        modifiers: list[tuple[int, int, Optional[Callable[["Card", int, "Card", GameState], None]]]] = []

        for source in game_state.get_all_cards():
            res = source.on_field_effect_trigger(self, value, attacker, game_state)
            if res:
                modifiers.append(res)
        
        modifiers.sort(key=lambda x: x[0])

        final_value = value
        for priority, modified_val, feedback_function in modifiers:
            final_value = modified_val
            if feedback_function:
                feedback_function(self, final_value, attacker, game_state)
        
        return final_value

    @final
    def damage_calculate(self, value: int, attacker: "Card", game_state: GameState, ability: bool=True) -> bool:
        game_state.game_statistics.increment(StatType.DAMAGE_TAKEN_COUNT, f"{self.owner}_{self.job_and_color}", 1)
        attacker.hit_cards.append(self)
        if self.damage_block(value, attacker, game_state): return False
        
        if ability:
            if attacker.ability(self, game_state):
                game_state.game_statistics.increment(StatType.ABILITY, f"{attacker.owner}_{attacker.job_and_color}", 1)
                attacker.ability_signal(self, game_state)
        
        value = attacker.damage_bonus(value, self, game_state)
        
        value = self.damage_reduce(value, game_state)
        
        value = self.special_damage_interceptor(value, attacker, game_state)
        
        if self.armor > 0 and self.armor >= value:
            game_state.game_statistics.add_damage_dealt(f"{attacker.owner}_{attacker.job_and_color}", value)
            game_state.game_statistics.add_damage_taken(f"{self.owner}_{self.job_and_color}", value)
            game_state.game_logger.log_attack(f"{attacker.owner}_{attacker.job_and_color}", f"{self.owner}_{self.job_and_color}", value)
            self.armor -= value
            self.been_attacked(attacker, value, game_state)
            self.been_attacked_signal(game_state)
            attacker.after_damage_calculated(self, value, game_state)
            return True
        elif self.armor > 0 and self.armor < value:
            game_state.game_statistics.add_damage_dealt(f"{attacker.owner}_{attacker.job_and_color}", value)
            game_state.game_statistics.add_damage_taken(f"{self.owner}_{self.job_and_color}", value)
            game_state.game_logger.log_attack(f"{attacker.owner}_{attacker.job_and_color}", f"{self.owner}_{self.job_and_color}", value)
            if self.health >= value-self.armor:
                pass
            if self.health < value-self.armor:
                pass
            overflow_value = -(self.armor-value)
            self.armor = 0
            self.health -= overflow_value
            self.been_attacked(attacker, value, game_state)
            self.been_attacked_signal(game_state)
            if self.health <= 0:
                value += self.health
                attacker.after_damage_calculated(self, value, game_state)
                attacker.killed(self, game_state)
                attacker.killed_signal(self, game_state)
                self.been_killed(attacker, game_state)
                self.been_killed_signal(attacker, game_state)
            else:
                attacker.after_damage_calculated(self, value, game_state)
            return True
        elif self.armor == 0:
            if self.health >= value:
                pass
            if self.health < value:
                value = self.health
            game_state.game_statistics.add_damage_dealt(f"{attacker.owner}_{attacker.job_and_color}", value)
            game_state.game_statistics.add_damage_taken(f"{self.owner}_{self.job_and_color}", value)
            game_state.game_logger.log_attack(f"{attacker.owner}_{attacker.job_and_color}", f"{self.owner}_{self.job_and_color}", value)
            self.health -= value
            self.been_attacked(attacker, value, game_state)
            self.been_attacked_signal(game_state)
            attacker.after_damage_calculated(self, value, game_state)
            if self.health == 0:
                game_state.game_statistics.add_kill(f"{attacker.owner}_{attacker.job_and_color}")
                game_state.game_statistics.add_death(f"{self.owner}_{self.job_and_color}")
                attacker.killed(self, game_state)
                attacker.killed_signal(self, game_state)
                self.been_killed(attacker, game_state)
                self.been_killed_signal(attacker, game_state)
            return True
        return False
    
    def heal(self, value: int, game_state: GameState) -> bool:
        if self.health+value <= self.max_health:
            # if self.canATK == False:
            #     self.canATK = True
            self.health += value
            # game_screen.data.data_update("damage_taken_count", f"{self.owner}_{self.job_and_color}", 1)
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
    
    def draw_basic_info(self, game_state: GameState) -> None:
        if not game_state.game_screen.info_text_font or not game_state.game_screen.small_text_font: raise ValueError("Text font cna't be None.")
        if not game_state.game_screen.surface or not self.surface: raise ValueError("Surface cna't be None.")
        if not self.text_color: raise ValueError("Text color cna't be None.")
        match self.job_and_color:
            case "MOVE":
                draw_text("MOVE", game_state.game_screen.big_text_font, self.text_color,
                         (game_state.game_screen.block_size*0.2725), (game_state.game_screen.block_size*0.3725), self.surface)
            case "HEAL":
                draw_text("HEAL", game_state.game_screen.big_text_font, self.text_color,
                         (game_state.game_screen.block_size*0.2725), (game_state.game_screen.block_size*0.3725), self.surface)
            case "SHADOW":
                return
            case _:
                draw_text(f"HP:{self.health}" if self.job_and_color != "SPG" else "HP: ?", game_state.game_screen.info_text_font, self.text_color,
                         (game_state.game_screen.block_size*0.1), (game_state.game_screen.block_size*0.03), self.surface)
                if not self.extra_damage:
                    draw_text(f"ATK:{self.damage}" if self.job_and_color != "SPG" else "ATK: ?", game_state.game_screen.info_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.6), (game_state.game_screen.block_size*0.03), self.surface)
                else:
                    draw_text(f"ATK:{self.damage}+{self.extra_damage}", game_state.game_screen.info_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.5), (game_state.game_screen.block_size*0.03), self.surface)
                if self.owner != "display":
                    draw_text(self.owner, game_state.game_screen.info_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.1), (game_state.game_screen.block_size*0.8), self.surface)
                else:
                    draw_text(self.job_and_color, game_state.game_screen.info_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.1), (game_state.game_screen.block_size*0.8), self.surface)
                if self.numbness:
                    draw_text("numbness", game_state.game_screen.small_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.6), (game_state.game_screen.block_size*0.85), self.surface)
                if self.armor > 0:
                    draw_text(f"arm:{self.armor}" if self.job_and_color != "SPG" else "arm: ?", game_state.game_screen.small_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.1), (game_state.game_screen.block_size*0.12), self.surface)
                if self.moving:
                    draw_text("Moving" if not self.mouse_selected else "Selected", game_state.game_screen.small_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.6), (game_state.game_screen.block_size*0.12), self.surface)
                if self.anger:
                    draw_text("Anger", game_state.game_screen.small_text_font, self.text_color,
                             (game_state.game_screen.block_size*0.6), (game_state.game_screen.block_size*0.7725), self.surface)

    def draw_shape(self, game_state: GameState) -> None:
        if not self.surface: return
        self.shape = self.shaped(game_state.game_screen.block_size)

    def update(self, game_state: GameState) -> None:
        self.display_update(game_state)

    @final
    def display_update(self, game_state: GameState, draw_text: bool=True, draw_shape: bool=True) -> None:
        if not self.surface:
            self.surface = pygame.Surface((game_state.game_screen.block_size, game_state.game_screen.block_size), pygame.SRCALPHA)
        else:
            self.surface.fill((0, 0, 0, 0))
        if not game_state.game_screen.block_size: raise ValueError("Block size cna't be None.")
        if draw_shape:
            self.draw_shape(game_state)
            match self.job:
                case "AP":
                    pygame.draw.circle(self.surface, self.color, self.shape, game_state.game_screen.block_size*0.2, int(game_state.game_screen.thickness/1.1))
                case _:
                    pygame.draw.lines(self.surface, self.color, True, self.shape, int(game_state.game_screen.thickness/1.1))
        if draw_text:
            self.draw_basic_info(game_state)
        
        game_state.game_screen.surface.blit(self.surface, ((game_state.game_screen.display_width/2-game_state.game_screen.block_size*2)+(self.board_x*game_state.game_screen.block_size), (game_state.game_screen.display_height/2-game_state.game_screen.block_size*1.65)+(self.board_y*game_state.game_screen.block_size)))

    def deploy(self, game_state: GameState) -> None:
        return

    def damage_block(self, value: int, attacker: "Card", game_state: GameState) -> bool:
        return False
    
    def ability(self, target: "Card", game_state: GameState) -> bool:
        return False
    
    def ability_signal(self, target: "Card", game_state: GameState) -> bool:
        return False

    def on_field_effect_trigger(self, victim: "Card", value: int, attacker: "Card", game_state: GameState) -> Optional[tuple[int, int, Optional[Callable[["Card", int, "Card", GameState], None]]]]:
        return None
    
    def after_damage_calculated(self, target: "Card", value: int, game_state: GameState) -> bool:
        return False
    
    def killed(self, victim: "Card", game_state: GameState) -> bool:
        return False

    def killed_signal(self, victim: "Card", game_state: GameState) -> bool:
        return False
    
    def moved(self, game_state: GameState) -> bool:
        return False

    def move_broadcast(self, target: "Card", game_state: GameState) -> bool:
        return False

    def been_attacked(self, attacker: "Card", value: int, game_state: GameState) -> bool:
        return False

    def been_attacked_signal(self, game_state: GameState) -> bool:
        return False

    def been_killed(self, attacker: "Card", game_state: GameState) -> bool:
        return False

    def been_killed_signal(self, victim: "Card", game_state: GameState) -> bool:
        return False

    def die(self, game_state: GameState) -> bool:
        return False

    def damage_bonus(self, value: int, victim: "Card", game_state: GameState) -> int:
        return value + self.extra_damage

    def damage_reduce(self, value: int, game_state: GameState) -> int:
        return value

    def can_be_killed(self, game_state: GameState) -> bool:
        return True
    
    @final
    def detection(self, attack_types: str, target_card_list: Iterable[CardType]) -> Generator[CardType, None, None]:
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
                    nearby_cards: list[CardType] = sorted(target_card_list, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y))
                    if nearby_cards:
                        temp_card = nearby_cards[0]
                        nearet_cards: list[CardType] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), nearby_cards))
                        yield random.choice(nearet_cards)
                case "farthest":
                    faraway_cards: list[CardType] = sorted(target_card_list, key=lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y), reverse=True)
                    if faraway_cards:
                        temp_card = faraway_cards[0]
                        farthest_cards: list[CardType] = list(filter(lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x)+abs(temp_card.board_y-self.board_y), faraway_cards))
                        yield random.choice(farthest_cards)
        return None
    
    @final
    def attack_areas(self, board_x: int, board_y: int, attack_types: str | None, game_state: GameState) -> Generator[tuple[int, int], None, None]:
        if not attack_types: return None
        board_list = tuple((game_state.board_dict.values()))
        for attack_type in attack_types.split(" "):
            match attack_type:
                case "small_cross":
                    for board in board_list:
                        if ((board.board_x == board_x-1 and board.board_y == board_y) or (board.board_x == board_x+1 and board.board_y == board_y) or (board.board_x == board_x and board.board_y == board_y-1) or (board.board_x == board_x and board.board_y == board_y+1)):
                            yield board.board_x, board.board_y
                case "large_cross":
                    for board in board_list:
                        if ((board.board_x == board_x or board.board_y == board_y) and not (board.board_x == board_x and board.board_y == board_y)):
                            yield board.board_x, board.board_y
                case "small_x":
                    for board in board_list:
                        if ((board.board_x == board_x+1 and board.board_y == board_y+1) or (board.board_x == board_x-1 and board.board_y == board_y+1) or (board.board_x == board_x-1 and board.board_y == board_y-1) or (board.board_x == board_x+1 and board.board_y == board_y-1)):
                            yield board.board_x, board.board_y
                case "large_x":
                    pass
                case"nearest":
                    nearby_cards: list["Card"] = sorted(game_state.get_all_cards(), key=lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y))
                    if nearby_cards:
                        temp_card = nearby_cards[0]
                        nearet_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y) == abs(temp_card.board_x-board_x)+abs(temp_card.board_y-board_y), nearby_cards))
                        for card in nearet_cards: yield card.board_x, card.board_y
                case "farthest":
                    faraway_cards: list["Card"] = sorted(game_state.get_all_cards(), key=lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y), reverse=True)
                    if faraway_cards:
                        temp_card = faraway_cards[0]
                        farthest_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y) == abs(temp_card.board_x-board_x)+abs(temp_card.board_y-board_y), faraway_cards))
                        for card in farthest_cards: yield card.board_x, card.board_y
        return None

    def attack_area_display(self, game_state: GameState) -> Iterable[tuple[int, int]]:
        return self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state)
    
    def attack(self, game_state: GameState) -> bool:
        attack_success = self.launch_attack(self.attack_types, game_state)
        self.hit_cards.clear()
        return attack_success
    
    def after_attack_broadcast(self, attacker: "Card", target: "Card", game_state: GameState) -> bool:
        return False

    @final
    def launch_attack(self, attack_types: str, game_state: GameState, custom_target_tuple: tuple[Card, ...] = tuple()) -> bool:
        if self.numbness or not attack_types: return False
        allies: filter["Card"] = filter(lambda card: card.health > 0, game_state.get_player_cards(self.owner))
        enemies: Iterable["Card"] = list(filter(lambda card: card.health > 0 and card.job_and_color != "SHADOW", game_state.get_side_cards(self.owner, True)))
        target_tuple = tuple(self.detection(attack_types, enemies)) if not custom_target_tuple else custom_target_tuple
        
        if target_tuple:
            game_state.game_statistics.add_hit(f"{self.owner}_{self.job_and_color}", 1)
            for target in target_tuple:
                # for card in player1.on_board + player2.on_board:
                #     card.before_attack_broadcast(self, target, game_state)
                target.damage_calculate(self.damage, self, game_state)
                for card in game_state.get_both_player_cards():
                    card.after_attack_broadcast(self, target, game_state)
            return True
        else:
            return False

    def start_of_the_turn(self, game_state: GameState) -> None:
        self.moving = False
        self.start_turn(game_state)
    
    def end_of_the_turn(self, game_state: GameState) -> None:
        self.moving = False
        game_state.game_statistics.increment(StatType.SCORED, f"{self.owner}_{self.job_and_color}", self.end_turn(False))
        match self.owner:
            case "player1":
                game_state.score -= self.end_turn(True)
            case "player2":
                game_state.score += self.end_turn(True)
    
    def start_turn(self, game_state: GameState) -> int:
        return 0
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1