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

"""Enchantments in battle.

Three ways an enchantment can act:

* **at deploy** - flat stats, the one-off effects (Burning, Mana), and the
  method overrides that ride along with the unit for the rest of its life.
  Assigning a function to an instance attribute shadows the class method, so
  ``Card.settle`` calling ``self.on_settle`` picks up the Radiant version
  without touching a single card class.
* **every tick** - the states that other cards keep trying to undo
  (Steady vs numbness, Rusted vs shields).
* **at the owner's turn start** - Bleeding and Artisan: Mend.

Dispersed is special: it changes which card class gets built, so it runs
before the unit exists, through the spawn resolver.
"""

from __future__ import annotations

from typing import Any, Iterator

from cards.card_blue import BlueCard
from cards.factory import CardFactory
from shared import card_code

from tower import card_pool
from tower.content import ENCHANTS

VANISHING_KEYS: frozenset[str] = frozenset({"ghost"})
NO_DISCARD_KEYS: frozenset[str] = frozenset({"ghost", "borrowed"})
PLATED_REDUCTION: int = 1
RADIANT_BONUS: int = 1
BURN_SCORE: int = 2
BLEED_DAMAGE: int = 1
MEND_HEAL: int = 1


# --------------------------------------------------------------------------
# deploy
# --------------------------------------------------------------------------

def apply(card: Any, keys: tuple[str, ...], game_state: Any) -> None:
    card.tower_enchants = keys

    if "disperse" in keys:
        _restore_base_stats(card)

    hp = sum(int(ENCHANTS[k]["hp"]) for k in keys if k in ENCHANTS)
    damage = sum(int(ENCHANTS[k]["damage"]) for k in keys if k in ENCHANTS)
    if hp:
        card.health = max(1, card.health + hp)
        card.max_health = max(1, card.max_health + hp)
        card.display_health = card.health
    if damage:
        card.damage = max(0, card.damage + damage)
        card.original_damage = max(0, card.original_damage + damage)

    if "steady" in keys:
        card.numbness = False
    if "radiant" in keys:
        _wrap_radiant(card)
    if "plated" in keys:
        _wrap_plated(card)
    if "sword" in keys:
        _wrap_sword(card)
    if "mana" in keys:
        gain_token(game_state, card.owner, 1)
    if "burn" in keys:
        _burn(card, game_state)


def _restore_base_stats(card: Any) -> None:
    """Dispersed keeps the original card's body, only the faction changes."""
    original = card_code.plain_code(getattr(card, "tower_code", "") or card.job_and_color)
    try:
        reference = CardFactory.create(original, "display", 0, 0)
    except (ValueError, KeyError):
        return
    card.health = reference.health
    card.max_health = reference.health
    card.display_health = card.health
    card.damage = reference.damage
    card.original_damage = reference.damage


def _wrap_radiant(card: Any) -> None:
    original = card.on_settle

    def on_settle(clear_numbness: bool = True) -> int:
        scored = original(clear_numbness)
        return scored + RADIANT_BONUS if scored else 0

    card.on_settle = on_settle


def _wrap_plated(card: Any) -> None:
    original = card.damage_reduce

    def damage_reduce(value: int, game_state: Any) -> int:
        return max(0, original(value, game_state) - PLATED_REDUCTION)

    card.damage_reduce = damage_reduce


def _wrap_sword(card: Any) -> None:
    original = card.on_attack

    def on_attack(game_state: Any) -> bool:
        if original(game_state):
            return True
        hit = card.launch_attack("nearest", game_state)
        card.hit_cards.clear()
        return hit

    card.on_attack = on_attack


def _burn(card: Any, game_state: Any) -> None:
    """The enemy scores, the first time each burning card is played this battle."""
    seen = getattr(game_state, "tower_burn_seen", None)
    if seen is None:
        seen = set()
        game_state.tower_burn_seen = seen
    key = (card.owner, getattr(card, "tower_code", "") or card.job_and_color)
    if key in seen:
        return
    seen.add(key)
    game_state.score += BURN_SCORE if card.owner == "player1" else -BURN_SCORE


def gain_token(game_state: Any, owner: str, amount: int = 1) -> None:
    """Add mana orbs and run the blue threshold, even with no blue card out."""
    if amount <= 0:
        return
    game_state.players_token[owner] += amount
    carrier = next((c for c in game_state.get_player_cards(owner)
                    if isinstance(c, BlueCard) and not c.nullify), None)
    if carrier is not None:
        carrier.got_token(game_state)
        return
    if game_state.players_token[owner] // game_state.tokens_to_draw_a_card >= 1:
        game_state.players_token[owner] -= game_state.tokens_to_draw_a_card
        game_state.card_to_draw[owner] += 1


# --------------------------------------------------------------------------
# spawn
# --------------------------------------------------------------------------

def resolve_spawn(spawn_name: str, keys: tuple[str, ...], game_state: Any) -> str:
    if "disperse" not in keys:
        return spawn_name
    job = card_pool.job_of(spawn_name)
    current = card_pool.color_tag_of(spawn_name)
    CardFactory.register_all()
    others = sorted(
        tag for tag in card_pool.COLOR_TAGS
        if tag != current and job + tag in CardFactory._registry
    )
    if not others:
        return spawn_name
    return job + game_state.rng.choice(others)


# --------------------------------------------------------------------------
# per tick and per turn
# --------------------------------------------------------------------------

def _enchanted_units(game_state: Any, player_name: str) -> Iterator[tuple[Any, tuple[str, ...]]]:
    for card in game_state.get_player(player_name).on_board:
        keys = getattr(card, "tower_enchants", ())
        if keys:
            yield card, keys


def enforce(game_state: Any, player_name: str) -> None:
    """States that other cards keep re-applying, so we re-clear them."""
    for card, keys in _enchanted_units(game_state, player_name):
        if card.nullify:
            continue
        if "steady" in keys and card.numbness:
            card.numbness = False
        if "rust" in keys and card.armor:
            card.armor = 0


def turn_start(game_state: Any, player_name: str) -> None:
    for card, keys in _enchanted_units(game_state, player_name):
        if card.nullify or card.health <= 0:
            continue
        if "art_mend" in keys and card.health < card.max_health:
            card.heal(MEND_HEAL, game_state)
        if "bleed" in keys:
            game_state.judge.deal(BLEED_DAMAGE, card, game_state)


# --------------------------------------------------------------------------
# install
# --------------------------------------------------------------------------

def install() -> None:
    card_code.set_enchant_hook(apply)
    card_code.set_spawn_resolver(resolve_spawn)
    card_code.set_vanishing_keys(VANISHING_KEYS)
    card_code.set_no_discard_keys(NO_DISCARD_KEYS)


def uninstall() -> None:
    card_code.set_enchant_hook(None)
    card_code.set_spawn_resolver(None)
    card_code.set_vanishing_keys(())
    card_code.set_no_discard_keys(())
