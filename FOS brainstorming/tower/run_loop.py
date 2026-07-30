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

"""Tower mode: menu, faction draft, then layer after layer until you fall."""

from __future__ import annotations

import random

from core.game_screen import GameScreen

from tower import (
    battle_flow, choice_screen, enchant_runtime, faction_select, grants,
    map_screen, menu_screen, notice_screen, rooms, run_state, tower_map,
    tower_save, ui_common,
)
from tower.content import ORB_DROP_CHANCE, RELIC_DROP_CHANCE


def main(game_screen: GameScreen) -> None:
    enchant_runtime.install()
    try:
        state = tower_save.load()
        while True:
            choice = menu_screen.main(game_screen, state)
            if choice is None:
                return
            if choice == "new":
                factions = faction_select.main(game_screen)
                if factions is None:
                    continue
                state["run"] = run_state.new_run(factions)
                tower_save.save(state)
            if state.get("run") is None:
                continue
            _play_run(game_screen, state)
    finally:
        enchant_runtime.uninstall()


def _play_run(game_screen: GameScreen, state: dict) -> None:
    while True:
        run = state["run"]
        action = map_screen.main(game_screen, run)
        if action is None:
            tower_save.save(state)
            return

        _enter, pick = action
        rng = run_state.layer_rng(run, salt=5)

        if pick is not None:
            run_state.record_pick(run, pick)
            room = tower_map.branch_choice_room(
                run_state.current_map(run), run["layer"], pick)
            if _visit(game_screen, state, run, room, rng) == "over":
                return
            outcome = run_state.advance_layer(run)
        else:
            layer = run_state.current_layer(run)
            kind = layer["kind"]

            if kind == "blessing":
                _claim_blessing(game_screen, run, rng)
                outcome = run_state.advance_layer(run)
            elif kind == "room":
                if _visit(game_screen, state, run, layer["room"], rng) == "over":
                    return
                outcome = run_state.advance_layer(run)
            elif kind == "battle":
                result = _fight(game_screen, run, layer["enemy"], rng)
                if result == "abandon":
                    tower_save.save(state)
                    return
                if result == "lose":
                    _end_run(game_screen, state, run, won=False)
                    return
                outcome = run_state.advance_layer(run)
            else:
                outcome = run_state.advance_layer(run)

        tower_save.save(state)
        if outcome == "win":
            _end_run(game_screen, state, run, won=True)
            return


def _visit(game_screen: GameScreen, state: dict, run: dict, room: dict,
           rng: random.Random) -> str:
    """Enter a room.  Returns "over" when it ended the climb."""
    result = rooms.enter(game_screen, run, room, rng)
    if result == "lose":
        _end_run(game_screen, state, run, won=False)
        return "over"
    if result == "abandon":
        tower_save.save(state)
        return "over"
    return ""


def _claim_blessing(game_screen: GameScreen, run: dict, rng: random.Random) -> None:
    offers = run_state.blessing_offers(run)
    options = [{"label": b["label"], "lines": [b["text"]], "color": ui_common.HILITE}
               for b in offers]
    choice = choice_screen.main(game_screen, "Opening blessing", options, run=run,
                                subtitle="one of the three is yours")
    if choice is None or choice == choice_screen.SKIP:
        choice = 0
    grants.apply_blessing(game_screen, run, offers[choice]["id"], rng)


def _fight(game_screen: GameScreen, run: dict, enemy: dict, rng: random.Random) -> str:
    result = battle_flow.fight(game_screen, run, enemy)
    # the last boss ends the climb, so there is nothing left to spend a reward on
    if result == "win" and not run_state.is_final_battle(run):
        _battle_reward(game_screen, run, enemy, rng)
    return result


def _battle_reward(game_screen: GameScreen, run: dict, enemy: dict,
                   rng: random.Random) -> None:
    gold = run_state.award_gold(run, enemy.get("gold", 0))
    lines = [f"+{gold} gold"]

    plunder = run_state.victory_bonus_gold(run)
    if plunder:
        run["gold"] += plunder
        lines.append(f"+{plunder} gold from your pirates")

    orb = enemy["kind"] == "boss" or rng.random() < ORB_DROP_CHANCE
    if orb:
        run["orbs"] += 1
        lines.append("+1 Forgetting Orb")

    notice_screen.main(game_screen, "Victory", lines, run=run, color=ui_common.HILITE)

    if enemy["kind"] == "boss":
        # a boss earns a real choice, and is the only source of special relics
        grants.choose_relic(game_screen, run, rng, "Boss spoils",
                            include_special=True,
                            decline_gold=grants.DECLINE_RELIC_GOLD)
    elif enemy["kind"] == "elite" or rng.random() < RELIC_DROP_CHANCE:
        grants.offer_relic(game_screen, run, rng, "Spoils")

    grants.offer_cards(game_screen, run, rng, "Pick a card")


def _end_run(game_screen: GameScreen, state: dict, run: dict, won: bool) -> None:
    act, layer = run["act"], run["layer"]
    new_best = tower_save.record_run_end(state, act, layer, won)

    title = "Tower cleared" if won else "You fall"
    lines = [
        f"act {act}, layer {layer}",
        f"battles won: {run.get('battles_won', 0)}",
        f"relics: {len(run.get('relics', []))}    gold: {run['gold']}",
    ]
    if new_best:
        lines.append("new best climb!")
    notice_screen.main(game_screen, title, lines,
                       color=ui_common.HILITE if won else ui_common.CURSE,
                       button_text="back to menu")
