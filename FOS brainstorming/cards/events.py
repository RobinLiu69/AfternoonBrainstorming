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

"""The closed set of timing windows an ability can hook.

Previously the timing of an ability was implied by which base method you
overrode, and you had to read ``damage_calculate`` to discover that ``ability()``
meant "on hit, before damage is applied". Naming the windows makes that
readable at the call site.
"""

from __future__ import annotations

from enum import StrEnum


class Event(StrEnum):
    # --- lifecycle ------------------------------------------------------
    DEPLOY_COST = "deploy_cost"
    """Replacement window run before a card is placed; cancelling it refuses
    the placement (Cyan's upgraded copies must be paid for)."""

    DEPLOYED = "deployed"
    """This card was just placed on the board."""

    TURN_START = "turn_start"
    """The owner's turn began (old on_refresh)."""

    TURN_END = "turn_end"
    """The owner's turn ended, before scoring (old on_settle side effects)."""

    ON_DEATH = "on_death"
    """This card is leaving the board."""

    TICK = "tick"
    """Per-frame upkeep. Dispatched only to cards whose definition asks for it,
    so it costs nothing for the cards that do not."""

    # --- combat ---------------------------------------------------------
    # The damage pipeline runs these in order:
    #   DAMAGE_PREVENTION -> ON_HIT -> DAMAGE_MODIFY -> (apply) -> AFTER_* -> LETHAL
    DAMAGE_PREVENTION = "damage_prevention"
    """Replacement window that can cancel a hit outright (old damage_block)."""

    DAMAGE_MODIFY = "damage_modify"
    """Replacement window that rewrites the amount (old damage_bonus /
    damage_reduce / on_field_effect_trigger, which were three mechanisms for
    one job)."""

    LETHAL = "lethal"
    """Replacement window fired when a card hits zero health; setting
    ``prevented`` keeps it alive (old on_can_be_killed)."""

    ATTACK_DECLARED = "attack_declared"
    """Replacement window before a player-initiated attack; cancelling it stops
    the attack without spending a charge."""

    ATTACKED = "attacked"
    """This card's own attack action hit something. Extra attacks issued from
    here go through the queue and do not re-enter the attack action."""

    ATTACK_MISSED = "attack_missed"
    """This card's attack action found no target. An effect may still salvage
    it (Fuchsia's shadows attack even when the body cannot reach)."""

    ON_HIT = "on_hit"
    """This card landed a hit; fires once per target, before damage applies."""

    AFTER_DAMAGE_DEALT = "after_damage_dealt"
    """This card dealt damage (old after_damage_calculated)."""

    AFTER_DAMAGE_TAKEN = "after_damage_taken"
    """This card took damage (old on_attacked_by)."""

    ON_KILL = "on_kill"
    """This card reduced another to zero health."""

    ON_KILLED = "on_killed"
    """This card was reduced to zero health."""

    # --- movement -------------------------------------------------------
    MOVED = "moved"
    """This card moved (old after_movement)."""

    CARD_MOVED = "card_moved"
    """Any card moved; every card on the board observes this."""

    # --- economy --------------------------------------------------------
    RESOURCE_GAINED = "resource_gained"
    """The owner gained luck / tokens / totems / coins."""

    CARD_DRAWN = "card_drawn"
    """The owner drew a card."""

    MODIFIER_GRANTED = "modifier_granted"
    """A single modifier was attached to a card."""

    BUFF_APPLIED = "buff_applied"
    """A card was buffed as one logical act (attack and armour together).

    Red's SP listens here to copy every friendly red buff onto itself, which is
    the whole of its ability — previously that behaviour did not live on SP at
    all, but was re-implemented as a lookup loop inside all seven other red
    cards.
    """


class Resource(StrEnum):
    """Per-player economies, previously four parallel dicts on GameState."""

    LUCK = "luck"
    TOKEN = "token"
    TOTEM = "totem"
    COIN = "coin"
    ATTACKS = "attacks"
    MOVES = "moves"
