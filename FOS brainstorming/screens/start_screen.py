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

from core.setting import WHITE, VERSION
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from utils.controls import key_pressed    


def main(game_screen: GameScreen) -> str:
    running = True
    box_width: int = int(game_screen.block_size/30)

    local_button = Button(game_screen.block_size*1.5, game_screen.block_size*0.75,
                        game_screen.display_width/2 - game_screen.block_size*0.75,
                        game_screen.display_height/2 - game_screen.block_size*0.8,
                        game_screen.block_size*0.4, game_screen.block_size*0.2,
                        box_width=box_width, font=game_screen.big_big_text_font, text="local")
    host_button = Button(game_screen.block_size*1.5, game_screen.block_size*0.75,
                        game_screen.display_width/2 - game_screen.block_size*0.75,
                        game_screen.display_height/2 + game_screen.block_size*0.1,
                        game_screen.block_size*0.4, game_screen.block_size*0.2,
                        box_width=box_width, font=game_screen.big_big_text_font, text="host")
    join_button = Button(game_screen.block_size*1.5, game_screen.block_size*0.75,
                        game_screen.display_width/2 - game_screen.block_size*0.75,
                        game_screen.display_height/2 + game_screen.block_size*1.0,
                        game_screen.block_size*0.45, game_screen.block_size*0.2,
                        box_width=box_width, font=game_screen.big_big_text_font, text="join")

    playback_button = Button(game_screen.block_size*1.5, game_screen.block_size*0.5,
                        game_screen.display_width/2 - game_screen.block_size*0.75,
                        game_screen.display_height/2 + game_screen.block_size*1.9,
                        game_screen.block_size*0.175, game_screen.block_size*0.1,
                        box_width=box_width, font=game_screen.big_big_text_font, text="playback")
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
                if host_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "host"
                if join_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "join"
                if playback_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "playback"
            
            if event.type == pygame.QUIT:
                running = False

        draw_text("Afternoon Brainstorming", game_screen.title_text_font, WHITE,
                game_screen.display_width/2 - game_screen.block_size*2.3,
                game_screen.display_height/2 - game_screen.block_size*2.1, game_screen.surface)
        draw_text("by Five O'clock Shadow Studio", game_screen.mid_text_font, WHITE,
                game_screen.display_width/2 + game_screen.block_size*1.2,
                game_screen.display_height/2 - game_screen.block_size*1.6, game_screen.surface)

        local_button.update(game_screen)
        host_button.update(game_screen)
        join_button.update(game_screen)
        playback_button.update(game_screen)
        
        # draw_text("(Experimental Content)", game_screen.mid_text_font, WHITE,
        #         game_screen.display_width/2 - game_screen.block_size*0.9,
        #         game_screen.display_height/2 + game_screen.block_size*2.8, game_screen.surface)

        draw_text(f"version: {VERSION}", game_screen.mid_text_font, WHITE,
                game_screen.display_width - game_screen.block_size*2,
                game_screen.display_height/2 + game_screen.block_size*2.6, game_screen.surface)


        pygame.display.update()
        clock.tick(60)
    return state