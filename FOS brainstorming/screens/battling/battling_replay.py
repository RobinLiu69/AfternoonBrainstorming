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

from pathlib import Path
from typing import Optional

import pygame

from shared.setting import WHITE, RED, VERSION
from core.game_state import GameState
from core.game_statistics import GameStatistics
from core.game_screen import GameScreen, draw_text, to_board_x, to_board_y
from core.player import Player
from core.neutral import Neutral
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.battling_dispatcher import BattlingDispatcher
from core.match_settings import TIME_CONTROL_OPTIONS
from core.replay_source import ReplaySource, ReplayClock
from rendering.game_renderer import GameRenderer
from screens.battling.battling_action import collect_actions
from screens.notices import notice_screen
from utils.logger import GameLogger
from campaign.boss_config import (
    apply_initial_buffs, apply_stage_one_shots, maintain_unit_buffs, apply_per_turn_buffs,
)


MIN_SPEED: float = 0.125
MAX_SPEED: float = 8.0
_ACTION_HOLD: float = 0.4  # minimum seconds to linger after each action (at 1x speed)
_MAX_SETTLE_TICKS: int = 64


class _CampaignReplayBuffs:
    def __init__(self, stage: str) -> None:
        self.stage = stage
        self._buffed_ids: set[str] = set()
        self._last_turn_seen: int = -1
        self._initialized: bool = False

    def reset(self) -> None:
        self._buffed_ids = set()
        self._last_turn_seen = -1
        self._initialized = False

    def _ensure_initialized(self, gs: GameState) -> None:
        if self._initialized:
            return
        p2 = gs.player2
        if not (p2.hand or p2.draw_pile or p2.discard_pile):
            return
        apply_stage_one_shots(self.stage, gs)
        apply_initial_buffs(self.stage, gs)
        self._initialized = True

    def tick(self, gs: GameState) -> None:
        self._ensure_initialized(gs)
        maintain_unit_buffs(self.stage, gs, self._buffed_ids)
        current = "player1" if gs.turn_number % 2 == 0 else "player2"
        if current != "player2":
            self._last_turn_seen = -1
            return
        if self._last_turn_seen != gs.turn_number:
            self._last_turn_seen = gs.turn_number
            apply_per_turn_buffs(self.stage, gs)


def _build_replay_game_state(source: ReplaySource) -> GameState:
    meta = source.metadata

    player1 = Player(
        name="player1",
        deck=list(meta.get("player1_deck", [])),
        hand=[],
        on_board=[],
        draw_pile=[],
        discard_pile=[],
    )
    player2 = Player(
        name="player2",
        deck=list(meta.get("player2_deck", [])),
        hand=[],
        on_board=[],
        draw_pile=[],
        discard_pile=[],
    )
    neutral = Neutral()

    silent_logger = GameLogger(
        enable_file=False,
        enable_console=False,
        enable_jsonl=False,
    )

    kwargs: dict = {"game_logger": silent_logger}
    if "rng_seed" in meta:
        kwargs["rng_seed"] = meta["rng_seed"]

    game_state = GameState(player1, player2, neutral, BoardConfig(), **kwargs)

    if "timer_mode" in meta:
        game_state.timer_mode = meta["timer_mode"]

    time_control = meta.get("time_control", "")
    if "countdown_seconds" in meta:
        game_state.countdown_time = int(meta["countdown_seconds"])
        game_state.turn_increment_seconds = int(meta.get("increment_seconds", 0))
    elif time_control in TIME_CONTROL_OPTIONS:
        countdown, increment = TIME_CONTROL_OPTIONS[time_control]
        game_state.countdown_time = countdown
        game_state.turn_increment_seconds = increment

    game_state.game_logger = GameLogger(
        enable_file=False,
        enable_console=False,
        enable_jsonl=False,
    )

    return game_state


def _initialize_players(game_state: GameState) -> None:
    game_state.player1.initialize(game_state)
    game_state.player2.initialize(game_state)
    game_state.player1.timer_start(game_state)
    game_state.player2.timer_start(game_state)


def _rebuild_and_fast_forward(
    source: ReplaySource,
    game_state: GameState,
    game_screen: GameScreen,
    game_renderer: GameRenderer,
    dispatcher: BattlingDispatcher,
    target_action_index: int,
    buffs: "Optional[_CampaignReplayBuffs]" = None,
    replay_clock: Optional[ReplayClock] = None,
) -> None:
    import random as _py_random
    from cards.base import reset_instance_counter

    reset_instance_counter()

    meta = source.metadata

    game_state.player1.deck = list(meta.get("player1_deck", []))
    game_state.player1.hand = []
    game_state.player1.on_board = []
    game_state.player1.draw_pile = []
    game_state.player1.discard_pile = []

    game_state.player2.deck = list(meta.get("player2_deck", []))
    game_state.player2.hand = []
    game_state.player2.on_board = []
    game_state.player2.draw_pile = []
    game_state.player2.discard_pile = []

    game_state.neutral.on_board = []


    game_state.number_of_attacks = {"player1": 0, "player2": 0}
    game_state.number_of_attacks = {"player1": 0, "player2": 0}
    game_state.number_of_attacks = {"player1": 0, "player2": 0}
    game_state.number_of_attacks = {"player1": 0, "player2": 0}
    game_state.number_of_attacks = {"player1": 0, "player2": 0}

    game_state.players_luck = {"player1": 50, "player2": 50, "neutral": 50}
    game_state.players_token = {"player1": 0, "player2": 0, "neutral": 0}
    game_state.players_totem = {"player1": 0, "player2": 0, "neutral": 0}
    game_state.players_coin = {"player1": 0, "player2": 0}
    game_state.card_to_draw = {"player1": 0, "player2": 0}
    game_state.skip_turn_draw = {"player1": False, "player2": False}

    game_state.number_of_attacks = {"player1": 0, "player2": 0}
    game_state.number_of_movings = {"player1": 0, "player2": 0}
    game_state.number_of_cubes = {"player1": 0, "player2": 0}
    game_state.number_of_heals = {"player1": 0, "player2": 0}

    game_state.game_statistics =  GameStatistics()

    game_state.score = 0
    game_state.turn_number = 0

    game_state.rng = _py_random.Random(game_state.rng_seed)

    game_state.board_dict = initialize_board(game_screen, game_state.board_config)
    _initialize_players(game_state)

    if replay_clock is not None:
        replay_clock.reset()
    else:
        game_state.player1.time_display = "--:--"
        game_state.player2.time_display = "--:--"
        game_state.player1.start_time = -1
        game_state.player2.start_time = -1

    import shared.setting as _core_setting
    prev_anim_setting = _core_setting.COMBAT_ANIMATIONS_ENABLED
    prev_anim_runtime = game_renderer.combat_animator.enabled
    _core_setting.COMBAT_ANIMATIONS_ENABLED = False
    game_renderer.combat_animator.enabled = False

    if buffs is not None:
        buffs.reset()

    try:
        source.reset()
        for _ in range(target_action_index):
            if buffs is not None:
                buffs.tick(game_state)
            action_index = source.current_action_index
            action = source.next_action()
            if action is None:
                break
            if replay_clock is not None:
                replay_clock.before_action(action_index)
            dispatcher._execute(action, game_state)
            for _ in range(_MAX_SETTLE_TICKS):
                game_state.player1.logic_update(game_state, game_renderer, False)
                game_state.player2.logic_update(game_state, game_renderer, False)
                game_state.neutral.update(game_state, game_renderer)
                game_state.update()
                if (game_state.card_to_draw["player1"] <= 0
                        and game_state.card_to_draw["player2"] <= 0):
                    break
        if buffs is not None:
            buffs.tick(game_state)
    finally:
        _core_setting.COMBAT_ANIMATIONS_ENABLED = prev_anim_setting
        game_renderer.combat_animator.enabled = prev_anim_runtime

    game_state.pending_combat_events.clear()
    for card in game_renderer.dying_cards:
        game_renderer.card_renderer.release(card.instance_id)
    game_renderer.dying_cards.clear()

    game_state._attack_anim_cursor = 0.0

    _skip_toggle_hints(source)


def _draw_hud(game_screen: GameScreen, source: ReplaySource, paused: bool, speed: float, save_log: bool) -> None:
    x = game_screen.block_size * 0.3
    y_top = game_screen.block_size * 0.2
    y_bottom = game_screen.display_height - game_screen.block_size * 0.2

    status = "PAUSED" if paused else "PLAYING"
    header = (
        f"REPLAY [{status}]  speed={speed:g}x  "
        f"{source.current_action_index}/{source.total_actions}  "
        f"log={'ON' if save_log else 'OFF'}"
    )
    draw_text(header, game_screen.mid_text_font, WHITE, x, y_top, game_screen.surface)

    replay_version = source.metadata.get("version")
    if replay_version is not None and replay_version != VERSION:
        warning = f"WARNING: Replay version {replay_version} != current {VERSION}, results may differ"
        draw_text(warning, game_screen.mid_text_font, RED, x + game_screen.block_size * 1.8, y_top - game_screen.block_size * 0.15, game_screen.surface)


    hint = "SPACE pause/play   LEFT prev   RIGHT next   UP/DOWN speed   R restart   T take over   V anim   L save-log   ESC exit"
    draw_text(hint, game_screen.mid_text_font, WHITE, x, y_bottom, game_screen.surface)


def _draw_takeover_hud(game_screen: GameScreen, controller: str) -> None:
    x = game_screen.block_size * 0.3
    y_top = game_screen.block_size * 0.2
    y_bottom = game_screen.display_height - game_screen.block_size * 0.2
    draw_text(f"TAKEOVER (live)  -  controlling {controller}",
              game_screen.mid_text_font, WHITE, x, y_top, game_screen.surface)
    hint = "A attack   M move   H heal   E end turn   1-9 play   R back to replay   ESC end (save on win)"
    draw_text(hint, game_screen.mid_text_font, WHITE, x, y_bottom, game_screen.surface)


def _collect_prefix_actions(source: ReplaySource, count: int) -> list:
    saved = source.current_action_index
    source.reset()
    actions = []
    for _ in range(count):
        action = source.next_action()
        if action is None:
            break
        actions.append(action)
    source.seek_to_action(saved)
    return actions


def _collect_action_types(source: ReplaySource) -> list[str]:
    saved = source.current_action_index
    source.reset()
    types: list[str] = []
    action = source.next_action()
    while action is not None:
        types.append(action.action_type)
        action = source.next_action()
    source.seek_to_action(saved)
    return types


def _skip_toggle_hints(source: ReplaySource) -> None:
    next = source.peek_action()
    while next is not None and next.action_type == "toggle_hint":
        source.next_action()
        next = source.peek_action()


def _prev_real_action_index(action_types: list[str], cursor: int) -> int:
    for j in range(min(cursor, len(action_types)) - 1, -1, -1):
        if action_types[j] != "toggle_hint":
            return j
    return 0


def _begin_takeover(source: ReplaySource, game_state: GameState) -> GameLogger:
    meta = source.metadata
    logger = GameLogger(enable_file=True, enable_console=False, enable_jsonl=True)
    logger.info(f"player1 deck {'-'.join(meta.get('player1_deck', []))}")
    logger.info(f"player2 deck {'-'.join(meta.get('player2_deck', []))}")
    logger.info(f"timer mode {meta.get('timer_mode', game_state.timer_mode)}")
    if meta.get("time_control"):
        logger.info(f"time control {meta['time_control']}",
                    countdown_seconds=game_state.countdown_time,
                    increment_seconds=game_state.turn_increment_seconds)
    if meta.get("campaign_stage"):
        logger.info(f"campaign stage {meta['campaign_stage']}")
    logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)
    logger.info(f"version {VERSION}", version=VERSION)
    for action in _collect_prefix_actions(source, source.current_action_index):
        logger.log_action(action, action.player)
    game_state.game_logger = logger
    game_state.player1.start_time = -1
    game_state.player2.start_time = -1
    return logger


def _export_replay_log(
    source: ReplaySource,
    game_state: GameState,
    game_screen: GameScreen,
    game_renderer: GameRenderer,
    dispatcher: BattlingDispatcher,
    buffs: "Optional[_CampaignReplayBuffs]",
    replay_clock: Optional[ReplayClock] = None,
) -> Optional[Path]:
    meta = source.metadata
    logger = GameLogger(enable_file=True, enable_console=False, enable_jsonl=False)
    logger.info(f"player1 deck {'-'.join(meta.get('player1_deck', []))}")
    logger.info(f"player2 deck {'-'.join(meta.get('player2_deck', []))}")
    logger.info(f"timer mode {meta.get('timer_mode', game_state.timer_mode)}")
    if meta.get("time_control"):
        logger.info(f"time control {meta['time_control']}",
                    countdown_seconds=game_state.countdown_time,
                    increment_seconds=game_state.turn_increment_seconds)
    if meta.get("campaign_stage"):
        logger.info(f"campaign stage {meta['campaign_stage']}")
    logger.info(f"rng_seed {game_state.rng_seed}", rng_seed=game_state.rng_seed)
    logger.info(f"version {meta.get('version', VERSION)}", version=meta.get('version', VERSION))

    prev_logger = game_state.game_logger
    game_state.game_logger = logger
    try:
        _rebuild_and_fast_forward(
            source, game_state, game_screen,
            game_renderer, dispatcher, source.total_actions, buffs, replay_clock,
        )
        recorded_version = meta.get("version")
        if recorded_version is not None and recorded_version != VERSION:
            logger.warning(
                f"replay recorded on version {recorded_version}, re-simulated on {VERSION}; "
                f"results may diverge from the original match"
            )
        if game_state.score <= -10:
            winner = "player1"
        elif game_state.score >= 10:
            winner = "player2"
        else:
            winner = f"undetermined (re-sim ended at score {game_state.score}, never reached +/-10)"
        logger.info(f"winner {winner}")
        logger.info(f"player1 timer {game_state.player1.time_display}")
        logger.info(f"player2 timer {game_state.player2.time_display}")
        logger.info(f"{game_state.game_statistics.export_for_charts()}")
        logger.info(f"{game_state.game_statistics.score_history}")
    finally:
        log_path = logger.log_file
        logger.detach()
        game_state.game_logger = prev_logger
    return log_path


def _discard_logger(logger: GameLogger) -> None:
    logger.close()
    for path in (logger.log_file, logger._jsonl_path):
        try:
            if path is not None and path.exists():
                path.unlink()
        except OSError:
            pass


def main(game_screen: GameScreen, replay_path: Path) -> Optional[GameState]:
    from cards.base import reset_instance_counter
    reset_instance_counter()

    try:
        source = ReplaySource(replay_path)
    except FileNotFoundError as e:
        print(f"[Replay] {e}")
        notice_screen.main(game_screen, "Replay Unavailable", "file not found")
        return None

    if source.total_actions == 0:
        print(f"[Replay] {replay_path.name} contains no actions — nothing to replay")
        notice_screen.main(game_screen, "Empty Replay", "this recording has no actions to play")
        return None

    game_state = _build_replay_game_state(source)
    game_state.board_config = BoardConfig()
    game_state.board_dict = initialize_board(game_screen, game_state.board_config)

    campaign_stage = source.metadata.get("campaign_stage")
    buffs = _CampaignReplayBuffs(campaign_stage) if campaign_stage else None

    action_types = _collect_action_types(source)

    game_renderer = GameRenderer(game_screen)
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")
    dispatcher.attach_renderer(game_renderer)

    _initialize_players(game_state)

    replay_clock = ReplayClock(source, game_state)
    replay_clock.reset()

    _skip_toggle_hints(source)

    paused: bool = True
    speed: float = 1.0
    step_once: bool = False
    action_hold_remaining: float = 0.0
    hint_on: bool = False
    save_log: bool = False
    controller: str = "player1"

    taken_over: bool = False
    takeover_logger: Optional[GameLogger] = None
    winner: str = "None"
    picked_hand_card: list = ["None", 0]

    clock = pygame.time.Clock()
    running: bool = True

    while running:
        dt = clock.tick(60) / 1000.0
        game_screen.render()

        if not taken_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_RIGHT:
                        step_once = True
                        paused = True
                    elif event.key == pygame.K_LEFT:
                        target = _prev_real_action_index(action_types, source.current_action_index)
                        _rebuild_and_fast_forward(
                            source, game_state, game_screen,
                            game_renderer, dispatcher, target, buffs, replay_clock,
                        )
                        paused = True
                    elif event.key == pygame.K_UP:
                        speed = min(speed * 2.0, MAX_SPEED)
                    elif event.key == pygame.K_DOWN:
                        speed = max(speed / 2.0, MIN_SPEED)
                    elif event.key == pygame.K_r:
                        _rebuild_and_fast_forward(
                            source, game_state, game_screen,
                            game_renderer, dispatcher, 0, buffs, replay_clock,
                        )
                        paused = True
                    elif event.key == pygame.K_t:
                        takeover_logger = _begin_takeover(source, game_state)
                        taken_over = True
                        paused = False
                        controller = "player1" if (game_state.turn_number % 2 == 0) else "player2"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_f:
                        hint_on = not hint_on
                    elif event.key == pygame.K_l:
                        save_log = not save_log
                    elif event.key == pygame.K_v:
                        import shared.setting as _core_setting
                        new_val = not game_renderer.combat_animator.enabled
                        game_renderer.combat_animator.enabled = new_val
                        _core_setting.COMBAT_ANIMATIONS_ENABLED = new_val
        else:
            events = pygame.event.get()
            if any(e.type == pygame.KEYDOWN and e.key == pygame.K_r for e in events):
                if takeover_logger is not None:
                    _discard_logger(takeover_logger)
                    takeover_logger = None
                game_state.game_logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
                taken_over = False
                winner = "None"
                controller = "player1"
                picked_hand_card = ["None", 0]
                _rebuild_and_fast_forward(
                    source, game_state, game_screen,
                    game_renderer, dispatcher, 0, buffs, replay_clock,
                )
                paused = True
            else:
                for action in collect_actions(controller, picked_hand_card, game_state, game_screen, events):
                    result = dispatcher.dispatch(action, game_state)
                    if action.action_type == "toggle_hint":
                        hint_on = not hint_on
                        continue
                    if action.action_type == "toggle_animation":
                        import shared.setting as _core_setting
                        new_val = not game_renderer.combat_animator.enabled
                        game_renderer.combat_animator.enabled = new_val
                        _core_setting.COMBAT_ANIMATIONS_ENABLED = new_val
                        continue
                    if result.end_turn:
                        controller = "player2" if controller == "player1" else "player1"
                    if result.quit:
                        if result.message:
                            winner = result.message
                        running = False

        if buffs is not None:
            buffs.tick(game_state)

        if not taken_over:
            action_hold_remaining = max(0.0, action_hold_remaining - dt * speed)

            should_advance: bool = False
            if step_once:
                should_advance = True
                step_once = False
            elif not paused and not source.exhausted:
                if not game_renderer.combat_animator.is_animating() and action_hold_remaining <= 0.0:
                    should_advance = True

            if should_advance and not source.exhausted:
                action_index = source.current_action_index
                action = source.next_action()
                while action is not None and action.action_type == "toggle_hint":
                    action_index = source.current_action_index
                    action = source.next_action()
                if action is not None:
                    replay_clock.before_action(action_index)
                    dispatcher._execute(action, game_state)
                    replay_clock.after_action()
                    controller = "player1" if (game_state.turn_number % 2 == 0) else "player2"
                    action_hold_remaining = _ACTION_HOLD
                    _skip_toggle_hints(source)
                else:
                    paused = True

        if taken_over:
            game_state.get_player(controller).logic_update(game_state, game_renderer, True)
            game_state.get_opponent(controller).logic_update(game_state, game_renderer, False)
            game_state.neutral.update(game_state, game_renderer)
            game_state.update()
            if game_state.player1.time_out:
                winner = "player2"
                running = False
            if game_state.player2.time_out:
                winner = "player1"
                running = False
        else:
            game_state.player1.logic_update(game_state, game_renderer, False)
            game_state.player2.logic_update(game_state, game_renderer, False)
            game_state.neutral.update(game_state, game_renderer)
            game_state.update()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        render_dt = dt if taken_over else dt * speed
        game_renderer.render_frame(controller, controller, mouse_x, mouse_y, to_board_x(mouse_x, game_screen), to_board_y(mouse_y, game_screen), game_state, hint_on, render_dt)
        if taken_over:
            _draw_takeover_hud(game_screen, controller)
        else:
            _draw_hud(game_screen, source, paused, speed, save_log)

        pygame.display.update()

    if taken_over:
        if winner not in ("None", ""):
            return game_state
        if takeover_logger is not None:
            _discard_logger(takeover_logger)
        return None

    reached_end = source.next_action() is None
    if save_log:
        _export_replay_log(source, game_state, game_screen, game_renderer, dispatcher, buffs, replay_clock)
    return game_state if reached_end else None