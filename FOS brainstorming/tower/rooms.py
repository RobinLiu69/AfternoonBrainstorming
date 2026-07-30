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

"""Entering a non-combat room."""

from __future__ import annotations

import random

from core.game_screen import GameScreen

from tower import events, grants, notice_screen, run_state, shop, shop_screen, ui_common
from tower.content import GOLD_MINE_REWARD


def enter(game_screen: GameScreen, run: dict, room: dict, rng: random.Random) -> str:
    """Returns "" normally, or "lose"/"abandon" if the room ended the climb."""
    kind = room.get("kind", "")

    if kind == "gold_mine":
        gained = run_state.award_gold(run, GOLD_MINE_REWARD)
        notice_screen.main(game_screen, "Gold Mine",
                           [f"you dig out {gained} gold."], run=run, color=ui_common.GOLD)

    elif kind == "relic_chest":
        grants.offer_relic(game_screen, run, rng, "Relic Chest")

    elif kind == "shop":
        stock = shop.generate_stock(run, rng)
        shop_screen.main(game_screen, run, stock, rng)

    elif kind == "event":
        return events.enter(game_screen, run, rng)

    else:
        notice_screen.main(game_screen, "Empty Room",
                           ["nothing here yet."], run=run, color=ui_common.DIM)

    return ""
