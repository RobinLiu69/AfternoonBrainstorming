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
from core.game_screen import GameScreen
from core.lobby_state import LobbyState
from core.match_prelude import (log_player_names, log_ban_draft, log_judge_bans,
                                resolve_ban_draft, judge_bans_of)
from core.replay_source import ReplaySource
from core.draft_state import tournament_ban_list
from screens import replay_prelude
from utils.logger import GameLogger


P1_DECK = ["ADCW", "APW", "TANKW", "HFW"]
P2_DECK = ["ADCB", "APB", "TANKB", "HFB"]


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


def _write_replay(tmp_path, with_names=True, tournament=False):
    from core.match_settings import MatchSettings
    from tests.helpers import make_game_state

    logger = GameLogger(log_file=tmp_path / "m.log", enable_console=False)

    state = LobbyState()
    if with_names:
        state.player_names = {"host": "Robin", "peer": "Angus"}
    state.settings = MatchSettings(ruleset="tournament" if tournament else "free play")
    state.bans = {"TANKG": "host", "APG": "host", "SPB": "peer"}
    ban_deck = (tournament_ban_list() if tournament else []) + list(state.bans)

    game_state = make_game_state()
    game_state.game_logger = logger
    state.settings.apply_to(game_state)

    ban_draft = resolve_ban_draft(state)
    log_player_names(logger, state)
    logger.info(f"player1 deck {'-'.join(P1_DECK)}")
    logger.info(f"player2 deck {'-'.join(P2_DECK)}")
    log_ban_draft(logger, ban_draft)
    log_judge_bans(logger, judge_bans_of(ban_deck, ban_draft))
    logger.info("rng_seed 42", rng_seed=42)
    logger.close()

    return ReplaySource(tmp_path / "m.jsonl").metadata


def test_metadata_extracts_names_bans_and_decks(tmp_path):
    metadata = _write_replay(tmp_path)

    assert metadata["player1_name"] == "Robin"
    assert metadata["player2_name"] == "Angus"
    assert metadata["player1_deck"] == P1_DECK
    assert metadata["player2_deck"] == P2_DECK
    assert metadata["bans"] == {"Robin": ["TANKG", "APG"], "Angus": ["SPB"]}
    assert "judge" not in metadata["bans"]


def test_metadata_includes_judge_bans_for_tournament(tmp_path):
    metadata = _write_replay(tmp_path, tournament=True)

    assert metadata["bans"]["judge"] == tournament_ban_list()
    assert [banner for banner, _ in replay_prelude._player_bans(metadata)] == ["Robin", "Angus"]


def test_metadata_carries_every_setting(tmp_path):
    from core.match_settings import MatchSettings

    metadata = _write_replay(tmp_path, tournament=True)
    settings = metadata["settings"]

    for name in MatchSettings().to_dict():
        assert name in settings
    assert settings["ruleset"] == "tournament"

    line = replay_prelude._settings_line(metadata)
    for name in MatchSettings().to_dict():
        if name in replay_prelude.UNLISTED_SETTINGS:
            assert name.replace("_", " ") not in line
        else:
            assert name.replace("_", " ") in line
    assert "ruleset: tournament" in line
    assert "file auto delete" not in line
    assert replay_prelude._settings_line({}) == ""

    free_play = _write_replay(tmp_path, tournament=False)
    assert "ruleset: free play" in replay_prelude._settings_line(free_play)


def test_prelude_falls_back_to_seats_without_names(tmp_path):
    metadata = _write_replay(tmp_path, with_names=False)

    assert replay_prelude._seat_label(metadata, "player1") == "player1"
    assert metadata["bans"] == {"player1": ["TANKG", "APG"], "player2": ["SPB"]}


def _drive(game_screen, metadata, key):
    import pygame
    pygame.event.clear()
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    return replay_prelude.main(game_screen, metadata)


def test_prelude_renders_and_e_starts_esc_exits(game_screen, tmp_path):
    import pygame
    metadata = _write_replay(tmp_path, tournament=True)

    assert _drive(game_screen, metadata, pygame.K_e) is True
    assert _drive(game_screen, metadata, pygame.K_ESCAPE) is False


def test_prelude_renders_with_no_bans(game_screen):
    import pygame
    metadata = {"player1_deck": P1_DECK, "player2_deck": P2_DECK}

    assert _drive(game_screen, metadata, pygame.K_e) is True
