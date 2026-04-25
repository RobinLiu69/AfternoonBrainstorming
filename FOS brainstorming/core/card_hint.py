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
from dataclasses import dataclass, field
from typing import cast

import pygame

from core.game_screen import GameScreen, draw_text
from shared.setting import BLACK, WHITE, RED, GREEN, CARDS_HINTS_DICTIONARY, JOB_DICTIONARY
from cards.base import Card, COLOR_TAG_LIST


def get_job_and_color(card_type: str) -> tuple[str, tuple[int, int, int]]:
    for tag in COLOR_TAG_LIST:
        if card_type.endswith(tag):
            color_name = JOB_DICTIONARY["colors_dict"][tag]
            color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][color_name].split(", "))))
            if card_type.count(tag) > 1:
                return card_type[::-1].replace(tag, "", 1)[::-1], color
            else:
                return card_type.replace(tag, "", 1), color
    return "None", (0, 0, 0)


def get_job_shape(job: str, block_size: float) -> tuple:
    match job:
        case "ADC":
            return (((block_size*0.42), (block_size*0.22)),
                    ((block_size*0.17), (block_size*0.62)),
                    ((block_size*0.67), (block_size*0.62)))
        case "AP":
            return ((block_size*0.42), (block_size*0.42))
        case "HF":
            return (((block_size*0.32), (block_size*0.32)),
                    ((block_size*0.52), (block_size*0.32)),
                    ((block_size*0.67), (block_size*0.57)),
                    ((block_size*0.17), (block_size*0.57)))
        case "LF":
            return (((block_size*0.42), (block_size*0.22)),
                    ((block_size*0.28), (block_size*0.34)),
                    ((block_size*0.3975), (block_size*0.47)),
                    ((block_size*0.28), (block_size*0.60)),
                    ((block_size*0.42), (block_size*0.72)),
                    ((block_size*0.56), (block_size*0.60)),
                    ((block_size*0.4425), (block_size*0.47)),
                    ((block_size*0.56), (block_size*0.34)))
        case "ASS":
            return (((block_size*0.42), (block_size*0.32)),
                    ((block_size*0.12), (block_size*0.57)),
                    ((block_size*0.42), (block_size*0.42)),
                    ((block_size*0.72), (block_size*0.57)))
        case "APT":
            return (((block_size*0.32), (block_size*0.22)),
                    ((block_size*0.17), (block_size*0.42)),
                    ((block_size*0.32), (block_size*0.62)),
                    ((block_size*0.52), (block_size*0.62)),
                    ((block_size*0.67), (block_size*0.42)),
                    ((block_size*0.52), (block_size*0.22)))
        case "SP":
            return (((block_size*0.295), (block_size*0.22)),
                    ((block_size*0.17), (block_size*0.37)),
                    ((block_size*0.42), (block_size*0.67)),
                    ((block_size*0.67), (block_size*0.37)),
                    ((block_size*0.545), (block_size*0.22)))
        case "TANK":
            return (((block_size*0.17), (block_size*0.17)),
                    ((block_size*0.17), (block_size*0.67)),
                    ((block_size*0.67), (block_size*0.67)),
                    ((block_size*0.67), (block_size*0.17)))
        case "CUBE":
            return (((block_size*0.45), (block_size*0.45)),
                    ((block_size*0.45), (block_size*0.55)),
                    ((block_size*0.55), (block_size*0.55)),
                    ((block_size*0.55), (block_size*0.45)))
        case "CUBES":
            return (((block_size*0.45), (block_size*0.45)),
                    ((block_size*0.45), (block_size*0.55)),
                    ((block_size*0.55), (block_size*0.55)),
                    ((block_size*0.55), (block_size*0.45)))
        case "LUCKYBLOCK":
            return (((block_size*0.4), (block_size*0.4)),
                    ((block_size*0.4), (block_size*0.6)),
                    ((block_size*0.6), (block_size*0.6)),
                    ((block_size*0.6), (block_size*0.4)))
    return (((block_size*0.45), (block_size*0.45)),
            ((block_size*0.45), (block_size*0.55)),
            ((block_size*0.55), (block_size*0.55)),
            ((block_size*0.55), (block_size*0.45)))


@dataclass(kw_only=True)
class HintBox:
    width: int
    height: int
    surface: pygame.Surface | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.x = 0
        self.y = 0
        self.turn_on = False

    def update(self, mouse_x: int, mouse_y: int, card: Card | str, game_screen: GameScreen) -> None:
        self.x = mouse_x
        self.y = mouse_y
        if card:
            self.display(card, game_screen)

    def display(self, card: Card | str, game_screen: GameScreen) -> None:
        if not self.surface:
            self.surface = pygame.Surface((self.width, game_screen.block_size*1.5), pygame.SRCALPHA)
        if self.turn_on:
            if isinstance(card, str):
                card_type = card
            elif isinstance(card, Card):
                card_type = card.job_and_color
            else:
                return
            if card_type not in CARDS_HINTS_DICTIONARY: return
            if card_type not in ["CUBE", "CUBES", "LUCKYBLOCK", "MOVE", "MOVEO", "HEAL"]:
                box_height = len(CARDS_HINTS_DICTIONARY[card_type].split("\n")) if len(CARDS_HINTS_DICTIONARY[card_type].split("\n")) > 4 else 4
                box_width = game_screen.block_size* 1.15 + game_screen.block_size*max(map(len, CARDS_HINTS_DICTIONARY[card_type].split("\n")))/12

                pygame.draw.rect(self.surface, WHITE, (0, 0, box_width, (game_screen.block_size*0.05)+game_screen.block_size*(0.15*box_height)), 2)
                pygame.draw.rect(self.surface, BLACK, ((game_screen.thickness//2), (game_screen.thickness//2), box_width-game_screen.thickness,
                                                       (game_screen.block_size*0.05) + (game_screen.block_size*0.15*box_height) - game_screen.thickness), 1000)

                pygame.draw.rect(self.surface, WHITE, (game_screen.block_size*0.05, game_screen.block_size*0.05,
                                                       game_screen.block_size*0.5, game_screen.block_size*0.5), 2)
                job, color = get_job_and_color(card_type.split()[0])
                if color == (0, 238, 238) and getattr(card, "upgrade", False):
                    card_type += " (+)"
                    draw_text("(+)", game_screen.text_font, color, (game_screen.block_size*0.213), (game_screen.block_size*0.235), self.surface)
                shape = get_job_shape(job, game_screen.block_size*0.7)
                match job:
                    case "AP":
                        pygame.draw.circle(self.surface, color, shape, game_screen.block_size*0.15, int(game_screen.thickness/1.1))
                    case _:
                        pygame.draw.lines(self.surface, color, True, shape, int(game_screen.thickness*1.1))
                for i, line in enumerate(CARDS_HINTS_DICTIONARY[card_type].split("\n")):
                    if i == 0:
                        if isinstance(card, str):
                            draw_text(f"{card_type} {line}", game_screen.text_fontCHI, WHITE,
                                      (game_screen.block_size*0.6), (game_screen.block_size*0.05), self.surface)
                        elif isinstance(card, Card):
                            draw_text(f"{card_type}", game_screen.text_fontCHI, WHITE, game_screen.block_size*0.6,
                                      (game_screen.block_size*0.05), self.surface)
                            draw_text(f"{card.health}", game_screen.text_fontCHI, RED if card.health < card.max_health else WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)), (game_screen.block_size*0.05), self.surface)
                            draw_text(f"/", game_screen.text_fontCHI, WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health))),
                                      (game_screen.block_size*0.05), self.surface)
                            draw_text(f"{card.damage}", game_screen.text_fontCHI,
                                      RED if card.damage < card.original_damage else GREEN if card.damage > card.original_damage else WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health))+1),
                                      (game_screen.block_size*0.05), self.surface)
                            atk_type = line.split("-")
                            draw_text(f"-{atk_type[1]}", game_screen.text_fontCHI, WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health))+len(str(card.damage))+1),
                                      (game_screen.block_size*0.05), self.surface)
                    elif i < 4:
                        draw_text(f"{line}", game_screen.text_fontCHI, WHITE, (game_screen.block_size*0.6),
                                  (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
                    else:
                        draw_text(f"{line}", game_screen.text_fontCHI, WHITE, (game_screen.block_size*0.6),
                                  (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
            else:
                box_height = len(CARDS_HINTS_DICTIONARY[card_type].split("\n")) if len(CARDS_HINTS_DICTIONARY[card_type].split("\n")) > 4 else 4
                box_width = game_screen.block_size*max(map(len, CARDS_HINTS_DICTIONARY[card_type].split("\n")))/7
                
                pygame.draw.rect(self.surface, WHITE, (0, 0, box_width, (game_screen.block_size*0.05)+game_screen.block_size*(0.15*box_height)), 2)
                pygame.draw.rect(self.surface, BLACK, ((game_screen.thickness//2), (game_screen.thickness//2), box_width-game_screen.thickness,
                                                       (game_screen.block_size*0.05) + (game_screen.block_size*0.15*box_height) - game_screen.thickness), 1000)
                
                for i, line in enumerate(CARDS_HINTS_DICTIONARY[card_type].split("\n")):
                    draw_text(f"{line}", game_screen.text_fontCHI, WHITE, (game_screen.block_size*0.05),
                              (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
            game_screen.surface.blit(self.surface, (self.x, self.y))
        self.surface.fill((0, 0, 0, 0))
