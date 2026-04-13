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

import random
from typing import TYPE_CHECKING

from core.game_state import GameState
from core.setting import CARD_SETTING
from core.game_screen import draw_text
from cards.factory import CardFactory, spawn_card
from cards.base import Card
from utils.logger import LogCategory


card_settings = CARD_SETTING["Green"]
color_code = "G"


class GreenCard(Card):
    @staticmethod
    def lucky_effects(target: Card, game_state: GameState, AP: bool=False, AP_target: bool=False, TANK: bool=False) -> None:
        if not AP_target and game_state.rng.randint(1, 100) <= game_state.players_luck[target.owner]:
            if AP_target or TANK: return
            game_state.players_luck[target.owner] += 1
            game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got lucky:",
                                        LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                        target_position=target.get_position())
            match game_state.rng.randint(1, 5):
                case 1:
                    target.armor += 4
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} added 4 armor",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                                target_position=target.get_position())
                case 2:
                    target.damage *= 2
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} damage multiplied by 2",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                                target_position=target.get_position())
                case 3:
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} launch attack",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                                target_position=target.get_position())
                    target.attack(game_state)
                case 4:
                    target.moving = True
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got moving",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                                target_position=target.get_position())
                case 5:
                    if AP:
                        game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got nothing (AP skip)",
                                                    LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                                    target_position=target.get_position())
                        return
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got lucky block spawn",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(),
                                                target_position=target.get_position())
                    offsets = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                    for dx, dy in offsets:
                        nx, ny = target.board_x + dx, target.board_y + dy
                        board = game_state.board_dict.get((nx, ny))
                        if board:
                            if spawn_card(nx, ny, "LUCKYBLOCK", "neutral",
                                          game_state.neutral.on_board, game_state):
                                game_state.game_logger.info(f"lucky block spawned at ({nx}, {ny})",
                                                            LogCategory.SPECIAL_ACTION, card_name="LUCKYBLOCK", position=(nx, ny))
        else:
            if AP:
                game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got nothing (AP skip)",
                                            LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
                return 
            game_state.players_luck[target.owner] -= 1
            game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got jinx:",
                                        LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
            match game_state.rng.randint(1, 5):
                case 1:
                    target.armor = 0
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} armor was destroyed",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
                case 2:
                    print("numbness")
                    target.numbness = True
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} got numbness",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
                case 3:
                    target.health //= 2
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} health halved",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
                case 4:
                    target.damage //= 2
                    game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} damage halved",
                                                LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
                case 5:
                    if target.health >= 2:                
                        target.health -= 2
                        game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} health reduced by 2",
                                                    LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())
                    else:
                        game_state.game_logger.info(f"{target.get_uid()}{target.get_position()} health too low, no effect",
                                                    LogCategory.SPECIAL_ACTION, target=target.get_uid(), target_position=target.get_position())


class LuckyBlock(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LUCKYBLOCK"]["health"],
                 damage: int = card_settings["LUCKYBLOCK"]["damage"]) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral",
                         job_and_color="LUCKYBLOCK", health=health, damage=damage,
                         board_x=board_x, board_y=board_y)
    
    # def draw_shape(self, game_state: GameState) -> None:
    #     if not self.surface: return
    #     self.shape = self.shaped(game_state.game_screen.block_size)
    #     if self.text_color:
    #         draw_text("?", game_state.game_screen.info_text_font, self.text_color, (game_state.game_screen.block_size*0.47), (game_state.game_screen.block_size*0.43), self.surface)
    
    def been_killed(self, attacker: Card, game_state: GameState) -> bool:
        self.lucky_effects(attacker, game_state)
        for card in filter(lambda card: card.job_and_color == "APTG", game_state.get_player_cards(attacker.owner)):
            card.armor += 1
        return True

    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 0


class Adc(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ADC"]["health"],
                 damage: int = card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        for board in game_state.board_dict.values():
            if (board.board_x == self.board_x or board.board_y == self.board_y) and not board.occupy:
                if game_state.rng.randint(1, 100) <= card_settings["ADC"]["chance_to_spawn_luckyblock"]:
                    game_state.neutral.on_board.append(LuckyBlock("None", board.board_x, board.board_y))
                    board.occupy = True
        return True


class Ap(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["AP"]["health"],
                 damage: int = card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        self.lucky_effects(target, game_state, AP_target=True)
        self.lucky_effects(self, game_state, AP=True)
        return True


class Tank(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["TANK"]["health"],
                 damage: int = card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, game_state: GameState) -> bool:
        self.lucky_effects(attacker, game_state, TANK=True)
        return True


class Hf(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["HF"]["health"],
                 damage: int = card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        if target.job_and_color == "LUCKYBLOCK":
            game_state.players_luck[self.owner] += card_settings["HF"]["luck_increase"]
            board_list = tuple(filter(lambda board: board.occupy == False, game_state.board_dict.values()))
            if board_list:
                board = board_list[game_state.rng.randrange(len(board_list))]
                game_state.neutral.on_board.append(LuckyBlock("None", board.board_x, board.board_y))
                board.occupy = True
        return True


class Lf(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["LF"]["health"],
                 damage: int = card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        if victim.job_and_color == "LUCKYBLOCK":
            for card in self.detection("nearest", filter(lambda card: card.health >= 0, game_state.get_opponent_cards(self.owner)), game_state):
                card.damage_calculate(self.damage, self, game_state, False)
            
            if game_state.rng.randint(1, 100) <= card_settings["LF"]["chance_to_get_attack_count_increase"]:
                game_state.number_of_attacks[self.owner] += card_settings["LF"]["number_of_attack_count_increase_from_killed_luckyblock"]
        return True


class Ass(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["ASS"]["health"],
                 damage: int = card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        game_state.players_luck[self.owner] += 5
        match self.owner:
            case "player1":
                game_state.players_luck["player2"] -= card_settings["ASS"]["luck_increase"]
            case "player2":
                game_state.players_luck["player1"] -= card_settings["ASS"]["luck_decrease"]
        return True


class Apt(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["APT"]["health"],
                 damage:int = card_settings["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def attack(self, game_state: GameState) -> bool:
        return False

    def start_turn(self, game_state: GameState) -> int:
        for board in game_state.board_dict.values():
            if ((board.board_x == self.board_x-1 and board.board_y == self.board_y) or
                (board.board_x == self.board_x+1 and board.board_y == self.board_y) or
                (board.board_x == self.board_x and board.board_y == self.board_y-1) or
                (board.board_x == self.board_x and board.board_y == self.board_y+1)) and not board.occupy:
                game_state.neutral.on_board.append(LuckyBlock("None", board.board_x, board.board_y))
                board.occupy = True
        return 0


class Sp(GreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int,
                 health: int = card_settings["SP"]["health"],
                 damage: int = card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        game_state.players_luck[self.owner] += card_settings["SP"]["luck_increase"]
        board_list = list(
            filter(
                lambda board:
                board.occupy == False and
                not (board.board_x == self.board_x and
                board.board_y == self.board_y),
                game_state.board_dict.values()
            )
        )
        if board_list:
            game_state.rng.shuffle(board_list)
            if game_state.players_luck[self.owner] > card_settings["SP"]["spawn_luckyblock_requires_minimum_luck"]:
                for i in range(
                    min(
                        (game_state.players_luck[self.owner]-card_settings["SP"]["spawn_luckyblock_requires_minimum_luck"]) // 10,
                        len(board_list)
                    )
                ):
                    game_state.neutral.on_board.append(LuckyBlock("None", board_list[i].board_x, board_list[i].board_y))
                    board_list[i].occupy = True


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)
CardFactory.register("LUCKYBLOCK", LuckyBlock)