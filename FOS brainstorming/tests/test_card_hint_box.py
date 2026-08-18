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

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from cards.factory import CardFactory
from core.card_hint import (HintBox, get_job_and_color, get_job_and_color_name,
                            get_job_shape, get_stat_prefix)
from core.game_screen import GameScreen
from shared.card_code import BARROW_CODE, WIGHT_CODE
from shared.setting import CARDS_HINTS_DICTIONARY, JOB_DICTIONARY


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


def test_a_lucky_block_reads_as_a_green_unit_not_a_nameless_one():
    green = tuple(JOB_DICTIONARY["RGB_colors"]["Green"])

    assert get_job_and_color("LUCKYBLOCK") == ("LUCKYBLOCK", green)
    assert get_job_and_color_name("LUCKYBLOCK") == ("LUCKYBLOCK", "Green")


def test_a_lucky_block_carries_stats_and_a_shape():
    assert get_stat_prefix("LUCKYBLOCK") == "1/0"
    assert len(get_job_shape("LUCKYBLOCK", 100)) == 4


def test_the_lucky_block_hint_spells_out_both_tables():
    text = CARDS_HINTS_DICTIONARY["LUCKYBLOCK"]

    for effect in ("+4護盾", "攻擊x2", "立即攻擊", "可移動", "生成方塊",
                   "護盾歸零", "麻痺", "血量減半", "攻擊減半", "-2血"):
        assert effect in text

    assert len(text.split("\n")) == 4


def test_every_board_unit_hint_renders(game_screen):
    box = HintBox(width=int(game_screen.block_size * 6), height=int(game_screen.block_size * 2))
    box.turn_on = True

    for code in ("LUCKYBLOCK", WIGHT_CODE, "ADCGY", "TANKW"):
        box.display(CardFactory.create(code, "player1", 1, 1), game_screen)
        box.display(code, game_screen)


def test_the_hand_only_codes_still_render_as_plain_text(game_screen):
    box = HintBox(width=int(game_screen.block_size * 6), height=int(game_screen.block_size * 2))
    box.turn_on = True

    for code in (BARROW_CODE, "CUBES", "HEAL", "MOVE"):
        box.display(code, game_screen)


def measure(box: HintBox, card, game_screen) -> tuple[float, float]:
    captured: list[tuple[float, float]] = []
    original = HintBox._place

    def spy(self, box_width, box_height, screen):
        captured.append((box_width, box_height))
        original(self, box_width, box_height, screen)

    HintBox._place = spy
    try:
        box.display(card, game_screen)
    finally:
        HintBox._place = original
    return captured[0]


def test_no_hint_is_ever_wider_or_taller_than_the_surface_it_draws_on(game_screen):
    clipped: list[str] = []
    try:
        for mode in ("60", "80", "100"):
            game_screen.apply_display_mode(mode)
            box = HintBox(width=int(game_screen.block_size * 3), height=int(game_screen.block_size))
            box.turn_on = True
            for code in CARDS_HINTS_DICTIONARY:
                box_width, box_height = measure(box, code, game_screen)
                assert box.surface is not None
                if box.surface.get_width() < box_width or box.surface.get_height() < box_height:
                    clipped.append(f"{mode} {code}: {box_width}x{box_height} on {box.surface.get_size()}")
    finally:
        game_screen.apply_display_mode("60")

    assert clipped == []


def test_a_hint_at_the_far_corner_slides_back_into_the_window(game_screen):
    box = HintBox(width=int(game_screen.block_size * 3), height=int(game_screen.block_size))
    box.turn_on = True
    box.x = game_screen.display_width - 4
    box.y = game_screen.display_height - 4

    box_width, box_height = measure(box, "LUCKYBLOCK", game_screen)
    x, y = box.anchor(box_width, box_height, game_screen)

    assert x + box_width <= game_screen.display_width
    assert y + box_height <= game_screen.display_height


def test_a_hint_opens_beside_the_cursor_rather_than_under_it(game_screen):
    box = HintBox(width=int(game_screen.block_size * 3), height=int(game_screen.block_size))
    box.turn_on = True
    box.x, box.y = 5, 7

    box_width, box_height = measure(box, "LUCKYBLOCK", game_screen)
    x, y = box.anchor(box_width, box_height, game_screen)

    assert x > 5 and y > 7
    assert x - 5 <= game_screen.block_size * 0.5
    assert y - 7 <= game_screen.block_size * 0.5


def test_a_hint_near_the_right_edge_opens_to_the_left_of_the_cursor(game_screen):
    box = HintBox(width=int(game_screen.block_size * 3), height=int(game_screen.block_size))
    box.turn_on = True
    box.x, box.y = game_screen.display_width - 20, 40

    box_width, box_height = measure(box, "LUCKYBLOCK", game_screen)
    x, _y = box.anchor(box_width, box_height, game_screen)

    assert x + box_width <= box.x


def test_a_hint_box_hugs_the_lines_it_actually_has(game_screen):
    box = HintBox(width=int(game_screen.block_size * 3), height=int(game_screen.block_size))
    box.turn_on = True

    short = measure(box, "CUBES", game_screen)[1]
    tall = measure(box, "TANKG", game_screen)[1]

    assert short < tall


def test_the_lucky_block_icon_fills_its_frame_like_a_real_unit():
    block = get_job_shape("LUCKYBLOCK", 100)
    tank = get_job_shape("TANK", 100)

    def span(points):
        xs = [x for x, _ in points]
        return max(xs) - min(xs)

    assert span(block) >= span(tank) * 0.8
