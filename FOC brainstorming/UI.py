from dataclasses import dataclass, field
import random, pygame
from typing import cast

from game_screen import GameScreen, draw_text, BLACK, WHITE, RED, BLUE, GREEN, Sequence, CARDS_HINTS_DICTIONARY, JOB_DICTIONARY
from card import Card, COLOR_TAG_LIST


@dataclass(kw_only=True)
class BasicUI:
    x: int = 0
    y: int = 0
    height: int = 0
    width: int = 0
    surface : pygame.Surface | None = field(init=False, default=None)

    def update(self, game_screen: GameScreen) -> None:
        self.display(game_screen)
    
    def display(self, game_screen: GameScreen) -> None:
        return


@dataclass
class HighLightBox(BasicUI):
    box_color: tuple[int, int, int] | None = None
    box_height: int = 0
    box_width: int = 0
    line_width: int = 0
    border_radius: int = 0
    visable: bool = False

    def update(self, index: int, length: int, game_screen: GameScreen) -> None:
        self.display(index, length, game_screen)

    def display(self, index: int, length: int, game_screen: GameScreen) -> None:
        if self.visable:
            prefix = 7 if index < 9 else 7.5
            self.box_width = game_screen.block_size/10*(length*0.8+prefix)
            self.y = game_screen.display_height/14*(index+0.8)
            pygame.draw.rect(game_screen.surface, self.box_color, (self.x, self.y, self.box_width, self.box_height), width=self.line_width)
            
@dataclass(kw_only=True)
class HandDisplay(BasicUI):
    def display(self, game_screen: GameScreen) -> None:
        ### 之後會需要更新這部份的東西
        return

class Button:
    def __init__(self, width: float, height: float, x: float, y: float, text_x: float, text_y: float, has_box: bool=True, box_color: Sequence[int]=WHITE, box_width: int=0, text_color: Sequence[int]=WHITE, text: str="", font: pygame.font.Font|None=None):
        self.height = height
        self.width = width
        self.has_box = has_box
        self.box_color = box_color
        self.box_width = box_width
        self.text_color = text_color
        self.x = x
        self.y = y
        self.text_x = text_x
        self.text_y = text_y
        self.text = text
        self.font = font
        self.surface = pygame.Surface((width, height))
        self.been_pressed: bool = False
    
    def update(self, game_screen: GameScreen):
        self.display(game_screen)

    def touch(self, mouse_x: float, mouse_y: float) -> bool:
        return self.x<mouse_x<self.x+self.width and self.y<mouse_y<self.y+self.height
    
    def display(self, game_screen: GameScreen):
        self.surface.fill((0, 0, 0, 0))
        if self.has_box:
            pygame.draw.rect(self.surface, self.box_color, (0, 0, self.width, self.height), self.box_width, border_radius=self.box_width*4)

        if self.font is not None:
            draw_text(self.text, self.font, self.text_color, self.text_x, self.text_y, self.surface)
        
        game_screen.surface.blit(self.surface, (self.x, self.y))


@dataclass(kw_only=True)
class AttackCountDisplay:
    player_name: str
    width: int
    height: int
    
    def display(self, attack_cout: int, game_screen: GameScreen) -> None:
        match self.player_name:
            case "player1":
                self.x, self.y = game_screen.display_width/2-game_screen.block_size*3.75, game_screen.display_height/2+game_screen.block_size*2.5
            case "player2":
                self.x, self.y = game_screen.display_width/2+game_screen.block_size*3.5, game_screen.display_height/2+game_screen.block_size*2.5    
        for i in range(1, 11):
            color = WHITE
            if attack_cout > 10:
                if attack_cout < 20:
                    if attack_cout%10 >= i:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                    else:
                        color = WHITE
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                elif attack_cout < 30:
                    if attack_cout%10 >= i:
                        color = (255, 100, 100)
                        pygame.draw.rect(game_screen.surface, color, (self.x+random.randint(0, round(self.width*0.1*(attack_cout*0.05)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(attack_cout*0.05)))*random.random(), self.width, self.height), round(self.width))
                    else:
                        color = (100, 255, 255)
                        pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
                else:
                    color = (255, 100, 100)
                    pygame.draw.rect(game_screen.surface, color, (self.x+random.randint(0, round(self.width*0.1*(attack_cout*0.1)))*random.random(), self.y-self.height*i*1.25+random.randint(0, round(self.height*0.1*(attack_cout*0.1)))*random.random(), self.width, self.height), round(self.width))
            elif i <= attack_cout:
                pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width))
            else:
                pygame.draw.rect(game_screen.surface, color, (self.x, self.y-self.height*i*1.25, self.width, self.height), round(self.width/10))
                
                
@dataclass(kw_only=True)
class ScoreDisplay:
    width: int
    height: int
       
    def display(self, controller: str, score: int, on_board_cards: list[Card],  game_screen: GameScreen) -> None:
        score_list: list[int] = [score]
        self.x, self.y = game_screen.display_width/2-self.width/2, game_screen.display_height/10
        match controller:
            case "player1":
                score = 0
                for card in filter(lambda card: card.owner == "player1", on_board_cards):
                    score -= card.end_turn(False)
                score_list.append(score_list[-1]+score)
                score = 0
                for card in filter(lambda card: card.owner == "player2", on_board_cards):
                    score += card.end_turn(False)
                score_list.append(score_list[-1]+score)
            case "player2":
                score = 0
                for card in filter(lambda card: card.owner == "player2", on_board_cards):
                    score += card.end_turn(False)
                score_list.append(score_list[-1]+score)
                score = 0
                for card in filter(lambda card: card.owner == "player1", on_board_cards):
                    score -= card.end_turn(False)
                score_list.append(score_list[-1]+score)
        
        for i in range(-10, 11):
            if i == score_list[0]:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            else:
                pygame.draw.rect(game_screen.surface, WHITE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))
            if i == score_list[1]:
                pygame.draw.rect(game_screen.surface, BLUE, (self.x+(self.width*i*1.25), self.y, self.width, self.height), self.width)
            if i == score_list[2]:
                pygame.draw.rect(game_screen.surface, RED, (self.x+(self.width*i*1.25), self.y, self.width, self.height), int(game_screen.thickness/1.5))


@dataclass(kw_only=True)
class TokenDisplay:
    player_name: str
    radius: int
    time: int = field(init=False, default=0)
    is_glowing: bool = field(init=False, default=True)
    
    def display(self, token_count: int, game_screen: GameScreen) -> None:
        if token_count > 0:
            if  self.is_glowing:
                self.time += 1
                if self.time == 60:
                    self.is_glowing = not self.is_glowing
            else:
                self.time -= 1
                if self.time == 1:
                    self.is_glowing = not self.is_glowing
            offset_y = 0
            match self.player_name:
                case "player1":
                    offset_y = -1
                case "player2":
                    offset_y = 1
            for i in range(0, token_count):
                pygame.draw.circle(game_screen.surface, (int(60*min(1, self.time/30)), int(100*min(1, self.time/30)), int(225*min(1, self.time/30))), (game_screen.display_width/2+(game_screen.block_size*2.5*offset_y), game_screen.display_height-(game_screen.block_size*0.5)-(self.radius*i*2.2)), self.radius)


@dataclass(kw_only=True)
class HintBox:
    width: int
    height: int
    surface: pygame.Surface | None = field(init=False, default=None)
    
    def __post_init__(self) -> None:
        self.x = 0
        self.y = 0
        self.turn_on = False
    
    def update(self, mouse_x: int, mouse_y: int, card, game_screen: GameScreen) -> None:
        self.x = mouse_x
        self.y = mouse_y
        if card != "None":
            self.display(card, game_screen)
    def get_job_and_color(self, card_type) -> str:
        for tag in COLOR_TAG_LIST:
            if card_type.endswith(tag):
                color_name = JOB_DICTIONARY["colors_dict"][tag]
                color = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"][color_name].split(", "))))
                if card_type.count(tag) > 1:
                    return card_type[::-1].replace(tag, "", 1)[::-1], color
                else:
                    return card_type.replace(tag, "", 1), color
        return "None"
    def shaped(self, job, block_size: float) -> tuple:
        match job:
            case "ADC":
                return (((block_size*0.42), (block_size*0.22)),
                        ((block_size*0.17), (block_size*0.62)),
                        ((block_size*0.67), (block_size*0.62)))
            case "AP":
                return ((block_size*0.42), (block_size*0.42))
            case "HF":
                return (((block_size*0.32), (block_size*0.32)),
                        ((block_size*0.52), (block_size*0.32)),
                        ((block_size*0.67), (block_size*0.57)),
                        ((block_size*0.17), (block_size*0.57)))
            case "LF":
                return (((block_size*0.42), (block_size*0.22)),
                        ((block_size*0.28), (block_size*0.34)),
                        ((block_size*0.3975), (block_size*0.47)),
                        ((block_size*0.28), (block_size*0.60)),
                        ((block_size*0.42), (block_size*0.72)),
                        ((block_size*0.56), (block_size*0.60)),
                        ((block_size*0.4425), (block_size*0.47)),
                        ((block_size*0.56), (block_size*0.34)))
            case "ASS":
                return (((block_size*0.42), (block_size*0.32)),
                        ((block_size*0.12), (block_size*0.57)),
                        ((block_size*0.42), (block_size*0.42)),
                        ((block_size*0.72), (block_size*0.57)))
            case "APT":
                return (((block_size*0.32), (block_size*0.22)),
                        ((block_size*0.17), (block_size*0.42)),
                        ((block_size*0.32), (block_size*0.62)), 
                        ((block_size*0.52), (block_size*0.62)),
                        ((block_size*0.67), (block_size*0.42)),
                        ((block_size*0.52), (block_size*0.22)))
            case "SP":
                return (((block_size*0.295), (block_size*0.22)),
                        ((block_size*0.17), (block_size*0.37)),
                        ((block_size*0.42), (block_size*0.67)),
                        ((block_size*0.67), (block_size*0.37)),
                        ((block_size*0.545), (block_size*0.22)))
            case "TANK":
                return (((block_size*0.17), (block_size*0.17)),
                        ((block_size*0.17), (block_size*0.67)),
                        ((block_size*0.67), (block_size*0.67)),
                        ((block_size*0.67), (block_size*0.17)))
            case "CUBE":
                return (((block_size*0.45), (block_size*0.45)),
                        ((block_size*0.45), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.45)))
            case "CUBES":
                return (((block_size*0.45), (block_size*0.45)),
                        ((block_size*0.45), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.55)),
                        ((block_size*0.55), (block_size*0.45))) 
            case "LUCKYBLOCK":
                return (((block_size*0.4), (block_size*0.4)),
                        ((block_size*0.4), (block_size*0.6)),
                        ((block_size*0.6), (block_size*0.6)),
                        ((block_size*0.6), (block_size*0.4)))
            
    def display(self, card, game_screen: GameScreen) -> None:
        if self.surface is None:
            self.surface = pygame.Surface((self.width, game_screen.block_size*1.5), pygame.SRCALPHA)
        if self.turn_on:
            if type(card) == str: #判斷卡牌是否在場上
                card_type = card
            else:
                card_type = card.job_and_color
            if card_type not in CARDS_HINTS_DICTIONARY: return
            box_height = len(CARDS_HINTS_DICTIONARY[card_type].split("\n")) if len(CARDS_HINTS_DICTIONARY[card_type].split("\n")) > 4 else 4
            pygame.draw.rect(self.surface, WHITE, (0, 0, self.width, (game_screen.block_size*0.05)+game_screen.block_size*(0.15*box_height)), 2)
            pygame.draw.rect(self.surface, BLACK, (0+(game_screen.thickness//2), 0+(game_screen.thickness//2), self.width-game_screen.thickness, (game_screen.block_size*0.05)+game_screen.block_size*(0.15*box_height)-game_screen.thickness), 1000)
            if card_type not in ["CUBE", "CUBES", "LUCKYBLOCK", "MOVE", "MOVEO", "HEAL"]: #排除魔法牌等
                pygame.draw.rect(self.surface, WHITE, (0+game_screen.block_size*0.05, 0+game_screen.block_size*0.05, game_screen.block_size*0.5, game_screen.block_size*0.5), 2)
                job, color = self.get_job_and_color(card_type.split()[0])
                if color == (0, 238, 238) and type(card) != str: #海盜特例排除
                    if card.upgrade:
                        card_type += " (+)"
                        draw_text("(+)", game_screen.text_font, color, (game_screen.block_size*0.213), (game_screen.block_size*0.235), self.surface)
                shape = self.shaped(job, game_screen.block_size*0.7)
                match job: #繪製
                    case "AP":
                        pygame.draw.circle(self.surface, color, shape, game_screen.block_size*0.15, int(game_screen.thickness/1.1))
                    case _:
                        pygame.draw.lines(self.surface, color, True, shape, int(game_screen.thickness*1.1))
                for i, line in enumerate(CARDS_HINTS_DICTIONARY[card_type].split("\n")):
                    if i == 0:
                        if type(card) == str:
                            draw_text(f"{card_type} {line}", game_screen.text_fontCHI, WHITE, 0+(game_screen.block_size*0.6), 0+(game_screen.block_size*0.05), self.surface)
                        else:
                            draw_text(f"{card_type}", game_screen.text_fontCHI, WHITE, 0+game_screen.block_size*0.6, 0+(game_screen.block_size*0.05), self.surface)
                            draw_text(f"{card.health}", game_screen.text_fontCHI, RED if card.health < card.max_health else WHITE, 0+game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)), 0+(game_screen.block_size*0.05), self.surface)
                            draw_text(f"/", game_screen.text_fontCHI, WHITE, 0+game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health))), 0+(game_screen.block_size*0.05), self.surface)
                            draw_text(f"{card.damage}", game_screen.text_fontCHI, RED if card.damage < card.original_damage else GREEN if card.damage > card.original_damage else WHITE, 0+game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health))+1), 0+(game_screen.block_size*0.05), self.surface)
                            atk_type = line.split("-")
                            draw_text(f"-{atk_type[1]}", game_screen.text_fontCHI, WHITE, 0+game_screen.block_size*0.6+game_screen.block_size*0.07*(len(card_type)+len(str(card.health))+len(str(card.damage))+1), 0+(game_screen.block_size*0.05), self.surface)         
                    elif i < 4:
                        draw_text(f"{line}", game_screen.text_fontCHI, WHITE, 0+(game_screen.block_size*0.6), (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
                    else:
                        draw_text(f"{line}", game_screen.text_fontCHI, WHITE, 0+(game_screen.block_size*0.05), (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
            else:
                for i, line in enumerate(CARDS_HINTS_DICTIONARY[card_type].split("\n")):
                    draw_text(f"{line}", game_screen.text_fontCHI, WHITE, 0+(game_screen.block_size*0.05), (game_screen.block_size*0.05)+(game_screen.block_size*0.15*i), self.surface)
            game_screen.surface.blit(self.surface, (self.x, self.y))
        self.surface.fill((0, 0, 0, 0))