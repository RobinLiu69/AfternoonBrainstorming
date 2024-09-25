import   pygame
from game_screen import GameScreen, os, __FOLDER_PATH
from chart_make import make_plot_chart#, make_pie_chart
from dataclasses import dataclass, field

@dataclass(kw_only=True)
class PieChart:
    x: int
    y: int
    width: int
    height: int
    player: str
    part: str
    visible: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        file_path = __FOLDER_PATH+f"/output/P{self.player}-{self.part}piechart.png"
        
        self.image: pygame.surface.Surface | None = None
        if os.path.exists(file_path):
            self.image = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), (self.width, self.height))

    def display(self, game_screen: GameScreen) -> None:
        if self.visible == True and self.image is not None:
            game_screen.surface.blit(self.image, (self.x, self.y))



@dataclass(kw_only=True)
class PlotChart:
    x: int
    y: int
    width: int
    height: int
    visible: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        file_path = __FOLDER_PATH+f"/output/plot_chart.png"
        self.image: pygame.surface.Surface | None = None
        if os.path.exists(file_path):
            self.image = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), (self.width, self.height))


    def display(self, game_screen: GameScreen) -> None:
        if self.visible == True and self.image is not None:
            game_screen.surface.blit(self.image, (self.x, self.y))

def making_image(game_screen: GameScreen) -> bool:
    make_plot_chart(game_screen.data.score_records)
    # player1_datas = {}
    # player2_datas = {}
    # for key, datas in game_screen.data.data_dicts.items():
    #     for data in datas.items():
    #         pass
    #     player1_datas[key] = ((filter(lambda data: data, datas)))
    return True

def main(game_screen: GameScreen) -> None:
    making_image(game_screen)

