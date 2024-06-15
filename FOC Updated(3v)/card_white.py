from dataclasses import dataclass, field
import os, json, pygame, game_screen
import random
from typing import Sequence, Any, cast

from type_hint import JobDictionary
from game_screen import GameScreen

__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))

with open(f"{__FOLDER_PATH}/job_dictionary.json", "r") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())

WHITE: tuple[int, int, int] = cast(tuple[int, int, int], map(int, JOB_DICTIONARY["RGB_colors"]["White"].split(", ")))

from card import Card


@dataclass(kw_only=True)
class Cube(Card):
    owner: str
    x: int
    y: int
    health: int = 4
    attack: int = 0
    attack_type: str | None = field(init=False, default=None)
    color: tuple[int, int, int] = field(init=False)

    def __post_init__(self):
        super().__init__(self.owner, "cube", self.health, self.attack, self.x, self.y)
        
    def display(self, game_screen: GameScreen):
        self.rect: tuple[float, float, float, float] = ((game_screen.display_width/2-game_screen.block_size*2)+(self.x*game_screen.block_size)+(game_screen.block_size*0.425),
                            (game_screen.display_height/2-game_screen.block_size*1.65)+(self.y*game_screen.block_size)+(game_screen.block_size*0.425),
                            game_screen.block_size*0.15, game_screen.block_size*0.15)
        pygame.draw.rect(game_screen.surface, self.color, self.rect, 4)
        
        self.update(game_screen)
        