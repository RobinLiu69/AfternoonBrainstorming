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

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text
from core.UI import Button
from utils.controls import key_pressed

from endless import run_state, endless_save, deck_picker


GOLD: tuple[int, int, int] = (255, 215, 0)
CURSE_COLOR: tuple[int, int, int] = (255, 90, 90)
SOLD_COLOR: tuple[int, int, int] = (110, 110, 110)
TEMP_COLOR: tuple[int, int, int] = (255, 170, 60)


def _price_of(item: dict, discount: float) -> int:
    return max(1, int(item["price"] * discount))


def _remove_price(run: dict) -> int:
    return 30 + 10 * run["shop_counters"]["remove_card"]


def _reroll_price(stock: dict) -> int:
    return 15 * (2 ** stock.get("reroll", 0))


def main(game_screen: GameScreen, state: dict, run: dict, stock: dict) -> str:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width: int = int(bs / 30)

    result = "leave"
    clock = pygame.time.Clock()
    discount = run_state.shop_discount(run)

    def build_buttons() -> list[tuple[Button, dict]]:
        buttons: list[tuple[Button, dict]] = []
        btn_w, btn_h = bs * 3.3, bs * 0.5
        for idx, item in enumerate(stock["items"]):
            col = idx // 5
            row = idx % 5
            x = cx - bs * 3.5 + col * (btn_w + bs * 0.25)
            y = cy - bs * 2.0 + row * (btn_h + bs * 0.1)
            if item["sold"]:
                label = "SOLD"
                color = SOLD_COLOR
            else:
                label = f"{item['label']}  [{_price_of(item, discount)}]"
                color = CURSE_COLOR if item["kind"] == "curse" else WHITE
                if item["kind"] == "card":
                    color = GOLD
            btn = Button(btn_w, btn_h, x, y,
                         position="Left", padding=bs * 0.12,
                         box_width=box_width, font=game_screen.text_font,
                         text=label, text_color=color, box_color=color)
            buttons.append((btn, item))
        return buttons

    def service_buttons() -> tuple[Button, Button, Button]:
        remove_btn = Button(bs * 2.2, bs * 0.55, cx - bs * 3.5, cy + 2.4 * bs,
                            box_width=box_width, font=game_screen.text_font,
                            text=f"remove a card  [{int(_remove_price(run) * discount)}]")
        reroll_btn = Button(bs * 2.0, bs * 0.55, cx - bs * 1.1, cy + 2.4 * bs,
                            box_width=box_width, font=game_screen.text_font,
                            text=f"reroll stock  [{int(_reroll_price(stock) * discount)}]")
        leave_btn = Button(bs * 1.6, bs * 0.55, cx + bs * 1.1, cy + 2.4 * bs,
                           box_width=box_width, font=game_screen.big_text_font, text="leave")
        return remove_btn, reroll_btn, leave_btn

    buttons = build_buttons()
    remove_btn, reroll_btn, leave_btn = service_buttons()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if key_pressed(keys) == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if leave_btn.touch(mouse_x, mouse_y):
                    running = False
                elif remove_btn.touch(mouse_x, mouse_y):
                    price = int(_remove_price(run) * discount)
                    if run["coins"] >= price and (run["deck"] or run["temp_deck"]):
                        picked = deck_picker.main(game_screen, run, "remove which card?")
                        if picked is not None:
                            source, i = picked
                            target = run["deck"] if source == "deck" else run["temp_deck"]
                            if 0 <= i < len(target):
                                target.pop(i)
                                run["coins"] -= price
                                run["shop_counters"]["remove_card"] += 1
                                endless_save.save(state)
                        remove_btn, reroll_btn, leave_btn = service_buttons()
                elif reroll_btn.touch(mouse_x, mouse_y):
                    price = int(_reroll_price(stock) * discount)
                    if run["coins"] >= price:
                        run["coins"] -= price
                        run["shop_counters"]["reroll"] += 1
                        new_stock = run_state.generate_shop_stock(run, stock.get("reroll", 0) + 1)
                        stock.clear()
                        stock.update(new_stock)
                        run["pending"] = {"kind": "shop", "stock": stock}
                        endless_save.save(state)
                        buttons = build_buttons()
                        remove_btn, reroll_btn, leave_btn = service_buttons()
                else:
                    for btn, item in buttons:
                        if btn.touch(mouse_x, mouse_y) and not item["sold"]:
                            price = _price_of(item, discount)
                            if run["coins"] < price:
                                continue
                            if item["kind"] == "card" and not run_state.can_add_card(run, item["card"]):
                                continue
                            run["coins"] -= price
                            item["sold"] = True
                            if item["kind"] == "perm":
                                run_state.apply_perm_buff(run, item["stat"], item.get("job", ""))
                            elif item["kind"] == "consumable":
                                run["armed_consumables"].append(item["item"])
                            elif item["kind"] == "curse":
                                run["curses"].append(item["item"])
                            elif item["kind"] == "card":
                                run["deck"].append(item["card"])
                            discount = run_state.shop_discount(run)
                            endless_save.save(state)
                            buttons = build_buttons()
                            remove_btn, reroll_btn, leave_btn = service_buttons()
                            break
            if event.type == pygame.QUIT:
                result = "menu"
                running = False

        draw_text(f"Shop  -  floor {run['floor']}", game_screen.title_text_font, WHITE,
                  cx - bs * 1.6, cy - bs * 3.1, game_screen.surface)
        draw_text(f"coins: {run['coins']}", game_screen.big_big_text_font, GOLD,
                  cx + bs * 2.2, cy - bs * 3.0, game_screen.surface)
        draw_text("bought cards are permanent - reward cards are temporary",
                  game_screen.text_font, TEMP_COLOR,
                  cx - bs * 3.5, cy - bs * 2.4, game_screen.surface)

        for btn, _item in buttons:
            btn.update(game_screen)

        for idx, (btn, item) in enumerate(buttons):
            if item["kind"] == "curse" and not item["sold"]:
                col = idx // 5
                row = idx % 5
                x = cx - bs * 3.5 + col * (bs * 3.3 + bs * 0.25)
                y = cy - bs * 2.0 + row * (bs * 0.5 + bs * 0.1)
                draw_text(f"curse: {item['curse_text']}", game_screen.small_text_font, CURSE_COLOR,
                          x + bs * 0.12, y + bs * 0.36, game_screen.surface)

        remove_btn.update(game_screen)
        reroll_btn.update(game_screen)
        leave_btn.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return result
