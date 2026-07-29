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

"""Last stop before a fight: see the enemy, and shuffle the bench if you want."""

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.UI import Button
from utils.controls import key_pressed

from tower import card_picker, card_pool, run_state, ui_common

DECK_ROWS: int = 7


def _effect_lines(effects: dict, subject: str) -> list[str]:
    lines: list[str] = []
    if effects.get("unit_hp_plus"):
        lines.append(f"{subject} units {effects['unit_hp_plus']:+d} HP")
    if effects.get("unit_damage_plus"):
        lines.append(f"{subject} units {effects['unit_damage_plus']:+d} damage")
    for job, amount in sorted(effects.get("job_hp_plus", {}).items()):
        lines.append(f"{subject} {job} {amount:+d} HP")
    for job, amount in sorted(effects.get("job_damage_plus", {}).items()):
        lines.append(f"{subject} {job} {amount:+d} damage")
    if effects.get("hand_plus"):
        lines.append(f"{subject} start with {effects['hand_plus']:+d} cards")
    return lines


def _swap_bench(game_screen: GameScreen, run: dict) -> None:
    picked_bench = card_picker.main(
        game_screen, run, "Swap: pick a bench card",
        subtitle="it will trade places with a card in your deck",
        allowed=lambda zone, index, code: zone == "bench",
    )
    if picked_bench is None:
        return
    picked_deck = card_picker.main(
        game_screen, run, "Swap: pick the deck card it replaces",
        allowed=lambda zone, index, code: zone == "deck",
    )
    if picked_deck is None:
        return
    run_state.swap_deck_bench(run, picked_deck[1], picked_bench[1])


def main(game_screen: GameScreen, run: dict, enemy: dict,
         player_effects: dict, enemy_effects: dict) -> str:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2
    box_width = ui_common.box_width(game_screen)

    start = Button(bs * 2.2, bs * 0.6, cx - bs * 0.3, cy + bs * 1.9,
                   box_width=box_width, font=game_screen.big_text_font, text="fight")
    swap = Button(bs * 2.2, bs * 0.6, cx - bs * 2.8, cy + bs * 1.9,
                  box_width=box_width, font=game_screen.big_text_font, text="swap bench")
    back = ui_common.back_button(game_screen, "back")

    result = "back"
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        can_swap = bool(run["bench"])

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if key_pressed(pygame.key.get_pressed()) == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.touch(mouse_x, mouse_y):
                    running = False
                elif start.touch(mouse_x, mouse_y):
                    result = "start"
                    running = False
                elif can_swap and swap.touch(mouse_x, mouse_y):
                    _swap_bench(game_screen, run)
            if event.type == pygame.QUIT:
                raise QuitGame

        ui_common.draw_run_bar(game_screen, run)
        ui_common.draw_relic_strip(game_screen, run)

        draw_text(ui_common.enemy_label(enemy), game_screen.title_text_font,
                  ui_common.enemy_color(enemy["kind"]),
                  cx - bs * 3.6, cy - bs * 2.4, game_screen.surface)
        if enemy.get("note"):
            draw_text(enemy["note"], game_screen.text_font, ui_common.CURSE,
                      cx - bs * 3.6, cy - bs * 1.9, game_screen.surface)

        y = cy - bs * 1.6
        draw_text("enemy deck", game_screen.mid_text_font, WHITE,
                  cx - bs * 3.6, y, game_screen.surface)
        y += bs * 0.35
        for chunk in _wrap(sorted(enemy["deck"]), 6):
            draw_text("  ".join(chunk), game_screen.text_font, WHITE,
                      cx - bs * 3.6, y, game_screen.surface)
            y += bs * 0.28

        if enemy.get("relics"):
            y += bs * 0.1
            for relic_id in enemy["relics"]:
                draw_text(f"{ui_common.relic_label(relic_id)} - {ui_common.relic_text(relic_id)}",
                          game_screen.small_text_font, ui_common.RELIC,
                          cx - bs * 3.6, y, game_screen.surface)
                y += bs * 0.26

        y += bs * 0.15
        for line in _effect_lines(enemy_effects, "enemy"):
            draw_text(line, game_screen.small_text_font, ui_common.CURSE,
                      cx - bs * 3.6, y, game_screen.surface)
            y += bs * 0.26

        y = cy - bs * 1.6
        draw_text(f"your deck  ({len(run['deck'])})", game_screen.mid_text_font, WHITE,
                  cx + bs * 0.6, y, game_screen.surface)
        y += bs * 0.35
        names = [card_pool.display_name(c) for c in run["deck"]]
        rows = _wrap(names, 2)
        for chunk in rows[:DECK_ROWS]:
            draw_text("   ".join(chunk), game_screen.small_text_font, WHITE,
                      cx + bs * 0.6, y, game_screen.surface)
            y += bs * 0.26
        hidden = sum(len(chunk) for chunk in rows[DECK_ROWS:])
        if hidden:
            draw_text(f"+{hidden} more", game_screen.small_text_font, ui_common.DIM,
                      cx + bs * 0.6, y, game_screen.surface)
            y += bs * 0.26

        if run["bench"]:
            y += bs * 0.15
            draw_text(f"bench  ({len(run['bench'])}/{run_state.bench_limit(run)})",
                      game_screen.text_font, card_picker.BENCH_COLOR,
                      cx + bs * 0.6, y, game_screen.surface)
            y += bs * 0.3
            for code in run["bench"]:
                draw_text(card_pool.display_name(code), game_screen.small_text_font,
                          card_picker.BENCH_COLOR, cx + bs * 0.6, y, game_screen.surface)
                y += bs * 0.26

        y += bs * 0.15
        for line in _effect_lines(player_effects, "your"):
            draw_text(line, game_screen.small_text_font, ui_common.HILITE,
                      cx + bs * 0.6, y, game_screen.surface)
            y += bs * 0.26

        if can_swap:
            swap.update(game_screen)
        start.update(game_screen)
        back.update(game_screen)

        pygame.display.update()
        clock.tick(60)

    return result


def _wrap(items, per_row: int) -> list[list[str]]:
    return [items[i:i + per_row] for i in range(0, len(items), per_row)]
