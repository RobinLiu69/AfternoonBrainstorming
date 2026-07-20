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

from rendering.combat_animator import CombatAnimator
from shared.combat_event import CombatEvent


def _drain_hurt_order(animator: CombatAnimator) -> list[int]:
    applied = []
    for _ in range(600):
        for anim in animator.update(1 / 60):
            if anim.event.kind == "hurt":
                applied.append(anim.event.post_health)
        if not animator.is_animating():
            break
    return applied


def test_hurt_events_at_same_position_complete_in_push_order():
    animator = CombatAnimator(None, enabled=True)
    animator.push(CombatEvent(kind="hurt", board_x=1, board_y=0, delay=0.176, post_health=6))
    animator.push(CombatEvent(kind="hurt", board_x=1, board_y=0, delay=0.0, post_health=3))

    assert _drain_hurt_order(animator) == [6, 3]


def test_hurt_events_at_other_positions_keep_their_delay():
    animator = CombatAnimator(None, enabled=True)
    animator.push(CombatEvent(kind="hurt", board_x=1, board_y=0, delay=0.5, post_health=6))
    early = CombatEvent(kind="hurt", board_x=2, board_y=2, delay=0.0, post_health=3)
    animator.push(early)

    assert early.delay == 0.0
    assert _drain_hurt_order(animator) == [3, 6]
