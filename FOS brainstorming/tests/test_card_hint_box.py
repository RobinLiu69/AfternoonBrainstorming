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


def test_the_lucky_block_icon_fills_its_frame_like_a_real_unit():
    block = get_job_shape("LUCKYBLOCK", 100)
    tank = get_job_shape("TANK", 100)

    def span(points):
        xs = [x for x, _ in points]
        return max(xs) - min(xs)

    assert span(block) >= span(tank) * 0.8
