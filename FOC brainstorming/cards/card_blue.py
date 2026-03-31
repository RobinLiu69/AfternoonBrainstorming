import random
from typing import TYPE_CHECKING
from core.game_state import GameState, StatType, CARD_SETTING
from cards.factory import CardFactory
from cards.base import Card

card_settings = CARD_SETTING["Blue"]
color_code = "B"


class BlueCard(Card):
    def got_token(self, game_state: GameState) -> None:
        cards = game_state.get_player_cards(self.owner)
        for card in cards:
            if isinstance(card, BlueCard):
                card.after_token(game_state)
        
        if game_state.players_token[self.owner] // game_state.how_many_token_to_draw_a_card >= 1:
            game_state.players_token[self.owner] -= game_state.how_many_token_to_draw_a_card
            game_state.card_to_draw[self.owner] += 1
            game_state.game_statistics.increment(StatType.TOKEN_USE, self.owner, 1)
            self.draw_card_effect(game_state)
        
    def draw_card_effect(self, game_state: GameState) -> None:
        for card in game_state.get_player_cards(self.owner):
            if isinstance(card, BlueCard):
                card.token_draw(game_state)

    def token_draw(self, game_state: GameState) -> bool:
        return False

    def after_token(self, game_state: GameState) -> bool:
        return False


class Adc(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ADC"]["health"], damage:int=card_settings["ADC"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ADCB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        game_state.players_token[self.owner] += card_settings["ADC"]["token_gets"]
        self.got_token(game_state)
        return True
    
    def token_draw(self, game_state: GameState) -> bool:
        if self.numbness:
            self.numbness = False
        else:
            self.attack(game_state)
            self.hit_cards.clear()
        return True


class Ap(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["AP"]["health"], damage:int=card_settings["AP"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="APB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        target.numbness = True
        game_state.players_token[self.owner] += card_settings["AP"]["token_gets"]
        for i in range(card_settings["AP"]["token_gets"]): self.got_token(game_state)
        return True


class Tank(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["TANK"]["health"], damage:int=card_settings["TANK"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="TANKB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def been_attacked(self, attacker: Card, value: int, game_state: GameState) -> bool:
        game_state.players_token[self.owner] += card_settings["TANK"]["token_gets"]
        for _ in range(card_settings["TANK"]["token_gets"]): self.got_token(game_state)
        return True


class Hf(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["HF"]["health"], damage:int=card_settings["HF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="HFB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def update(self, game_state: GameState) -> None:
        self.extra_damage = game_state.players_token[self.owner]
    
    def damage_bonus(self, value: int, victim: Card, game_state: GameState) -> int:
        return value + self.extra_damage


class Lf(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["LF"]["health"], damage:int=card_settings["LF"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="LFB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        game_state.players_token[self.owner] += card_settings["LF"]["token_gets"]
        for _ in range(card_settings["LF"]["token_gets"]): self.got_token(game_state)
        return True


class Ass(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["ASS"]["health"], damage:int=card_settings["ASS"]["damage"]) -> None:
        
        super().__init__(owner=owner, job_and_color="ASSB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def killed(self, victim: Card, game_state: GameState) -> bool:
        game_state.players_token[self.owner] += card_settings["ASS"]["token_gets"]
        for _ in range(card_settings["ASS"]["token_gets"]): self.got_token(game_state)
        return True


class Apt(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["APT"]["health"], damage:int=card_settings["APT"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="APTB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def ability(self, target: Card, game_state: GameState) -> bool:
        game_state.players_token[self.owner] += self.armor//card_settings["APT"]["token_from_armor_divisor"]
        for _ in range(self.armor//card_settings["APT"]["token_from_armor_divisor"]): self.got_token(game_state)
        return True

    def after_token(self, game_state: GameState) -> bool:
        self.armor += 1
        return True


class Sp(BlueCard):
    def __init__(self, owner: str, board_x: int, board_y: int, health: int=card_settings["SP"]["health"], damage:int=card_settings["SP"]["damage"]) -> None:

        super().__init__(owner=owner, job_and_color="SPB", health=health, damage=damage, board_x=board_x, board_y=board_y)
    
    def deploy(self, game_state: GameState) -> None:
        enemies = list(filter(lambda card: card.health > 0, game_state.get_side_cards(self.owner, True)))
        if enemies:
            count = len(game_state.get_player(self.owner).on_board+game_state.get_player(self.owner).discard_pile)
            for i in range(count):
                if enemies:
                    enemies[random.randrange(len(enemies))].damage_calculate(card_settings["SP"]["spawn_damage"], self, game_state)
                    enemies = list(filter(lambda card: card.health > 0, game_state.get_side_cards(self.owner, True)))


CardFactory.register("ADC" + color_code, Adc)
CardFactory.register("AP" + color_code, Ap)
CardFactory.register("TANK" + color_code, Tank)
CardFactory.register("HF" + color_code, Hf)
CardFactory.register("LF" + color_code, Lf)
CardFactory.register("ASS" + color_code, Ass)
CardFactory.register("APT" + color_code, Apt)
CardFactory.register("SP" + color_code, Sp)