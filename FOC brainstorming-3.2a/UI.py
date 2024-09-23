from dataclasses import dataclass, field
import random, pygame
from typing import cast

from game_screen import GameScreen, draw_text, BLACK, WHITE, RED, BLUE
from card import Card



@dataclass(kw_only=True)
class AttackCountDisplay:
    player: str
    width: int
    height: int
    
    def display_blocks(self, number: int, game_screen: GameScreen) -> None:
        match self.player:
            case "player1":
                self.x, self.y = game_screen.display_width/2-(game_screen.block_size*4), game_screen.display_height/2+(game_screen.block_size*2.5)
            case "player2":
                self.x, self.y = game_screen.display_width/2+(game_screen.block_size*3.5), game_screen.display_height/2+(game_screen.block_size*2.5)    
        for i in range(1, 11):
            color = WHITE
            if number > 10:
                if number < 20:
                    if number%10 >= i:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                    else:
                        color = WHITE
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                elif number < 30:
                    if number%10 >= i:
                        color = (255, 100, 100)
                        pygame.draw.rect(game_screen.surface, color, (self.x+random.randint(0, round(self.width*0.1*(number*0.05)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(number*0.05)))*random.random(), self.width, self.height), round(self.width))
                    else:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                else:
                    color = (255, 100, 100)
                    pygame.draw.rect(game_screen.surface, color, (self.x+random.randint(0, round(self.width*0.1*(number*0.1)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(number*0.1)))*random.random(), self.width, self.height), round(self.width))
            elif i <= number:
                pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
            else:
                pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width/10))
                
                
@dataclass(kw_only=True)
class ScoreDisplay:
    width: int
    height: int
       
    def display_blocks(self, controller: str, score: int, on_board_cards: list[Card],  game_screen: GameScreen):
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
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.time = 0
        self.rea = True
    
    def displayCircle(self, game_screen, number: int):
        if  self.bool:
            self.time += 1
            if self.time == 60:
                self.bool = not self.bool
        else:
            self.time -= 1
            if self.time == 0:
                self.bool = not self.bool
        if number > 0:
            for i in range(0, number):
                pygame.draw.circle(game_screen.surface, (60*min(1, self.time/30), 100*min(1, self.time/30), 225*min(1, self.time/30)), (self.x, self.y-self.radius*i*2.2), self.radius)
            