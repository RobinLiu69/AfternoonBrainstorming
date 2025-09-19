from dataclasses import dataclass, field
import os, json, pygame
from typing import cast

#December 22nd, 2024 7:30 PM
#Vic Yeh 到此一遊
#學測倒數29天


from card import Card, COLOR_TAG_LIST
import card_white as white
import card_red as red
import card_green as green
import card_blue as blue
import card_orange as orange
import card_purple as purple
import card_dark_green as darkgreen
import card_cyan as cyan
import card_fuchsia as fuchsia
from game_screen import GameScreen, draw_text, WHITE, RED, GREEN, BLACK, CARDS_HINTS_DICTIONARY, JOB_DICTIONARY




all_exhibit_cards: list[list[Card]] = [[white.Adc("display", 0, 0), white.Ap("display", 1, 0), white.Tank("display", 2, 0), white.Hf("display", 3, 0), white.Lf("display", 0, 1), white.Ass("display", 1, 1), white.Apt("display", 2, 1), white.Sp("display", 3, 1)],
                                       [red.Adc("display", 0, 0), red.Ap("display", 1, 0), red.Tank("display", 2, 0), red.Hf("display", 3, 0), red.Lf("display", 0, 1), red.Ass("display", 1, 1), red.Apt("display", 2, 1), red.Sp("display", 3, 1)],
                                       [green.Adc("display", 0, 0), green.Ap("display", 1, 0), green.Tank("display", 2, 0), green.Hf("display", 3, 0), green.Lf("display", 0, 1), green.Ass("display", 1, 1), green.Apt("display", 2, 1), green.Sp("display", 3, 1)],
                                       [blue.Adc("display", 0, 0), blue.Ap("display", 1, 0), blue.Tank("display", 2, 0), blue.Hf("display", 3, 0), blue.Lf("display", 0, 1), blue.Ass("display", 1, 1), blue.Apt("display", 2, 1), blue.Sp("display", 3, 1)],
                                       [orange.Adc("display", 0, 0), orange.Ap("display", 1, 0), orange.Tank("display", 2, 0), orange.Hf("display", 3, 0), orange.Lf("display", 0, 1), orange.Ass("display", 1, 1), orange.Apt("display", 2, 1), orange.Sp("display", 3, 1)],
                                       [darkgreen.Adc("display", 0, 0), darkgreen.Ap("display", 1, 0), darkgreen.Tank("display", 2, 0), darkgreen.Hf("display", 3, 0), darkgreen.Lf("display", 0, 1), darkgreen.Ass("display", 1, 1), darkgreen.Apt("display", 2, 1), darkgreen.Sp("display", 3, 1)],
                                       [cyan.Adc("display", 0, 0), cyan.Ap("display", 1, 0), cyan.Tank("display", 2, 0), cyan.Hf("display", 3, 0), cyan.Lf("display", 0, 1), cyan.Ass("display", 1, 1), cyan.Apt("display", 2, 1), cyan.Sp("display", 3, 1)],
                                       [fuchsia.Adc("display", 0, 0), fuchsia.Ap("display", 1, 0), fuchsia.Tank("display", 2, 0), fuchsia.Hf("display", 3, 0), fuchsia.Lf("display", 0, 1), fuchsia.Ass("display", 1, 1), fuchsia.Apt("display", 2, 1), fuchsia.Sp("display", 3, 1)],
                                       
                                       [purple.Ap("display", 1, 0), purple.Tank("display", 2, 0), purple.Hf("display", 3, 0), purple.Ass("display", 1, 1)],
                                       [white.Cube("display", 0, 2), white.Heal("display", 1, 2), white.Move("display", 2, 2)]]


def exhibit(page: int, game_screen: GameScreen):
    for card in all_exhibit_cards[page]:
        card.display_update(game_screen)
    for card in all_exhibit_cards[-1]:
        card.display_update(game_screen)

def get_card_name_in_menu(page: int, board_x: int, board_y: int) -> str:
    for card in all_exhibit_cards[page]:
        if card.board_x == board_x and card.board_y == board_y:
            return card.job_and_color
    
    for card in all_exhibit_cards[-1]:
        if card.board_x == board_x and card.board_y == board_y:
            return card.job_and_color
    
    return "None"

def get_card_name_in_battling(all_on_board_cards: list[Card], board_x: int, board_y: int) -> str:
    for card in all_on_board_cards:
        if card.board_x == board_x and card.board_y == board_y:
            return card.job_and_color
    return "None"

def get_card_in_battling(all_on_board_cards: list[Card], board_x: int, board_y: int) -> str:
    for card in all_on_board_cards:
        if card.board_x == board_x and card.board_y == board_y:
            return card
    return "None"

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