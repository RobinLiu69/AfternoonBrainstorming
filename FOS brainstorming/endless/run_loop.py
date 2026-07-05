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

from core.game_screen import GameScreen
from screens.battling import battling

from endless import (
    run_state, endless_save, menu_screen, floor_preview,
    reward_screen, shop_screen, event_screen, game_over_screen,
)
from endless.battle_builder import build_endless_game_state
from endless.endless_ai import EndlessAIController


def main(game_screen: GameScreen) -> None:
    state = endless_save.load()
    while True:
        choice = menu_screen.main(game_screen, state)
        if choice is None:
            return
        if choice == "new":
            state["run"] = run_state.new_run()
            endless_save.save(state)
        if state.get("run") is None:
            continue
        _play_run(game_screen, state)


def _play_run(game_screen: GameScreen, state: dict) -> None:
    while True:
        run = state.get("run")
        if run is None:
            return
        phase = run.get("phase", "battle")

        if phase == "battle":
            spec = run_state.ensure_floor_spec(run)
            endless_save.save(state)

            if spec["kind"] == "event":
                event_screen.main(game_screen, run, spec)
                run_state.advance_floor(run)
                endless_save.save(state)
                continue

            player_fx, ai_fx = run_state.battle_effects(run, spec)
            preview = floor_preview.main(game_screen, spec, ai_fx, player_fx)
            if preview != "start":
                endless_save.save(state)
                return

            game_state = build_endless_game_state(run, spec)
            ai_controller = EndlessAIController({**spec, "ai_effects": ai_fx}, player_fx)
            winner = battling.main(game_state, game_screen, mode="campaign", ai_controller=ai_controller)

            if winner in ("None", ""):
                endless_save.save(state)
                return
            if winner == "player2":
                floors_cleared = run["floor"] - 1
                new_best = endless_save.record_run_end(state, floors_cleared)
                game_over_screen.main(game_screen, run, state, floors_cleared, new_best)
                return

            lost = run_state.settle_temp_deck(run, ai_controller.p1_consumption(game_state))
            run["armed_consumables"] = []
            coins = run_state.award_floor_coins(run, spec)
            run["phase"] = "reward"
            run["pending"] = {
                "kind": "reward",
                "options": run_state.generate_reward_options(run, spec["kind"]),
                "coins_gained": coins,
                "lost": lost,
            }
            endless_save.save(state)

        elif phase == "reward":
            pending = run.get("pending") or {}
            options = pending.get("options") or run_state.generate_reward_options(run, "normal")
            chosen = reward_screen.main(game_screen, run, options, pending)
            if chosen is None:
                endless_save.save(state)
                return
            if chosen.get("type") == "card":
                run["temp_deck"].append(chosen["card"])
            elif chosen.get("type") == "relic":
                run["relics"].append(chosen["relic"])
            elif chosen.get("type") == "skip":
                run["coins"] += 10
            if run["floor"] % 5 == 0:
                run["phase"] = "shop"
                run["pending"] = {"kind": "shop", "stock": run_state.generate_shop_stock(run)}
            else:
                run_state.advance_floor(run)
            endless_save.save(state)

        elif phase == "shop":
            pending = run.get("pending") or {}
            stock = pending.get("stock") or run_state.generate_shop_stock(run)
            run["pending"] = {"kind": "shop", "stock": stock}
            result = shop_screen.main(game_screen, state, run, stock)
            if result == "leave":
                run_state.advance_floor(run)
                endless_save.save(state)
            else:
                endless_save.save(state)
                return

        else:
            run["phase"] = "battle"
            endless_save.save(state)
