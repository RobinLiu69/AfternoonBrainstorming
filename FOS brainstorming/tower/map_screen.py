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

"""The act map: a strip of nine layers plus a detail panel for the current one.

Returns ``("enter", pick)`` where ``pick`` is the chosen branch option (or
``None`` on a non-branch layer), or ``None`` when the player leaves the climb.
"""

from typing import Optional

import pygame

from shared.setting import WHITE
from core.game_screen import GameScreen, draw_text, QuitGame
from core.setting_config import load_setting
from core.UI import Button
from utils.controls import key_pressed

from rendering import style
from tower import card_pool, relic_screen, roster_screen, run_state, tower_map, ui_common
from tower.content import ENEMY_LABELS

SHORT_ENEMY: dict[str, str] = {
    "weak": "Weak", "normal": "Fight", "elite": "Elite", "boss": "BOSS",
}
SHORT_ROOM: dict[str, str] = {
    "event": "Event", "shop": "Shop", "gold_mine": "Gold", "relic_chest": "Relic",
}

# route columns sit 2.8 blocks apart, so their text wraps well before that
ROUTE_WRAP: int = 26


def _blind_flags(run: dict) -> tuple[bool, bool]:
    effects = run_state.merged_effects(run)
    return bool(effects.get("hide_rooms")), bool(effects.get("hide_enemies"))


def _layer_tag(run: dict, layer: dict, blind: tuple[bool, bool]) -> tuple[str, tuple[int, int, int]]:
    _hide_rooms, hide_enemies = blind
    kind = layer["kind"]
    if kind == "blessing":
        return "Bless", style.INK
    if kind == "skip":
        return "-", style.INK_DISABLED
    if kind == "battle":
        enemy = layer["enemy"]
        if hide_enemies and enemy["kind"] != "boss":
            return "???", style.INK_MUTED
        return SHORT_ENEMY.get(enemy["kind"], "?"), ui_common.enemy_color(enemy["kind"])
    if kind == "branch":
        return "Fork", style.INK

    pick = run_state.pick_for(run, layer["source"])
    if pick is None:
        return "?", style.INK_MUTED
    option = tower_map.layer_at(run_state.current_map(run), layer["source"])["options"][pick]
    if kind == "battle_linked":
        enemy = option["enemy"]
        return SHORT_ENEMY.get(enemy["kind"], "?"), ui_common.enemy_color(enemy["kind"])
    return SHORT_ROOM.get(option["rooms"][1]["kind"], "?"), style.INK


def _option_lines(option: dict, blind: tuple[bool, bool]) -> list[str]:
    hide_rooms, hide_enemies = blind
    lines: list[str] = []
    room = option.get("room")
    if room is not None:
        label = "???" if hide_rooms else ui_common.room_label(room["kind"])
        lines.append(f"room now: {label}")
    for i, room in enumerate(option.get("rooms", [])):
        label = "???" if hide_rooms else ui_common.room_label(room["kind"])
        lines.append(f"room {i + 1}: {label}")
    enemy = option.get("enemy")
    if enemy is not None:
        if hide_enemies:
            lines.append("then: ???")
        else:
            lines.append(f"then: {ui_common.enemy_label(enemy)}")
            lines.append(f"({len(enemy['deck'])} cards, {ENEMY_LABELS[enemy['kind']]})")
            if enemy.get("enemy_first"):
                lines.append("they move first")
    return lines


def render(game_screen: GameScreen, run: dict, act_map, layers, layer, options,
           current: int, blind, strip_x0: float, strip_y: float,
           strip_w: float, strip_h: float, strip_gap: float, panel_y: float,
           box_width: int, action_buttons: list, leave, roster, relics,
           hint_on: bool) -> None:
    bs = game_screen.block_size

    ui_common.draw_run_bar(game_screen, run)

    boss = tower_map.boss_of(act_map)
    style.muted_text(game_screen,
                     f"act {run['act']}  -  {boss['label']} waits at the top",
                     strip_x0, ui_common.title_y(game_screen),
                     game_screen.mid_text_font)

    for i, entry in enumerate(layers):
        x = strip_x0 + i * (strip_w + strip_gap)
        rect = pygame.Rect(int(x), int(strip_y), int(strip_w), int(strip_h))
        tag, color = _layer_tag(run, entry, blind)
        if entry["index"] < current:
            color = ui_common.DONE
        pygame.draw.rect(game_screen.surface, color, rect, box_width)
        if entry["index"] == current:
            pygame.draw.rect(game_screen.surface, ui_common.HILITE,
                             rect.inflate(int(bs * 0.12), int(bs * 0.12)), box_width)
        draw_text(str(entry["index"]), game_screen.small_text_font, color,
                  rect.x + bs * 0.06, rect.y + bs * 0.04, game_screen.surface)
        draw_text(tag, game_screen.small_text_font, color,
                  rect.x + bs * 0.08, rect.y + bs * 0.35, game_screen.surface)

    _draw_panel(game_screen, run, layer, options, panel_y, blind)

    for btn, _pick in action_buttons:
        btn.update(game_screen)
    leave.update(game_screen)
    roster.update(game_screen)
    relics.update(game_screen)

    ui_common.draw_relic_strip(game_screen, run, detailed=hint_on)


def main(game_screen: GameScreen, run: dict) -> Optional[tuple[str, Optional[int]]]:
    running = True
    bs = game_screen.block_size
    cx = game_screen.display_width / 2
    box_width = ui_common.box_width(game_screen)

    act_map = run_state.current_map(run)
    layers = act_map["layers"]
    current = run["layer"]
    layer = tower_map.layer_at(act_map, current)
    blind = _blind_flags(run)

    # later acts are longer, so the strip shrinks to keep every layer on screen
    strip_gap = bs * 0.06
    usable = game_screen.display_width - bs * 0.8
    strip_w = min(bs * 0.95, (usable - strip_gap * (len(layers) - 1)) / len(layers))
    strip_h = bs * 0.75
    strip_x0 = (game_screen.display_width - (len(layers) * (strip_w + strip_gap) - strip_gap)) / 2
    strip_y = bs * 1.05

    panel_y = bs * 2.6
    options = layer.get("options", [])

    action_buttons: list[tuple[Button, Optional[int]]] = []
    if options:
        btn_w = bs * 2.6
        total = len(options) * (btn_w + bs * 0.2) - bs * 0.2
        for i in range(len(options)):
            x = cx - total / 2 + i * (btn_w + bs * 0.2)
            action_buttons.append((Button(
                btn_w, bs * 0.55, x, panel_y + bs * 1.7, box_width=box_width,
                font=game_screen.mid_text_font, text=f"take route {i + 1}"), i))
    else:
        action_buttons.append((Button(
            bs * 2.6, bs * 0.6, cx - bs * 1.3, panel_y + bs * 1.7, box_width=box_width,
            font=game_screen.big_text_font, text=_enter_label(layer)), None))

    leave = ui_common.back_button(game_screen, "leave")
    roster = Button(bs * 2.4, bs * 0.6, bs * 2.2,
                    game_screen.display_height - bs * 0.85,
                    box_width=box_width, font=game_screen.mid_text_font,
                    text="[D] deck")
    relics = Button(bs * 2.4, bs * 0.6, bs * 4.8,
                    game_screen.display_height - bs * 0.85,
                    box_width=box_width, font=game_screen.mid_text_font,
                    text="[R] relics")

    hint_on = load_setting("hint_on")
    result: Optional[tuple[str, Optional[int]]] = None
    clock = pygame.time.Clock()

    while running:
        game_screen.render()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = key_pressed(pygame.key.get_pressed())
                if key == pygame.K_ESCAPE:
                    running = False
                if key == pygame.K_d:
                    roster_screen.main(game_screen, run)
                if key == pygame.K_r:
                    relic_screen.main(game_screen, run)
                if key == pygame.K_f:
                    hint_on = not hint_on
            if event.type == pygame.MOUSEBUTTONDOWN:
                if leave.touch(mouse_x, mouse_y):
                    running = False
                elif roster.touch(mouse_x, mouse_y):
                    roster_screen.main(game_screen, run)
                elif relics.touch(mouse_x, mouse_y):
                    relic_screen.main(game_screen, run)
                for btn, pick in action_buttons:
                    if btn.touch(mouse_x, mouse_y):
                        result = ("enter", pick)
                        running = False
                        break
            if event.type == pygame.QUIT:
                raise QuitGame

        render(game_screen, run, act_map, layers, layer, options, current,
               blind, strip_x0, strip_y, strip_w, strip_h, strip_gap,
               panel_y, box_width, action_buttons, leave, roster, relics,
               hint_on)
        pygame.display.update()
        clock.tick(60)

    return result


def _enter_label(layer: dict) -> str:
    kind = layer["kind"]
    if kind == "blessing":
        return "claim blessing"
    if kind in ("battle", "battle_linked"):
        return "fight"
    if kind == "room_linked":
        return "enter room"
    return "continue"


def _draw_panel(game_screen: GameScreen, run: dict, layer: dict,
                options: list[dict], panel_y: float,
                blind: tuple[bool, bool]) -> None:
    bs = game_screen.block_size
    cx = game_screen.display_width / 2

    if options:
        pad = bs * style.PANEL_PAD
        panel_w = bs * 3.1
        total = len(options) * (panel_w + bs * 0.3) - bs * 0.3
        top = panel_y - bs * 0.35
        rows = [ui_common.wrap_all(_option_lines(option, blind), ROUTE_WRAP)
                for option in options]
        height = (bs * style.HEADER_HEIGHT + pad
                  + bs * 0.28 * max(len(lines) for lines in rows) + pad * 0.5)
        for i, lines in enumerate(rows):
            x = cx - total / 2 + i * (panel_w + bs * 0.3)
            style.section(game_screen, f"ROUTE {i + 1}", x, top, panel_w, height)
            y = top + bs * style.HEADER_HEIGHT + pad * 0.8
            for line in lines:
                ui_common.draw_auto(game_screen, line, "text_font", style.INK,
                                    x + pad, y)
                y += bs * 0.28
        return

    resolved = run_state.current_layer(run)
    kind = resolved["kind"]
    y = panel_y
    if kind == "battle":
        enemy = resolved["enemy"]
        draw_text(ui_common.enemy_label(enemy), game_screen.big_big_text_font,
                  ui_common.enemy_color(enemy["kind"]), cx - bs * 2.0, y, game_screen.surface)
        y += bs * 0.55
        if enemy.get("enemy_first"):
            draw_text("they move first", game_screen.mid_text_font, ui_common.CURSE,
                      cx - bs * 2.0, y, game_screen.surface)
        else:
            draw_text("you move first", game_screen.mid_text_font, ui_common.HILITE,
                      cx - bs * 2.0, y, game_screen.surface)
        y += bs * 0.42
        names = sorted({card_pool.display_name(c) for c in enemy["deck"]})
        for line in ui_common.wrap(f"deck: {' '.join(names)}", ui_common.PANEL_WRAP):
            ui_common.draw_auto(game_screen, line, "text_font", WHITE,
                                cx - bs * 2.0, y)
            y += bs * 0.26
        if enemy.get("relics"):
            names = ", ".join(ui_common.relic_label(r) for r in enemy["relics"])
            for line in ui_common.wrap(f"relics: {names}", ui_common.PANEL_WRAP):
                ui_common.draw_auto(game_screen, line, "text_font",
                                    ui_common.RELIC, cx - bs * 2.0, y)
                y += bs * 0.26
    elif kind == "room":
        ui_common.draw_auto(game_screen, ui_common.room_label(resolved["room"]["kind"]),
                            "big_big_text_font", ui_common.GOLD, cx - bs * 1.2, y)
    elif kind == "blessing":
        draw_text("An opening blessing awaits.", game_screen.big_text_font, ui_common.HILITE,
                  cx - bs * 1.8, y, game_screen.surface)
    else:
        draw_text("Onward.", game_screen.big_text_font, WHITE,
                  cx - bs * 0.6, y, game_screen.surface)
