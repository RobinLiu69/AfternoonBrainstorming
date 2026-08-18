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
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from campaign import deck_builder
from rendering.game_renderer import GameRenderer
from screens.lobby import ban_draft


def _order(source: str, marks: dict[str, str]) -> dict[str, int]:
    return {name: source.index(needle) for name, needle in marks.items()}


class TestTooltipsSitAboveChromeAndBelowModals:
    def test_the_battle_frame_draws_the_hint_after_the_net_overlays(self) -> None:
        source = inspect.getsource(GameRenderer.render_frame)
        at = _order(source, {
            "netinfo": "render_netinfo_overlay",
            "hint": "self._render_hint(",
            "pause": "_render_pause_overlay",
        })

        assert at["netinfo"] < at["hint"] < at["pause"]

    def test_the_ban_draft_draws_the_hint_after_its_panels(self) -> None:
        source = inspect.getsource(ban_draft.main)
        at = _order(source, {
            "panel": "_grid_panel(game_screen",
            "header": "_render_header(game_screen",
            "hint": "_render_hint(game_screen",
            "confirm": "_render_leave_confirm(game_screen",
        })

        assert at["panel"] < at["header"] < at["hint"] < at["confirm"]

    def test_the_deck_builder_draws_the_hint_after_its_help_panel(self) -> None:
        source = inspect.getsource(deck_builder.main)
        at = _order(source, {
            "frame": "renderer.render_frame(",
            "help": "_draw_help(game_screen",
            "hint": "renderer._render_hint(",
        })

        assert at["frame"] < at["help"] < at["hint"]

    def test_the_deck_builder_does_not_let_the_frame_draw_the_hint_early(self) -> None:
        source = inspect.getsource(deck_builder.main)

        assert "render_frame(page, 0, bx, by, draft_state, hint_on=False)" in source
