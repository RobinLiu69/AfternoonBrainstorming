from card import Board, Card, GameScreen, DarkGreen_setting, DARKGREEN

card_settings = DarkGreen_setting


def engraved_totem(target: Card, times: int, player1_on_board: list[Card], player2_on_board: list[Card], game_screen: GameScreen) -> None:
    for i in range(times):
        game_screen.players_totem[target.owner] += (1*(card_settings["SP"]["engraved_totem_coefficient"]**len(tuple(filter(lambda card: card.owner == target.owner and card.job_and_color == "SPDKG", player1_on_board+player2_on_board)))))

class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["ADC"]["health"], damage:int=DarkGreen_setting["ADC"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="ADCDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)

    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.extra_damage = (game_screen.players_totem[self.owner]//DarkGreen_setting["ADC"]["damage_divisor"])
        self.display_update(game_screen)
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        return value + self.extra_damage


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["AP"]["health"], damage:int=DarkGreen_setting["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        engraved_totem(self, DarkGreen_setting["AP"]["engraved_totem"], player1_on_board, player2_on_board, game_screen)
        return True


class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["TANK"]["health"], damage:int=DarkGreen_setting["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: "Card", value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        engraved_totem(self, DarkGreen_setting["TANK"]["engraved_totem"], player1_on_board, player2_on_board, game_screen)
        return True


class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["HF"]["health"], damage:int=DarkGreen_setting["HF"]["damage"]) -> None:

        self.extra_damage = 0
        
        super().__init__(owner=owner, job_and_color="HFDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.heal(1, game_screen)
        return True
    
    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        self.damage_calculate(2, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, False)
        engraved_totem(self, DarkGreen_setting["HF"]["engraved_totem"], player1_on_board, player2_on_board, game_screen)
        return 0

    


class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["LF"]["health"], damage:int=DarkGreen_setting["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        for target in self.detection("small_cross", tuple(filter(lambda card: card.owner != self.owner and card.health > 0, on_board_neutral+player1_on_board+player2_on_board))):
            target.damage_calculate(game_screen.players_totem[self.owner]//4, self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        return self
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        engraved_totem(self, DarkGreen_setting["LF"]["engraved_totem"], player1_on_board, player2_on_board, game_screen)
        return True
    


class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["ASS"]["health"], damage:int=DarkGreen_setting["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.health = 0
        engraved_totem(self, DarkGreen_setting["ASS"]["engraved_totem"], player1_on_board, player2_on_board, game_screen)
        return True


class Apt(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["APT"]["health"], damage:int=DarkGreen_setting["APT"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APTDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.extra_damage = game_screen.players_totem[self.owner]//2
        self.display_update(game_screen)
    
    def damage_bonus(self, value: int, victim: Card, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        engraved_totem(self, self.armor//2, player1_on_board, player2_on_board, game_screen)
        return value + self.extra_damage
    
    def after_damage_calculated(self, target: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        self.armor += value//2
        return True
    

class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=DarkGreen_setting["SP"]["health"], damage:int=DarkGreen_setting["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPDKG", health=health, damage=damage, board_x=board_x, board_y=board_y)