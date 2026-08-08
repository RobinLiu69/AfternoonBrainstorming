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

"""Tower content in Chinese: the switch, the translations, and CJK wrapping."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer available")

from cards.factory import CardFactory
from core.game_screen import GameScreen
from core.setting_config import DEFAULT_SETTING, VALID_SETTING

from tower import card_pool, language, ui_common
from tower.content import ENCHANTS, RELICS
from tower.content_zh import ENCHANTS_ZH, RELICS_ZH, TIERS_ZH


@pytest.fixture(scope="module")
def game_screen():
    CardFactory.register_all()
    screen = GameScreen()
    screen.apply_display_mode("60")
    return screen


@pytest.fixture
def english():
    language.use(language.ENGLISH)
    yield
    language.use(None)


@pytest.fixture
def chinese():
    language.use(language.CHINESE)
    yield
    language.use(None)


# --------------------------------------------------------------------------
# the setting
# --------------------------------------------------------------------------

def test_the_setting_exists_and_only_takes_two_values():
    assert VALID_SETTING["tower_language"] == ("en", "zh")
    assert DEFAULT_SETTING["tower_language"] in ("en", "zh")


def test_use_overrides_the_setting_and_none_restores_it():
    language.use(language.ENGLISH)
    assert language.current() == "en"
    language.use(language.CHINESE)
    assert language.is_chinese() is True
    language.use(None)
    assert language.current() in ("en", "zh")


def test_a_nonsense_language_is_ignored():
    language.use("klingon")
    assert language.current() in ("en", "zh")
    language.use(None)


# --------------------------------------------------------------------------
# coverage
# --------------------------------------------------------------------------

def test_every_relic_has_a_chinese_name_and_description():
    missing = sorted(set(RELICS) - set(RELICS_ZH))
    assert missing == [], f"untranslated relics: {missing}"
    for relic_id in RELICS:
        name, text = RELICS_ZH[relic_id]
        assert name and text


def test_every_enchantment_has_a_chinese_name_and_description():
    missing = sorted(set(ENCHANTS) - set(ENCHANTS_ZH))
    assert missing == [], f"untranslated enchantments: {missing}"


def test_no_translation_describes_a_relic_that_does_not_exist():
    assert sorted(set(RELICS_ZH) - set(RELICS)) == []
    assert sorted(set(ENCHANTS_ZH) - set(ENCHANTS)) == []


def test_every_tier_has_a_chinese_name():
    tiers = {relic["tier"] for relic in RELICS.values()}
    assert tiers <= set(TIERS_ZH)


def test_every_blessing_has_a_chinese_name():
    from tower.content import BLESSINGS
    from tower.content_zh import BLESSINGS_ZH
    missing = sorted({b["id"] for b in BLESSINGS} - set(BLESSINGS_ZH))
    assert missing == [], f"untranslated blessings: {missing}"


def test_every_room_kind_has_a_chinese_name():
    from tower.content import ROOM_KINDS
    from tower.content_zh import ROOMS_ZH
    assert set(ROOM_KINDS) <= set(ROOMS_ZH)


def test_every_altar_deal_has_a_chinese_name():
    from tower import events
    from tower.content_zh import EVENT_TEXT_ZH
    for deal in events.ALTAR_DEALS:
        assert f"deal_{deal['id']}" in EVENT_TEXT_ZH


def test_rooms_and_blessings_follow_the_language(english):
    from tower.content import BLESSING_POOLS
    blessing = BLESSING_POOLS["logistics"][0]

    assert ui_common.room_label("gold_mine") == "Gold Mine"
    assert ui_common.blessing_label(blessing) == blessing["label"]

    language.use(language.CHINESE)
    assert ui_common.room_label("gold_mine") == "金礦"
    assert ui_common.blessing_label(blessing) == "擴建營地"
    assert "備戰區" in ui_common.blessing_text(blessing)


def test_event_lines_format_their_fields(chinese):
    assert language.event_text("mine_text", "you dig out {gold}", gold=120) == \
        "你挖出了 120 金幣"
    label, text = language.event_option("visitor_fight", ("fight", "beat them"))
    assert label == "來一把吧！"
    assert text


def test_an_untranslated_event_line_falls_back(chinese):
    assert language.event_text("no_such_key", "plain english") == "plain english"
    assert language.event_option("no_such_key", ("a", "b")) == ("a", "b")


def test_enemy_and_faction_names_stay_english(chinese):
    from tower.content import FACTION_NAMES
    from tower import enemies
    import random

    assert FACTION_NAMES["R"] == "Red"
    assert enemies.white_lord(random.Random(1))["label"] == "White Lord"
    assert enemies.weak_enemy("warriors")["label"] == "White Warriors"


# --------------------------------------------------------------------------
# the accessors switch
# --------------------------------------------------------------------------

def test_relic_names_follow_the_language(english):
    assert ui_common.relic_label("piggy_bank") == "Piggy Bank"
    assert ui_common.tier_label("common") == "common"
    language.use(language.CHINESE)
    assert ui_common.relic_label("piggy_bank") == "小豬撲滿"
    assert ui_common.tier_label("common") == "普通"


def test_enchantment_names_follow_the_language(english):
    assert card_pool.enchant_label("sharp") == "Sharp"
    assert card_pool.display_name("TANKW*sharp") == "TANKW [Sharp]"
    language.use(language.CHINESE)
    assert card_pool.enchant_label("sharp") == "鋒利"
    assert card_pool.display_name("TANKW*sharp") == "TANKW [鋒利]"


def test_the_card_code_itself_never_gets_translated(chinese):
    # deck lists, saves and the factory all key off the raw code
    assert card_pool.display_name("TANKW") == "TANKW"
    assert "TANKW" in card_pool.display_name("TANKW*sharp")


def test_an_untranslated_entry_falls_back_to_english(chinese, monkeypatch):
    monkeypatch.delitem(RELICS_ZH, "piggy_bank")
    assert ui_common.relic_label("piggy_bank") == "Piggy Bank"


# --------------------------------------------------------------------------
# fonts
# --------------------------------------------------------------------------

def test_chinese_content_gets_the_chinese_face(game_screen, chinese):
    for size in ("small_text_font", "text_font", "mid_text_font",
                 "big_text_font", "title_text_font"):
        assert language.font(game_screen, size) is getattr(game_screen, size + "CHI")


def test_english_content_gets_the_latin_face(game_screen, english):
    for size in ("small_text_font", "text_font", "mid_text_font"):
        assert language.font(game_screen, size) is getattr(game_screen, size)


def test_auto_font_follows_the_string_not_the_setting(game_screen, english):
    """Even in English mode a Chinese string must get the Chinese face."""
    assert ui_common.auto_font(game_screen, "金礦", "text_font") is game_screen.text_fontCHI
    assert ui_common.auto_font(game_screen, "Gold Mine", "text_font") is game_screen.text_font


def test_every_piece_of_translated_content_gets_a_face_that_can_draw_it(
        game_screen, chinese):
    """The bug this guards: a translated name drawn with the latin face comes
    out as blank boxes, because that face has no CJK glyphs."""
    from tower.content import BLESSINGS, ROOM_KINDS

    strings = [ui_common.room_label(kind) for kind in ROOM_KINDS]
    strings += [ui_common.blessing_label(b) for b in BLESSINGS]
    strings += [ui_common.blessing_text(b) for b in BLESSINGS]
    strings += [ui_common.relic_label(r) for r in RELICS]
    strings += [ui_common.relic_text(r) for r in RELICS]
    strings += [card_pool.enchant_label(e) for e in ENCHANTS]

    chinese_faces = {getattr(game_screen, name + "CHI")
                     for name in ("small_text_font", "text_font", "mid_text_font",
                                  "big_text_font", "big_big_text_font",
                                  "title_text_font")}
    for text in strings:
        assert ui_common.has_cjk(text), f"expected Chinese, got {text!r}"
        for size in ("text_font", "mid_text_font", "big_big_text_font"):
            assert ui_common.auto_font(game_screen, text, size) in chinese_faces


def test_room_labels_are_translated_and_drawable(game_screen, chinese):
    label = ui_common.room_label("gold_mine")
    assert label == "金礦"
    assert ui_common.auto_font(game_screen, label, "big_big_text_font") is \
        game_screen.big_big_text_fontCHI


def test_the_latin_face_would_have_mismeasured_the_chinese(game_screen):
    """Why the font swap matters: the latin face reports a width for glyphs
    it cannot draw, which would quietly break every measured layout."""
    text = RELICS_ZH["piggy_bank"][1]
    assert game_screen.text_font.size(text)[0] != game_screen.text_fontCHI.size(text)[0]


# --------------------------------------------------------------------------
# wrapping
# --------------------------------------------------------------------------

def test_chinese_actually_wraps():
    text = RELICS_ZH["credit_card"][1]
    assert len(ui_common.wrap(text, 20)) > 1


def test_a_chinese_glyph_counts_as_two_columns():
    assert ui_common.wrap("鋒利加固狂化", 4) == ["鋒利", "加固", "狂化"]


def test_closing_punctuation_never_starts_a_line():
    text = "你的坦克職業牌的生命值加一，同時只能持有一個"
    for width in range(6, 30, 2):
        for line in ui_common.wrap(text, width):
            assert line[0] not in "，。、；：）」』？！"


def test_latin_runs_inside_chinese_stay_whole():
    lines = ui_common.wrap("獲得的金錢增加 25% 並且 TANK +1", 8)
    joined = "".join(lines)
    assert "25%" in joined
    assert "TANK" in joined


def test_author_spacing_is_preserved():
    assert "增加 25%" in "".join(ui_common.wrap("獲得的金錢增加 25%", 40))


def test_measured_wrapping_fits_the_column_in_chinese(game_screen, chinese):
    font = language.font(game_screen, "text_font")
    for relic_id in RELICS:
        text = ui_common.relic_text(relic_id)
        for line in ui_common.wrap_to_width(text, font, 260):
            assert font.size(line)[0] <= 260 or len(line) == 1


def test_english_wrapping_is_unchanged():
    assert ui_common.wrap("your TANK cards gain +1 HP, only one at a time", 30) == [
        "your TANK cards gain +1 HP,", "only one at a time"]
