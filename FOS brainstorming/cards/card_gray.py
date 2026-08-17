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
from typing import TYPE_CHECKING, Iterable

from shared.card_code import BARROW_CODE, WIGHT_CODE
from shared.combat_event import CombatEvent
from shared.setting import ANIM_LUNGE_STEP, CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card

if TYPE_CHECKING:
    from core.game_state import GameState


card_settings = CARD_SETTING["Gray"]
color_code = "GY"
SACRIFICE_DAMAGE = 9999


def gain_barrow(game_state: GameState, owner: str, count: int = 1) -> None:
    if count <= 0 or owner not in ("player1", "player2"):
        return
    game_state.get_player(owner).hand.extend([BARROW_CODE] * count)


def friendly_wights(game_state: GameState, owner: str) -> list[Card]:
    return [card for card in game_state.get_player_cards(owner)
            if card.job_and_color == WIGHT_CODE and card.health > 0]


def wight_strike(source: Card, wights: Iterable[Card], value: int, game_state: GameState) -> bool:
    enemies = [card for card in game_state.get_side_cards(source.owner, True) if card.health > 0]
    struck = False
    for wight in wights:
        if not enemies:
            break
        if wight.health <= 0:
            continue
        for target in wight.detection("nearest", enemies, game_state):
            lunge_delay = game_state._attack_anim_cursor
            game_state.emit(
                CombatEvent(kind="attack", board_x=wight.board_x, board_y=wight.board_y,
                            target_x=target.board_x, target_y=target.board_y, delay=lunge_delay)
            )
            before = target.health
            hit = target.damage_calculate(value, wight, game_state, False,
                                          anim_delay=lunge_delay + ANIM_LUNGE_STEP * 0.55)
            game_state._attack_anim_cursor = lunge_delay + ANIM_LUNGE_STEP
            if hit:
                struck = True
                if before > 0 and target.health == 0 and not source.nullify:
                    source.on_kill(target, game_state)
        wight.hit_cards.clear()
        enemies = [card for card in enemies if card.health > 0]
    return struck


class GrayCard(Card):
    def barrow_on_death(self, game_state: GameState) -> int:
        return 1

    def on_death(self, game_state: GameState) -> bool:
        if self.nullify:
            return False
        gain_barrow(game_state, self.owner, self.barrow_on_death(game_state))
        return True

    def wights_in_range(self, game_state: GameState) -> list[Card]:
        area = set(self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state))
        return [wight for wight in friendly_wights(game_state, self.owner)
                if (wight.board_x, wight.board_y) in area]

    def strike_after_attack(self, wights: list[Card], value: int, game_state: GameState) -> bool:
        if self.numbness or not self.attack_types:
            return False
        attacked = self.launch_attack(self.attack_types, game_state)
        self.hit_cards.clear()
        fired = wight_strike(self, wights, value, game_state)
        return attacked or fired


class Wight(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["WIGHT"]["health"],
                 damage: int = card_settings["WIGHT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color=WIGHT_CODE, health=health, damage=damage, board_x=board_x, board_y=board_y)
        self.attack_types = ""
        self.numbness = False

    def on_death(self, game_state: GameState) -> bool:
        return False

    def on_settle(self, clear_numbness: bool = True) -> int:
        if self.numbness and clear_numbness:
            self.numbness = False
        return 0


class Adc(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ADCGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def barrow_on_death(self, game_state: GameState) -> int:
        return 1 + card_settings["ADC"]["extra_barrow_on_death"]

    def on_attack(self, game_state: GameState) -> bool:
        wights = self.wights_in_range(game_state)
        return self.strike_after_attack(wights, self.damage, game_state)


class Ap(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def ability(self, target: Card, game_state: GameState) -> bool:
        gain_barrow(game_state, self.owner, card_settings["AP"]["barrow_on_attack"])
        return True


class Tank(GrayCard):
    reflecting: bool = False

    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="TANKGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_attacked_by(self, attacker: Card, value: int, game_state: GameState) -> bool:
        if self.reflecting:
            return False
        self.reflecting = True
        try:
            reflect = card_settings["TANK"]["reflect_damage"]
            delay = game_state._attack_anim_cursor + ANIM_LUNGE_STEP
            enemies = [card for card in game_state.get_side_cards(self.owner, True) if card.health > 0]
            for target in self.detection("nearest", enemies, game_state):
                game_state.judge.deal(reflect, target, game_state, anim_delay=delay)
            if self.health > 0:
                game_state.judge.deal(reflect, self, game_state, anim_delay=delay)
        finally:
            self.reflecting = False
        return True


class Hf(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="HFGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_attack(self, game_state: GameState) -> bool:
        wights = self.wights_in_range(game_state)
        return self.strike_after_attack(wights, card_settings["HF"]["wight_strike_damage"], game_state)

    def on_death(self, game_state: GameState) -> bool:
        granted = super().on_death(game_state)
        if self.nullify:
            return granted
        debuff = card_settings["HF"]["on_death_enemy_debuff"]
        area = set(self.attack_areas(self.board_x, self.board_y, self.attack_types, game_state))
        for card in game_state.get_side_cards(self.owner, True):
            if card.health > 0 and (card.board_x, card.board_y) in area:
                card.adjust_stats(game_state, health=-debuff["health"], damage=-debuff["atk"], source=self)
        return granted


class Lf(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="LFGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def deploy(self, game_state: GameState) -> None:
        allies = [card for card in game_state.get_player_cards(self.owner)
                  if card is not self and card.health > 0]
        for victim in self.detection("nearest", allies, game_state):
            stolen_health = victim.health
            stolen_damage = victim.damage
            game_state.judge.deal(SACRIFICE_DAMAGE, victim, game_state)
            self.adjust_stats(game_state, armor=stolen_health, extra_damage=stolen_damage)


class Ass(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ASSGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_kill(self, victim: Card, game_state: GameState) -> bool:
        self.adjust_stats(game_state, damage=card_settings["ASS"]["damage_gain_per_kill"],
                          anim_delay=game_state._attack_anim_cursor + ANIM_LUNGE_STEP)
        return True

    def barrow_on_death(self, game_state: GameState) -> int:
        return 1 + max(0, self.damage - card_settings["ASS"]["barrow_damage_threshold"])


class Apt(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["APT"]["health"],
                 damage: int = card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_death(self, game_state: GameState) -> bool:
        granted = super().on_death(game_state)
        if self.nullify:
            return granted
        buff = card_settings["APT"]["on_death_ally_buff"]
        allies = [card for card in game_state.get_player_cards(self.owner)
                  if card is not self and card.health > 0]
        for ally in self.detection("nearest", allies, game_state):
            ally.adjust_stats(game_state, armor=buff["armor"], damage=buff["atk"])
        return granted


class Sp(GrayCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPGY", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def on_attack(self, game_state: GameState) -> bool:
        wights = friendly_wights(game_state, self.owner)
        return self.strike_after_attack(wights, card_settings["SP"]["wight_strike_damage"], game_state)

    def on_kill(self, victim: Card, game_state: GameState) -> bool:
        gain_barrow(game_state, self.owner, card_settings["SP"]["barrow_on_kill"])
        return True


CardFactory.register(WIGHT_CODE, Wight)
CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)
