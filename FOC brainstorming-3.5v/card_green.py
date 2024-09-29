from dataclasses import dataclass, field
import os, json
import random
from typing import Sequence, Any, cast

from card import Board, Card, GameScreen, Green_setting, GREEN

card_settings = Green_setting

def lucky_effects(target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen, AP: bool=False, AP_target: bool=False, TANK: bool=False) -> None:
    if random.randint(1, 100) <= game_screen.players_luck[target.owner]:
        if AP_target or TANK: return
        game_screen.players_luck[target.owner] += 1
        match random.randint(1, 5):
            case 1:
                target.armor += 4
            case 2:
                target.damage *= 2 
            case 3:
                target.attack(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            case 4:
                target.moving = True
            case 5:
                if AP: return
                for board in board_dict.values():
                    if ((board.board_x == target.board_x+1 and board.board_y == target.board_y+1) or (board.board_x == target.board_x-1 and board.board_y == target.board_y+1) or (board.board_x == target.board_x-1 and board.board_y == target.board_y-1) or (board.board_x == target.board_x+1 and board.board_y == target.board_y-1)):
                        if board.occupy: return
                        on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                        for card in filter(lambda card: card.owner == target.owner, on_board_neutral+player1_on_board+player2_on_board):
                            card.spawned_luckyblock()
                        board.occupy = True
    else:
        if AP: return
        game_screen.players_luck[target.owner] -= 1
        match random.randint(1, 5):
            case 1:
                target.armor = 0
            case 2:
                target.numbness = True 
            case 3:
                target.health //= 2
            case 4:
                target.damage //= 2
            case 5:
                if target.health >= 2:
                    target.health -= 2



class LuckyBlock(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LUCKYBLOCK"]["health"], damage:int=card_settings["LUCKYBLOCK"]["damage"]) -> None:
        self.owner = owner if owner == "display" else "neutral"
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LUCKYBLOCK", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def been_killed(self, attacker: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        lucky_effects(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return True
    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 0


class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ADCG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for board in board_dict.values():
            if (board.board_x == self.board_x or board.board_y == self.board_y) and not board.occupy:
                if random.randint(1, 100) <= card_settings["ADC"]["chance_to_spawn_luckyblock"]:
                    on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                    for card in filter(lambda card: card.owner == self.owner, on_board_neutral+player1_on_board+player2_on_board):
                        card.spawned_luckyblock()
                    board.occupy = True
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        lucky_effects(target, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, AP_target=True)
        lucky_effects(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, AP=True)
        return True



class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="TANKG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def been_attacked(self, attacker: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        lucky_effects(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, TANK=True)
        return True



class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="HFG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.job_and_color == "LUCKYBLOCK":
            game_screen.players_luck[self.owner] += card_settings["HF"]["luck_increase"]
        board_list = list(filter(lambda board: board.occupy == False, board_dict.values()))
        if board_list:
            board = board_list[random.randrange(len(board_list))]
            on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
            for card in filter(lambda card: card.owner == self.owner, on_board_neutral+player1_on_board+player2_on_board):
                card.spawned_luckyblock()
            board.occupy = True
        return True



class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="LFG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if victim.job_and_color == "LUCKYBLOCK":
            cards = tuple(self.detection("nearest", filter(lambda card: card.owner != self.owner and card.health >= 0 and card != self, player1_on_board + player2_on_board)))
            if cards:
                cards[0].damage_calculate(card_settings["LF"]["damage_from_killed_luckyblock"], self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, False)
            
            if random.randint(1, 100) <= card_settings["LF"]["chance_to_get_attack_count_increase"]:
                game_screen.number_of_attacks[self.owner] += card_settings["LF"]["number_of_attack_increase_from_killed_luckyblock"]
        return True



class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="ASSG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        game_screen.players_luck[self.owner] += 5
        match self.owner:
            case "player1":
                game_screen.players_luck["player2"] -= card_settings["ASS"]["luck_increase"]
            case "player2":
                game_screen.players_luck["player1"] -= card_settings["ASS"]["luck_decrease"]
        return True



class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="APTG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for board in board_dict.values():
            if ((board.board_x == self.board_x-1 and board.board_y == self.board_y) or (board.board_x == self.board_x+1 and board.board_y == self.board_y) or (board.board_x == self.board_x and board.board_y == self.board_y-1) or (board.board_x == self.board_x and board.board_y == self.board_y+1)) and not board.occupy:
                on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                for card in filter(lambda card: card.owner == self.owner, on_board_neutral+player1_on_board+player2_on_board):
                    card.spawned_luckyblock()
                board.occupy = True
        return True

    def spawned_luckyblock(self) -> bool:
        self.armor += card_settings["APT"]["luck_increase"]
        return True



class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        self.owner = owner
        self.board_x = board_x
        self.board_y = board_y
        self.health = health
        self.damage = damage
        
        super().__init__(owner=self.owner, job_and_color="SPG", health=self.health, damage=self.damage, board_x=self.board_x, board_y=self.board_y)
    
    def deploy(self, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        game_screen.players_luck[self.owner] += card_settings["SP"]["luck_add"]
        board_list = list(filter(lambda board: board.occupy == False and board.board_x != self.board_x and board.board_y != self.board_y, board_dict.values()))
        if board_list:
            random.shuffle(board_list)
            if game_screen.players_luck[self.owner] > card_settings["SP"]["spawn_luckyblock_requires_minimum_luck"]:
                for i in range(min((game_screen.players_luck[self.owner]-card_settings["SP"]["spawn_luckyblock_requires_minimum_luck"])//10, len(board_list))):
                    on_board_neutral.append(LuckyBlock("None", board_list[i].board_x, board_list[i].board_y))
                    for card in filter(lambda card: card.owner == self.owner, on_board_neutral+player1_on_board+player2_on_board):
                        card.spawned_luckyblock()
                    board_list[i].occupy = True
        return self
