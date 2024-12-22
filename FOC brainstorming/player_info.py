from dataclasses import dataclass, field
import random, time
from typing import cast

from spawn import spawn_card
from card import Card, Board, GameScreen, draw_text, WHITE, GREEN, DARKGREEN, CYAN
from UI import AttackCountDisplay, TokenDisplay

MAGIC_CARDS = ["CUBES", "MOVE", "MOVEO", "HEAL"]
    

@dataclass(kw_only=True)
class Player:
    name: str
    deck: list[str]
    in_hand: list[str]
    on_board: list[Card]
    draw_deck: list[str]
    discard_pile: list[str]

    def __post_init__(self) -> None:
        self.short_name: str = self.name[0].upper()+self.name[-1]
        self.time: str = "0:00"
        self.start_time: float = 0
        self.elapsed_time: int = 0
        self.time_out: bool = False
        self.time_minutes_and_seconds: str = "00:00"
        self.menu_deck_offset_y: float = 1
        
        
        
        self.clock_offset_x: float = 1.25
        self.deck_info_offeset_x: float = 2
        self.totem_offeset_x: float = 2.5
        self.luck_offeset_x: float = 2
        self.coin_offeset_x: float = 4.4
        
        if self.name == "player1":
            self.menu_deck_offset_y = 1
            self.clock_offset_x = 1.25
            self.deck_info_offeset_x = 2
            self.totem_offeset_x = 4
            self.luck_offeset_x = 2
            self.coin_offeset_x = 4.4
        elif self.name == "player2":
            self.menu_deck_offset_y = 1.5
            self.clock_offset_x = -0.7
            self.deck_info_offeset_x = -0.7
            self.totem_offeset_x = -3.25
            self.luck_offeset_x = -1.3
            self.coin_offeset_x = -3.75
    
    def init_cards(self, game_screen: GameScreen) -> None:
        match self.name:
            case "player1":
                self.discard_pile = self.deck.copy()
                for i in range(3): self.draw_card()
                game_screen.number_of_attacks[self.name] += 1
            case "player2":
                self.discard_pile = self.deck.copy()
                for i in range(3): self.draw_card()
    
    def initialize(self, game_screen: GameScreen) -> None:
        self.attack_count_display = AttackCountDisplay(player_name=self.name, width=int(game_screen.block_size*0.1), height=int(game_screen.block_size*0.1))
        self.token_count_display = TokenDisplay(player_name=self.name, radius=int(game_screen.block_size*0.1))
        self.init_cards(game_screen)
        self.timer_start(game_screen)
    
    def turn_start(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        self.draw_card()
        game_screen.number_of_attacks[self.name] += 1
        for card in self.on_board:
            game_screen.data.data_update("rounds_survived", f"{card.owner}_{card.job_and_color}", 1)
            card.start_of_the_turn(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)


    def turn_end(self, game_screen: GameScreen) -> None:
        self.in_hand = list(filter(lambda card: card != "MOVEO", self.in_hand))
        for card in self.on_board:
            card.end_of_the_turn(game_screen)
    
    def attack(self, board_x: int, board_y: int, player1_in_hand: list[str], playuer2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        if game_screen.number_of_attacks[self.name] > 0:
            for card in self.on_board:
                if card.board_x == board_x and card.board_y == board_y:
                    if card.attack(player1_in_hand, playuer2_in_hand, on_board_neutral, player1_on_board ,player2_on_board, board_dict, game_screen):
                        game_screen.number_of_attacks[self.name] -= 1
                        break
    
    def draw_card(self) -> None:
        if self.draw_deck:
            card = self.draw_deck.pop()
            self.in_hand.append(card)
            print(f"{self.name} drew a {card}.")
        else:
            if self.discard_pile:
                random.shuffle(self.discard_pile)
                self.draw_deck = self.discard_pile.copy()
                self.discard_pile = []
                card = self.draw_deck.pop()
                self.in_hand.append(card)
                print(f"{self.name} drew a {card}.")
            else:
                print(f"{self.name} has no more cards to draw.")
    
    def play_card(self, board_x: int, board_y: int, index: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        if -len(self.in_hand) > index or index >= len(self.in_hand):
            print("Invalid card index.")
            return
        card = self.in_hand[index]
        game_screen.data.data_update("card_use_count", self.name, 1)
        match card:
            case "HEAL":
                game_screen.number_of_heals[self.name] += 1
                self.discard_pile.append(self.in_hand.pop(index))
            case "MOVE":
                game_screen.number_of_movings[self.name] += 1
                self.discard_pile.append(self.in_hand.pop(index))
            case "MOVEO":
                game_screen.number_of_movings[self.name] += 1
                self.in_hand.pop(index)
            case "CUBES":
                game_screen.number_of_cudes[self.name] += 2
                self.discard_pile.append(self.in_hand.pop(index))
            case _:
                if spawn_card(board_x, board_y, card, self.name, player1_in_hand, player2_in_hand, self.on_board, on_board_neutral, player1_on_board, player2_on_board, self.discard_pile, board_dict, game_screen):
                    self.in_hand.pop(index)
                    print(f"{self.name} played a {card} on board position {board_x}, {board_y}.")
                else:
                    print(f"Invalid position to play a {card}.")
    
    def heal_card(self, board_x: int, board_y: int, game_screen: GameScreen) -> None:
        if game_screen.number_of_heals[self.name] > 0:
            game_screen.number_of_heals[self.name] -= 1
            game_screen.data.data_update("use_heal_count", self.name, 1)
            for card in self.on_board:
                if card.board_x == board_x and card.board_y == board_y:
                    card.heal(5, game_screen)
                    break
    
    def move_card(self, board_x: int, board_y: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        moving_cards = list(filter(lambda card: card.moving, self.on_board))
        if len(moving_cards) == 0:
            for card in self.on_board:
                if card.board_x == board_x and card.board_y == board_y and not card.numbness:
                    if game_screen.number_of_movings[self.name] > 0:
                        card.moving = True
                        game_screen.number_of_movings[self.name] -= 1
                    break
            
        else:
            selected_cards = list(filter(lambda card: card.mouse_selected, self.on_board))
            if len(selected_cards) == 1:
                selected_card = selected_cards[0]
                selected_card.mouse_selected = False
                selected_card.moving = True
                if selected_card.move(board_x, board_y, player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                    print(f"{self.name} moved a card to board position {board_x}, {board_y}.")
            elif len(selected_cards) == 0:
                for card in self.on_board:
                    if card.board_x == board_x and card.board_y == board_y:
                        card.mouse_selected = True
                        break
                
    
    def recycle_cards(self, player1_in_hand: list[str], player2_in_hand:list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for i, card in enumerate(self.on_board):
            if card.health <= 0 and card.can_be_killed(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen):
                card.die(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
                card_name = self.on_board.pop(i).job_and_color
                match card_name:
                    case "SHADOW":
                        None
                    case _:
                        self.discard_pile.append(card_name)
                board_dict[str(card.board_x)+"-"+str(card.board_y)].occupy = False
                print(f"{self.name} recycled a {card.job_and_color}.")
    
    def add_card_to_deck(self, card: str) -> None:
        if card != "None" and len(self.deck) < 12 and ((self.deck.count(card) < 2 and card not in MAGIC_CARDS) or (self.deck.count(card) < 3 and card in MAGIC_CARDS)):
            self.deck.append(card)
    
    def pop_card_from_deck(self) -> None:
        if len(self.deck) > 0:
            self.deck.pop()
    
    def spawn_cude(self, mouse_board_x: int, mouse_board_y: int, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        if game_screen.number_of_cudes[self.name] > 0:
            if spawn_card(mouse_board_x, mouse_board_y, "CUBE", "None", player1_in_hand, player2_in_hand, self.on_board, on_board_neutral, player1_on_board, player2_on_board, self.discard_pile, board_dict, game_screen):
                game_screen.number_of_cudes[self.name] -= 1
                game_screen.data.data_update("cube_used_count", self.name, 1)
                print(f"{self.name} spawned a CUBE.")
    
    def menu_display_timer_state(self, game_screen: GameScreen) -> None:
        match self.name:
            case "player1":
                draw_text(f"Timer Mode: {game_screen.timer_mode}", game_screen.text_font, WHITE, game_screen.display_width/5, game_screen.display_height/1.4+(game_screen.block_size*0.2), game_screen.surface)
            case _:
                pass
    
    def menu_file_auto_delet_state(self, game_screen: GameScreen) -> None:
        match self.name:
            case "player1":
                draw_text("File Mode: Save" if not game_screen.file_auto_delet else "File Mode: Delet", game_screen.text_font, WHITE, game_screen.display_width/5+game_screen.block_size*1.5, game_screen.display_height/1.4+(game_screen.block_size*0.2), game_screen.surface)
            case _:
                pass
    
    def menu_deck_display(self, menu_state: str, game_screen: GameScreen) -> None:
        draw_text(f"{self.short_name}Deck:", game_screen.text_font, WHITE, game_screen.display_width//16*2, game_screen.display_height-(game_screen.display_height//5/self.menu_deck_offset_y), game_screen.surface)
        match menu_state:
            case "player1":
                match self.name:
                    case "player1":
                        for i, card in enumerate(self.deck):
                            draw_text(card, game_screen.text_font, WHITE,game_screen.display_width/16*(i+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)
                        if len(self.deck) < 12:
                            draw_text("<--", game_screen.text_font, WHITE,game_screen.display_width/16*(len(self.deck)+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)
                    case "player2":
                        for i, card in enumerate(self.deck):
                            draw_text("??" if i > 5 else card, game_screen.text_font, WHITE,game_screen.display_width/16*(i+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)
            case "player2":
                match self.name:
                    case "player1":
                        for i, card in enumerate(self.deck):
                            draw_text("??" if i > 5 else card, game_screen.text_font, WHITE,game_screen.display_width/16*(i+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)
                    case "player2":
                        for i, card in enumerate(self.deck):
                            draw_text(card, game_screen.text_font, WHITE,game_screen.display_width/16*(i+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)
                        if len(self.deck) < 12:
                            draw_text("<--", game_screen.text_font, WHITE,game_screen.display_width/16*(len(self.deck)+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)
            case _:
                for i, card in enumerate(self.deck):
                    draw_text("??", game_screen.text_font, WHITE,game_screen.display_width/16*(i+3), game_screen.display_height-(game_screen.display_height/5/self.menu_deck_offset_y), game_screen.surface)

    def timer_start(self, game_screen: GameScreen) -> None:
        self.start_time = time.time()
        match game_screen.timer_mode:
            case "countdown":
                self.elapsed_time = game_screen.coutdown_time
        self.update_timer(game_screen)
    
    def update(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], update_timer: bool, game_screen: GameScreen) -> None:
        self.recycle_cards(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        if update_timer:
            self.update_timer(game_screen)
        else:
            self.display_timer(game_screen)
        self.display_hand_cards(game_screen)
        self.display_on_board_cards(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen)
        self.display_deck_info(game_screen)
        self.display_luck(game_screen)
        self.display_totems(game_screen)
        self.display_coins(game_screen)
        self.attack_count_display.display_blocks(game_screen.number_of_attacks[self.name], game_screen)
        self.token_count_display.display_circle(game_screen.players_token[self.name], game_screen)
        
        if game_screen.card_to_draw[self.name] > 0:
            game_screen.card_to_draw[self.name] -= 1
            self.draw_card()
    
    def display_totems(self, game_screen: GameScreen) -> None:
        if game_screen.players_totem[self.name]:
            draw_text(f"totems: {game_screen.players_totem[self.name]}", game_screen.text_font, DARKGREEN, game_screen.display_width/2-(game_screen.block_size*self.totem_offeset_x), game_screen.display_height-(game_screen.block_size*0.4), game_screen.surface)
    
    def display_coins(self, game_screen: GameScreen) -> None:
        if game_screen.players_coin[self.name]:
            draw_text(f"coins: {game_screen.players_coin[self.name]}", game_screen.text_font, CYAN, game_screen.display_width/2-(game_screen.block_size*self.coin_offeset_x), game_screen.display_height/2+(game_screen.block_size*1.3), game_screen.surface)
    
    
    def display_on_board_cards(self, player1_in_hand: list[str], player2_in_hand: list[str], on_board_neutral: list[Card], player1_on_board: list[Card], player2_on_board: list[Card], board_dict: dict[str, Board], game_screen: GameScreen) -> None:
        for card in self.on_board:
            card.update(player1_in_hand, player2_in_hand, on_board_neutral, player1_on_board, player2_on_board, board_dict, game_screen) 
    
    def display_hand_cards(self, game_screen: GameScreen) -> None:
        match self.name:
            case "player1":
                x_position = game_screen.display_width/2-(game_screen.block_size*3.2)
            case "player2":
                x_position = game_screen.display_width/2+(game_screen.block_size*2.1)
        for i, card in enumerate(self.in_hand):
            draw_text(f"{self.short_name}hand " + str(i+1) + ": "+card, game_screen.text_font, WHITE, x_position, game_screen.display_height/14*(i+1), game_screen.surface)
    
    def hand_card_hints(self, mouse_x: int, mouse_y: int, game_screen: GameScreen) -> tuple[str, int]:
        if (mouse_x < game_screen.display_width/2-game_screen.block_size*2.1 and mouse_x > game_screen.display_width/2-game_screen.block_size*3.3) or\
           (mouse_x > game_screen.display_width/2+game_screen.block_size*2.1 and mouse_x < game_screen.display_width/2+game_screen.block_size*3.3):
            i = int(mouse_y*14/game_screen.display_height+0.5)-1
            if -1 < i < len(self.in_hand):
                return self.in_hand[i], i
        return "None", 0
    
    def display_deck_info(self, game_screen: GameScreen) -> None:
        draw_text(f"{self.short_name}DrawDeck: {len(self.draw_deck)} cards", game_screen.text_font, WHITE, game_screen.display_width/2-(game_screen.block_size*self.deck_info_offeset_x), game_screen.display_height-(game_screen.block_size*0.5), game_screen.surface)
        draw_text(f"{self.short_name}DiscardPile: {len(self.discard_pile)} cards", game_screen.text_font, WHITE, game_screen.display_width/2-(game_screen.block_size*self.deck_info_offeset_x), game_screen.display_height-(game_screen.block_size*0.4), game_screen.surface)
    
    def display_luck(self, game_screen: GameScreen) -> None:
        draw_text(f"{self.short_name}Luck: {game_screen.players_luck[self.name]}%", game_screen.text_font, GREEN, game_screen.display_width/2-(game_screen.block_size*self.luck_offeset_x), (game_screen.block_size*1.1), game_screen.surface)
        
    def update_timer(self, game_screen: GameScreen) -> None:
        match game_screen.timer_mode:
            case "countdown":
                if self.start_time == -1:
                    self.start_time = time.time()
                current_time = time.time()
                if current_time - self.start_time > 1:
                    self.start_time = -1
                    self.elapsed_time -= 1
                time_minutes = str(int(self.elapsed_time//60)) if len(str(int(self.elapsed_time//60))) > 1 else "0"+str(int(self.elapsed_time//60))
                time_seconds = str(int(self.elapsed_time%60)) if len(str(int(self.elapsed_time%60))) > 1 else "0"+str(int(self.elapsed_time%60))
                self.time_minutes_and_seconds = time_minutes+":"+time_seconds
                if self.elapsed_time <= 0:
                    self.time_out = True
            case "timer":
                if self.start_time == -1:
                    self.start_time = time.time()
                current_time = time.time()
                if current_time - self.start_time > 1:
                    self.start_time = -1
                    self.elapsed_time += 1
                time_minutes = str(int(self.elapsed_time//60)) if len(str(int(self.elapsed_time//60))) > 1 else "0"+str(int(self.elapsed_time//60))
                time_seconds = str(int(self.elapsed_time%60)) if len(str(int(self.elapsed_time%60))) > 1 else "0"+str(int(self.elapsed_time%60))
                self.time_minutes_and_seconds = time_minutes+":"+time_seconds
        self.display_timer(game_screen)

        
    def display_timer(self, game_screen: GameScreen) -> None:
        draw_text(f"{self.short_name}Clock: "+self.time_minutes_and_seconds, game_screen.text_font, WHITE, game_screen.display_width/2-(game_screen.display_width/6)*self.clock_offset_x, game_screen.display_height/6.4, game_screen.surface)