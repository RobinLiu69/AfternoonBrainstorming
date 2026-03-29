from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import random, time

from core.game_screen import GameScreen, draw_text
from core.UI import AttackCountDisplay, TokenDisplay, HighLightBox
from core.game_state import GameState, StatType, WHITE, BLUE, RED, CYAN, DARKGREEN, GREEN
from cards.base import Card
from cards.factory import spawn_card

if TYPE_CHECKING:
    from core.neutral import Neutral
    from core.board_block import Board

MAGIC_CARDS = ["CUBES", "MOVE", "MOVEO", "HEAL"]


@dataclass(kw_only=True)
class Player:
    name: str
    deck: list[str]
    hand: list[str]
    on_board: list[Card]
    draw_pile: list[str]
    discard_pile: list[str]

    def __post_init__(self) -> None:
        self.short_name: str = self.name[0].upper()+self.name[-1]
        self.time: str = "0:00"
        self.start_time: float = 0
        self.elapsed_time: int = 0
        self.time_out: bool = False
        self.time_minutes_and_seconds: str = "00:00"
        self.menu_deck_offset_y: float = 1
        
        self.selected_card_index: int = -1
        self.selected_highlight: Optional[HighLightBox] = None
        
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
    
    def init_cards(self, game_state: GameState) -> None:
        match self.name:
            case "player1":
                self.discard_pile = self.deck.copy()
                for i in range(3): self.draw_card(game_state)
                game_state.number_of_attacks[self.name] += 1
            case "player2":
                self.discard_pile = self.deck.copy()
                for i in range(3): self.draw_card(game_state)
    
    def init_highlight_display(self, game_state: GameState) -> None:
        game_screen = game_state.game_screen
        x = game_screen.display_width/2-(game_screen.block_size*3.3) if self.name == "player1" else game_screen.display_width/2+(game_screen.block_size*2.025)
        self.selected_highlight = HighLightBox(x=x, y=0, box_color=BLUE if self.name=="player1" else RED,
        box_height=int(game_screen.block_size/3), box_width=int(game_screen.block_size), line_width=int(game_screen.block_size//50))
    
    def initialize(self, game_state: GameState) -> None:
        self.attack_count_display = AttackCountDisplay(player_name=self.name, width=int(game_state.game_screen.block_size*0.1), height=int(game_state.game_screen.block_size*0.1))
        self.token_count_display = TokenDisplay(player_name=self.name, radius=int(game_state.game_screen.block_size*0.1))
        self.init_cards(game_state)
        self.init_highlight_display(game_state)
        self.timer_start(game_state)
    
    def turn_start(self, game_state: GameState) -> None:
        game_state.game_logger.log_turn_start(self.name, game_state.turn_number)
        self.draw_card(game_state)
        game_state.number_of_attacks[self.name] += 1
        for card in self.on_board:
            game_state.game_statistics.increment(StatType.ROUNDS_SURVIVED, f"{card.owner}_{card.job_and_color}", 1)
            if self.name == "player1":
                card.start_of_the_turn(game_state)
            else:
                card.start_of_the_turn(game_state)

    def turn_end(self, game_state: GameState) -> None:
        self.selected_card_index = -1
        self.hand = list(filter(lambda card: card != "MOVEO", self.hand))
        game_state.number_of_cudes[self.name] = 0
        game_state.number_of_movings[self.name] = 0
        game_state.number_of_heals[self.name] = 0
        
        for card in self.on_board:
            card.end_of_the_turn(game_state)
    
    def attack(self, board_x: int, board_y: int, game_state: GameState) -> None:
        if game_state.number_of_attacks[self.name] > 0:
            for card in self.on_board:
                if card.board_x == board_x and card.board_y == board_y:
                    if self.name == "player1":
                        if card.attack(game_state):
                            game_state.number_of_attacks[self.name] -= card.attack_uses
                            break
                    else:
                        if card.attack(game_state):
                            game_state.number_of_attacks[self.name] -= card.attack_uses
                            break

    def draw_card(self, game_state: GameState) -> None:
        card_name: str = ""
        if self.draw_pile:
            card_name = self.draw_pile.pop()
            self.hand.append(card_name)
        else:
            if self.discard_pile:
                random.shuffle(self.discard_pile)
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile = []
                card_name = self.draw_pile.pop()
                self.hand.append(card_name)
        if card_name:
            game_state.game_logger.log_card_drew(self.name, card_name)
        else:
            game_state.game_logger.info(f"{self.name} draw pile is empty, no card to draw")

    def selecte_card_from_hand(self, index: Optional[int]) -> None:
        if not self.selected_highlight or index is None: return
        self.selected_card_index = index
        if self.selected_card_index != -1:
            self.selected_highlight.visable = True

    def play_card(self, board_x: int, board_y: int, index: int, game_state: GameState) -> None:
        if -len(self.hand) > index or index >= len(self.hand): return
        card_name = self.hand[index]
        game_state.game_statistics.add_card_use(self.name, 1)
        match card_name:
            case "HEAL":
                game_state.number_of_heals[self.name] += 1
                self.discard_pile.append(self.hand.pop(index))
            case "MOVE":
                game_state.number_of_movings[self.name] += 1
                self.discard_pile.append(self.hand.pop(index))
            case "MOVEO":
                game_state.number_of_movings[self.name] += 1
                self.hand.pop(index)
            case "CUBES":
                game_state.number_of_cudes[self.name] += 2
                self.discard_pile.append(self.hand.pop(index))
            case _:
                if spawn_card(board_x, board_y, card_name, self.name, self.on_board, game_state):
                    self.hand.pop(index)
                    game_state.game_logger.log_card_played(self.name, card_name, (board_x, board_y))
                pass

    def heal_card(self, board_x: int, board_y: int, game_state: GameState) -> None:
        game_state.game_logger.log_card_played(self.name, "HEAL", (board_x, board_y))
        if game_state.number_of_heals[self.name] > 0:
            game_state.game_statistics.increment(StatType.HEAL_USE, self.name, 1)
            for card in self.on_board:
                if card.board_x == board_x and card.board_y == board_y:
                    card.heal(6, game_state)
                    game_state.number_of_heals[self.name] -= 1
                    break
    
    def move_card(self, board_x: int, board_y: int, game_state: GameState) -> None:
        game_state.game_logger.log_card_played(self.name, "MOVE", (board_x, board_y))
        moving_cards = list(filter(lambda card: card.moving, self.on_board))
        if len(moving_cards) == 0:
            for card in self.on_board:
                if card.board_x == board_x and card.board_y == board_y and not card.numbness:
                    if game_state.number_of_movings[self.name] > 0:
                        card.moving = True
                        game_state.number_of_movings[self.name] -= 1
                    break
            
        else:
            selected_cards = list(filter(lambda card: card.mouse_selected, self.on_board))
            if len(selected_cards) == 1:
                selected_card = selected_cards[0]
                selected_card.mouse_selected = False
                selected_card.moving = True
                selected_card.move(board_x, board_y, game_state)
            elif len(selected_cards) == 0:
                for card in self.on_board:
                    if card.board_x == board_x and card.board_y == board_y:
                        card.mouse_selected = True
                        break
                
    
    def recycle_cards(self, game_state: GameState) -> None:
        for i, card in enumerate(self.on_board):
            if card.health <= 0 and card.can_be_killed(game_state):
                card.die(game_state)
                card_name = self.on_board.pop(i).job_and_color
                self.discard_pile.append(card_name)
                game_state.board_dict[card.board_x, card.board_y].occupy = False
                game_state.game_logger.log_card_recycled(self.name, card_name, (card.board_x, card.board_y))
    
    def add_card_to_deck(self, card: str) -> None:
        if card != "None" and len(self.deck) < 12 and ((self.deck.count(card) < 2 and card not in MAGIC_CARDS) or (self.deck.count(card) < 3 and card in MAGIC_CARDS)):
            self.deck.append(card)
    
    def pop_card_from_deck(self) -> None:
        if len(self.deck) > 0:
            self.deck.pop()

    def remove_card_from_deck(self, card_name: str, from_end: bool=True) -> None:
        if len(self.deck) > 0 and card_name in self.deck:
            deck = self.deck[::-1] if from_end else self.deck
            deck.remove(card_name)
            self.deck = deck[::-1] if from_end else deck
            
    def spawn_cude(self, board_x: int, board_y: int, game_state: GameState) -> None:
        game_state.game_logger.log_card_played(self.name, "CUBE", (board_x, board_y))
        if game_state.number_of_cudes[self.name] > 0:
            if spawn_card(board_x, board_y, "CUBE", "neutral", game_state.neutral.on_board, game_state):
                game_state.number_of_cudes[self.name] -= 1
                game_state.game_statistics.increment(StatType.CUBE_USE, self.name, 1)
            pass

    def menu_display_timer_state(self, game_state: GameState) -> None:
        game_screen = game_state.game_screen
        match self.name:
            case "player1":
                draw_text(f"Timer Mode: {game_state.timer_mode}", game_screen.text_font, WHITE, game_screen.display_width/5, game_screen.display_height/1.4+(game_screen.block_size*0.2), game_screen.surface)
            case _:
                pass
    
    def menu_file_auto_delet_state(self, game_state: GameState) -> None:
        game_screen = game_state.game_screen
        match self.name:
            case "player1":
                draw_text("File Mode: Save" if not game_state.file_auto_delet else "File Mode: Delet", game_screen.text_font, WHITE, game_screen.display_width/5+game_screen.block_size*1.5, game_screen.display_height/1.4+(game_screen.block_size*0.2), game_screen.surface)
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

    def timer_start(self, game_state: GameState) -> None:
        self.start_time = time.time()
        match game_state.timer_mode:
            case "countdown":
                self.elapsed_time = game_state.coutdown_time
        self.update_timer(game_state)
    
    def update(self, game_state: GameState, update_timer: bool) -> None:
        self.recycle_cards(game_state)
        if update_timer:
            self.update_timer(game_state)
        else:
            self.display_timer(game_state.game_screen)
        self.display_hand(game_state.game_screen)
        self.display_seleted_card(game_state.game_screen)
        self.display_on_board_cards(game_state)
        self.display_deck_info(game_state.game_screen)
        self.display_luck(game_state)
        self.display_totems(game_state)
        self.display_coins(game_state)
        self.attack_count_display.display(game_state.number_of_attacks[self.name], game_state.game_screen)
        self.token_count_display.display(game_state.players_token[self.name], game_state.game_screen)
        
        if game_state.card_to_draw[self.name] > 0:
            game_state.card_to_draw[self.name] -= 1
            self.draw_card(game_state)
    
    def display_seleted_card(self, game_screen: GameScreen) -> None:
        if not self.selected_highlight: return
        if self.selected_card_index == -1 or len(self.hand) <= self.selected_card_index: return
        self.selected_highlight.update(self.selected_card_index, len(self.hand[self.selected_card_index]), game_screen)

    def display_totems(self, game_state: GameState) -> None:
        game_screen = game_state.game_screen
        if game_state.players_totem[self.name]:
            draw_text(f"totems: {game_state.players_totem[self.name]}", game_screen.text_font, DARKGREEN, game_screen.display_width/2-(game_screen.block_size*self.totem_offeset_x), game_screen.display_height-(game_screen.block_size*0.4), game_screen.surface)
    
    def display_coins(self, game_state: GameState) -> None:
        game_screen = game_state.game_screen
        if game_state.players_coin[self.name]:
            draw_text(f"coins: {game_state.players_coin[self.name]}", game_screen.text_font, CYAN, game_screen.display_width/2-(game_screen.block_size*self.coin_offeset_x), game_screen.display_height/2+(game_screen.block_size*1.3), game_screen.surface)
    
    
    def display_on_board_cards(self, game_state: GameState) -> None:
        for card in self.on_board:
            card.update(game_state) 
    
    def display_hand(self, game_screen: GameScreen) -> None:
        x = 0
        match self.name:
            case "player1":
                x = game_screen.display_width/2-(game_screen.block_size*3.2)
            case "player2":
                x = game_screen.display_width/2+(game_screen.block_size*2.1)
        for i, card in enumerate(self.hand):
            draw_text(f"{self.short_name}hand " + str(i+1) + ": "+card, game_screen.text_font, WHITE, x, game_screen.display_height/14*(i+1), game_screen.surface)
    
    def get_hand_name_by_mouse_pos(self, mouse_x: int, mouse_y: int, game_screen: GameScreen) -> tuple[str, int]:
        if (mouse_x < game_screen.display_width/2-game_screen.block_size*2.1 and mouse_x > game_screen.display_width/2-game_screen.block_size*3.3) or\
           (mouse_x > game_screen.display_width/2+game_screen.block_size*2.1 and mouse_x < game_screen.display_width/2+game_screen.block_size*3.3):
            i = int(mouse_y*14/game_screen.display_height+0.5)-1
            if -1 < i < len(self.hand):
                return self.hand[i], i
        return "None", 0
    
    def display_deck_info(self, game_screen: GameScreen) -> None:
        draw_text(f"{self.short_name}DrawDeck: {len(self.draw_pile)} cards", game_screen.text_font, WHITE, game_screen.display_width/2-(game_screen.block_size*self.deck_info_offeset_x), game_screen.display_height-(game_screen.block_size*0.5), game_screen.surface)
        draw_text(f"{self.short_name}DiscardPile: {len(self.discard_pile)} cards", game_screen.text_font, WHITE, game_screen.display_width/2-(game_screen.block_size*self.deck_info_offeset_x), game_screen.display_height-(game_screen.block_size*0.4), game_screen.surface)
    
    def display_luck(self, game_state: GameState) -> None:
        game_screen = game_state.game_screen
        draw_text(f"{self.short_name}Luck: {game_state.players_luck[self.name]}%", game_screen.text_font, GREEN, game_screen.display_width/2-(game_screen.block_size*self.luck_offeset_x), (game_screen.block_size*1.1), game_screen.surface)
        
    def update_timer(self, game_state: GameState) -> None:
        match game_state.timer_mode:
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
        self.display_timer(game_state.game_screen)

        
    def display_timer(self, game_screen: GameScreen) -> None:
        draw_text(f"{self.short_name}Clock: "+self.time_minutes_and_seconds, game_screen.text_font, WHITE, game_screen.display_width/2-(game_screen.display_width/6)*self.clock_offset_x, game_screen.display_height/6.4, game_screen.surface)