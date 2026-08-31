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
from core.setting_config import load_setting
from core.UI import Button
from utils.controls import key_pressed

from rendering import style
from tower import card_picker, card_pool, run_state, ui_common

DECK_ROWS: int = 7


def _effect_lines(effects: dict, subject: str) -> list[str]:
    lines: list[str] = []
    if effects.get("unit_hp_plus"):
        lines.append(f"{subject} units {effects['unit_hp_plus']:+d} HP")
    if effects.get("unit_damage_plus"):
        lines.append(f"{subject} units {effects['unit_damage_plus']:+d} damage")
    hp_by_job = effects.get("job_hp_plus", {})
    damage_by_job = effects.get("job_damage_plus", {})
    for job in sorted(set(hp_by_job) | set(damage_by_job)):
        parts = []
        if hp_by_job.get(job):
            parts.append(f"{hp_by_job[job]:+d} HP")
        if damage_by_job.get(job):
            parts.append(f"{damage_by_job[job]:+d} damage")
        lines.append(f"{subject} {job} {'  '.join(parts)}")
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


def render(game_screen: GameScreen, run: dict, enemy: dict,
           player_effects: dict, enemy_effects: dict, can_swap: bool,
           swap, start, back, hint_on: bool) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    cy = game_screen.display_height / 2

    ui_common.draw_run_bar(game_screen, run)

    draw_text(ui_common.enemy_label(enemy), game_screen.title_text_font,
              style.INK, cx - bs * 3.6, ui_common.title_y(game_screen),
              game_screen.surface)
    first_text, first_color = (("they move first", ui_common.CURSE)
                               if enemy.get("enemy_first")
                               else ("you move first", ui_common.HILITE))
    draw_text(first_text, game_screen.big_text_font, first_color,
              cx - bs * 3.6, ui_common.subtitle_y(game_screen), game_screen.surface)
    if enemy.get("note"):
        for i, line in enumerate(ui_common.wrap(enemy["note"], 34)):
            draw_text(line, game_screen.text_font, ui_common.CURSE,
                      cx - bs * 1.5, cy - bs * (2.0 - 0.26 * i), game_screen.surface)

    pad = bs * style.PANEL_PAD
    column_w = bs * 3.4
    column_h = ui_common.column_bottom(game_screen) - ui_common.content_top(game_screen)
    style.section(game_screen, "ENEMY", cx - bs * 3.75,
                  ui_common.content_top(game_screen), column_w, column_h,
                  right=ui_common.enemy_label(enemy))
    style.section(game_screen, "YOURS", cx + bs * 0.25,
                  ui_common.content_top(game_screen), column_w, column_h,
                  right=f"{len(run['deck'])} cards")
    inner_bottom = ui_common.content_top(game_screen) + column_h - pad

    y = ui_common.content_top(game_screen) + bs * style.HEADER_HEIGHT + pad
    draw_text("deck", game_screen.mid_text_font, style.INK_MUTED,
              cx - bs * 3.6, y, game_screen.surface)
    y += bs * 0.34
    enemy_names = sorted(card_pool.display_name(c) for c in enemy["deck"])
    for chunk in _wrap(enemy_names, 3):
        ui_common.draw_auto(game_screen, "  ".join(chunk), "text_font", WHITE,
                            cx - bs * 3.6, y)
        y += bs * 0.27

    if enemy.get("relics"):
        y += bs * 0.1
        for relic_id in enemy["relics"]:
            ui_common.draw_auto(game_screen, ui_common.relic_label(relic_id),
                                "text_font", ui_common.RELIC, cx - bs * 3.6, y)
            y += bs * 0.25
            if hint_on:
                for line in ui_common.wrap(ui_common.relic_text(relic_id), 34):
                    ui_common.draw_auto(game_screen, line, "small_text_font",
                                        ui_common.DIM, cx - bs * 3.45, y)
                    y += bs * 0.21

    y += bs * 0.1
    ui_common.draw_capped_lines(game_screen, _effect_lines(enemy_effects, "enemy"),
                                "text_font", ui_common.CURSE,
                                cx - bs * 3.6, y, 0.25, inner_bottom)

    y = ui_common.content_top(game_screen) + bs * style.HEADER_HEIGHT + pad * 0.7
    draw_text("deck", game_screen.mid_text_font, style.INK_MUTED,
              cx + bs * 0.4, y, game_screen.surface)
    y += bs * 0.32
    names = [card_pool.display_name(c) for c in run["deck"]]
    rows = _wrap(names, 4)
    for chunk in rows[:DECK_ROWS]:
        ui_common.draw_auto(game_screen, "  ".join(chunk), "text_font", WHITE,
                            cx + bs * 0.4, y)
        y += bs * 0.25
    hidden = sum(len(chunk) for chunk in rows[DECK_ROWS:])
    if hidden:
        draw_text(f"+{hidden} more  ([D] on the map for the full list)",
                  game_screen.small_text_font, ui_common.DIM,
                  cx + bs * 0.4, y, game_screen.surface)
        y += bs * 0.25

    if run["bench"]:
        y += bs * 0.1
        label = f"bench  ({len(run['bench'])}/{run_state.bench_limit(run)})"
        draw_text(label, game_screen.mid_text_font, card_picker.BENCH_COLOR,
                  cx + bs * 0.4, y, game_screen.surface)
        names = "  ".join(card_pool.display_name(code) for code in run["bench"])
        ui_common.draw_auto(game_screen, names, "text_font", card_picker.BENCH_COLOR,
                            cx + bs * 0.4 + game_screen.mid_text_font.size(label)[0]
                            + bs * 0.2, y)
        y += bs * 0.34

    y += bs * 0.06
    ui_common.draw_capped_lines(game_screen, _effect_lines(player_effects, "your"),
                                "text_font", ui_common.HILITE,
                                cx + bs * 0.4, y, 0.25, inner_bottom)


    if can_swap:
        swap.update(game_screen)
    start.update(game_screen)
    back.update(game_screen)

    ui_common.draw_relic_strip(game_screen, run, detailed=hint_on)


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
    hint_on = load_setting("hint_on")
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        can_swap = bool(run["bench"])

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key == pygame.K_ESCAPE:
                    running = False
                if key == pygame.K_f:
                    hint_on = not hint_on
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

        render(game_screen, run, enemy, player_effects, enemy_effects,
               can_swap, swap, start, back, hint_on)
        pygame.display.update()
        clock.tick(60)

    return result


def _wrap(items, per_row: int) -> list[list[str]]:
    return [items[i:i + per_row] for i in range(0, len(items), per_row)]

