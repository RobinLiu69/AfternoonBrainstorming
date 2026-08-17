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

"""The merchant: eight goods, one reroll price, one relic buy-back per visit."""

from __future__ import annotations

import random

import pygame

from shared import card_code
from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from core.card_hint import HintBox
from core.setting_config import load_setting
from utils.controls import key_pressed

from tower import card_picker, card_pool, choice_screen, grants, run_state, shop, ui_common


def _item_label(item: dict) -> tuple[str, str, tuple[int, int, int]]:
    if item["kind"] == "orb":
        return "Forgetting Orb", "burn a card from your deck", ui_common.ORB
    if item["kind"] == "relic":
        return (ui_common.relic_label(item["relic"]),
                ui_common.relic_text(item["relic"]),
                ui_common.relic_color(item["relic"]))
    return card_pool.display_name(item["card"]), "", ui_common.GOLD


def _buy(game_screen: GameScreen, run: dict, item: dict, price: int,
         rng: random.Random) -> bool:
    if not run_state.affordable(run, price):
        return False

    if item["kind"] == "orb":
        run_state.spend_gold(run, price)
        run["orbs"] += 1
        return True

    if item["kind"] == "relic":
        if not run_state.can_take_relic(run, item["relic"]):
            return False
        run_state.spend_gold(run, price)
        grants.grant_relic(game_screen, run, item["relic"], rng)
        return True

    if run_state.next_slot(run) == "full":
        return False
    if not grants.grant_card(game_screen, run, item["card"]):
        return False
    run_state.spend_gold(run, price)
    return True


def _scrap_curse(game_screen: GameScreen, run: dict, stock: dict) -> bool:
    """Relics are never bought back - a curse can only be paid to remove."""
    cursed = shop.curses_held(run)
    if not cursed:
        return False

    options = [{
        "label": ui_common.relic_label(relic_id),
        "lines": [ui_common.relic_text(relic_id),
                  f"costs {shop.CURSE_REMOVAL_PRICE} to be rid of it"],
        "color": ui_common.relic_color(relic_id),
    } for relic_id in cursed]

    choice = choice_screen.main(game_screen, "Scrap a curse", options,
                                run=run, cancel_label="cancel")
    if choice is None or choice == choice_screen.SKIP:
        return False
    if not run_state.spend_gold(run, shop.CURSE_REMOVAL_PRICE):
        return False

    run["relics"].remove(cursed[choice])
    stock["curse_scrapped"] = True
    return True


def _burn_card(game_screen: GameScreen, run: dict) -> bool:
    if run.get("orbs", 0) <= 0:
        return False
    picked = card_picker.main(game_screen, run, "Burn which card?",
                              subtitle="costs 1 Forgetting Orb")
    if picked is None:
        return False
    return run_state.spend_orb_to_remove(run, picked[0], picked[1])


def main(game_screen: GameScreen, run: dict, stock: dict, rng: random.Random) -> None:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width = ui_common.box_width(game_screen)

    hint_box = HintBox(width=int(bs * 3), height=int(bs))
    hint_on = load_setting("hint_on")

    def build_items() -> list[tuple[Button, dict]]:
        out: list[tuple[Button, dict]] = []
        discount = run_state.shop_discount(run)
        btn_w, btn_h = bs * 3.6, bs * 0.5
        for i, item in enumerate(stock["items"]):
            col, row = i // 4, i % 4
            x = cx - bs * 3.8 + col * (btn_w + bs * 0.3)
            y = cy - bs * 1.7 + row * (btn_h + bs * 0.12)
            label, _text, color = _item_label(item)
            if item["sold"]:
                label, color = "sold", ui_common.DIM
                text = f"{label}"
            else:
                text = f"{label}   [{shop.price_of(item, discount)}]"
            out.append((Button(btn_w, btn_h, x, y, position="Left", padding=bs * 0.12,
                               box_width=box_width,
                               font=ui_common.auto_font(game_screen, text, "mid_text_font"),
                               text=text, text_color=color, box_color=color), item))
        return out

    def build_actions() -> dict[str, Button]:
        y = cy + bs * 1.4
        return {
            "burn": Button(bs * 2.2, bs * 0.55, cx - bs * 3.8, y, box_width=box_width,
                           font=game_screen.mid_text_font,
                           text=f"burn a card  (orbs: {run.get('orbs', 0)})"),
            "scrap": Button(bs * 2.2, bs * 0.55, cx - bs * 1.4, y, box_width=box_width,
                            font=game_screen.text_font,
                            text=f"scrap a curse  [{shop.CURSE_REMOVAL_PRICE}]"),
            "reroll": Button(bs * 2.2, bs * 0.55, cx + bs * 1.0, y, box_width=box_width,
                             font=game_screen.text_font,
                             text=f"reroll  [{shop.reroll_price(run, stock)}]"),
            "leave": Button(bs * 1.8, bs * 0.6, cx - bs * 0.9, cy + bs * 2.1,
                            box_width=box_width, font=game_screen.big_text_font,
                            text="leave"),
        }

    buttons = build_items()
    actions = build_actions()
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        discount = run_state.shop_discount(run)

        hovered = None
        for btn, item in buttons:
            if btn.touch(mouse_x, mouse_y) and not item["sold"]:
                hovered = item

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key == pygame.K_ESCAPE:
                    running = False
                if key == pygame.K_f:
                    hint_on = not hint_on
            if event.type == pygame.MOUSEBUTTONDOWN:
                if actions["leave"].touch(mouse_x, mouse_y):
                    running = False
                elif actions["burn"].touch(mouse_x, mouse_y):
                    _burn_card(game_screen, run)
                    buttons, actions = build_items(), build_actions()
                elif actions["scrap"].touch(mouse_x, mouse_y) and not stock["curse_scrapped"]:
                    _scrap_curse(game_screen, run, stock)
                    buttons, actions = build_items(), build_actions()
                elif actions["reroll"].touch(mouse_x, mouse_y) and shop.can_reroll(run, stock):
                    price = shop.reroll_price(run, stock)
                    if price == 0:
                        stock["free_rerolls_used"] += 1
                    else:
                        run_state.spend_gold(run, price)
                    stock["rerolls"] += 1
                    fresh = shop.generate_stock(run, rng)
                    stock["items"] = fresh["items"]
                    buttons, actions = build_items(), build_actions()
                else:
                    for btn, item in buttons:
                        if btn.touch(mouse_x, mouse_y) and not item["sold"]:
                            if _buy(game_screen, run, item, shop.price_of(item, discount), rng):
                                item["sold"] = True
                            buttons, actions = build_items(), build_actions()
                            break
            if event.type == pygame.QUIT:
                raise QuitGame

        ui_common.draw_run_bar(game_screen, run)
        ui_common.draw_relic_strip(game_screen, run, detailed=hint_on)

        draw_text("Merchant", game_screen.title_text_font, ui_common.GOLD,
                  cx - bs * 3.8, cy - bs * 2.5, game_screen.surface)
        draw_text(grants.slot_hint(run), game_screen.mid_text_font, WHITE,
                  cx - bs * 3.8, cy - bs * 2.0, game_screen.surface)

        for btn, _item in buttons:
            btn.update(game_screen)

        for name, btn in actions.items():
            if name == "scrap" and (stock["curse_scrapped"] or not shop.curses_held(run)):
                btn.text_color = btn.box_color = ui_common.DIM
            if name == "reroll" and not shop.can_reroll(run, stock):
                btn.text_color = btn.box_color = ui_common.DIM
            if name == "burn" and run.get("orbs", 0) <= 0:
                btn.text_color = btn.box_color = ui_common.DIM
            btn.update(game_screen)

        if hovered is not None:
            _label, text, color = _item_label(hovered)
            y = cy + bs * 1.0
            for line in ui_common.wrap(text, ui_common.PANEL_WRAP):
                ui_common.draw_auto(game_screen, line, "mid_text_font", color,
                                    cx - bs * 3.8, y)
                y += bs * 0.3
            if hovered["kind"] == "card":
                for line in ui_common.wrap_all(card_pool.enchant_lines(hovered["card"]),
                                               ui_common.PANEL_WRAP):
                    ui_common.draw_auto(game_screen, line, "text_font",
                                        card_picker.ENCHANT_COLOR, cx - bs * 3.8, y)
                    y += bs * 0.26

        hint_box.turn_on = hint_on
        if hint_on and hovered is not None and hovered["kind"] == "card":
            hint_box.update(mouse_x, mouse_y, hovered["card"], game_screen)

        pygame.display.update()
        clock.tick(60)
