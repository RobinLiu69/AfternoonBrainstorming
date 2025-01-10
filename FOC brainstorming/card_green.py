import random
from card import Board, Card, GameScreen, draw_text, Green_setting, GREEN

card_settings = Green_setting


def lucky_effects(target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen, AP: bool=False, AP_target: bool=False, TANK: bool=False) -> None:
    if not AP_target and random.randint(1, 100) <= game_screen.players_luck[target.owner]:
        if AP_target or TANK: return
        game_screen.players_luck[target.owner] += 1
        print(f"{target.board_x}-{target.board_y}:{target.job_and_color} - 獲得好運效果:")
        match random.randint(1, 5):
            case 1:
                print(f"抽到4點護盾")
                target.armor += 4
            case 2:
                print(f"抽到傷害翻倍")
                target.damage *= 2 
            case 3:
                print(f"抽到再次攻擊")
                target.attack(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
            case 4:
                print(f"抽到移動效果")
                target.moving = True
            case 5:
                if AP:
                    print(f"抽到無")
                    return
                print(f"抽到生成幸運方塊")
                for board in board_dict.values():
                    if ((board.board_x == target.board_x+1 and board.board_y == target.board_y+1) or (board.board_x == target.board_x-1 and board.board_y == target.board_y+1) or (board.board_x == target.board_x-1 and board.board_y == target.board_y-1) or (board.board_x == target.board_x+1 and board.board_y == target.board_y-1)):
                        if board.occupy: continue
                        on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                        board.occupy = True
    else:
        if AP: return
        print(f"{target.board_x}-{target.board_y}:{target.job_and_color} - 獲得壞運效果:")
        game_screen.players_luck[target.owner] -= 1
        match random.randint(1, 5):
            case 1:
                print(f"抽到破盾")
                target.armor = 0
            case 2:
                print(f"抽到麻痺")
                target.numbness = True 
            case 3:
                print(f"抽到血量除2")
                target.health //= 2
            case 4:
                print(f"抽到攻擊除2")
                target.damage //= 2
            case 5:
                if target.health >= 2:                
                    print(f"抽到血量減2")
                    target.health -= 2
                else:
                    print(f"抽到無")


class LuckyBlock(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LUCKYBLOCK"]["health"], damage:int=card_settings["LUCKYBLOCK"]["damage"]) -> None:
        
        super().__init__(owner=owner if owner == "display" else "neutral", job_and_color="LUCKYBLOCK", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def draw_shape(self, game_screen: GameScreen) -> None:
        if self.surface is None: return
        self.shape = self.shaped(game_screen.block_size)
        if self.text_color:
            draw_text("?", game_screen.info_text_font, self.text_color, (game_screen.block_size*0.47), (game_screen.block_size*0.43), self.surface)
    
    def been_killed(self, attacker: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        lucky_effects(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        for card in filter(lambda card: card.owner == self.owner and card.job_and_color == "APTG", on_board_neutral+player1_on_board+player2_on_board):
            card.armor += 1
        return True

    
    def end_turn(self, clear_numbness: bool=True) -> int:
        if self.numbness == True and clear_numbness:
            self.numbness = False
            return 0
        else:
            return 0


class Adc(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        for board in board_dict.values():
            if (board.board_x == self.board_x or board.board_y == self.board_y) and not board.occupy:
                if random.randint(1, 100) <= card_settings["ADC"]["chance_to_spawn_luckyblock"]:
                    on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                    board.occupy = True
        return True


class Ap(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        target.numbness = True
        lucky_effects(target, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, AP_target=True)
        lucky_effects(self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, AP=True)
        return True



class Tank(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        lucky_effects(attacker, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, TANK=True)
        return True



class Hf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if target.job_and_color == "LUCKYBLOCK":
            game_screen.players_luck[self.owner] += card_settings["HF"]["luck_increase"]
            board_list = tuple(filter(lambda board: board.occupy == False, board_dict.values()))
            if board_list:
                board = board_list[random.randrange(len(board_list))]
                on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                board.occupy = True
        return True



class Lf(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        if victim.job_and_color == "LUCKYBLOCK":
            for card in self.detection("nearest", filter(lambda card: card.owner != self.owner and card.health >= 0 and card != self, player1_on_board + player2_on_board)):
                card.damage_calculate(card_settings["LF"]["damage_from_killed_luckyblock"], self, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen, False)
            
            if random.randint(1, 100) <= card_settings["LF"]["chance_to_get_attack_count_increase"]:
                game_screen.number_of_attacks[self.owner] += card_settings["LF"]["number_of_attack_increase_from_killed_luckyblock"]
        return True



class Ass(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
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
        
        super().__init__(owner=owner, job_and_color="APTG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def attack(self, plsyer1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
        return False

    def start_turn(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list["Card"], player1_on_board: list["Card"], player2_on_board: list["Card"], board_dict: dict[str, Board], game_screen: GameScreen) -> int:
        for board in board_dict.values():
            if ((board.board_x == self.board_x-1 and board.board_y == self.board_y) or (board.board_x == self.board_x+1 and board.board_y == self.board_y) or (board.board_x == self.board_x and board.board_y == self.board_y-1) or (board.board_x == self.board_x and board.board_y == self.board_y+1)) and not board.occupy:
                on_board_neutral.append(LuckyBlock("None", board.board_x, board.board_y))
                board.occupy = True
        return 0


class Sp(Card):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="SPG", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> Card:
        game_screen.players_luck[self.owner] += card_settings["SP"]["luck_increase"]
        board_list = list(filter(lambda board: board.occupy == False and board.board_x != self.board_x and board.board_y != self.board_y, board_dict.values()))
        if board_list:
            random.shuffle(board_list)
            if game_screen.players_luck[self.owner] > card_settings["SP"]["spawn_luckyblock_requires_minimum_luck"]:
                for i in range(min((game_screen.players_luck[self.owner]-card_settings["SP"]["spawn_luckyblock_requires_minimum_luck"])//10, len(board_list))):
                    on_board_neutral.append(LuckyBlock("None", board_list[i].board_x, board_list[i].board_y))
                    board_list[i].occupy = True
        return self
