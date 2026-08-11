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

"""Deterministic headless game driver used to record behaviour goldens.

The point of this module is to pin down *observable* behaviour of the card
system before it is rewritten. It plays a scripted game with a fixed seed and
records a normalised snapshot of the full game state after every action, so any
change in ability resolution shows up as a golden diff.
"""

from __future__ import annotations

import random
from typing import Any, Iterable

from core.battling_dispatcher import BattlingDispatcher
from core.board_block import Board
from core.board_config import BoardConfig
from core.game_action import GameAction
from core.game_state import GameState
from core.neutral import Neutral
from core.player import Player
from cards.base import reset_instance_counter
from cards.factory import CardFactory
from shared.setting import JOB_DICTIONARY, JOB_ORDER
from utils.logger import GameLogger


COLOR_CODES: dict[str, str] = {
    name: tag for tag, name in JOB_DICTIONARY["colors_dict"].items()
}

# Wall-clock / renderer-owned fields carry no ability semantics and would make
# goldens unstable, so they are dropped before comparison.
_VOLATILE_PLAYER_KEYS = ("start_time", "elapsed_time", "time_out", "time_display")


class _DyingCardSink:
    """Stand-in for GameRenderer in headless runs."""

    def __init__(self) -> None:
        self.dying_cards: list[Any] = []


def deck_for_color(color_name: str, magic: Iterable[str] = ("MOVE", "HEAL", "CUBES")) -> list[str]:
    """A legal 12-card deck: the three magic cards plus units of one colour.

    Mirrors the deck rules in Player.add_card_to_deck (max 12 total, max 2 per
    unit card). The magic cards are placed first so they survive the size cap —
    without them the driver never exercises move/heal/cube resolution.
    """
    CardFactory.register_all()
    code = COLOR_CODES[color_name]
    units = [job + code for job in JOB_ORDER if job + code in CardFactory._registry]
    deck: list[str] = list(magic)
    for copy in range(2):
        for name in units:
            if len(deck) >= 12:
                return deck
            deck.append(name)
    return deck


def _free_cells(game_state: GameState) -> list[tuple[int, int]]:
    return [pos for pos, board in game_state.board_dict.items() if not board.occupy]


def _own_cards(game_state: GameState, seat: str) -> list[Any]:
    return list(game_state.get_player_cards(seat))


def make_game_state(seed: int, deck1: list[str], deck2: list[str]) -> GameState:
    logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
    p1 = Player(name="player1", deck=list(deck1), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    p2 = Player(name="player2", deck=list(deck2), hand=[], on_board=[], draw_pile=[], discard_pile=[])
    config = BoardConfig()
    board_dict = {
        (x, y): Board(width=100, height=100, occupy=False, color=(255, 255, 255), board_x=x, board_y=y)
        for y in range(config.height)
        for x in range(config.width)
    }
    game_state = GameState(
        p1, p2, Neutral(), config,
        board_dict=board_dict,
        game_logger=logger,
        rng_seed=seed,
    )
    p1.initialize(game_state)
    p2.initialize(game_state)
    return game_state


def _settle_loop(game_state: GameState, sink: _DyingCardSink) -> None:
    """Mirror the per-frame maintenance order used by screens/battling."""
    game_state.player1.logic_update(game_state, sink, False)
    game_state.player2.logic_update(game_state, sink, False)
    game_state.neutral.update(game_state, sink)
    game_state.update()


def _card_view(card: Any) -> dict:
    """Observable state of one card.

    Deliberately *not* card.to_dict(): the serialisation format is an
    implementation detail that the rewrite is free to change, whereas these are
    the values the rules, the UI and the AI actually respond to. Keeping the
    projection stable is what lets the goldens survive a rewrite and still mean
    something.
    """
    render = card.get_render_data()
    return {
        "name": card.job_and_color,
        "owner": card.owner,
        "pos": [card.board_x, card.board_y],
        "hp": card.health,
        "max_hp": card.max_health,
        "atk": card.damage,
        "extra_atk": card.extra_damage,
        "base_atk": card.original_damage,
        "armor": card.armor,
        "numb": card.numbness,
        "moving": card.moving,
        "anger": card.anger,
        "nullify": card.nullify,
        "dying": card.pending_death,
        "pattern": card.attack_types,
        # Extra render entries are companion sprites (Fuchsia shadows).
        "companions": [[r.board_x, r.board_y] for r in render[1:]],
    }


def _snapshot(game_state: GameState, label: str) -> dict:
    board = (
        list(game_state.player1.on_board)
        + list(game_state.player2.on_board)
        + list(game_state.neutral.on_board)
    )
    view = {
        "_label": label,
        "score": game_state.score,
        "turn": game_state.turn_number,
        "luck": dict(game_state.players_luck),
        "token": dict(game_state.players_token),
        "totem": dict(game_state.players_totem),
        "coin": dict(game_state.players_coin),
        "attacks": dict(game_state.number_of_attacks),
        "moves": dict(game_state.number_of_movings),
        "cubes": dict(game_state.number_of_cubes),
        "heals": dict(game_state.number_of_heals),
        "to_draw": dict(game_state.card_to_draw),
        "skip_draw": dict(game_state.skip_turn_draw),
        # Lists, not tuples: these round-trip through JSON and must compare equal
        # to what comes back out of the golden file.
        "occupied": [list(pos) for pos in sorted(
            pos for pos, b in game_state.board_dict.items() if b.occupy
        )],
        "hands": {
            seat: list(game_state.get_player(seat).hand) for seat in ("player1", "player2")
        },
        "piles": {
            seat: {
                "draw": list(game_state.get_player(seat).draw_pile),
                "discard": list(game_state.get_player(seat).discard_pile),
            }
            for seat in ("player1", "player2")
        },
        "board": [_card_view(c) for c in board],
        "events": [
            {"kind": e.kind, "at": [e.board_x, e.board_y], "dmg": e.damage,
             "post_hp": e.post_health, "to": [e.target_x, e.target_y]}
            for e in game_state.pending_combat_events
        ],
    }
    # Combat events are drained by the renderer in a real run; drain them here so
    # each snapshot records only the events produced by the action just taken.
    game_state.pending_combat_events.clear()
    return view


def play_game(seed: int, deck1: list[str], deck2: list[str], turns: int = 16) -> list[dict]:
    """Play a scripted game and return one normalised snapshot per action.

    The action policy is intentionally dumb but exhaustive: it plays cards,
    spends every movement/heal/cube charge, and attacks with every unit that
    can attack. It is seeded separately from the game RNG so game-side
    randomness stays attributable.
    """
    reset_instance_counter()
    CardFactory.register_all()

    game_state = make_game_state(seed, deck1, deck2)
    dispatcher = BattlingDispatcher(game_state, mode="local")
    sink = _DyingCardSink()
    policy = random.Random(seed ^ 0x5EED)

    snapshots: list[dict] = [_snapshot(game_state, "initial")]

    def act(action_type: str, seat: str, **kwargs) -> None:
        result = dispatcher.dispatch(
            GameAction(player=seat, action_type=action_type, **kwargs), game_state
        )
        _settle_loop(game_state, sink)
        snapshots.append(_snapshot(game_state, f"{action_type}:{seat}:{result.success}"))

    for _ in range(turns):
        seat = "player1" if game_state.turn_number % 2 == 0 else "player2"
        player = game_state.get_player(seat)

        # --- play up to two cards from hand -------------------------------
        for _ in range(2):
            if not player.hand:
                break
            cells = _free_cells(game_state)
            if not cells:
                break
            index = policy.randrange(len(player.hand))
            x, y = cells[policy.randrange(len(cells))]
            act("play_card", seat, hand_index=index, board_x=x, board_y=y)

        # --- spend cube charges -------------------------------------------
        while game_state.number_of_cubes[seat] > 0:
            cells = _free_cells(game_state)
            if not cells:
                break
            x, y = cells[policy.randrange(len(cells))]
            act("spawn_cube", seat, board_x=x, board_y=y)

        # --- spend heal charges -------------------------------------------
        while game_state.number_of_heals[seat] > 0:
            own = _own_cards(game_state, seat)
            if not own:
                break
            target = own[policy.randrange(len(own))]
            act("heal", seat, board_x=target.board_x, board_y=target.board_y)

        def move_phase() -> None:
            """Move anything that can move.

            Two sources of movement: a spent MOVE/MOVEO charge, or a card that
            was already armed by its own ability (Orange attacks set moving).
            Both funnel through the same arm/select/place protocol in
            Player.move_card.
            """
            for _ in range(6):
                own = _own_cards(game_state, seat)
                armed = [c for c in own if c.moving]
                if armed:
                    mover = armed[0]
                elif game_state.number_of_movings[seat] > 0:
                    ready_to_arm = [c for c in own if not c.numbness]
                    if not ready_to_arm:
                        return
                    mover = ready_to_arm[policy.randrange(len(ready_to_arm))]
                    act("move_to", seat, board_x=mover.board_x, board_y=mover.board_y)
                    if not mover.moving:
                        return
                else:
                    return
                adjacent = [
                    (x, y) for (x, y) in _free_cells(game_state)
                    if abs(x - mover.board_x) <= 1 and abs(y - mover.board_y) <= 1
                ]
                if not adjacent:
                    return
                act("move_to", seat, board_x=mover.board_x, board_y=mover.board_y)
                x, y = adjacent[policy.randrange(len(adjacent))]
                act("move_to", seat, board_x=x, board_y=y)

        move_phase()

        # --- attack with everything that can ------------------------------
        guard = 0
        while game_state.number_of_attacks[seat] > 0 and guard < 12:
            guard += 1
            ready = [c for c in _own_cards(game_state, seat) if not c.numbness and c.health > 0]
            if not ready:
                break
            attacker = ready[policy.randrange(len(ready))]
            before = game_state.number_of_attacks[seat]
            act("attack", seat, board_x=attacker.board_x, board_y=attacker.board_y)
            if game_state.number_of_attacks[seat] == before:
                break  # nothing landed; stop burning iterations

        # Abilities that grant movement on attack (Orange) arm their card here.
        move_phase()

        act("end_turn", seat)
        if abs(game_state.score) >= game_state.win_threshold:
            break

    return snapshots
