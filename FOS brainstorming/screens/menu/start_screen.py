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
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from utils.controls import key_pressed    


def main(game_screen: GameScreen) -> str:
    running = True
    box_width: int = int(game_screen.block_size/30)

    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    main_w, main_h = bs * 1.5, bs * 0.75
    main_x = cx - main_w / 2
    main_text_x = bs * 0.4
    main_text_y = bs * 0.2

    local_button = Button(main_w, main_h, main_x, cy - bs * 1.7,
                        box_width=box_width, font=game_screen.big_big_text_font, text="local")
    campaign_button = Button(main_w, main_h, main_x, cy - bs * 0.8,
                        box_width=box_width, font=game_screen.big_big_text_font, text="campaign")
    host_button = Button(main_w, main_h, main_x, cy + bs * 0.1,
                        box_width=box_width, font=game_screen.big_big_text_font, text="host")
    join_button = Button(main_w, main_h, main_x, cy + bs * 1.0,
                        box_width=box_width, font=game_screen.big_big_text_font, text="join")

    playback_h = bs * 0.45
    playback_button = Button(main_w, playback_h, main_x, cy + bs * 1.9,
                        box_width=box_width, font=game_screen.big_big_text_font, text="playback")

    settings_button = Button(bs * 1.25, bs * 0.55, bs, game_screen.display_height - bs * 1,
                        box_width=box_width, font=game_screen.mid_text_font, text="settings")

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
                if local_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "local"
                if campaign_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "campaign"
                if host_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "host"
                if join_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "join"
                if playback_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "playback"
                if settings_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "settings"

            if event.type == pygame.QUIT:
                running = False

        draw_text("Afternoon Brainstorming", game_screen.title_text_font, WHITE,
                cx - bs * 2.3, cy - bs * 2.4, game_screen.surface)
        draw_text("by Five O'clock Shadow Studio", game_screen.mid_text_font, WHITE,
                cx + bs * 1.2, cy - bs * 1.9, game_screen.surface)

        local_button.update(game_screen)
        campaign_button.update(game_screen)
        host_button.update(game_screen)
        join_button.update(game_screen)
        playback_button.update(game_screen)
        settings_button.update(game_screen)

        draw_text(f"version: {VERSION}", game_screen.mid_text_font, WHITE,
                game_screen.display_width - bs * 2,
                cy + bs * 2.5, game_screen.surface)


        pygame.display.update()
        clock.tick(60)
    return state