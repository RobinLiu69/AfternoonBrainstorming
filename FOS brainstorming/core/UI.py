# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Optional, Sequence, TYPE_CHECKING

import pygame

from core.game_screen import GameScreen, draw_text
from core.setting import WHITE, RED, BLUE

if TYPE_CHECKING:
    from core.game_state import GameState


@dataclass(kw_only=True)
class BasicUI:
    x: float = 0
    y: float = 0
    height: float = 0
    width: float = 0
    surface : pygame.Surface | None = field(init=False, default=None)


@dataclass
class HighLightBox(BasicUI):
    box_color: Optional[tuple[int, int, int]] = None
    box_height: float = 0
    box_width: float = 0
    line_width: int = 0
    border_radius: int = 0
    visable: bool = False

    def update(self, index: int, length: int, game_screen: GameScreen) -> None:
        self.display(index, length, game_screen)

    def display(self, index: int, length: int, game_screen: GameScreen) -> None:
        if self.visable:
            prefix = 7 if index < 9 else 7.5
            self.box_width = game_screen.block_size/10*(length*0.8+prefix)
            self.y = game_screen.display_height/14*(index+0.8)
            if self.box_color:
                pygame.draw.rect(game_screen.surface, self.box_color, (self.x, self.y, self.box_width, self.box_height), width=self.line_width)


class Button:
    def __init__(self, width: float, height: float, x: float, y: float, text_x: float, text_y: float,
                 has_box: bool=True, box_color: Sequence[int]=WHITE, box_width: int=0, text_color: Sequence[int]=WHITE,
                 text: str="", font: pygame.font.Font|None=None):
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

        if self.font:
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
                        pygame.draw.rect(game_screen.surface, color,
                                         (self.x+random.randint(0, round(self.width*0.1*(attack_cout*0.05)))*random.random(),
                                          self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(attack_cout*0.05)))*random.random(),
                                          self.width, self.height), round(self.width))
                    else:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                else:
                    color = (255, 100, 100)
                    pygame.draw.rect(game_screen.surface, color,
                                     (self.x+random.randint(0, round(self.width*0.1*(attack_cout*0.1)))*random.random(),
                                      self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(attack_cout*0.1)))*random.random(),
                                      self.width, self.height), round(self.width))
            elif i <= attack_cout:
                pygame.draw.rect(game_screen.surface, color,
                                 (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
            else:
                pygame.draw.rect(game_screen.surface, color,
                                 (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width/10))


@dataclass(kw_only=True)
class ScoreDisplay:
    width: int
    height: int
       
    def display(self, local_controller: str, controller: str, game_state: GameState, game_screen: GameScreen) -> None:
        score_list: list[int] = [game_state.score]
        self.x, self.y = game_screen.display_width/2-self.width/2, game_screen.display_height/10

        score = 0
        for card in game_state.get_player_cards(controller):
            score -= card.end_turn(False) if controller == "player1" else -card.end_turn(False)
        score_list.append(score_list[-1]+score)
        score = 0
        for card in game_state.get_opponent_cards(controller):
            score -= card.end_turn(False) if controller == "player2" else -card.end_turn(False)
        score_list.append(score_list[-1]+score)
        
        for i in range(-10, 11):
            if i == score_list[0]:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            else:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))
            if i == score_list[1]:
                pygame.draw.rect(game_screen.surface, BLUE if controller == local_controller else RED, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            if i == score_list[2]:
                pygame.draw.rect(game_screen.surface, RED if controller == local_controller else BLUE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))


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
                pygame.draw.circle(game_screen.surface, (int(60*min(1, self.time/30)), int(100*min(1, self.time/30)), int(225*min(1, self.time/30))),
                                   (game_screen.display_width/2+(game_screen.block_size*2.5*offset_y),
                                    game_screen.display_height-(game_screen.block_size*0.5)-(self.radius*i*2.2)), self.radius)
