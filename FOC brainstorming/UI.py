from dataclasses import dataclass, field
import random, pygame

from game_screen import GameScreen, draw_text, BLACK, WHITE, RED, BLUE, Sequence
from card import Card

class Button:
    def __init__(self, width: float, height: float, x: float, y: float, text_x: float, text_y: float, has_box: bool=True, box_color: Sequence[int]=WHITE, box_width: int=0, text_color: Sequence[int]=WHITE, text: str="", font: pygame.font.Font|None=None):
        self.height = height
        self.width = width
        self.has_box = has_box
        self.box_color = box_color
        self.box_width = box_width
        self.text_color = text_color
        self.x = x
        self.y = y
        self.text_x = text_x
        self.text_y = text_y
        self.text = text
        self.font = font
        self.surface = pygame.Surface((width, height))
        self.been_pressed: bool = False
    
    def update(self, game_screen: GameScreen):
        self.display(game_screen)

    def touch(self, mouse_x: float, mouse_y: float) -> bool:
        return self.x<mouse_x<self.x+self.width and self.y<mouse_y<self.y+self.height
    
    def display(self, game_screen: GameScreen):
        self.surface.fill((0, 0, 0, 0))
        if self.has_box:
            pygame.draw.rect(self.surface, self.box_color, (0, 0, self.width, self.height), self.box_width, border_radius=self.box_width*4)

        if self.font is not None:
            draw_text(self.text, self.font, self.text_color, self.text_x, self.text_y, self.surface)
        
        game_screen.surface.blit(self.surface, (self.x, self.y))


@dataclass(kw_only=True)
class AttackCountDisplay:
    player_name: str
    width: int
    height: int
    
    def display(self, attack_cout: int, game_screen: GameScreen) -> None:
        match self.player_name:
            case "player1":
                self.x, self.y = game_screen.display_width/2-game_screen.block_size*3.75, game_screen.display_height/2+game_screen.block_size*2.5
            case "player2":
                self.x, self.y = game_screen.display_width/2+game_screen.block_size*3.5, game_screen.display_height/2+game_screen.block_size*2.5    
        for i in range(1, 11):
            color = WHITE
            if attack_cout > 10:
                if attack_cout < 20:
                    if attack_cout%10 >= i:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                    else:
                        color = WHITE
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                elif attack_cout < 30:
                    if attack_cout%10 >= i:
                        color = (255, 100, 100)
                        pygame.draw.rect(game_screen.surface, color, (self.x+random.randint(0, round(self.width*0.1*(attack_cout*0.05)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(attack_cout*0.05)))*random.random(), self.width, self.height), round(self.width))
                    else:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                else:
                    color = (255, 100, 100)
                    pygame.draw.rect(game_screen.surface, color, (self.x+random.randint(0, round(self.width*0.1*(attack_cout*0.1)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(attack_cout*0.1)))*random.random(), self.width, self.height), round(self.width))
            elif i <= attack_cout:
                pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
            else:
                pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width/10))
                
                
@dataclass(kw_only=True)
class ScoreDisplay:
    width: int
    height: int
       
    def display(self, controller: str, score: int, on_board_cards: list[Card],  game_screen: GameScreen) -> None:
        score_list: list[int] = [score]
        self.x, self.y = game_screen.display_width/2-self.width/2, game_screen.display_height/10
        match controller:
            case "player1":
                score = 0
                for card in filter(lambda card: card.owner == "player1", on_board_cards):
                    score -= card.end_turn(False)
                score_list.append(score_list[-1]+score)
                score = 0
                for card in filter(lambda card: card.owner == "player2", on_board_cards):
                    score += card.end_turn(False)
                score_list.append(score_list[-1]+score)
            case "player2":
                score = 0
                for card in filter(lambda card: card.owner == "player2", on_board_cards):
                    score += card.end_turn(False)
                score_list.append(score_list[-1]+score)
                score = 0
                for card in filter(lambda card: card.owner == "player1", on_board_cards):
                    score -= card.end_turn(False)
                score_list.append(score_list[-1]+score)
        
        for i in range(-10, 11):
            if i == score_list[0]:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            else:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))
            if i == score_list[1]:
                pygame.draw.rect(game_screen.surface, BLUE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            if i == score_list[2]:
                pygame.draw.rect(game_screen.surface, RED, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))


@dataclass(kw_only=True)
class TokenDisplay:
    player_name: str
    radius: int
    time: int = field(init=False, default=0)
    is_glowing: bool = field(init=False, default=True)
    
    def display(self, token_count: int, game_screen: GameScreen) -> None:
        if token_count > 0:
            if  self.is_glowing:
                self.time += 1
                if self.time == 60:
                    self.is_glowing = not self.is_glowing
            else:
                self.time -= 1
                if self.time == 1:
                    self.is_glowing = not self.is_glowing
            offset_y = 0
            match self.player_name:
                case "player1":
                    offset_y = -1
                case "player2":
                    offset_y = 1
            for i in range(0, token_count):
                pygame.draw.circle(game_screen.surface, (int(60*min(1, self.time/30)), int(100*min(1, self.time/30)), int(225*min(1, self.time/30))), (game_screen.display_width/2+(game_screen.block_size*2.5*offset_y), game_screen.display_height-(game_screen.block_size*0.5)-(self.radius*i*2.2)), self.radius)