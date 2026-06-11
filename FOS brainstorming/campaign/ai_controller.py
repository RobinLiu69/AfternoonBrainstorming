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

LETHAL_SCORE_THRESHOLD: float = float(CAMPAIGN_SETTINGS["thresholds"]["lethal_score_threshold"])

_PANIC = CAMPAIGN_SETTINGS["panic"]
MIN_PANIC_THRESHOLD: float = float(_PANIC["min_panic_threshold"])
_PANIC_NO_DROP_BELOW: int = int(_PANIC["deficit_no_drop_below"])
_PANIC_DROP_PER_STEP: float = float(_PANIC["deficit_drop_per_step"])

_HEAL = CAMPAIGN_SETTINGS["heal"]
HEAL_AMOUNT: int = int(_HEAL["amount"])
HEAL_MIN_AMOUNT: int = int(_HEAL["min_amount"])
HEAL_MIN_SCORE: float = float(_HEAL["min_score"])
_HEAL_LOW_RATIO: float = float(_HEAL["low_ratio_threshold"])
_HEAL_LOW_RATIO_BONUS: float = float(_HEAL["low_ratio_bonus"])
_HEAL_SAVE_BASE: float = float(_HEAL["save_from_lethal_base"])
_HEAL_SAVE_DMG_MULT: float = float(_HEAL["save_from_lethal_damage_mult"])
_HEAL_INCOME_MULT: float = float(_HEAL["score_income_mult"])
_HEAL_DAMAGE_MULT: float = float(_HEAL["damage_mult"])


class AIController:

    def __init__(self, stage: str, player_name: str = "player2"):
        strategy_cls = STRATEGY_REGISTRY.get(stage)
        if strategy_cls is None:
            raise ValueError(f"No strategy registered for stage {stage!r}")
        self.stage: str = stage
        self.strategy: Strategy = strategy_cls()
        overrides = CAMPAIGN_SETTINGS.get("faction_overrides", {}).get(stage, {})
        for key, val in overrides.items():
            if hasattr(self.strategy, key):
                setattr(self.strategy, key, val)
        self.player_name: str = player_name
        self._next_release_ms: int = 0
        self._last_turn_seen: int = -1
        self._initialized: bool = False
        self._buffed_unit_ids: set[str] = set()
        self.focus_position: tuple[int, int] | None = None

    def tick(self, gs: "GameState", now_ms: int, renderer_busy: bool = False) -> list[GameAction]:
        self._ensure_initialized(gs)
        maintain_unit_buffs(self.stage, gs, self._buffed_unit_ids)

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

        if gs.pending_combat_events or gs.pending_attacks or renderer_busy:
            self._next_release_ms = now_ms + AI_BUSY_RECHECK_MS
            return []

        action = self._decide_next(gs)
        if action is None:
            self.focus_position = None
            return []

        if (
            action.action_type in ("play_card", "attack")
            and action.board_x is not None
            and action.board_y is not None
        ):
            self.focus_position = (action.board_x, action.board_y)
        else:
            self.focus_position = None

        delay = AI_ATTACK_DELAY_MS if action.action_type == "attack" else AI_ACTION_DELAY_MS
        self._next_release_ms = now_ms + delay
        return [action]

    def _ensure_initialized(self, gs: "GameState") -> None:
        if self._initialized:
            return
        if not gs.board_dict:
            return
        player2 = gs.player2
        if not (player2.hand or player2.draw_pile or player2.discard_pile):
            return
        apply_stage_one_shots(self.stage, gs)
        apply_initial_buffs(self.stage, gs)
        self._initialized = True

    def _effective_attack_min(self, gs: "GameState") -> float:
        base = float(self.strategy.attack_min_score)
        deficit = -gs.score if self.player_name == "player2" else gs.score
        if deficit <= _PANIC_NO_DROP_BELOW:
            return base
        return max(MIN_PANIC_THRESHOLD, base - (deficit - _PANIC_NO_DROP_BELOW) * _PANIC_DROP_PER_STEP)

    def _decide_next(self, gs: "GameState") -> Optional[GameAction]:
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

        if attack is not None and attack.score >= LETHAL_SCORE_THRESHOLD and attack_action is not None:
            return attack_action

        heal_action = self._best_heal(gs)
        if heal_action is not None:
            return heal_action

        if play_action is not None:
            return play_action

        if attack_action is not None:
            return attack_action

        return GameAction(player=self.player_name, action_type="end_turn")

    def _best_heal(self, gs: "GameState") -> Optional[GameAction]:
        if gs.number_of_heals.get(self.player_name, 0) <= 0:
            return None

        best_score = HEAL_MIN_SCORE
        best_target = None
        for c in gs.get_player(self.player_name).on_board:
            if c.health <= 0:
                continue
            deficit = c.max_health - c.health
            heal_amount = min(HEAL_AMOUNT, deficit)
            if heal_amount < HEAL_MIN_AMOUNT:
                continue

            score = heal_amount * 2.0
            score += ai_evaluator.estimate_score_per_turn(c.job_and_color) * _HEAL_INCOME_MULT
            score += c.damage * _HEAL_DAMAGE_MULT

            ratio = c.health / max(1, c.max_health)
            if ratio < _HEAL_LOW_RATIO:
                score += _HEAL_LOW_RATIO_BONUS

            incoming = ai_query.incoming_damage_at_position(
                gs, self.player_name, c.board_x, c.board_y
            )
            if incoming >= c.health and incoming < c.health + heal_amount:
                score += _HEAL_SAVE_BASE + c.damage * _HEAL_SAVE_DMG_MULT

            if score > best_score:
                best_score = score
                best_target = c

        if best_target is None:
            return None
        return GameAction(
            player=self.player_name, action_type="heal",
            board_x=best_target.board_x, board_y=best_target.board_y,
        )

    def _start_unit_move(self, gs: "GameState") -> Optional[GameAction]:
        if gs.number_of_movings.get(self.player_name, 0) <= 0:
            return None
        on_board = gs.get_player(self.player_name).on_board
        if any(c.moving for c in on_board):
            return None

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
            return None

        return GameAction(
            player=self.player_name, action_type="move_to",
            board_x=best_unit.board_x, board_y=best_unit.board_y,
        )

    def _play_moveo(self, gs: "GameState") -> Optional[GameAction]:
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
        movers = ai_query.units_with_pending_move(gs, self.player_name)
        if not movers:
            return None

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
