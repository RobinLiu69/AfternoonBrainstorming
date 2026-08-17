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
from shared import card_code
from shared.setting import BLACK, WHITE, RED, GREEN, CARD_SETTING, CARDS_HINTS_DICTIONARY, JOB_DICTIONARY
from cards.base import Card, COLOR_TAG_LIST


TAGLESS_UNITS: dict[str, str] = {"LUCKYBLOCK": "Green"}


def get_job_and_color(card_type: str) -> tuple[str, tuple[int, int, int]]:
    color_name = TAGLESS_UNITS.get(card_type)
    if color_name is not None:
        r, g, b = JOB_DICTIONARY["RGB_colors"][color_name]
        return card_type, (r, g, b)
    for tag in COLOR_TAG_LIST:
        if card_type.endswith(tag):
            color_name = JOB_DICTIONARY["colors_dict"][tag]
            color = tuple(JOB_DICTIONARY["RGB_colors"][color_name])
            if card_type.count(tag) > 1:
                return card_type[::-1].replace(tag, "", 1)[::-1], color
            else:
                return card_type.replace(tag, "", 1), color
    return "None", (0, 0, 0)


def get_job_and_color_name(card_type: str) -> tuple[str, str]:
    color_name = TAGLESS_UNITS.get(card_type)
    if color_name is not None:
        return card_type, color_name
    for tag in COLOR_TAG_LIST:
        if card_type.endswith(tag):
            color_name = JOB_DICTIONARY["colors_dict"][tag]
            if card_type.count(tag) > 1:
                return card_type[::-1].replace(tag, "", 1)[::-1], color_name
            else:
                return card_type.replace(tag, "", 1), color_name
    return "None", "None"


def get_stat_prefix(card_type: str) -> str:
    upgraded = card_type.endswith("(+)")
    job, color_name = get_job_and_color_name(card_code.plain_code(card_type))
    settings = CARD_SETTING.get(color_name, {}).get(job)
    if not settings:
        return ""
    if "cost" in settings:
        health = settings["upgrade_health"] if upgraded else settings["health"]
        damage = settings["upgrade_damage"] if upgraded else settings["damage"]
        return f"{health}/{damage}({settings['cost']})"
    return f"{settings['health']}/{settings['damage']}"


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
            return (((block_size*0.20), (block_size*0.20)),
                    ((block_size*0.20), (block_size*0.64)),
                    ((block_size*0.64), (block_size*0.64)),
                    ((block_size*0.64), (block_size*0.20)))
        case "WIGHT":
            return (((block_size*0.42), (block_size*0.24)),
                    ((block_size*0.24), (block_size*0.42)),
                    ((block_size*0.42), (block_size*0.60)),
                    ((block_size*0.60), (block_size*0.42)))
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

    def _prepare(self, box_width: float, box_height: float) -> pygame.Surface:
        needed_width = int(box_width) + 1
        needed_height = int(box_height) + 1
        if (self.surface is None or self.surface.get_width() < needed_width
                or self.surface.get_height() < needed_height):
            self.surface = pygame.Surface((max(needed_width, self.width),
                                           max(needed_height, self.height)), pygame.SRCALPHA)
        return self.surface

    def anchor(self, box_width: float, box_height: float, game_screen: GameScreen) -> tuple[float, float]:
        return (max(0, min(self.x, game_screen.display_width - box_width)),
                max(0, min(self.y, game_screen.display_height - box_height)))

    def _place(self, box_width: float, box_height: float, game_screen: GameScreen) -> None:
        if self.surface is None:
            return
        game_screen.surface.blit(self.surface, self.anchor(box_width, box_height, game_screen),
                                 pygame.Rect(0, 0, int(box_width) + 1, int(box_height) + 1))
        self.surface.fill((0, 0, 0, 0))

    def display(self, card: Card | str, game_screen: GameScreen) -> None:
        if self.turn_on:
            if isinstance(card, str):
                decorated = card
                card_type = card_code.base_code(card)
            elif isinstance(card, Card):
                decorated = getattr(card, "tower_code", "") or card.job_and_color
                card_type = card.job_and_color
            else:
                return
            if card_type not in CARDS_HINTS_DICTIONARY: return
            enchant_lines = card_code.describe_enchants(decorated)
            if card_type not in ["CUBE", "CUBES", "MOVE", "MOVEO", "HEAL", card_code.BARROW_CODE]:
                job, color = get_job_and_color(card_type.split()[0])
                upgraded = color == (0, 238, 238) and getattr(card, "upgrade", False)
                if upgraded:
                    card_type += " (+)"
                hint_lines = CARDS_HINTS_DICTIONARY[card_type].split("\n") + enchant_lines
                if isinstance(card, Card):
                    first_line = f"{card_type}{card.health+card.armor}/{card.damage}-{hint_lines[0]}"
                else:
                    first_line = f"{card_type} {get_stat_prefix(card_type)}-{hint_lines[0]}"
                display_lines = [first_line, *hint_lines[1:]]
                box_height = len(display_lines) if len(display_lines) > 4 else 4
                if isinstance(card, Card):
                    stats_span = game_screen.block_size*0.07*(
                        len(card_type) + len(str(card.health+card.armor)) + len(str(card.damage)) + 1)
                    first_width = stats_span + game_screen.text_fontCHI.size(f"-{hint_lines[0]}")[0]
                else:
                    first_width = game_screen.text_fontCHI.size(first_line)[0]
                box_width = game_screen.block_size*0.75 + max(
                    [first_width, *(game_screen.text_fontCHI.size(line)[0] for line in display_lines[1:])])
                box_pixel_height = (game_screen.block_size*0.05)+game_screen.block_size*(0.15*box_height)
                self._prepare(box_width, box_pixel_height)

                pygame.draw.rect(self.surface, WHITE, (0, 0, box_width, box_pixel_height), 2)
                pygame.draw.rect(self.surface, BLACK, ((game_screen.thickness//2), (game_screen.thickness//2), box_width-game_screen.thickness,
                                                       box_pixel_height - game_screen.thickness), 1000)

                pygame.draw.rect(self.surface, WHITE, (game_screen.block_size*0.05, game_screen.block_size*0.05,
                                                       game_screen.block_size*0.5, game_screen.block_size*0.5), 2)
                if upgraded:
                    draw_text("(+)", game_screen.text_font, color, (game_screen.block_size*0.213), (game_screen.block_size*0.235), self.surface)
                shape = get_job_shape(job, game_screen.block_size*0.7)
                match job:
                    case "AP":
                        pygame.draw.circle(self.surface, color, shape, game_screen.block_size*0.15, int(game_screen.thickness/1.1))
                    case _:
                        pygame.draw.lines(self.surface, color, True, shape, int(game_screen.thickness*1.1))
                if job == "LUCKYBLOCK":
                    draw_text("?", game_screen.text_font, color, game_screen.block_size*0.275,
                              game_screen.block_size*0.245, self.surface)
                for i, line in enumerate(hint_lines):
                    if i == 0:
                        if isinstance(card, str):
                            draw_text(f"{card_type} {get_stat_prefix(card_type)}-{line}", game_screen.text_fontCHI, WHITE,
                                      (game_screen.block_size*0.6), (game_screen.block_size*0.05), self.surface)
                        elif isinstance(card, Card):
                            draw_text(f"{card_type}", game_screen.text_fontCHI, WHITE, game_screen.block_size*0.6,
                                      (game_screen.block_size*0.05), self.surface)
                            draw_text(f"{card.health+card.armor}", game_screen.text_fontCHI, RED if card.health+card.armor < card.max_health else WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)), (game_screen.block_size*0.05), self.surface)
                            draw_text(f"/", game_screen.text_fontCHI, WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health+card.armor))),
                                      (game_screen.block_size*0.05), self.surface)
                            draw_text(f"{card.damage}", game_screen.text_fontCHI,
                                      RED if card.damage < card.original_damage else GREEN if card.damage > card.original_damage else WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health+card.armor))+1),
                                      (game_screen.block_size*0.05), self.surface)
                            draw_text(f"-{line}", game_screen.text_fontCHI, WHITE,
                                      game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health+card.armor))+len(str(card.damage))+1),
                                      (game_screen.block_size*0.05), self.surface)
                    elif i < 4:
                        draw_text(f"{line}", game_screen.text_fontCHI, WHITE, (game_screen.block_size*0.6),
                                  (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
                    else:
                        draw_text(f"{line}", game_screen.text_fontCHI, WHITE, (game_screen.block_size*0.6),
                                  (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
            else:
                spell_lines = CARDS_HINTS_DICTIONARY[card_type].split("\n") + enchant_lines
                box_height = len(spell_lines) if len(spell_lines) > 4 else 4
                box_width = game_screen.block_size*0.15 + max(
                    game_screen.text_fontCHI.size(line)[0] for line in spell_lines)
                box_pixel_height = (game_screen.block_size*0.05)+game_screen.block_size*(0.15*box_height)
                self._prepare(box_width, box_pixel_height)

                pygame.draw.rect(self.surface, WHITE, (0, 0, box_width, box_pixel_height), 2)
                pygame.draw.rect(self.surface, BLACK, ((game_screen.thickness//2), (game_screen.thickness//2), box_width-game_screen.thickness,
                                                       box_pixel_height - game_screen.thickness), 1000)

                for i, line in enumerate(spell_lines):
                    draw_text(f"{line}", game_screen.text_fontCHI, WHITE, (game_screen.block_size*0.05),
                              (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
            self._place(box_width, box_pixel_height, game_screen)
