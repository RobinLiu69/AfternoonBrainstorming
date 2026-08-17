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

"""The relic page, and the promise that nothing on it overlaps."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from cards.factory import CardFactory
from core.game_screen import GameScreen

from tower import relic_screen, run_state, ui_common
from tower.content import RELICS

FACTIONS = ["R", "B", "C", "BR"]


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


@pytest.fixture
def escape(monkeypatch):
    def _install(module):
        monkeypatch.setattr(module, "key_pressed", lambda keys: pygame.K_ESCAPE)
        monkeypatch.setattr(pygame.event, "get",
                            lambda: [pygame.event.Event(pygame.KEYDOWN)])
    return _install


def run_with(relic_ids) -> dict:
    run = run_state.new_run(FACTIONS, seed=3)
    run["relics"] = list(relic_ids)
    return run


def blocks_of(game_screen, relic_ids):
    return relic_screen._Layout(game_screen, list(relic_ids))


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------

def test_no_two_relics_share_space(game_screen):
    """Every block must sit clear of the others in its column."""
    layout = blocks_of(game_screen, sorted(RELICS))
    for page in layout.pages:
        for column_x in layout.column_x:
            column = sorted((b for b in page if b.x == column_x), key=lambda b: b.y)
            for earlier, later in zip(column, column[1:]):
                height = (layout.name_step
                          + layout.line_step * len(earlier.lines))
                assert earlier.y + height <= later.y


def test_nothing_runs_off_the_bottom_or_into_the_footer(game_screen):
    layout = blocks_of(game_screen, sorted(RELICS))
    for page in layout.pages:
        for block in page:
            bottom = (block.y + layout.name_step
                      + layout.line_step * len(block.lines))
            assert block.y >= layout.top
            assert bottom <= layout.bottom + layout.block_gap


def test_no_line_is_wider_than_its_column(game_screen):
    layout = blocks_of(game_screen, sorted(RELICS))
    for page in layout.pages:
        for block in page:
            for line in block.lines:
                assert layout.text_font.size(line)[0] <= layout.column_width


def test_columns_stay_inside_the_screen(game_screen):
    layout = blocks_of(game_screen, sorted(RELICS))
    assert layout.column_x[0] >= 0
    right_edge = layout.column_x[-1] + layout.column_width
    assert right_edge <= game_screen.display_width


def test_columns_do_not_overlap_each_other(game_screen):
    layout = blocks_of(game_screen, sorted(RELICS))
    for left, right in zip(layout.column_x, layout.column_x[1:]):
        assert left + layout.column_width <= right


def test_every_relic_lands_on_exactly_one_page(game_screen):
    everything = sorted(RELICS)
    layout = blocks_of(game_screen, everything)
    placed = [b.relic_id for page in layout.pages for b in page]
    assert sorted(placed) == everything
    assert len(placed) == len(set(placed))


def test_a_small_collection_needs_only_one_page(game_screen):
    layout = blocks_of(game_screen, ["piggy_bank", "courier", "worn_pack"])
    assert layout.page_count() == 1


def test_the_whole_catalogue_spills_onto_more_pages(game_screen):
    assert blocks_of(game_screen, sorted(RELICS)).page_count() > 1


def test_an_empty_collection_still_has_a_page(game_screen):
    layout = blocks_of(game_screen, [])
    assert layout.page_count() == 1
    assert layout.pages == [[]]


def test_relics_are_grouped_by_tier(game_screen):
    ids = ["worn_pack", "limit_break", "piggy_bank", "sewing_kit", "prepared_pack"]
    layout = blocks_of(game_screen, ids)
    order = [b.relic_id for page in layout.pages for b in page]
    assert order.index("limit_break") < order.index("sewing_kit")
    assert order.index("sewing_kit") < order.index("prepared_pack")
    assert order.index("prepared_pack") < order.index("piggy_bank")
    assert order[-1] == "worn_pack"


def test_each_block_says_what_the_relic_does(game_screen):
    from tower import language

    language.use(language.ENGLISH)
    try:
        block = blocks_of(game_screen, ["piggy_bank"]).pages[0][0]
        assert "Piggy Bank" in block.heading
        assert "common" in block.heading
        assert block.lines
        assert "gold" in " ".join(block.lines)
    finally:
        language.use(None)


def test_a_block_speaks_chinese_when_the_setting_says_so(game_screen):
    from tower import language

    language.use(language.CHINESE)
    try:
        block = blocks_of(game_screen, ["piggy_bank"]).pages[0][0]
        assert "小豬撲滿" in block.heading
        assert "普通" in block.heading
        assert "25%" in " ".join(block.lines)
    finally:
        language.use(None)


# --------------------------------------------------------------------------
# wrapping helper
# --------------------------------------------------------------------------

def test_measured_wrapping_never_exceeds_the_width(game_screen):
    font = game_screen.text_font
    text = "shields from overhealing are doubled and then some more words follow"
    for width in (120, 240, 480):
        for line in ui_common.wrap_to_width(text, font, width):
            assert font.size(line)[0] <= width or " " not in line


def test_measured_wrapping_keeps_every_word(game_screen):
    text = "gain 2 coins at the start of your turn"
    lines = ui_common.wrap_to_width(text, game_screen.text_font, 150)
    assert " ".join(lines).split() == text.split()
    assert ui_common.wrap_to_width("", game_screen.text_font, 150) == []


# --------------------------------------------------------------------------
# the screen itself
# --------------------------------------------------------------------------

def test_the_screen_renders_with_relics(game_screen, escape):
    escape(relic_screen)
    relic_screen.main(game_screen, run_with(["piggy_bank", "courier", "worn_pack"]))


def test_the_screen_renders_with_none(game_screen, escape):
    escape(relic_screen)
    relic_screen.main(game_screen, run_with([]))


def test_the_screen_renders_a_hoard(game_screen, escape):
    escape(relic_screen)
    relic_screen.main(game_screen, run_with(sorted(RELICS)))
