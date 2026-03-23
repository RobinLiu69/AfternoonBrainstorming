from cards.card import Board, Card
from core.game_screen import GameScreen, DarkGreen_setting, DARKGREEN
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral

card_settings = DarkGreen_setting

class DarkGreenCard(Card):
    def engraved_totem(self, times: int, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for i in range(times):
            game_screen.players_totem[self.owner] += (1*(card_settings["SP"]["engraved_totem_coefficient"]**len(tuple(filter(lambda card: card.owner == self.owner and card.job_and_color == "SPDKG", player1.on_board+player2.on_board)))))

class Adc(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["ADC"]["health"], damage:int=DarkGreen_setting["ADC"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ADCDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.extra_damage = (game_screen.players_totem[self.owner]//DarkGreen_setting["ADC"]["damage_divisor"])
        self.display_update(game_screen)
    
    def damage_bonus(self, value: int, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage


class Ap(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["AP"]["health"], damage:int=DarkGreen_setting["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        self.engraved_totem(DarkGreen_setting["AP"]["engraved_totem"], player1, player2, neutral, board_dict, game_screen)
        return True


class Tank(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["TANK"]["health"], damage:int=DarkGreen_setting["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: "Card", value: int, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.engraved_totem(DarkGreen_setting["TANK"]["engraved_totem"], player1, player2, neutral, board_dict, game_screen)
        return True


class Hf(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["HF"]["health"], damage:int=DarkGreen_setting["HF"]["damage"]) -> None:

        self.extra_damage = 0
        
        super().__init__(owner=owner, job_and_color="HFDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.heal(1, game_screen)
        return True
    
    def start_turn(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        self.damage_calculate(2, self, player1, player2, neutral, board_dict, game_screen, False)
        self.engraved_totem(DarkGreen_setting["HF"]["engraved_totem"], player1, player2, neutral, board_dict, game_screen)
        return 0

    


class Lf(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["LF"]["health"], damage:int=DarkGreen_setting["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        for target in self.detection("small_cross", tuple(filter(lambda card: card.owner != self.owner and card.health > 0, neutral.on_board + player1.on_board + player2.on_board))):
            target.damage_calculate(game_screen.players_totem[self.owner]//4, self, player1, player2, neutral, board_dict, game_screen)
        return self
    
    def ability(self, target: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.engraved_totem(DarkGreen_setting["LF"]["engraved_totem"], player1, player2, neutral, board_dict, game_screen)
        return True
    


class Ass(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["ASS"]["health"], damage:int=DarkGreen_setting["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.health = 0
        self.engraved_totem(DarkGreen_setting["ASS"]["engraved_totem"], player1, player2, neutral, board_dict, game_screen)
        return True


class Apt(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["APT"]["health"], damage:int=DarkGreen_setting["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def update(self, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.extra_damage = game_screen.players_totem[self.owner]//2
        self.display_update(game_screen)
    
    def damage_bonus(self, value: int, victim: Card, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        self.engraved_totem(self.armor//2, player1, player2, neutral, board_dict, game_screen)
        return value + self.extra_damage
    
    def after_damage_calculated(self, target: Card, value: int, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += value//2
        return True
    

class Sp(DarkGreenCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["SP"]["health"], damage:int=DarkGreen_setting["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)