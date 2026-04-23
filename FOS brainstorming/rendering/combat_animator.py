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
# MERCHANTABILITY or FITNESS FOR active PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received active copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from core.combat_event import CombatEvent

if TYPE_CHECKING:
    from core.game_screen import GameScreen


_LUNGE_DURATION = 0.32   # seconds for attacker lunge
_HURT_DURATION = 0.38   # seconds for red flash + shake
_FLOAT_DURATION = 0.70   # seconds for floating damage number
_DEATH_DURATION = 0.10  # seconds before death

_LUNGE_DIST_FRAC = 0.33   # fraction of block_size to lunge toward target
_SHAKE_PX = 4      # max pixel amplitude of hurt shake
_TINT_MAX_ALPHA = 170    # 0-255 — peak red overlay alpha
_FLOAT_RISE_PX = 28     # total pixels damage number rises before fading
_MOVE_DURATION = 0.28     # seconds for unit slide from old to new tile

def _sin_ease(t: float) -> float:
    return math.sin(t * math.pi)


@dataclass
class _Anim:
    event: CombatEvent
    elapsed: float
    duration: float

    @property
    def progress(self) -> float:
        return min(max(self.elapsed / self.duration, 0.0), 1.0)

    @property
    def started(self) -> bool:
        return self.elapsed >= 0.0


_DURATIONS: dict[str, float] = {
    "attack": _LUNGE_DURATION,
    "hurt":   _HURT_DURATION,
    "float":  _FLOAT_DURATION,
    "move":   _MOVE_DURATION,
    "death":  _DEATH_DURATION,
}


class CombatAnimator:
    def __init__(self, game_screen: GameScreen, enabled: bool = True) -> None:
        self._game_screen    = game_screen
        self._active: list[_Anim] = []
        self._enabled = enabled
        self._pending_display_health: list[CombatEvent] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        if not value:
            self._active.clear()

    def get_active_positions(self) -> set[tuple[int, int]]:
        positions = set()
        for active in self._active:
            if active.event.kind == "move":
                continue
            positions.add((active.event.board_x, active.event.board_y))
            if active.event.kind == "attack":
                positions.add((active.event.target_x, active.event.target_y))
        return positions

    def push(self, event: CombatEvent) -> None:
        if not self._enabled:
            if event.kind == "hurt" and event.post_health >= 0:
                self._pending_display_health.append(event)
            return

        if event.kind == "move":
            self._active = [
                active for active in self._active
                if not (active.event.kind == "move"
                        and active.event.board_x == event.board_x
                        and active.event.board_y == event.board_y)
            ]

        duration = _DURATIONS.get(event.kind, 0.35)
        self._active.append(_Anim(event=event, elapsed=-event.delay, duration=duration))

    def drain_skipped_display_updates(self) -> list[CombatEvent]:
        out = self._pending_display_health
        self._pending_display_health = []
        return out

    def update(self, dt: float) -> list[_Anim]:
        for active in self._active:
            active.elapsed += dt
        completed = [active for active in self._active if active.elapsed >= active.duration and active.started]
        self._active = [active for active in self._active if active.elapsed < active.duration]
        return completed

    def is_animating(self) -> bool:
        return bool(self._active)
    
    def get_offset(self, board_x: int, board_y: int) -> tuple[float, float]:
        if not self._enabled:
            return 0.0, 0.0

        dx = dy = 0.0

        best_lunge_mag = 0.0
        best_lunge_nx = 0.0
        best_lunge_ny = 0.0

        for active in self._active:
            if not active.started:
                continue
            event = active.event

            if event.kind == "attack" and event.board_x == board_x and event.board_y == board_y:
                raw_dx = event.target_x - event.board_x
                raw_dy = event.target_y - event.board_y
                length = math.hypot(raw_dx, raw_dy) or 1.0
                nx, ny = raw_dx / length, raw_dy / length
                magnitude = _sin_ease(active.progress) * _LUNGE_DIST_FRAC * self._game_screen.block_size
                if magnitude > best_lunge_mag:
                    best_lunge_mag = magnitude
                    best_lunge_nx  = nx
                    best_lunge_ny  = ny

            elif event.kind == "hurt" and event.board_x == board_x and event.board_y == board_y:
                amp = (1.0 - active.progress) * _SHAKE_PX
                dx += random.uniform(-amp, amp)
                dy += random.uniform(-amp, amp)
            
            elif event.kind == "move" and event.board_x == board_x and event.board_y == board_y:
                remaining = 1.0 - active.progress
                dx += (event.target_x - event.board_x) * self._game_screen.block_size * remaining
                dy += (event.target_y - event.board_y) * self._game_screen.block_size * remaining

        dx += best_lunge_nx * best_lunge_mag
        dy += best_lunge_ny * best_lunge_mag

        return dx, dy

    def render_overlays(self, surface: pygame.Surface) -> None:
        if not self._enabled:
            return

        game_screen = self._game_screen

        for active in self._active:
            if not active.started:
                continue
            event = active.event

            if event.kind == "hurt":
                alpha = int(_TINT_MAX_ALPHA * (1.0 - active.progress))
                if alpha > 0:
                    x, y = self._to_screen(event.board_x, event.board_y)
                    bs = int(game_screen.block_size)
                    tint = pygame.Surface((bs, bs), pygame.SRCALPHA)
                    tint.fill((255, 0, 0, alpha))
                    surface.blit(tint, (int(x), int(y)))

            elif event.kind == "float" and event.damage > 0:
                t = active.progress
                if t < 0.2:
                    alpha = int(255 * (t/0.2))
                else:
                    alpha = int(255 * (1.0 - (t - 0.2) / 0.8))
                alpha = max(0, min(255, alpha))

                x, y = self._to_screen(event.board_x, event.board_y)
                rise = t * _FLOAT_RISE_PX
                cx = x + game_screen.block_size*0.5
                cy = y + game_screen.block_size*0.15 - rise

                text_surf = game_screen.text_font.render(f"-{event.damage}", True, (255, 70, 70))
                text_surf.set_alpha(alpha)
                tw, th = text_surf.get_size()
                surface.blit(text_surf, (int(cx - tw/2), int(cy - th/2)))

    def _to_screen(self, board_x: int, board_y: int) -> tuple[float, float]:
        game_screen = self._game_screen
        x = (game_screen.display_width/2 - game_screen.block_size*2) + board_x*game_screen.block_size
        y = (game_screen.display_height/2 - game_screen.block_size*1.65) + board_y*game_screen.block_size
        return x, y