# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
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
from typing import Literal, Optional, Sequence, TYPE_CHECKING

import pygame

from core.game_screen import GameScreen, draw_text
from shared.setting import WHITE, RED, BLUE

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


TextPosition = Literal["Left", "Middle", "Right"]


class Button:
    def __init__(self, width: float, height: float, x: float, y: float,
        position: TextPosition = "Middle", padding: float = 10,
        has_box: bool=True, box_color: Sequence[int]=WHITE,
        box_width: int=0, text_color: Sequence[int]=WHITE,
        text: str="", font: pygame.font.Font|None=None,
        fill_color: Sequence[int]|None=None, radius: int|None=None):
        self.height = height
        self.width = width
        self.has_box = has_box
        self.box_color = box_color
        self.box_width = box_width
        self.text_color = text_color
        self.fill_color = fill_color
        self.radius = box_width * 2 if radius is None else radius
        self.x = x
        self.y = y
        self.position = position
        self.padding = padding
        self.text = text
        self.font = font
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.been_pressed: bool = False

    def update(self, game_screen: GameScreen):
        self.display(game_screen)

    def touch(self, mouse_x: float, mouse_y: float) -> bool:
        return self.x < mouse_x < self.x+self.width and self.y < mouse_y < self.y+self.height

    def display(self, game_screen: GameScreen):
        self.surface.fill((0, 0, 0, 0))
        radius = self.radius
        if self.fill_color is not None:
            pygame.draw.rect(self.surface, self.fill_color,
                             (0, 0, self.width, self.height), 0, border_radius=radius)
        if self.has_box:
            pygame.draw.rect(self.surface, self.box_color, (0, 0, self.width, self.height), self.box_width, border_radius=radius)

        if self.font and self.text:
            rendered = self.font.render(self.text, True, self.text_color)
            ink = rendered.get_bounding_rect()
            ref_ink = self.font.render("Ay", True, self.text_color).get_bounding_rect()

            if self.position == "Left":
                tx = self.padding - ink.x
            elif self.position == "Right":
                tx = self.width - self.padding - ink.right
            else:
                tx = (self.width - ink.width) / 2 - ink.x

            ty = (self.height - ref_ink.height) / 2 - ref_ink.y

            draw_text(self.text, self.font, self.text_color, tx, ty, self.surface)

        game_screen.surface.blit(self.surface, (self.x, self.y))


@dataclass(kw_only=True)
class AttackCountDisplay:
    player_name: str
    width: int
    height: int

    def display(self, attack_cout: int, game_screen: GameScreen,
                x: float, y: float) -> None:
        pitch = self.width * 1.35
        tiers = (WHITE, (100, 255, 255), (255, 100, 100))
        full = min(2, max(0, (attack_cout - 1) // 10))
        shaking = attack_cout > 20
        for i in range(1, 11):
            lit = attack_cout % 10 >= i if attack_cout > 10 else i <= attack_cout
            if attack_cout >= 30:
                lit = True
            color = tiers[full] if lit else tiers[max(0, full - 1)] if attack_cout > 10 else WHITE
            border = round(self.width) if lit or attack_cout > 10 else round(self.width / 10)
            jitter = self.width * 0.25
            dx = random.uniform(-jitter, jitter) if shaking and lit else 0
            dy = random.uniform(-jitter, jitter) if shaking and lit else 0
            pygame.draw.rect(game_screen.surface, color,
                             (x + pitch * (i - 1) + dx, y + dy, self.width, self.height),
                             border)


@dataclass(kw_only=True)
class ScoreDisplay:
    width: int
    height: int
       
    def display(self, local_controller: str, controller: str, game_state: GameState, game_screen: GameScreen) -> None:
        score_list: list[int] = [game_state.score]
        self.x, self.y = game_screen.display_width/2-self.width/2, game_screen.display_height/10

        score = 0
        for card in game_state.get_player_cards(controller):
            score -= card.on_settle(False) if controller == "player1" else -card.on_settle(False)
        score_list.append(score_list[-1]+score)
        score = 0
        for card in game_state.get_opponent_cards(controller):
            score -= card.on_settle(False) if controller == "player2" else -card.on_settle(False)
        score_list.append(score_list[-1]+score)

        # Spectators use player1's perspective: BLUE = player1 side, RED = player2 side.
        effective_local = local_controller if local_controller in ("player1", "player2") else "player1"
        for i in range(-10, 11):
            if i == score_list[0]:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            else:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))
            if i == score_list[1]:
                pygame.draw.rect(game_screen.surface, BLUE if controller == effective_local else RED, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            if i == score_list[2]:
                pygame.draw.rect(game_screen.surface, RED if controller == effective_local else BLUE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))
