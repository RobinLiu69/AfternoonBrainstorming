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
from screens.battling.finalize import finalize_battle

from campaign import stage_select, pre_battle, deck_builder, campaign_save
from campaign.campaign_manager import build_campaign_game_state
from campaign.ai_controller import AIController


def main(game_screen: GameScreen) -> None:
    while True:
        stage = stage_select.main(game_screen)
        if stage is None:
            return

        if pre_battle.main(game_screen, stage) != "start":
            continue

        save_state = campaign_save.load()
        player_deck = deck_builder.main(game_screen, stage, set(save_state.get("cleared", [])))
        if player_deck is None:
            continue

        game_state = build_campaign_game_state(stage, player_deck_override=player_deck)
        ai_controller = AIController(stage, player_name="player2")
        winner = battling.main(game_state, game_screen, mode="campaign",
                               ai_controller=ai_controller)
        if winner in ("None", ""):
            continue

        if winner == "player1":
            campaign_save.mark_cleared(stage)
        finalize_battle(game_state, game_screen, winner)
