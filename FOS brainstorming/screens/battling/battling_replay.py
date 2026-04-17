# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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
from pathlib import Path
from typing import Optional

import pygame

from core.setting import WHITE, RED, VERSION
from core.game_state import GameState
from core.game_screen import GameScreen, draw_text, to_board_x, to_board_y
from core.player import Player
from core.neutral import Neutral
from core.board_config import BoardConfig
from core.board_block import initialize_board
from core.battling_dispatcher import BattlingDispatcher
from core.replay_source import ReplaySource
from rendering.game_renderer import GameRenderer
from utils.logger import GameLogger


FRAMES_PER_ACTION: int = 30
MIN_SPEED: float = 0.125
MAX_SPEED: float = 8.0


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

    game_state.game_logger = GameLogger(
        enable_file=False,
        enable_console=False,
        enable_jsonl=False,
    )

    return game_state


def _initialize_players(game_state: GameState, game_screen: GameScreen) -> None:
    game_state.player1.initialize(game_state, game_screen)
    game_state.player2.initialize(game_state, game_screen)
    game_state.player1.initialize_display(game_state, game_screen)
    game_state.player2.initialize_display(game_state, game_screen)


def _rebuild_and_fast_forward(
    source: ReplaySource,
    game_state: GameState,
    game_screen: GameScreen,
    game_renderer: GameRenderer,
    dispatcher: BattlingDispatcher,
    target_action_index: int,
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
    
    game_state.number_of_attacks = {"player1": 0, "player2": 0}
    game_state.number_of_movings = {"player1": 0, "player2": 0}
    game_state.number_of_cudes = {"player1": 0, "player2": 0}
    game_state.number_of_heals = {"player1": 0, "player2": 0}

    game_state.score = 0
    game_state.turn_number = 0

    game_state.rng = _py_random.Random(game_state.rng_seed)

    game_state.board_dict = initialize_board(game_screen, game_state.board_config)
    _initialize_players(game_state, game_screen)

    game_state.player1.time_minutes_and_seconds = "--:--"
    game_state.player2.time_minutes_and_seconds = "--:--"
    game_state.player1.start_time = -1
    game_state.player2.start_time = -1

    import core.setting as _core_setting
    prev_anim_setting = _core_setting.COMBAT_ANIMATIONS_ENABLED
    prev_anim_runtime = game_renderer.combat_animator.enabled
    _core_setting.COMBAT_ANIMATIONS_ENABLED = False
    game_renderer.combat_animator.enabled = False

    try:
        source.reset()
        for _ in range(target_action_index):
            action = source.next_action()
            if action is None:
                break
            dispatcher._execute(action, game_state)
            game_state.player1.logic_update(game_state, game_renderer, False)
            game_state.player2.logic_update(game_state, game_renderer, False)
            game_state.neutral.update(game_state, game_renderer)
            game_state.update()
    finally:
        _core_setting.COMBAT_ANIMATIONS_ENABLED = prev_anim_setting
        game_renderer.combat_animator.enabled = prev_anim_runtime

    game_state.pending_combat_events.clear()
    for card in game_renderer.dying_cards:
        game_renderer.card_renderer.release(card.instance_id)
    game_renderer.dying_cards.clear()

    game_state._attack_anim_cursor = 0.0


def _draw_hud(game_screen: GameScreen, source: ReplaySource, paused: bool, speed: float) -> None:
    x = game_screen.block_size * 0.3
    y_top = game_screen.block_size * 0.2
    y_bottom = game_screen.display_height - game_screen.block_size * 0.2

    status = "PAUSED" if paused else "PLAYING"
    header = (
        f"REPLAY [{status}]  speed={speed:g}x  "
        f"{source.current_action_index}/{source.total_actions}"
    )
    draw_text(header, game_screen.mid_text_font, WHITE, x, y_top, game_screen.surface)

    replay_version = source.metadata.get("version")
    if replay_version is not None and replay_version != VERSION:
        warning = f"WARNING: Replay version {replay_version} != current {VERSION}, results may differ"
        draw_text(warning, game_screen.mid_text_font, RED, x + game_screen.block_size * 1.8, y_top - game_screen.block_size * 0.15, game_screen.surface)
    

    hint = "SPACE pause/play   RIGHT step   UP/DOWN speed   R restart   V toggle anim   ESC exit"
    draw_text(hint, game_screen.mid_text_font, WHITE, x, y_bottom, game_screen.surface)


def main(game_screen: GameScreen, replay_path: Path) -> str:
    from cards.base import reset_instance_counter
    reset_instance_counter()

    try:
        source = ReplaySource(replay_path)
    except FileNotFoundError as e:
        print(f"[Replay] {e}")
        return "end"

    if source.total_actions == 0:
        print(f"[Replay] {replay_path.name} contains no actions — nothing to replay")
        return "end"

    game_state = _build_replay_game_state(source)
    game_state.board_config = BoardConfig()
    game_state.board_dict = initialize_board(game_screen, game_state.board_config)

    game_renderer = GameRenderer(game_screen)
    dispatcher = BattlingDispatcher(game_state=game_state, mode="local")
    dispatcher.attach_renderer(game_renderer)

    _initialize_players(game_state, game_screen)

    game_state.player1.time_minutes_and_seconds = "--:--"
    game_state.player2.time_minutes_and_seconds = "--:--"
    game_state.player1.start_time = -1
    game_state.player2.start_time = -1

    paused: bool = True
    speed: float = 1.0
    frame_accumulator: float = 0.0
    step_once: bool = False
    hint_on: bool = False
    controller: str = "player1"

    clock = pygame.time.Clock()
    running: bool = True

    while running:
        dt = clock.tick(60) / 1000.0
        game_screen.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_RIGHT:
                    step_once = True
                    paused = True
                elif event.key == pygame.K_UP:
                    speed = min(speed * 2.0, MAX_SPEED)
                elif event.key == pygame.K_DOWN:
                    speed = max(speed / 2.0, MIN_SPEED)
                elif event.key == pygame.K_r:
                    _rebuild_and_fast_forward(
                        source, game_state, game_screen,
                        game_renderer, dispatcher, 0,
                    )
                    paused = True
                    frame_accumulator = 0.0
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    hint_on = not hint_on
                elif event.key == pygame.K_v:
                    import core.setting as _core_setting
                    new_val = not game_renderer.combat_animator.enabled
                    game_renderer.combat_animator.enabled = new_val
                    _core_setting.COMBAT_ANIMATIONS_ENABLED = new_val

        should_advance: bool = False
        if step_once:
            should_advance = True
            step_once = False
        elif not paused and not source.exhausted:
            frame_accumulator += speed
            if frame_accumulator >= FRAMES_PER_ACTION:
                frame_accumulator = 0.0
                should_advance = True

        if should_advance and not source.exhausted:
            action = source.next_action()
            if action is not None:
                dispatcher._execute(action, game_state)
                controller = "player1" if (game_state.turn_number % 2 == 0) else "player2"
            else:
                paused = True

        game_state.player1.logic_update(game_state, game_renderer, False)
        game_state.player2.logic_update(game_state, game_renderer, False)
        game_state.neutral.update(game_state, game_renderer)
        game_state.update()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        game_renderer.render_frame(controller, controller, mouse_x, mouse_y, to_board_x(mouse_x, game_screen), to_board_y(mouse_y, game_screen), game_state, hint_on, dt)
        _draw_hud(game_screen, source, paused, speed)

        pygame.display.update()

    return "end"