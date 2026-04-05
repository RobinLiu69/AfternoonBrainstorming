from dataclasses import dataclass, asdict
from typing import Optional, TYPE_CHECKING
import random
import time

from core.game_screen import GameScreen, draw_text
from core.UI import AttackCountDisplay, TokenDisplay, HighLightBox
from core.setting import WHITE, BLUE, RED
from core.game_statistics import StatType
from cards.base import Card
from cards.factory import spawn_card

if TYPE_CHECKING:
    from rendering.game_renderer import GameRenderer
    from core.game_state import GameState

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
    
    def _init_cards(self, game_state: GameState) -> None:
        match self.name:
            case "player1":
                self.discard_pile = self.deck.copy()
                for i in range(3): self.draw_card(game_state)
                game_state.number_of_attacks[self.name] += 1
            case "player2":
                self.discard_pile = self.deck.copy()
                for i in range(3): self.draw_card(game_state)
    
    def _init_highlight_display(self, game_screen: GameScreen) -> None:
        x = game_screen.display_width/2-(game_screen.block_size*3.3) if self.name == "player1" else game_screen.display_width/2+(game_screen.block_size*2.025)
        self.selected_highlight = HighLightBox(x=x, y=0, box_color=BLUE if self.name=="player1" else RED,
        box_height=int(game_screen.block_size/3), box_width=int(game_screen.block_size), line_width=int(game_screen.block_size//50))
    
    def initialize(self, game_state: GameState, game_screen: GameScreen) -> None:
        self.attack_count_display = AttackCountDisplay(player_name=self.name, width=int(game_screen.block_size*0.1), height=int(game_screen.block_size*0.1))
        self.token_count_display = TokenDisplay(player_name=self.name, radius=int(game_screen.block_size*0.1))
        self._init_cards(game_state)
        self._init_highlight_display(game_screen)
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
                
    
    def recycle_cards(self, game_state: GameState, game_renderer: GameRenderer) -> None:
        for i, card in enumerate(self.on_board):
            if card.health <= 0 and card.can_be_killed(game_state):
                card.die(game_state)
                game_renderer.card_renderer.release(card.get_uid())
                card_name = self.on_board.pop(i).job_and_color
                self.discard_pile.append(card_name)
                game_state.board_dict[card.board_x, card.board_y].occupy = False
                game_state.game_logger.log_card_recycled(self.name, card_name, (card.board_x, card.board_y))
    
    def add_card_to_deck(self, card: str) -> None:
        if (card != "None" and len(self.deck) < 12 and
        ((self.deck.count(card) < 2 and card not in MAGIC_CARDS) or (self.deck.count(card) < 3 and card in MAGIC_CARDS))):
            self.deck.append(card)
    
    def pop_card_from_deck(self) -> None:
        if len(self.deck) > 0:
            self.deck.pop()

    def remove_card_from_deck(self, card_name: str, from_end: bool=True) -> None:
        if len(self.deck) > 0 and card_name in self.deck:
            deck = self.deck[::-1] if from_end else self.deck
            deck.remove(card_name)
            self.deck = deck[::-1] if from_end else deck
            
    def spawn_cube(self, board_x: int, board_y: int, game_state: GameState) -> None:
        if game_state.number_of_cudes[self.name] > 0:
            if spawn_card(board_x, board_y, "CUBE", "neutral", game_state.neutral.on_board, game_state):
                game_state.game_logger.log_card_played(self.name, "CUBE", (board_x, board_y))
                game_state.number_of_cudes[self.name] -= 1
                game_state.game_statistics.increment(StatType.CUBE_USE, self.name, 1)
            pass
    
    def timer_start(self, game_state: GameState) -> None:
        self.start_time = time.time()
        match game_state.timer_mode:
            case "countdown":
                self.elapsed_time = game_state.coutdown_time
        self._update_timer_logic(game_state.timer_mode)
    
    def logic_update(self, game_state: GameState, game_renderer: GameRenderer, update_timer: bool) -> None:
        self.recycle_cards(game_state, game_renderer)
        if game_state.card_to_draw[self.name] > 0:
            game_state.card_to_draw[self.name] -= 1
            self.draw_card(game_state)

        if update_timer:
            self._update_timer_logic(game_state.timer_mode)

    def get_hand_name_by_mouse_pos(self, mouse_x: int, mouse_y: int, game_screen: GameScreen) -> tuple[str, int]:
        if ((mouse_x < game_screen.display_width/2-game_screen.block_size*2.1 and mouse_x > game_screen.display_width/2-game_screen.block_size*3.3) or
           (mouse_x > game_screen.display_width/2+game_screen.block_size*2.1 and mouse_x < game_screen.display_width/2+game_screen.block_size*3.3)):
            i = int(mouse_y*14/game_screen.display_height+0.5)-1
            if -1 < i < len(self.hand):
                return self.hand[i], i
        return "None", 0

    def _update_timer_logic(self, timer_mode: str) -> None:
        match timer_mode:
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

    def to_dict(self) -> dict:
        return {
                "name": self.name,
                "deck": self.deck,
                "hand": self.hand,
                "on_board": self.on_board,
                "draw_pile": self.draw_pile,
                "discard_pile": self.discard_pile,
                "start_time": self.start_time,
                "elapsed_time": self.elapsed_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Player:
        player = cls(
            name=data["name"],
            deck=data["deck"],
            hand=data["hand"],
            on_board=data["on_board"],
            draw_pile=data["draw_pile"],
            discard_pile=data["discard_pile"]
        )

        player.start_time = data["start_time"]
        player.elapsed_time = data["elapsed_time"]
        return player