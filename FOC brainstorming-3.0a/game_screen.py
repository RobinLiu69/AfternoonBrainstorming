from dataclasses import dataclass, field
import os, json, pygame
import random
from typing import cast
pygame.init()

from type_hint import JobDictionary

__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))

with open(f"{__FOLDER_PATH}/setting.json", "r") as file:
    SETTING: dict[str, str] = json.loads(file.read())

with open(f"{__FOLDER_PATH}/job_dictionary.json", "r") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())
        
BLACK: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Black"].split(", "))))
WHITE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["White"].split(", "))))
BLUE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Blue"].split(", "))))
RED: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Red"].split(", "))))
GREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Green"].split(", "))))
ORANGE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Orange"].split(", "))))

def draw_text(text: str, font: pygame.font.Font, textColor: tuple[int, ...], x: float, y: float, surface: pygame.surface.Surface) -> None:
    rendered_text = font.render(text, True, textColor)
    surface.blit(rendered_text, (x, y))

@dataclass(kw_only=True)
class GameScreen:
    display_width: int = pygame.display.get_desktop_sizes()[0][0]
    display_height: int = pygame.display.get_desktop_sizes()[0][1]
    
    def __post_init__(self) -> None:
        print(self.display_width, self.display_height)
        self.surface, self.block_size = self.fitting_screen()
        print(self.display_width, self.display_height)
        self.thickness = self.display_width // 400
        self.font_init()
        self.clock = pygame.time.Clock()
        self.timer_mode: str = "timer"
        self.coutdown_time = int(SETTING["countdown_time"])
        self.score: int = 0
        self.players_luck: dict[str, int] = {"player1": 50, "player2": 50, "neutral": 50}
        self.how_many_token_to_draw_a_card: int = int(SETTING["how_many_token_to_draw_a_card"])
        self.players_token: dict[str, int] = {"player1": 0, "player2": 50, "neutral": 0}
        
        self.number_of_attacks: dict[str, int] = {"player1": 0, "player2": 0}
        self.number_of_movings: dict[str, int] = {"player1": 0, "player2": 0}
        self.number_of_cudes: dict[str, int] = {"player1": 0, "player2": 0}
        self.number_of_heals: dict[str, int] = {"player1": 0, "player2": 0}
    
    def fitting_screen(self) -> tuple[pygame.surface.Surface, float]:
        if self.display_width/self.display_height == 1.6:
            surface = pygame.display.set_mode(
                (self.display_width, self.display_height))
            block_size = (self.display_width/8)/1.2
        else:
            maxvalue = [0, 0]
            for H in range(self.display_height, 0, -1):
                for W in range(self.display_width, 0, -1):
                    if W/H == 1.6:
                        maxvalue = [W, H]
                        break
                if maxvalue != [0, 0]:
                    break
            self.display_width = maxvalue[0]
            self.display_height = maxvalue[1]
            surface = pygame.display.set_mode(
                (self.display_width, self.display_height))
            block_size = (self.display_width/8)/1.2
        return surface, block_size

    def font_init(self) -> None:
        self.text_font_size: int = int(self.display_width/1500*16.5)
        self.text_font: pygame.font.Font = pygame.font.Font(SETTING["basic_font"], self.text_font_size)
        self.info_text_font: pygame.font.Font = pygame.font.Font(SETTING["basic_font"], int(self.text_font_size/1.1))
        self.big_text_font: pygame.font.Font = pygame.font.Font(SETTING["basic_font"], int(self.display_width/1500*25))
        self.small_text_font: pygame.font.Font = pygame.font.Font(SETTING["basic_font"], int(self.text_font_size/15*8.66))
        self.text_fontCHI: pygame.font.Font = pygame.font.Font(SETTING["chinese_font"], self.text_font_size)


    def update(self) -> None:
        self.surface.fill(pygame.Color(BLACK))