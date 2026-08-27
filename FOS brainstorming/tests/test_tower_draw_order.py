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

import inspect
import unittest

from tower import (battle_prep, card_picker, choice_screen, map_screen,
                   notice_screen, roster_screen, shop_screen)

OVERLAY = "draw_relic_strip"
RUN_BAR = "draw_run_bar"


class TestTheRelicOverlayIsDrawnLast(unittest.TestCase):
    def _assert_last(self, module):
        source = inspect.getsource(module.render)
        self.assertIn(OVERLAY, source, module.__name__)
        tail = source[source.index(OVERLAY):]
        self.assertNotIn(".update(game_screen)", tail, module.__name__)
        self.assertNotIn("draw_text(", tail, module.__name__)

    def test_every_screen_that_shows_relics_draws_them_over_its_content(self):
        for module in (map_screen, shop_screen, card_picker, choice_screen,
                       notice_screen, roster_screen, battle_prep):
            self._assert_last(module)


class TestTheRunBarIsDrawnFirst(unittest.TestCase):
    def test_the_run_bar_comes_before_the_screen_content(self):
        for module in (map_screen, shop_screen, card_picker, roster_screen,
                       battle_prep):
            source = inspect.getsource(module.render)
            self.assertLess(source.index(RUN_BAR), source.index(OVERLAY),
                            module.__name__)


if __name__ == "__main__":
    unittest.main()
