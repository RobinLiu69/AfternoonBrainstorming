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

"""One screen for every "pick one of these" moment in a climb.

An option is a dict::

    {"label": str, "lines": [str, ...], "color": (r, g, b), "card": "TANKW*sharp"}

``card`` is optional; when present the real card art is drawn above the text.
Returns the chosen index, ``SKIP`` if the skip button was used, or ``None``
when the player backed out.
"""

from typing import Optional

import pygame

from shared import card_code
from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, cell_origin, QuitGame
from core.UI import Button
from core.card_hint import HintBox
from core.setting_config import load_setting
from cards.factory import CardFactory
from rendering.card_renderer import CardRenderer
from utils.controls import key_pressed

from tower import ui_common

SKIP: int = -1

_COLUMN_SLOTS: dict[int, list[float]] = {
    1: [1.5],
    2: [0.5, 2.5],
    3: [-0.5, 1.5, 3.5],
    4: [-1.0, 0.75, 2.5, 4.25],
}


def _slots(count: int) -> list[float]:
    if count in _COLUMN_SLOTS:
        return _COLUMN_SLOTS[count]
    return [i * 1.6 - (count - 1) * 0.8 + 1.5 for i in range(count)]


def main(game_screen: GameScreen, title: str, options: list[dict],
         subtitle: str = "", run: Optional[dict] = None,
         skip_label: str = "", cancel_label: str = "") -> Optional[int]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width = ui_common.box_width(game_screen)

    card_renderer = CardRenderer(game_screen)
    hint_box = HintBox(width=int(bs * 3), height=int(bs))
    hint_on = load_setting("hint_on")

    slots = _slots(len(options))
    display_cards: dict[int, object] = {}
    for i, option in enumerate(options):
        code = option.get("card")
        if not code:
            continue
        try:
            display_cards[i] = CardFactory.create(
                card_code.plain_code(code), "display", slots[i], 1)
        except (ValueError, KeyError):
            pass

    def rect_for(index: int) -> pygame.Rect:
        x, y = cell_origin(game_screen, slots[index], 1)
        return pygame.Rect(int(x), int(y), int(bs), int(bs))

    skip_button = None
    if skip_label:
        skip_button = Button(bs * 2.6, bs * 0.55, cx - bs * 1.3, cy + bs * 2.2,
                             box_width=box_width, font=game_screen.big_text_font,
                             text=skip_label)
    cancel = ui_common.back_button(game_screen, cancel_label) if cancel_label else None

    chosen: Optional[int] = None
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        hover = -1
        for i in range(len(options)):
            if rect_for(i).inflate(int(bs * 0.2), int(bs * 1.6)).collidepoint(mouse_x, mouse_y):
                hover = i

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key == pygame.K_ESCAPE:
                    running = False
                if key == pygame.K_f:
                    hint_on = not hint_on
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cancel is not None and cancel.touch(mouse_x, mouse_y):
                    running = False
                elif skip_button is not None and skip_button.touch(mouse_x, mouse_y):
                    chosen = SKIP
                    running = False
                elif hover >= 0:
                    chosen = hover
                    running = False
            if event.type == pygame.QUIT:
                raise QuitGame

        if run is not None:
            ui_common.draw_run_bar(game_screen, run)
            ui_common.draw_relic_strip(game_screen, run)

        draw_text(title, game_screen.title_text_font, WHITE,
                  cx - bs * 3.4, cy - bs * 3.0, game_screen.surface)
        if subtitle:
            draw_text(subtitle, game_screen.mid_text_font, ui_common.GOLD,
                      cx - bs * 3.4, cy - bs * 2.3, game_screen.surface)

        for i, option in enumerate(options):
            rect = rect_for(i)
            color = option.get("color", WHITE)
            card = display_cards.get(i)
            if card is not None:
                for render_object in card.get_render_data():
                    card_renderer.render(render_object)
            else:
                pygame.draw.rect(game_screen.surface, color, rect, box_width)

            draw_text(option.get("label", ""), game_screen.text_font, color,
                      rect.x - bs * 0.25, rect.y - bs * 0.45, game_screen.surface)
            line_y = rect.y + bs * 1.15
            for line in option.get("lines", []):
                draw_text(line, game_screen.small_text_font, color,
                          rect.x - bs * 0.25, line_y, game_screen.surface)
                line_y += bs * 0.28

            if i == hover:
                pygame.draw.rect(game_screen.surface, ui_common.HILITE,
                                 rect.inflate(int(bs * 0.15), int(bs * 0.15)), box_width)

        if skip_button is not None:
            skip_button.update(game_screen)
        if cancel is not None:
            cancel.update(game_screen)

        hint_box.turn_on = hint_on
        if hint_on and hover >= 0 and options[hover].get("card"):
            hint_box.update(mouse_x, mouse_y,
                            card_code.plain_code(options[hover]["card"]), game_screen)

        pygame.display.update()
        clock.tick(60)

    return chosen
