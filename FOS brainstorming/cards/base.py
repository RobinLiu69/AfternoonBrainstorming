# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import TypeVar, cast, Generator, Iterable, Optional, Callable, TYPE_CHECKING, final

from core.game_statistics import StatType
from core.setting import JOB_DICTIONARY, COMBAT_ANIMATIONS_ENABLED, ANIM_LUNGE_STEP
from core.combat_event import CombatEvent


if TYPE_CHECKING:
    from core.game_state import GameState


COLOR_TAG_LIST: list[str] = sorted(JOB_DICTIONARY["colors_dict"].keys(), key=len, reverse=True)

_instance_counter: int = 0

 
def _next_instance_id() -> str:
    global _instance_counter
    _instance_counter += 1
    return f"c{_instance_counter}"
 
 
def reset_instance_counter() -> None:
    global _instance_counter
    _instance_counter = 0


Elements = TypeVar("Elements")
CardType = TypeVar("CardType", bound="Card")


def most_frequent_elements(lst: list[Elements], min_count: int = 0) -> list[Elements]:
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


@dataclass
class CardRenderData:
    instance_id: str
    job_and_color: str
    job: str
    color: tuple[int, int, int]
    board_x: int
    board_y: int
    health: int
    max_health: int
    damage: int
    original_damage: int
    armor: int
    extra_damage: int
    numbness: bool
    moving: bool
    mouse_selected: bool
    anger: bool
    been_targeted: bool
    owner: str
    shape_type: str
    shape_points: tuple
    
    use_sprite: bool = True
    sprite_key: str = ""
    sprite_alpha: int = 255
    render_shape: bool = True
    show_stats: bool = True


@dataclass(kw_only=True)
class Card(ABC):
    owner: str
    job_and_color: str
    health: int
    damage: int
    board_x: int
    board_y: int

    instance_id: str = field(init=False, default="")
    job: str = field(init=False, default="")
    color_name: str = field(init=False, default="")
    color: tuple[int, int, int] = field(init=False, default=(0, 0, 0))
    text_color: tuple[int, int, int] = field(init=False, default=(0, 0, 0))
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

    pending_death: bool = False
    
    max_health: int = field(init=False)
    original_damage: int = field(init=False)
    hit_cards: list["Card"] = field(init=False, default_factory=list)
    
    shape: tuple = field(init=False, default=())
    recursion_limit: int = field(init=False, default=20)

    def __post_init__(self) -> None:
        self.display_health = self.health

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
            self.color = cast(tuple[int, int, int], tuple(map(int, rgb_str.split(", "))))
            self.text_color = self.color
        
        if self.job == "ASS" and self.owner != "display":
            self.numbness = False
        
        if not self.instance_id:
            self.instance_id = _next_instance_id()
    
    @classmethod
    def init_args_from_dict(cls, data: dict) -> dict:
        return {
            "owner": data["owner"],
            "board_x": data["board_x"],
            "board_y": data["board_y"],
            "health": data["health"],
            "damage": data["damage"],
        }

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
    def get_position(self) -> tuple[int, int]:
        return self.board_x, self.board_y

    @final
    def get_uid(self) -> str:
        return f"{self.owner}_{self.job_and_color}"
    
    @final
    def get_attack_type(self) -> str:
        return JOB_DICTIONARY["attack_type_tags"][self.job]
    
    @final
    def get_color_name(self) -> str:
        return JOB_DICTIONARY["colors_dict"][[tag for tag in COLOR_TAG_LIST if self.job_and_color.endswith(tag)][0]]
    
    @final
    def get_RGB_color(self) -> tuple[int, int, int]:
        if not self.color_name: raise ValueError("color_name must be string.")
        return cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][self.color_name].split(", "))))
    
    def _compute_shape_points(self) -> tuple[tuple[float, float], ...]:
        match self.job:
            case "ADC":
                return ((0.5, 0.3), (0.25, 0.7), (0.75, 0.7))
            case "AP":
                return ((0.5, 0.5),)
            case "HF":
                return ((0.4, 0.4), (0.6, 0.4), (0.75, 0.65), (0.25, 0.65))
            case "LF":
                return ((0.5, 0.3), (0.36, 0.42), (0.4775, 0.55), (0.36, 0.68), (0.5, 0.8), (0.64, 0.68), (0.5225, 0.55), (0.64, 0.42))
            case "ASS":
                return ((0.5, 0.4), (0.2, 0.65), (0.5, 0.5), (0.8, 0.65))
            case "APT":
                return ((0.4, 0.3), (0.25, 0.5), (0.4, 0.7), (0.6, 0.7), (0.75, 0.5), (0.6, 0.3))
            case "SP":
                return ((0.375, 0.3), (0.25, 0.45), (0.5, 0.75), (0.75, 0.45), (0.625, 0.3))
            case "TANK":
                return ((0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25))
            case "CUBE":
                return ((0.45, 0.45), (0.45, 0.55), (0.55, 0.55), (0.55, 0.45))
            case "CUBE":
                return ((0.45, 0.45), (0.45, 0.55), (0.55, 0.55), (0.55, 0.45)) 
            case "LUCKYBLOCK":
                return ((0.4, 0.4), (0.4, 0.6), (0.6, 0.6), (0.6, 0.4)) 
            case "MOVE":
                return ((-10, -10), (-10, -10))
            case "HEAL":
                return ((-10, -10), (-10, -10))
            case _:
                return ((0, 0), (0, 0))
    
    @final
    def move(self, board_x: int, board_y: int, game_state: GameState) -> bool:
        if self.custom_move(board_x, board_y, game_state): return True
        if not self.movable: return False
        if game_state.board_dict[board_x, board_y].occupy == False:
            if not (((abs(self.board_y-board_y) == 1 and
                  (abs(self.board_x-board_x) == 1 or
                   abs(self.board_x-board_x) == 0)) or
                   (abs(self.board_y-board_y) == 0 and
                    abs(self.board_x-board_x) == 1)) and
                    (self.board_y != board_y or self.board_x != board_x) and self.moving == True):
                self.moving = False
                return False
            game_state.game_logger.log_card_moved(self.owner, self.job_and_color, self.get_position(), (board_x, board_y))
            game_state.game_statistics.increment(StatType.MOVE, self.get_uid(), 1)
            game_state.board_dict[self.board_x, self.board_y].occupy = False
            self.board_x = board_x
            self.board_y = board_y
            game_state.board_dict[board_x, board_y].occupy = True
            self.moving = False

            self.after_movement(board_x, board_y, game_state)
            
            for card in game_state.get_all_cards():
                card.move_broadcast(self, game_state)
            
            return True
        self.moving = False
        return False

    def custom_move(self, board_x: int, board_y: int, game_state: GameState) -> bool:
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
    def damage_calculate(self, value: int, attacker: "Card", game_state: GameState, ability: bool = True, anim_delay: float = 0.0) -> bool:
        if self.health <= 0: return False
        game_state.game_statistics.increment(StatType.DAMAGE_TAKEN_COUNT, self.get_uid(), 1)
        attacker.hit_cards.append(self)
        if self.damage_block(value, attacker, game_state): return False
        
        if ability:
            if attacker.ability(self, game_state):
                game_state.game_statistics.increment(StatType.ABILITY, attacker.get_uid(), 1)
                attacker.ability_signal(self, game_state)
        
        value = attacker.damage_bonus(value, self, game_state)
        
        value = self.damage_reduce(value, game_state)
        
        value = self.special_damage_interceptor(value, attacker, game_state)
        
        if self.armor > 0 and self.armor >= value:
            game_state.game_statistics.add_damage_dealt(attacker.get_uid(), value)
            game_state.game_statistics.add_damage_taken(self.get_uid(), value)
            if COMBAT_ANIMATIONS_ENABLED:
                game_state.pending_combat_events.append(
                    CombatEvent(kind="hurt",  board_x=self.board_x, board_y=self.board_y, delay=anim_delay, post_health=self.health)
                )
                game_state.pending_combat_events.append(
                    CombatEvent(kind="float", board_x=self.board_x, board_y=self.board_y, damage=value, delay=anim_delay)
                )
            else:
                self.display_health = self.health
            game_state.game_logger.log_attack(attacker.get_uid(),attacker.get_position(),
                                              self.get_uid(), self.get_position(), value)
            self.armor -= value
            self.been_attacked(attacker, value, game_state)
            self.been_attacked_signal(game_state)
            attacker.after_damage_calculated(self, value, game_state)
            return True
        elif self.armor > 0 and self.armor < value:
            game_state.game_statistics.add_damage_dealt(attacker.get_uid(), value)
            game_state.game_statistics.add_damage_taken(self.get_uid(), value)
            if COMBAT_ANIMATIONS_ENABLED:
                game_state.pending_combat_events.append(
                    CombatEvent(kind="hurt",  board_x=self.board_x, board_y=self.board_y, delay=anim_delay, post_health=self.health)
                )
                game_state.pending_combat_events.append(
                    CombatEvent(kind="float", board_x=self.board_x, board_y=self.board_y, damage=value, delay=anim_delay)
                )
            else:
                self.display_health = self.health
            game_state.game_logger.log_attack(attacker.get_uid(), attacker.get_position(),
                                              self.get_uid(), self.get_position(), value)
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
            game_state.game_statistics.add_damage_dealt(attacker.get_uid(), value)
            game_state.game_statistics.add_damage_taken(self.get_uid(), value)
            if COMBAT_ANIMATIONS_ENABLED:
                game_state.pending_combat_events.append(
                    CombatEvent(kind="hurt",  board_x=self.board_x, board_y=self.board_y, delay=anim_delay, post_health=self.health)
                )
                game_state.pending_combat_events.append(
                    CombatEvent(kind="float", board_x=self.board_x, board_y=self.board_y, damage=value, delay=anim_delay)
                )
            else:
                self.display_health = self.health
            game_state.game_logger.log_attack(attacker.get_uid(), attacker.get_position(),
                                              self.get_uid(), self.get_position(), value)
            self.health -= value
            self.been_attacked(attacker, value, game_state)
            self.been_attacked_signal(game_state)
            attacker.after_damage_calculated(self, value, game_state)
            if self.health == 0:
                game_state.game_statistics.add_kill(attacker.get_uid())
                game_state.game_statistics.add_death(self.get_uid())
                attacker.killed(self, game_state)
                attacker.killed_signal(self, game_state)
                self.been_killed(attacker, game_state)
                self.been_killed_signal(attacker, game_state)

                self.pending_death = True
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
            self.armor += (self.health-self.max_health) // 2
            self.health = self.max_health
            return True
        # elif self.canATK == False:
        #     self.canATK = True
        #     return True
        return False

    def get_render_data(self) -> list[CardRenderData]:
        return [CardRenderData(
            instance_id=self.instance_id, 
            job_and_color=self.job_and_color,
            job=self.job,
            color=self.color,
            board_x=self.board_x,
            board_y=self.board_y,
            health=self.display_health,
            max_health=self.max_health,
            damage=self.damage,
            original_damage=self.original_damage,
            armor=self.armor,
            extra_damage=self.extra_damage,
            numbness=self.numbness,
            moving=self.moving,
            mouse_selected=self.mouse_selected,
            anger=self.anger,
            been_targeted=self.been_targeted,
            owner=self.owner,
            shape_type="circle" if self.job == "AP" else "polygon",
            shape_points=self._compute_shape_points(),
            use_sprite=False,
            sprite_key=self.job_and_color,
            sprite_alpha=255,
            render_shape=True if self.job != "CUBES" else False
        )]

    def update(self, game_state: GameState) -> None:
        return
        
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
    def detection(self, attack_types: str, target_card_list: Iterable[CardType], game_state: GameState) -> Generator[CardType, None, None]:
        target_card_list = tuple(filter(lambda card: card.health > 0, target_card_list))
        for attack_type in attack_types.split(" "):
            match attack_type:
                case "small_cross":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x - 1 and card.board_y == self.board_y) or
                            (card.board_x == self.board_x + 1 and card.board_y == self.board_y) or
                            (card.board_x == self.board_x and card.board_y == self.board_y - 1) or
                            (card.board_x == self.board_x and card.board_y == self.board_y + 1)):
                            yield card
                case "large_cross":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x or card.board_y == self.board_y) and
                        not (card.board_x == self.board_x and card.board_y == self.board_y)):
                            yield card
                case "small_x":
                    for card in target_card_list:
                        if ((card.board_x == self.board_x + 1 and card.board_y == self.board_y + 1) or
                            (card.board_x == self.board_x - 1 and card.board_y == self.board_y + 1) or
                            (card.board_x == self.board_x - 1 and card.board_y == self.board_y - 1) or
                            (card.board_x == self.board_x + 1 and card.board_y == self.board_y - 1)):
                            yield card
                case "large_x":
                    pass
                case"nearest":
                    nearby_cards: list[CardType] = sorted(
                        target_card_list,
                        key=lambda card: abs(card.board_x - self.board_x) + abs(card.board_y - self.board_y)
                    )
                    if nearby_cards:
                        temp_card = nearby_cards[0]
                        nearet_cards: list[CardType] = list(
                            filter(
                                lambda card: abs(card.board_x-self.board_x) + abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x) + abs(temp_card.board_y-self.board_y)
                                , nearby_cards
                            )
                        )
                        yield game_state.rng.choice(nearet_cards)
                case "farthest":
                    faraway_cards: list[CardType] = sorted(target_card_list, 
                        key=lambda card: abs(card.board_x-self.board_x) + abs(card.board_y-self.board_y),
                        reverse=True
                    )
                    if faraway_cards:
                        temp_card = faraway_cards[0]
                        farthest_cards: list[CardType] = list(
                            filter(
                                lambda card: abs(card.board_x-self.board_x)+abs(card.board_y-self.board_y) == abs(temp_card.board_x-self.board_x) + abs(temp_card.board_y-self.board_y),
                                faraway_cards
                            )
                        )
                        yield game_state.rng.choice(farthest_cards)
        return None
    
    @final
    def attack_areas(self, board_x: int, board_y: int, attack_types: str | None, game_state: GameState) -> Generator[tuple[int, int], None, None]:
        if not attack_types: return None
        board_list = tuple((game_state.board_dict.values()))
        for attack_type in attack_types.split(" "):
            match attack_type:
                case "small_cross":
                    for board in board_list:
                        if ((board.board_x == board_x-1 and board.board_y == board_y) or
                            (board.board_x == board_x+1 and board.board_y == board_y) or
                            (board.board_x == board_x and board.board_y == board_y-1) or
                            (board.board_x == board_x and board.board_y == board_y+1)):
                            yield board.board_x, board.board_y
                case "large_cross":
                    for board in board_list:
                        if ((board.board_x == board_x or board.board_y == board_y) and
                            not (board.board_x == board_x and board.board_y == board_y)):
                            yield board.board_x, board.board_y
                case "small_x":
                    for board in board_list:
                        if ((board.board_x == board_x+1 and board.board_y == board_y+1) or
                            (board.board_x == board_x-1 and board.board_y == board_y+1) or
                            (board.board_x == board_x-1 and board.board_y == board_y-1) or
                            (board.board_x == board_x+1 and board.board_y == board_y-1)):
                            yield board.board_x, board.board_y
                case "large_x":
                    pass
                case"nearest":
                    nearby_cards: list["Card"] = sorted(game_state.get_side_cards(self.owner, True), key=lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y))
                    if nearby_cards:
                        temp_card = nearby_cards[0]
                        nearet_cards: list["Card"] = list(filter(lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y) == abs(temp_card.board_x-board_x)+abs(temp_card.board_y-board_y), nearby_cards))
                        for card in nearet_cards: yield card.board_x, card.board_y
                case "farthest":
                    faraway_cards: list["Card"] = sorted(game_state.get_side_cards(self.owner, True), key=lambda card: abs(card.board_x-board_x)+abs(card.board_y-board_y), reverse=True)
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
    def launch_attack(self, attack_types: str, game_state: GameState, custom_target_tuple: tuple[Card, ...] = tuple(), ignore_numbness: bool = False, use_ability: bool = True) -> bool:
        if not ignore_numbness and (self.numbness or not attack_types): return False

        allies: filter["Card"] = filter(lambda card: card.health > 0, game_state.get_player_cards(self.owner))
        enemies: Iterable["Card"] = list(filter(lambda card: card.health > 0, game_state.get_side_cards(self.owner, True)))
        target_tuple = tuple(self.detection(attack_types, enemies, game_state)) if not custom_target_tuple else custom_target_tuple

        if target_tuple:
            game_state.game_statistics.add_hit(self.get_uid(), 1)
            for i, target in enumerate(target_tuple):
                atk_delay  = i * ANIM_LUNGE_STEP
                hurt_delay = atk_delay + ANIM_LUNGE_STEP * 0.55
                if COMBAT_ANIMATIONS_ENABLED:
                    game_state.pending_combat_events.append(
                        CombatEvent(
                            kind="attack",
                            board_x=self.board_x,
                            board_y=self.board_y,
                            target_x=target.board_x,
                            target_y=target.board_y,
                            delay=atk_delay,
                        )
                    )
                game_state.game_logger.log_launch_attack(self.get_uid(), self.get_position())
                # for card in player1.on_board + player2.on_board:
                #     card.before_attack_broadcast(self, target, game_state)
                if target.damage_calculate(self.damage, self, game_state, use_ability, anim_delay=hurt_delay):
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
        game_state.game_statistics.increment(StatType.SCORED, self.get_uid(), self.end_turn(False))
        match self.owner:
            case "player1":
                game_state.score -= self.end_turn(True)
            case "player2":
                game_state.score += self.end_turn(True)
    
    def start_turn(self, game_state: GameState) -> int:
        return 0
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness:
            if clear_numbness:
                self.numbness = False
            return 0
        else:
            return 1
    
    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "owner": self.owner,
            "job_and_color": self.job_and_color,
            "health": self.health,
            "damage": self.damage,
            "board_x": self.board_x,
            "board_y": self.board_y,
            "attack_types": self.attack_types,
            "numbness": self.numbness,
            "moving": self.moving,
            "mouse_selected": self.mouse_selected,
            "been_targeted": self.been_targeted,
            "armor": self.armor,
            "attack_uses": self.attack_uses,
            "extra_damage": self.extra_damage,
            "movable": self.movable,
            "anger": self.anger,
            "max_health": self.max_health,
            "original_damage": self.original_damage,
            "pending_death": self.pending_death,
            "display_health": self.display_health,
        }
 
    def collect_pending_refs(self, data: dict) -> None:
        """Stash unresolved card references from dict.
        Called during apply_dict. Store instance_ids as _pending_*_iid."""
        pass

    def resolve_references(self, all_cards_by_iid: dict) -> None:
        """Resolve pending references after all cards are rebuilt.
        Called once by GameState.apply_dict at the end."""
        pass
    
    def apply_dict(self, data: dict) -> None:
        self.health = data["health"]
        self.damage = data["damage"]
        self.board_x = data["board_x"]
        self.board_y = data["board_y"]
        self.job_and_color = data["job_and_color"]
        self.attack_types = data["attack_types"]
        self.numbness = data["numbness"]
        self.moving = data["moving"]
        self.mouse_selected = data["mouse_selected"]
        self.been_targeted = data["been_targeted"]
        self.armor = data["armor"]
        self.attack_uses = data["attack_uses"]
        self.extra_damage = data["extra_damage"]
        self.movable = data["movable"]
        self.anger = data["anger"]
        self.max_health = data["max_health"]
        self.original_damage = data["original_damage"]
        self.pending_death = data["pending_death"]
        self.display_health = data["display_health"]
 