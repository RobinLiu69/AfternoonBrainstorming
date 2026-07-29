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

"""Decorated card codes.

Deck / hand / draw pile / discard pile are plain ``list[str]`` of card codes
(``"TANKW"``).  Tower mode needs per-copy enchantments, so it decorates the
code with a suffix:

    TANKW*shp           one enchantment
    TANKW*shp.fort      two enchantments
    APC*mana (+)        enchanted and cyan-upgraded

The upgrade marker ``" (+)"`` always stays last so the existing cyan upgrade
path keeps working.  Modes other than tower never produce a ``*`` suffix, so
plain codes round-trip through every function here unchanged.
"""

from __future__ import annotations

from typing import Any, Callable, Optional


ENCHANT_SEP: str = "*"
ENCHANT_JOIN: str = "."
UPGRADE_SUFFIX: str = " (+)"


def split_upgrade(name: str) -> tuple[str, bool]:
    if name.endswith(UPGRADE_SUFFIX):
        return name[: -len(UPGRADE_SUFFIX)], True
    return name, False


def base_code(name: str) -> str:
    """Card code with enchantments stripped, upgrade marker kept."""
    body, upgraded = split_upgrade(name)
    body = body.split(ENCHANT_SEP, 1)[0]
    return body + UPGRADE_SUFFIX if upgraded else body


def plain_code(name: str) -> str:
    """Card code with both enchantments and the upgrade marker stripped."""
    return split_upgrade(name)[0].split(ENCHANT_SEP, 1)[0]


def enchant_keys(name: str) -> tuple[str, ...]:
    body, _upgraded = split_upgrade(name)
    if ENCHANT_SEP not in body:
        return ()
    _base, _sep, tail = body.partition(ENCHANT_SEP)
    return tuple(key for key in tail.split(ENCHANT_JOIN) if key)


def has_enchant(name: str, key: str) -> bool:
    return key in enchant_keys(name)


def is_enchanted(name: str) -> bool:
    return bool(enchant_keys(name))


def with_enchants(name: str, keys) -> str:
    """Replace the enchantment set of ``name`` with ``keys`` (order preserved)."""
    body, upgraded = split_upgrade(name)
    base = body.split(ENCHANT_SEP, 1)[0]
    unique: list[str] = []
    for key in keys:
        if key and key not in unique:
            unique.append(key)
    out = base + (ENCHANT_SEP + ENCHANT_JOIN.join(unique) if unique else "")
    return out + UPGRADE_SUFFIX if upgraded else out


def add_enchant(name: str, key: str) -> str:
    return with_enchants(name, list(enchant_keys(name)) + [key])


def remove_enchants(name: str) -> str:
    return with_enchants(name, ())


# --------------------------------------------------------------------------
# deploy hooks
# --------------------------------------------------------------------------
# core spawns cards from the base code and then asks whoever owns the
# enchantment rules to decorate the fresh unit.  Tower mode registers its
# handlers when the mode starts; every other mode leaves these unset, and
# every function below is then a no-op.

EnchantHook = Callable[[Any, tuple[str, ...], Any], None]
SpawnResolver = Callable[[str, tuple[str, ...], Any], str]

_enchant_hook: Optional[EnchantHook] = None
_spawn_resolver: Optional[SpawnResolver] = None
_ephemeral_keys: frozenset[str] = frozenset()


def set_enchant_hook(hook: Optional[EnchantHook]) -> None:
    global _enchant_hook
    _enchant_hook = hook


def run_enchant_hook(card: Any, name: str, game_state: Any) -> None:
    keys = enchant_keys(name)
    if keys and _enchant_hook is not None:
        _enchant_hook(card, keys, game_state)


def set_spawn_resolver(resolver: Optional[SpawnResolver]) -> None:
    global _spawn_resolver
    _spawn_resolver = resolver


def resolve_spawn_code(spawn_name: str, name: str, game_state: Any) -> str:
    """Let the enchantment owner swap which card class actually gets built."""
    keys = enchant_keys(name)
    if keys and _spawn_resolver is not None:
        return _spawn_resolver(spawn_name, keys, game_state)
    return spawn_name


def set_ephemeral_keys(keys) -> None:
    """Enchantments whose cards leave play without reaching the discard pile."""
    global _ephemeral_keys
    _ephemeral_keys = frozenset(keys)


def is_ephemeral(name: str) -> bool:
    if not _ephemeral_keys:
        return False
    return any(key in _ephemeral_keys for key in enchant_keys(name))
