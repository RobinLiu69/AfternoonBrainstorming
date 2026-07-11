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

import random

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from utils.controls import key_pressed

from endless.content import EVENTS, CONSUMABLES
from endless import deck_picker


GOLD: tuple[int, int, int] = (255, 215, 0)


def _choices_for(event_name: str, run: dict) -> list[tuple[str, str]]:
    if event_name == "fountain":
        return [("supplies", "drink deep  (gain a random supply for next battle)"),
                ("coins", "toss it for luck  (+15 coins)")]
    if event_name == "gambler":
        choices = []
        if run["coins"] >= 20:
            choices.append(("bet", "bet 20 coins  (50/50 double or nothing)"))
        choices.append(("walk", "walk away"))
        return choices
    if event_name == "altar":
        choices = []
        if run["deck"] or run["temp_deck"]:
            choices.append(("sacrifice", "sacrifice a card  (+10 coins)"))
        choices.append(("leave", "leave the altar"))
        return choices
    return [("leave", "move on")]


def main(game_screen: GameScreen, run: dict, spec: dict) -> None:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    event_name = spec.get("event", "fountain")
    info = EVENTS.get(event_name, {"label": event_name, "text": ""})
    rng = random.Random(run["seed"] * 1000003 + run["floor"] * 97 + 5)

    result_text = ""
    done = False

    def build_buttons() -> list[tuple[str, Button]]:
        btn_w, btn_h = bs * 4.2, bs * 0.6
        btn_x = cx - btn_w / 2
        built: list[tuple[str, Button]] = []
        if done:
            built.append(("continue", Button(btn_w, btn_h, btn_x, cy + bs * 0.6,
                                             box_width=box_width, font=game_screen.big_text_font,
                                             text="continue")))
            return built
        for i, (choice_id, label) in enumerate(_choices_for(event_name, run)):
            built.append((choice_id, Button(btn_w, btn_h, btn_x, cy - bs * 0.4 + i * (btn_h + bs * 0.2),
                                            box_width=box_width, font=game_screen.big_text_font,
                                            text=label)))
        return built

    buttons = build_buttons()
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE and done:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for choice_id, btn in buttons:
                    if not btn.touch(mouse_x, mouse_y):
                        continue
                    if choice_id == "continue":
                        running = False
                    elif choice_id == "supplies":
                        item = rng.choice(sorted(CONSUMABLES))
                        run["armed_consumables"].append(item)
                        result_text = f"gained: {CONSUMABLES[item]['label']}"
                        done = True
                    elif choice_id == "coins":
                        run["coins"] += 15
                        result_text = "+15 coins"
                        done = True
                    elif choice_id == "bet":
                        if rng.random() < 0.5:
                            run["coins"] += 20
                            result_text = "you won!  +20 coins"
                        else:
                            run["coins"] -= 20
                            result_text = "you lost 20 coins..."
                        done = True
                    elif choice_id == "sacrifice":
                        picked = deck_picker.main(game_screen, run, "sacrifice which card?")
                        if picked is not None:
                            source, idx = picked
                            target = run["deck"] if source == "deck" else run["temp_deck"]
                            if 0 <= idx < len(target):
                                lost = target.pop(idx)
                                run["coins"] += 10
                                result_text = f"sacrificed {lost}  (+10 coins)"
                                done = True
                    elif choice_id in ("walk", "leave"):
                        result_text = "you move on."
                        done = True
                    buttons = build_buttons()
                    break
            if event.type == pygame.QUIT:
                running = False

        draw_text(f"Floor {run['floor']}  -  {info['label']}", game_screen.title_text_font, WHITE,
                  cx - bs * 2.6, cy - bs * 2.8, game_screen.surface)
        draw_text(info["text"], game_screen.big_text_font, WHITE,
                  cx - bs * 2.6, cy - bs * 1.9, game_screen.surface)
        draw_text(f"coins: {run['coins']}", game_screen.big_text_font, GOLD,
                  cx - bs * 2.6, cy - bs * 1.4, game_screen.surface)
        if result_text:
            draw_text(result_text, game_screen.big_big_text_font, GOLD,
                      cx - bs * 2.6, cy - bs * 0.5, game_screen.surface)

        for _choice_id, btn in buttons:
            btn.update(game_screen)

        pygame.display.update()
        clock.tick(60)
