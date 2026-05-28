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
from typing import TYPE_CHECKING, Optional

from core.game_action import GameAction
from campaign import ai_query, ai_evaluator
from campaign.ai_strategies.base import Strategy
from campaign.ai_strategies.white import WhiteStrategy
from campaign.ai_strategies.red import RedStrategy
from campaign.ai_strategies.blue import BlueStrategy
from campaign.ai_strategies.green import GreenStrategy
from campaign.ai_strategies.orange import OrangeStrategy
from campaign.ai_strategies.boss import BossStrategy
from campaign.boss_config import apply_per_turn_buffs, apply_initial_buffs, apply_stage_one_shots, maintain_unit_buffs
from campaign.config_loader import CAMPAIGN_SETTINGS

if TYPE_CHECKING:
    from core.game_state import GameState


STRATEGY_REGISTRY: dict[str, type[Strategy]] = {
    "white":  WhiteStrategy,
    "red":    RedStrategy,
    "blue":   BlueStrategy,
    "green":  GreenStrategy,
    "orange": OrangeStrategy,
    "boss":   BossStrategy,
}


_DELAYS = CAMPAIGN_SETTINGS["ai_delay_ms"]
AI_ACTION_DELAY_MS: int = int(_DELAYS["action"])
AI_ATTACK_DELAY_MS: int = int(_DELAYS["attack"])
AI_TURN_START_DELAY_MS: int = int(_DELAYS["turn_start"])
AI_BUSY_RECHECK_MS: int = int(_DELAYS["busy_recheck"])
"""Polling interval while waiting for combat animations / pending attacks to drain."""

LETHAL_SCORE_THRESHOLD: float = float(CAMPAIGN_SETTINGS["thresholds"]["lethal_score_threshold"])
"""evaluate_attack adds KILL_BONUS_BASE=100 for a kill; same threshold gates priority."""


class AIController:
    """GameAction producer for campaign mode.

    Each tick returns at most one GameAction, gated by a per-action delay so the
    human player can follow what's happening. The AI re-evaluates the live
    GameState every tick — no pre-planned action queue, which avoids stale
    decisions after card abilities mutate the board.
    """

    def __init__(self, stage: str, player_name: str = "player2"):
        strategy_cls = STRATEGY_REGISTRY.get(stage)
        if strategy_cls is None:
            raise ValueError(f"No strategy registered for stage {stage!r}")
        self.stage: str = stage
        self.strategy: Strategy = strategy_cls()
        # Apply per-faction config overrides (campaign_setting.json) on top of class defaults.
        overrides = CAMPAIGN_SETTINGS.get("faction_overrides", {}).get(stage, {})
        for key, val in overrides.items():
            if hasattr(self.strategy, key):
                setattr(self.strategy, key, val)
        self.player_name: str = player_name
        self._next_release_ms: int = 0
        self._last_turn_seen: int = -1
        self._initialized: bool = False
        self.focus_position: tuple[int, int] | None = None

    def tick(self, gs: "GameState", now_ms: int, renderer_busy: bool = False) -> list[GameAction]:
        # Apply stage one-shots / initial buffs as soon as the world is ready (board_dict
        # populated and players initialized). Runs every tick but no-ops after first run.
        self._ensure_initialized(gs)
        # Idempotent per-tick: tag and buff any new AI units (boss +1 HP).
        maintain_unit_buffs(self.stage, gs)

        current = "player1" if gs.turn_number % 2 == 0 else "player2"
        if current != self.player_name:
            self._last_turn_seen = -1
            return []
        if gs.paused:
            return []

        if self._last_turn_seen != gs.turn_number:
            self._last_turn_seen = gs.turn_number
            self._next_release_ms = now_ms + AI_TURN_START_DELAY_MS
            apply_per_turn_buffs(self.stage, gs)
            return []

        if now_ms < self._next_release_ms:
            return []

        # Wait for combat animations / pending attacks / dying cards to drain before
        # issuing the next action. `pending_combat_events` only stays non-empty for the
        # single frame before the renderer drains it into combat_animator; after that
        # `renderer_busy` is the only signal that animations are still in flight.
        if gs.pending_combat_events or gs.pending_attacks or renderer_busy:
            self._next_release_ms = now_ms + AI_BUSY_RECHECK_MS
            return []

        action = self._decide_next(gs)
        if action is None:
            self.focus_position = None
            return []

        if action.action_type in ("play_card", "attack"):
            self.focus_position = (action.board_x, action.board_y)
        else:
            self.focus_position = None

        delay = AI_ATTACK_DELAY_MS if action.action_type == "attack" else AI_ACTION_DELAY_MS
        self._next_release_ms = now_ms + delay
        return [action]

    def _ensure_initialized(self, gs: "GameState") -> None:
        if self._initialized:
            return
        # Wait until battling.main has populated the board and called player.initialize
        # (signaled by a non-empty board_dict + non-empty hand+pile on player2).
        if not gs.board_dict:
            return
        player2 = gs.player2
        if not (player2.hand or player2.draw_pile or player2.discard_pile):
            return
        apply_stage_one_shots(self.stage, gs)
        apply_initial_buffs(self.stage, gs)
        self._initialized = True

    def _effective_attack_min(self, gs: "GameState") -> float:
        """Lower the attack threshold proportionally as the AI falls behind.

        `gs.score` is signed: positive = player2 leads, negative = player1 leads. The
        AI is always player2 in campaign, so a negative score means trailing.
        Hoarding attacks while losing is dead weight — at any nontrivial deficit start
        cashing in chip damage instead, and at deep deficit drop the threshold to 0 so
        any damage at all is preferred over end_turn.
        """
        base = float(self.strategy.attack_min_score)
        deficit = -gs.score if self.player_name == "player2" else gs.score
        if deficit <= 2:
            return base
        return max(0.0, base - (deficit - 2) * 3.5)

    def _decide_next(self, gs: "GameState") -> Optional[GameAction]:
        # Move chain (highest priority — tempo lost if interrupted):
        #   1. Drive a unit already in moving=True state to select / commit destination.
        #   2. If we have unused movings count, set a fresh unit's moving=True.
        #   3. If MOVEO sits in hand, play it to inject a free movings count.
        # All three cascade; the next tick walks down the chain until exhausted.
        move = self._best_move_action(gs)
        if move is not None:
            return move
        start = self._start_unit_move(gs)
        if start is not None:
            return start
        moveo = self._play_moveo(gs)
        if moveo is not None:
            return moveo

        attack = self.strategy.best_attack(gs, self.player_name)
        play = self.strategy.best_placement(gs, self.player_name)

        effective_min = self._effective_attack_min(gs)
        attack_action: Optional[GameAction] = None
        if attack is not None and attack.score >= effective_min:
            attack_action = GameAction(
                player=self.player_name,
                action_type="attack",
                board_x=attack.x,
                board_y=attack.y,
            )

        play_action: Optional[GameAction] = None
        if play is not None and play.score >= self.strategy.placement_min_score:
            play_action = GameAction(
                player=self.player_name,
                action_type="play_card",
                board_x=play.x,
                board_y=play.y,
                hand_index=play.hand_index,
            )

        # 1. Lethal attack from an already-deployed unit is cheapest: spends 1 attack,
        #    no card. Take it before placing anything.
        if attack is not None and attack.score >= LETHAL_SCORE_THRESHOLD and attack_action is not None:
            return attack_action

        # 2. Placement (lethal_placement_bonus folds same-turn ASS kills in here, so
        #    a kill-enabling placement still ranks above generic build-board placements).
        if play_action is not None:
            return play_action

        # 3. Non-lethal attack (chip damage, anti-armor pokes).
        if attack_action is not None:
            return attack_action

        return GameAction(player=self.player_name, action_type="end_turn")

    def _start_unit_move(self, gs: "GameState") -> Optional[GameAction]:
        """Use a banked movings count to set the best orange unit's moving=True.

        Caller must already have established that no unit is mid-move (`_best_move_action`
        handles that case). When `number_of_movings > 0` and the AI clicks on a unit at
        its own cell, [core/player.py move_card] branch 1 fires and consumes 1 count
        to enter the moving=True state, ready for the standard select/dest chain.
        """
        if gs.number_of_movings.get(self.player_name, 0) <= 0:
            return None
        on_board = gs.get_player(self.player_name).on_board
        if any(c.moving for c in on_board):
            return None  # _best_move_action will handle the in-progress mover

        candidates = [c for c in on_board if not c.numbness and c.health > 0]
        if not candidates:
            return None

        def best_dest_score(unit) -> float:
            dests = ai_query.move_destinations_for(gs, unit)
            if not dests:
                return float("-inf")
            return max(ai_evaluator.score_move_destination(unit, d, gs) for d in dests)

        best_unit = max(candidates, key=best_dest_score)
        if best_dest_score(best_unit) <= 0:
            return None  # no destination would generate net value

        return GameAction(
            player=self.player_name, action_type="move_to",
            board_x=best_unit.board_x, board_y=best_unit.board_y,
        )

    def _play_moveo(self, gs: "GameState") -> Optional[GameAction]:
        """Play MOVEO from hand to gain +1 movings.

        Only fire when there's at least one non-numb orange unit that could plausibly
        consume the movings count this turn — otherwise the magic card discards into
        the void at turn_end (`number_of_movings` resets to 0). We don't pre-pay for
        a movings count we can't use.
        """
        hand = gs.get_player(self.player_name).hand
        try:
            idx = hand.index("MOVEO")
        except ValueError:
            return None

        movable = [
            c for c in gs.get_player(self.player_name).on_board
            if not c.numbness and c.health > 0 and ai_query.move_destinations_for(gs, c)
        ]
        if not movable:
            return None
        return GameAction(
            player=self.player_name, action_type="play_card",
            board_x=0, board_y=0, hand_index=idx,
        )

    def _best_move_action(self, gs: "GameState") -> Optional[GameAction]:
        """Two-step move: first tick selects the unit, second tick commits the dest."""
        movers = ai_query.units_with_pending_move(gs, self.player_name)
        if not movers:
            return None

        # If something is already mouse_selected, the next move_to commits the actual move.
        selected = [m for m in movers if m.mouse_selected]
        if selected:
            unit = selected[0]
            dests = ai_query.move_destinations_for(gs, unit)
            if not dests:
                return None
            best_dest = max(dests, key=lambda d: ai_evaluator.score_move_destination(unit, d, gs))
            return GameAction(
                player=self.player_name, action_type="move_to",
                board_x=best_dest[0], board_y=best_dest[1],
            )

        # Nothing selected yet — pick the best mover (one with the highest-scoring dest)
        # and emit move_to on its own cell to select it.
        def best_dest_score(unit) -> float:
            dests = ai_query.move_destinations_for(gs, unit)
            if not dests:
                return float("-inf")
            return max(ai_evaluator.score_move_destination(unit, d, gs) for d in dests)

        unit = max(movers, key=best_dest_score)
        if best_dest_score(unit) == float("-inf"):
            return None
        return GameAction(
            player=self.player_name, action_type="move_to",
            board_x=unit.board_x, board_y=unit.board_y,
        )
