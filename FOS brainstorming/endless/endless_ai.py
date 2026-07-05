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

from __future__ import annotations
from typing import TYPE_CHECKING

from campaign.ai_controller import AIController
from endless import effects

if TYPE_CHECKING:
    from core.game_state import GameState


TRACKED_MAGIC: tuple[str, ...] = ("HEAL", "MOVE", "CUBES", "MOVEO")


class EndlessAIController(AIController):

    def __init__(self, spec: dict, player_effects: dict):
        super().__init__(spec["strategy"], player_name="player2")
        for key, val in spec.get("strategy_overrides", {}).items():
            if hasattr(self.strategy, key):
                setattr(self.strategy, key, val)
        self.ai_effects: dict = dict(spec.get("ai_effects", {}))
        self.player_effects: dict = dict(player_effects)
        self._p1_buffed_ids: set[str] = set()
        self._p1_turn_seen: int = -1
        self._p1_seen_iids: set[str] = set()
        self._p1_prev_hand: dict[str, int] = {}
        self._p1_prev_turn: int = -1
        self._p1_hand_primed: bool = False
        self.p1_played_counts: dict[str, int] = {}
        self.p1_magic_plays: dict[str, int] = {code: 0 for code in TRACKED_MAGIC}

    def _maintain_units(self, gs: "GameState") -> None:
        effects.maintain_side_unit_buffs(self.ai_effects, gs, "player2", self._buffed_unit_ids)
        effects.maintain_side_unit_buffs(self.player_effects, gs, "player1", self._p1_buffed_ids)
        if gs.turn_number % 2 == 0 and gs.turn_number != self._p1_turn_seen:
            self._p1_turn_seen = gs.turn_number
            effects.apply_side_per_turn(self.player_effects, gs, "player1")
        self._track_player1(gs)

    def _per_turn(self, gs: "GameState") -> None:
        effects.apply_side_per_turn(self.ai_effects, gs, "player2")

    def _apply_one_shots(self, gs: "GameState") -> None:
        effects.apply_side_one_shots(self.ai_effects, gs, "player2")
        effects.apply_side_one_shots(self.player_effects, gs, "player1")

    def _apply_initial(self, gs: "GameState") -> None:
        effects.apply_side_initial_hand(self.ai_effects, gs, "player2")
        effects.apply_side_initial_hand(self.player_effects, gs, "player1")

    def _track_player1(self, gs: "GameState") -> None:
        for c in gs.player1.on_board:
            if c.instance_id not in self._p1_seen_iids:
                self._p1_seen_iids.add(c.instance_id)
                self.p1_played_counts[c.job_and_color] = self.p1_played_counts.get(c.job_and_color, 0) + 1

        hand = gs.player1.hand
        counts = {code: hand.count(code) for code in TRACKED_MAGIC}
        if self._p1_hand_primed:
            turn_changed = gs.turn_number != self._p1_prev_turn
            for code in TRACKED_MAGIC:
                drop = self._p1_prev_hand.get(code, 0) - counts[code]
                if drop > 0:
                    if code == "MOVEO" and turn_changed:
                        continue
                    self.p1_magic_plays[code] += drop
        self._p1_prev_hand = counts
        self._p1_prev_turn = gs.turn_number
        self._p1_hand_primed = True

    def p1_consumption(self, gs: "GameState") -> dict[str, int]:
        alive: dict[str, int] = {}
        for c in gs.player1.on_board:
            if c.health > 0:
                alive[c.job_and_color] = alive.get(c.job_and_color, 0) + 1
        consumed: dict[str, int] = {}
        for code, played in self.p1_played_counts.items():
            died = played - alive.get(code, 0)
            if died > 0:
                consumed[code] = consumed.get(code, 0) + died
        for code, plays in self.p1_magic_plays.items():
            if plays > 0:
                consumed[code] = consumed.get(code, 0) + plays
        return consumed
