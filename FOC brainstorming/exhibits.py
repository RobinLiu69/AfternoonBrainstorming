from dataclasses import dataclass, field
import os, json, pygame
from typing import cast

#December 22nd, 2024 7:30 PM
#Vic Yeh 到此一遊
#學測倒數29天


from card import Card
import card_white as white
import card_red as red
import card_green as green
import card_blue as blue
import card_orange as orange
import card_purple as purple
import card_dark_green as darkgreen
import card_cyan as cyan
import card_fuchsia as fuchsia
from game_screen import GameScreen, draw_text, WHITE, RED, GREEN, BLACK




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
