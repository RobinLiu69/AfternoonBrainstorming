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

"""Which language tower mode names its content in.

Only the *content* is translated - relics, enchantments, blessings, events,
rooms and enemies.  The chrome (menus, buttons, the run bar) stays English,
matching the rest of the game, where card hints are already Chinese while
the interface is not.

Content tables carry both languages side by side::

    "piggy_bank": {"label": "Piggy Bank", "label_zh": "小豬撲滿", ...}

and everything reads them through ``pick()``, so a missing translation falls
back to English instead of blowing up.
"""

from __future__ import annotations

from core.setting_config import load_setting, save_setting

ENGLISH: str = "en"
CHINESE: str = "zh"

_override: str | None = None


def current() -> str:
    """The tower content language, from the setting unless overridden."""
    if _override is not None:
        return _override
    return load_setting("tower_language")


def set_language(language: str) -> None:
    if language in (ENGLISH, CHINESE):
        save_setting("tower_language", language)


def use(language: str | None) -> None:
    """Force a language for the current process.  ``None`` restores the setting."""
    global _override
    _override = language if language in (ENGLISH, CHINESE) else None


def is_chinese() -> bool:
    return current() == CHINESE


def _translated(table: dict, key: str, index: int) -> str:
    if not is_chinese():
        return ""
    entry = table.get(key)
    return entry[index] if entry else ""


def relic_label(relic_id: str, fallback: str) -> str:
    from tower.content_zh import RELICS_ZH
    return _translated(RELICS_ZH, relic_id, 0) or fallback


def relic_text(relic_id: str, fallback: str) -> str:
    from tower.content_zh import RELICS_ZH
    return _translated(RELICS_ZH, relic_id, 1) or fallback


def enchant_label(key: str, fallback: str) -> str:
    from tower.content_zh import ENCHANTS_ZH
    return _translated(ENCHANTS_ZH, key, 0) or fallback


def enchant_text(key: str, fallback: str) -> str:
    from tower.content_zh import ENCHANTS_ZH
    return _translated(ENCHANTS_ZH, key, 1) or fallback


def blessing_label(blessing_id: str, fallback: str) -> str:
    from tower.content_zh import BLESSINGS_ZH
    return _translated(BLESSINGS_ZH, blessing_id, 0) or fallback


def blessing_text(blessing_id: str, fallback: str) -> str:
    from tower.content_zh import BLESSINGS_ZH
    return _translated(BLESSINGS_ZH, blessing_id, 1) or fallback


def room_label(kind: str, fallback: str) -> str:
    if not is_chinese():
        return fallback
    from tower.content_zh import ROOMS_ZH
    return ROOMS_ZH.get(kind) or fallback


def event_text(key: str, fallback: str = "", **fields) -> str:
    """A one-off line from an event screen, formatted with ``fields``."""
    text = fallback
    if is_chinese():
        from tower.content_zh import EVENT_TEXT_ZH
        text = EVENT_TEXT_ZH.get(key) or fallback
    return text.format(**fields) if fields else text


def event_option(key: str, fallback: tuple[str, str], **fields) -> tuple[str, str]:
    """An event choice as ``(label, description)``."""
    label, text = fallback
    if is_chinese():
        from tower.content_zh import EVENT_TEXT_ZH
        translated = EVENT_TEXT_ZH.get(key)
        if translated:
            label, text = translated
    if fields:
        label, text = label.format(**fields), text.format(**fields)
    return label, text


# --------------------------------------------------------------------------
# fonts
# --------------------------------------------------------------------------
# The latin face has no CJK glyphs.  It still reports a width for them, so
# drawing Chinese with it gives blank boxes *and* a layout measured against
# the wrong numbers - every content font goes through here instead.

_CHINESE_FONTS: dict[str, str] = {
    "small_text_font": "small_text_fontCHI",
    "info_text_font": "info_text_fontCHI",
    "text_font": "text_fontCHI",
    "mid_text_font": "mid_text_fontCHI",
    "big_text_font": "big_text_fontCHI",
    "big_big_text_font": "big_big_text_fontCHI",
    "title_text_font": "title_text_fontCHI",
}


def chinese_font(game_screen, size: str = "text_font"):
    """The Chinese face at the given size, whatever the language setting."""
    chinese = _CHINESE_FONTS.get(size)
    if chinese and hasattr(game_screen, chinese):
        return getattr(game_screen, chinese)
    return getattr(game_screen, size)


def font(game_screen, size: str = "text_font"):
    """The font to draw translated content in, at the given size."""
    if is_chinese():
        return chinese_font(game_screen, size)
    return getattr(game_screen, size)
