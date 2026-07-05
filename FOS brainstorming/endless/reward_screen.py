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

from typing import Optional

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from core.card_hint import HintBox
from core.setting_config import load_setting
from cards.factory import CardFactory
from rendering.card_renderer import CardRenderer
from utils.controls import key_pressed

from endless.content import RELICS


TEMP_COLOR: tuple[int, int, int] = (255, 170, 60)
RELIC_COLOR: tuple[int, int, int] = (255, 215, 0)
GOLD: tuple[int, int, int] = (255, 215, 0)


def _cell_rect(game_screen: GameScreen, bx: int, by: int) -> pygame.Rect:
    bs = game_screen.block_size
    x = game_screen.display_width / 2 - bs * 2 + bx * bs
    y = game_screen.display_height / 2 - bs * 1.65 + by * bs
    return pygame.Rect(int(x), int(y), int(bs), int(bs))


def main(game_screen: GameScreen, run: dict, options: list[dict], pending: dict) -> Optional[dict]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    card_renderer = CardRenderer(game_screen)
    hint_box = HintBox(width=int(bs * 3), height=int(bs))
    hint_on = load_setting("hint_on")

    display_cards: dict[int, object] = {}
    for i, option in enumerate(options[:3]):
        if option.get("type") == "card":
            try:
                display_cards[i] = CardFactory.create(option["card"], "display", i, 1)
            except ValueError:
                pass

    skip_button = Button(bs * 2.2, bs * 0.55, cx - bs * 1.1, cy + bs * 2.1,
                         bs * 0.3, bs * 0.13,
                         box_width=box_width, font=game_screen.big_text_font,
                         text="skip  (+10 coins)")

    chosen: Optional[dict] = None
    clock = pygame.time.Clock()
    coins_gained = pending.get("coins_gained", 0)
    lost = pending.get("lost", [])

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        hover_index = -1
        for i in range(len(options[:3])):
            if _cell_rect(game_screen, i, 1).collidepoint(mouse_x, mouse_y):
                hover_index = i

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE:
                    running = False
                if key_pressed(keys) == pygame.K_f:
                    hint_on = not hint_on
            if event.type == pygame.MOUSEBUTTONDOWN:
                if skip_button.touch(mouse_x, mouse_y):
                    chosen = {"type": "skip"}
                    running = False
                elif hover_index >= 0:
                    chosen = options[hover_index]
                    running = False
            if event.type == pygame.QUIT:
                running = False

        draw_text(f"Floor {run['floor']} cleared!", game_screen.title_text_font, WHITE,
                  cx - bs * 1.9, cy - bs * 3.1, game_screen.surface)
        draw_text(f"+{coins_gained} coins   (total: {run['coins']})",
                  game_screen.big_text_font, GOLD,
                  cx - bs * 1.9, cy - bs * 2.4, game_screen.surface)
        if lost:
            draw_text(f"lost in battle: {' '.join(lost)}", game_screen.mid_text_font, (255, 90, 90),
                      cx - bs * 1.9, cy - bs * 1.95, game_screen.surface)
        draw_text("choose one:", game_screen.big_text_font, WHITE,
                  cx - bs * 1.9, cy - bs * 1.35, game_screen.surface)

        for i, option in enumerate(options[:3]):
            rect = _cell_rect(game_screen, i, 1)
            if option.get("type") == "card":
                card = display_cards.get(i)
                if card is not None:
                    for render_object in card.get_render_data():
                        card_renderer.render(render_object)
                else:
                    pygame.draw.rect(game_screen.surface, WHITE, rect, box_width)
                    draw_text(option["card"], game_screen.big_text_font, WHITE,
                              rect.x + bs * 0.1, rect.y + bs * 0.35, game_screen.surface)
                draw_text("temporary", game_screen.text_font, TEMP_COLOR,
                          rect.x + bs * 0.08, rect.y + bs * 1.05, game_screen.surface)
            elif option.get("type") == "relic":
                relic = RELICS[option["relic"]]
                pygame.draw.rect(game_screen.surface, RELIC_COLOR, rect, box_width)
                draw_text(relic["label"], game_screen.text_font, RELIC_COLOR,
                          rect.x + bs * 0.08, rect.y + bs * 0.15, game_screen.surface)
                draw_text("relic", game_screen.small_text_font, RELIC_COLOR,
                          rect.x + bs * 0.08, rect.y + bs * 0.45, game_screen.surface)
                draw_text(relic["text"], game_screen.text_font, RELIC_COLOR,
                          rect.x + bs * 0.08, rect.y + bs * 1.05, game_screen.surface)
            if i == hover_index:
                pygame.draw.rect(game_screen.surface, WHITE, rect.inflate(int(bs * 0.1), int(bs * 0.1)), box_width)

        draw_text("units: lost when they die    magic: lost when used",
                  game_screen.text_font, TEMP_COLOR,
                  cx - bs * 1.9, cy + bs * 1.6, game_screen.surface)

        skip_button.update(game_screen)

        hint_box.turn_on = hint_on
        if hint_on and hover_index >= 0 and options[hover_index].get("type") == "card":
            hint_box.update(mouse_x, mouse_y, options[hover_index]["card"], game_screen)

        pygame.display.update()
        clock.tick(60)

    return chosen
