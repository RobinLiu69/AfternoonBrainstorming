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


def test_text_floats_at_the_same_tile_are_staggered():
    animator = CombatAnimator(None, enabled=True)
    animator.push(CombatEvent(kind="float", board_x=1, board_y=1, text="+4 ARMOR", good=True, delay=0.15))
    animator.push(CombatEvent(kind="float", board_x=1, board_y=1, text="FREE MOVE", good=True, delay=0.15))
    animator.push(CombatEvent(kind="float", board_x=1, board_y=1, text="HP HALVED", delay=0.15))

    delays = [round(-anim.elapsed, 3) for anim in animator._active]
    assert delays == sorted(delays)
    assert len(set(delays)) == 3


def test_a_damage_number_never_waits_on_a_text_float():
    animator = CombatAnimator(None, enabled=True)
    animator.push(CombatEvent(kind="float", board_x=1, board_y=1, text="NUMBED", delay=0.15))
    animator.push(CombatEvent(kind="float", board_x=1, board_y=1, damage=7))

    assert round(-animator._active[-1].elapsed, 3) == 0.0


def test_text_floats_at_other_tiles_keep_their_delay():
    animator = CombatAnimator(None, enabled=True)
    animator.push(CombatEvent(kind="float", board_x=1, board_y=1, text="NUMBED", delay=0.4))
    animator.push(CombatEvent(kind="float", board_x=2, board_y=2, text="ATK x2", good=True, delay=0.0))

    assert round(-animator._active[-1].elapsed, 3) == 0.0


def test_a_float_label_survives_the_wire():
    event = CombatEvent(kind="float", board_x=1, board_y=2, text="SPAWN BLOCKS", good=True)
    restored = CombatEvent.from_dict(event.to_dict())

    assert (restored.text, restored.good) == ("SPAWN BLOCKS", True)


def test_an_old_float_payload_still_loads():
    restored = CombatEvent.from_dict({"kind": "float", "board_x": 0, "board_y": 0, "damage": 3})

    assert restored.text == "" and restored.good is False


def test_a_fortune_label_lingers_longer_than_a_damage_number():
    animator = CombatAnimator(None, enabled=True)
    animator.push(CombatEvent(kind="float", board_x=0, board_y=0, damage=4))
    animator.push(CombatEvent(kind="float", board_x=3, board_y=3, text="ATK x2", good=True))

    damage, label = animator._active
    assert label.duration > damage.duration * 1.5


def test_a_fortune_label_holds_full_opacity_before_it_fades():
    from rendering.combat_animator import _hold_fade_alpha

    assert _hold_fade_alpha(0.0) == 0
    assert _hold_fade_alpha(0.3) == 255
    assert _hold_fade_alpha(0.6) == 255
    assert _hold_fade_alpha(1.0) == 0
    assert 0 < _hold_fade_alpha(0.85) < 255
