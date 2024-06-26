import pygame, os, json
from dataclasses import dataclass, field
pygame.init()


__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))

with open(f"{__FOLDER_PATH}/setting.json", "r") as file:
    SETTING: dict[str, str] = json.loads(file.read())

def draw_text(text: str, font: pygame.font.Font, textColor: tuple[int, ...], x: float, y: float, surface: pygame.surface.Surface) -> None:
    img = font.render(text, True, textColor)
    surface.blit(img, (x, y))

@dataclass(kw_only=True)
class GameScreen:
    display_width: int = pygame.display.get_desktop_sizes()[0][0]
    display_height: int = pygame.display.get_desktop_sizes()[0][1]
    # surface: pygame.surface.Surface | None = field(init=False, default=None)
    # block_size: float | None = field(init=False, default=None)
    # text_font_size: int | None = field(init=False, default=None)
    # text_font: pygame.font.Font | None = field(init=False, default=None)
    # big_text_font: pygame.font.Font | None = field(init=False, default=None)
    # small_text_font: pygame.font.Font | None = field(init=False, default=None)
    # chinese_text_font: pygame.font.Font | None = field(init=False, default=None)
    
    
    def fitting_screen(self) -> tuple[pygame.surface.Surface, float]:
        if self.display_width/self.display_height == 1.6:
            surface = pygame.display.set_mode(
                (self.display_width, self.display_height), pygame.FULLSCREEN)
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
        self.text_font: pygame.font.Font = pygame.font.Font(SETTING["basic font"], self.text_font_size)
        self.big_text_font: pygame.font.Font = pygame.font.Font(SETTING["basic font"], int(self.display_width/1500*25))
        self.small_text_font: pygame.font.Font = pygame.font.Font(SETTING["basic font"], int(self.text_font_size/15*8.66))
        self.text_fontCHI: pygame.font.Font = pygame.font.Font(SETTING["chinese font"], self.text_font_size)
    

    def __post__init__(self) -> int:
        print(self.display_width, self.display_height)
        self.surface, self.block_size = self.fitting_screen()
        print(self.display_width, self.display_height)
        self.font_init()
        
        return 0