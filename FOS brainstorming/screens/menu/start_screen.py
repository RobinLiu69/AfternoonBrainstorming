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

import pygame

from shared.setting import WHITE, VERSION
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from rendering import style
from utils.controls import key_pressed


def main(game_screen: GameScreen) -> str:
    running = True
    box_width: int = int(game_screen.block_size/30)

    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    main_w, main_h = bs * 1.5, bs * 0.75
    main_x = cx - main_w / 2

    def menu_button(width, height, x, y, font, text):
        return Button(width, height, x, y, box_width=box_width, font=font, text=text,
                      fill_color=style.CONTROL_FILL, radius=style.corner_radius(game_screen))

    big = game_screen.big_big_text_font
    play_button = menu_button(main_w, main_h, main_x, cy - bs * 1.7, big, "play")
    campaign_button = menu_button(main_w, main_h, main_x, cy - bs * 0.8, big, "campaign")
    tower_button = menu_button(main_w, main_h, main_x, cy + bs * 0.1, big, "tower")
    donate_button = menu_button(main_w, main_h, main_x, cy + bs * 1.0, big, "donate")
    playback_button = menu_button(main_w, bs * 0.45, main_x, cy + bs * 1.9, big, "playback")
    settings_button = menu_button(bs * 1.25, bs * 0.55, bs,
                                  game_screen.display_height - bs * 1,
                                  game_screen.mid_text_font, "settings")

    state = "quit"

    clock = pygame.time.Clock()

    while running:
        game_screen.render()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "play"
                if campaign_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "campaign"
                if tower_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "tower"
                if donate_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "donate"
                if playback_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "playback"
                if settings_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "settings"

            if event.type == pygame.QUIT:
                raise QuitGame
        draw_text("Afternoon Brainstorming", game_screen.title_text_font, style.INK,
                cx - bs * 2.3, cy - bs * 2.4, game_screen.surface)
        style.muted_text(game_screen, "by Five O'clock Shadow Studio",
                cx + bs * 1.2, cy - bs * 1.9)

        play_button.update(game_screen)
        campaign_button.update(game_screen)
        tower_button.update(game_screen)
        donate_button.update(game_screen)
        playback_button.update(game_screen)
        settings_button.update(game_screen)

        style.muted_text(game_screen, f"version: {VERSION}",
                game_screen.display_width - bs * 2, cy + bs * 2.5)


        pygame.display.update()
        clock.tick(60)
    return state