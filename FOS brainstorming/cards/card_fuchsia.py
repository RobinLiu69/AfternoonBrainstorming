# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
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
import math
from typing import Callable, Iterable, Optional, TYPE_CHECKING

from cards.base import CardRenderData
from shared.setting import CARD_SETTING
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
        self._pending_shadow_iids: Optional[str] = None
    
    def after_movement(self, board_x: int, board_y: int, game_state: GameState) -> None:
        for shadow in self.shadows:
            if shadow.movable:
                shadow.board_x, shadow.board_y = game_state.board_config.get_symmetric_pos(board_x, board_y)

    def spawn_shadow(self, owner: str, board_x: int, board_y: int, attack_types: str, movable: bool=True) -> None:
        self.shadows.append(Shadow(owner, board_x, board_y, self, attack_types, movable))

    def get_render_data(self) -> list[CardRenderData]:
        render_objects: list[CardRenderData] = super().get_render_data()
        for shadow in self.shadows:
            render_objects += shadow.get_render_data()
        return render_objects
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["shadows"] = [s.to_dict() for s in self.shadows]
        return data
 
    def apply_dict(self, data: dict) -> None:
        super().apply_dict(data)
        self._reconcile_shadows(data.get("shadows", []))
 
    def _reconcile_shadows(self, shadow_dicts: list) -> None:
        old_by_iid = {s.instance_id: s for s in getattr(self, "shadows", [])}
        
        new_shadows = []
        for sdata in shadow_dicts:
            iid = sdata["instance_id"]
            existing = old_by_iid.get(iid)
            if existing is not None:
                existing.apply_dict(sdata)
                existing.linker = self
                new_shadows.append(existing)
            else:
                fresh = CardFactory.from_dict(sdata)
                fresh.linker = self  # type: ignore[attr-defined]
                fresh.job = self.job
                new_shadows.append(fresh)
        self.shadows = new_shadows


class Shadow(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int, linker: FuchsiaCard, attack_types: str, movable: bool) -> None:
        
        super().__init__(owner=owner, job_and_color="SHADOW", health=1, damage=0, board_x=board_x, board_y=board_y)
        self.attack_types = attack_types
        self.movable = movable
        self.linker = linker
        self.job = linker.job if linker is not None else ""
    
    @classmethod
    def init_args_from_dict(cls, data: dict) -> dict:
        return {
            "owner": data["owner"],
            "board_x": data["board_x"],
            "board_y": data["board_y"],
            "linker": None,
            "attack_types": data.get("attack_types", ""),
            "movable": data.get("movable", True),
        }
    
    def heal(self, value: int, game_state: GameState) -> bool:
        return False

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
        cards = tuple(filter(lambda card: card.health > 0 and
                             self.board_x == card.board_x and
                             self.board_y == card.board_y, game_state.get_all_cards()))
        if not cards:
            game_state.board_dict[self.board_x, self.board_y].occupy = False
        return False
    
    def get_render_data(self) -> list[CardRenderData]:
        shape_points = tuple((x*1.1, y*1.1) for x, y in self._compute_shape_points())
        return [CardRenderData(
                instance_id=self.instance_id,
                job_and_color=self.job_and_color,
                job=self.job,
                color=self.color,
                board_x=self.board_x,
                board_y=self.board_y,
                health=self.health,
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
                shape_points=shape_points,
                use_sprite=False,
                sprite_key=self.job_and_color,
                sprite_alpha=255,
                render_shape=True if self.job != "CUBES" else False,
                show_stats=False
        )]
    
    def attack(self, game_state: GameState) -> bool:
        enemies: Iterable["Card"] = list(filter(lambda card: card.health > 0 and
                                                card.job_and_color != "SHADOW",
                                                game_state.get_side_cards(self.owner, True)))
        if self.linker.launch_attack(self.attack_types, game_state,
                                     tuple(self.detection(self.attack_types, enemies, game_state))):
            return True
        else:
            return False
    
    def on_settle(self, clear_numbness: bool=True) -> int:
        return 0

    def to_dict(self) -> dict:
        data = Card.to_dict(self)
        data["attack_types"] = self.attack_types
        data["movable"] = self.movable
        return data
 
    def apply_dict(self, data: dict) -> None:
        Card.apply_dict(self, data)
        self.attack_types = data["attack_types"]
        self.movable = data["movable"]


class Adc(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
    def attack_area_display(self, game_state: GameState) -> Iterable[tuple[int, int]]:
        yield from self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state)
        for shadow in self.shadows:
            yield from shadow.attack_areas(shadow.board_x, shadow.board_y, shadow.attack_types, game_state)
    
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


class Ap(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage:int=card_settings["AP"]["damage"]) -> None:
        
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

    def on_refresh(self, game_state: GameState) -> int:
        for shadow in self.shadows:
            enemies = tuple(filter(lambda card: card.health > 0 and
                                   shadow.is_same_location(card),
                                   game_state.get_side_cards(self.owner, True)))
            for enemy in enemies:
                enemy.numbness = True
        return 0
    

class Tank(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)
            
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            game_state.board_dict[shadow.board_x, shadow.board_y].occupy = True
            shadow.update(game_state)
    
    def die(self, game_state: GameState) -> bool:
        for shadow in self.shadows:
            shadow.die(game_state)
        return False

    
class Hf(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
    def attack_area_display(self, game_state: GameState) -> Iterable[tuple[int, int]]:
        yield from self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state)
        for shadow in self.shadows:
            yield from shadow.attack_areas(shadow.board_x, shadow.board_y, shadow.attack_types, game_state)
    
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
    

class Lf(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:
        
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


class Ass(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSF", health=health, damage=damage, board_x=board_x, board_y=board_y)
        
    def attack_area_display(self, game_state: GameState) -> Iterable[tuple[int, int]]:
        yield from self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state)
        for shadow in self.shadows:
            yield from shadow.attack_areas(shadow.board_x, shadow.board_y, shadow.attack_types, game_state)

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


class Apt(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["APT"]["health"],
                 damage: int = card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTF", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def deploy(self, game_state: GameState) -> None:
        if self.owner != "display":
            board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
            self.spawn_shadow(self.owner, board_x, board_y, self.attack_types)
    
    def update(self, game_state: GameState) -> None:
        for shadow in self.shadows:
            shadow.update(game_state)

    def on_field_effect_trigger(self, victim: Card, value: int, attacker: Card, game_state: GameState) -> tuple[int, int, Callable[[Card, int, Card, GameState], None] | None] | None:
        for shadow in self.shadows:
            if (self.health > 0 and victim.owner == self.owner and shadow.is_same_location(victim) and victim != self):
                self.armor += math.floor(value * 0.5)
                return (20, math.ceil(value * 0.5), None)
        return None


class Sp(FuchsiaCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPF", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        targets: tuple[FuchsiaCard] = tuple(
            filter(
                lambda card: card.health > 0 and
                isinstance(card, FuchsiaCard) and
                card.job_and_color != "SPF", game_state.get_player_cards(self.owner)
            )
        ) # pyright: ignore[reportAssignmentType]
        if targets:
            for card in self.detection("farthest", targets, game_state):
                board_x, board_y = game_state.board_config.get_symmetric_pos(self.board_x, self.board_y)
                card.spawn_shadow(self.owner, board_x, board_y, card.attack_types, False)


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)
CardFactory.register("SHADOW", Shadow)