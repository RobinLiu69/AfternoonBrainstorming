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

from typing import TypeVar, overload

from core.game_state import GameState
from core.player import Player
from core.neutral import Neutral
from core.board_config import BoardConfig
from core.board_block import Board
from cards.factory import CardFactory
from cards.base import Card
from utils.logger import GameLogger

_CardType = TypeVar("_CardType", bound=Card)

CardFactory.register_all()


def make_game_state(rng_seed: int = 42) -> GameState:
    logger = GameLogger(enable_file=False, enable_console=False, enable_jsonl=False)
    p1 = Player(name="player1", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    p2 = Player(name="player2", deck=[], hand=[], on_board=[], draw_pile=[], discard_pile=[])
    neutral = Neutral()
    config = BoardConfig()
    board_dict: dict[tuple[int, int], Board] = {
        (x, y): Board(width=100, height=100, occupy=False, color=(255, 255, 255), board_x=x, board_y=y)
        for y in range(config.height)
        for x in range(config.width)
    }
    return GameState(
        p1, p2, neutral, config,
        board_dict=board_dict,
        game_logger=logger,
        rng_seed=rng_seed,
    )


@overload
def place_card(game_state: GameState, card_name: type[_CardType], owner: str, x: int, y: int) -> _CardType: ...
@overload
def place_card(game_state: GameState, card_name: str, owner: str, x: int, y: int) -> Card: ...
def place_card(game_state: GameState, card_name, owner: str, x: int, y: int) -> Card:
    card = CardFactory.create(card_name, owner, x, y)
    game_state.get_player(owner).on_board.append(card)
    game_state.board_dict[(x, y)].occupy = True
    return card


def do_attack(attacker: Card, game_state: GameState) -> bool:
    result = attacker.launch_attack(attacker.attack_types, game_state, ignore_numbness=True)
    attacker.hit_cards.clear()
    return result
