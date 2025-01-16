import pygame

from game_screen import GameScreen, draw_text, WHITE
from UI import Button
from controls import key_pressed
    


def main(game_screen: GameScreen) -> str:
    running = True
    box_width: int = int(game_screen.block_size/30)
    start_button = Button(game_screen.block_size*1.5, game_screen.block_size*0.75, game_screen.display_width/2-game_screen.block_size*0.75, game_screen.display_height/2+game_screen.block_size*0.1, game_screen.block_size*0.4, game_screen.block_size*0.2, box_width=box_width, font=game_screen.big_big_text_font, text="start")
    playback_button = Button(game_screen.block_size*1.5, game_screen.block_size*0.75, game_screen.display_width/2-game_screen.block_size*0.75, game_screen.display_height/2+game_screen.block_size*1.3, game_screen.block_size*0.2, game_screen.block_size*0.2, box_width=box_width, font=game_screen.big_big_text_font, text="playback")
    state = "quit"
    while running:
        game_screen.update()
        
        
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "start"
                if playback_button.touch(mouse_x, mouse_y):
                    running = False
                    state = "playback"

            if event.type == pygame.QUIT:
                running = False
        


        draw_text("Afternoon Brainstorming", game_screen.title_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*2.3, game_screen.display_height/2-game_screen.block_size*1.2, game_screen.surface)
        draw_text("by FOC stuido", game_screen.mid_text_font, WHITE, game_screen.display_width/2+game_screen.block_size*1.2, game_screen.display_height/2-game_screen.block_size*0.7, game_screen.surface)
        start_button.update(game_screen)
        playback_button.update(game_screen)
        draw_text("(Experimental Content)", game_screen.mid_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*0.9, game_screen.display_height/2+game_screen.block_size*1.1, game_screen.surface)
        
        
        pygame.display.update()
        game_screen.clock.tick(60)
    return state
