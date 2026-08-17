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

import re
from pathlib import Path

from cards.card_white import Tank as WhiteTank
from shared.combat_event import CombatEvent
from tests.helpers import make_game_state, place_card


class _Animator:
    def __init__(self) -> None:
        self.played: list[CombatEvent] = []

    def push(self, event: CombatEvent) -> None:
        self.played.append(event)


class _Renderer:
    def __init__(self) -> None:
        self.combat_animator = _Animator()


def _client() -> tuple:
    client = make_game_state()
    renderer = _Renderer()
    return client, renderer


def _wound(game_state, card, amount: int = 1) -> None:
    card.adjust_stats(game_state, health=-amount)


class TestEverySourceStampsASequence:
    def test_emitting_hands_out_rising_numbers(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.drain_combat_events()

        _wound(gs, card)
        _wound(gs, card)

        seqs = [event.seq for event in gs.pending_combat_events]
        assert seqs == sorted(seqs)
        assert len(set(seqs)) == len(seqs)

    def test_draining_does_not_rewind_the_counter(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)

        _wound(gs, card)
        highest = max(event.seq for event in gs.pending_combat_events)
        gs.drain_combat_events()
        _wound(gs, card)

        assert min(event.seq for event in gs.pending_combat_events) > highest

    def test_nothing_appends_to_the_queue_behind_emit(self) -> None:
        pattern = re.compile(r"pending_combat_events\s*\.\s*(append|extend|insert)")
        root = Path(__file__).resolve().parent.parent
        offenders: list[str] = []
        for glob in ("cards/*.py", "core/*.py", "tower/*.py", "rendering/*.py",
                     "campaign/*.py", "screens/battling/*.py"):
            for path in sorted(root.glob(glob)):
                if path.name == "game_state.py":
                    continue
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if pattern.search(line):
                        offenders.append(f"{path.name}:{number}: {line.strip()}")

        assert offenders == []


class TestAClientNeverPlaysTheSameEventTwice:
    def test_the_same_payload_arriving_twice_only_plays_once(self) -> None:
        host = make_game_state()
        card = place_card(host, WhiteTank, "player1", 1, 1)
        host.drain_combat_events()
        client, renderer = _client()
        client.apply_dict(host.to_dict_for("player2"), renderer)

        _wound(host, card)
        payload = host.to_dict_for("player2")

        client.apply_dict(payload, renderer)
        first = len(renderer.combat_animator.played)
        client.apply_dict(payload, renderer)

        assert first > 0
        assert len(renderer.combat_animator.played) == first

    def test_a_later_payload_still_plays_its_new_events(self) -> None:
        host = make_game_state()
        card = place_card(host, WhiteTank, "player1", 1, 1)
        host.drain_combat_events()
        client, renderer = _client()
        client.apply_dict(host.to_dict_for("player2"), renderer)

        _wound(host, card)
        client.apply_dict(host.to_dict_for("player2"), renderer)
        before = len(renderer.combat_animator.played)

        _wound(host, card)
        client.apply_dict(host.to_dict_for("player2"), renderer)

        assert len(renderer.combat_animator.played) > before

    def test_a_joining_client_does_not_replay_the_backlog(self) -> None:
        host = make_game_state()
        card = place_card(host, WhiteTank, "player1", 1, 1)
        _wound(host, card)
        _wound(host, card)
        assert host.pending_combat_events

        client, renderer = _client()
        client.apply_dict(host.to_dict_for("player2"), renderer)

        assert renderer.combat_animator.played == []

    def test_a_joining_client_still_sees_what_happens_next(self) -> None:
        host = make_game_state()
        card = place_card(host, WhiteTank, "player1", 1, 1)
        _wound(host, card)

        client, renderer = _client()
        client.apply_dict(host.to_dict_for("player2"), renderer)
        host.drain_combat_events()

        _wound(host, card)
        client.apply_dict(host.to_dict_for("player2"), renderer)

        assert renderer.combat_animator.played

    def test_a_packet_without_sequence_numbers_still_plays(self) -> None:
        client, renderer = _client()
        client._combat_primed = True
        legacy = CombatEvent(kind="hurt", board_x=1, board_y=1, post_health=3).to_dict()
        legacy.pop("seq")

        client._play_incoming_events([legacy, legacy], renderer)

        assert len(renderer.combat_animator.played) == 2
