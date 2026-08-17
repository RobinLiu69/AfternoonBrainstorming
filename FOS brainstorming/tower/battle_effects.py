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

"""One side's relic effects, driven from the tower controller.

``SideRuntime`` holds the bookkeeping a side needs across a battle: which
units it has already buffed, whether its deck has reshuffled, and whether it
has cast a spell yet.  The controller owns one per side and calls into it.

A handful of relics need core to read a number it cannot know about
(healing size, minimum damage, overheal shields).  Those travel through
``tower_*`` attributes stashed on the game state by ``install_side_channels``
- core reads them with a ``getattr`` default, so no other mode is affected.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from shared import card_code

from tower import enchant_runtime

if TYPE_CHECKING:
    from core.game_state import GameState


BASE_HAND_SIZE: int = 3
BASE_LUCK: int = 50
GHOST_SPELLS: tuple[str, ...] = ("HEAL", "CUBES", "MOVE")
MAGIC_CODES: frozenset[str] = frozenset({"HEAL", "CUBES", "MOVE", "MOVEO"})


def install_side_channels(gs: "GameState", effects_by_side: dict[str, dict]) -> None:
    gs.tower_heal_bonus = {
        side: int(effects.get("heal_bonus", 0))
        for side, effects in effects_by_side.items()
    }
    gs.tower_min_damage = {
        side: int(effects.get("min_damage", 0))
        for side, effects in effects_by_side.items()
    }
    gs.tower_overheal_mult = {
        side: max(1, int(effects.get("overheal_shield_mult", 1)))
        for side, effects in effects_by_side.items()
    }


def _punish_double_hits(card, extra: int) -> None:
    """Ninja Scroll: landing on the same enemy twice in one swing hurts more."""
    original = card.after_damage_calculated

    def after_damage_calculated(target, value: int, game_state) -> bool:
        result = original(target, value, game_state)
        if card.hit_cards.count(target) == 2 and target.health > 0:
            game_state.judge.deal(extra, target, game_state)
        return result

    card.after_damage_calculated = after_damage_calculated


def _suppress_numbing(card) -> None:
    """Blasting Wand: an AP unit keeps its ability but stops numbing targets."""
    original = card.ability

    def ability(target, game_state) -> bool:
        was_numb = target.numbness
        result = original(target, game_state)
        target.numbness = was_numb
        return result

    card.ability = ability


class SideRuntime:

    def __init__(self, effects: dict, player_name: str):
        self.effects: dict = dict(effects)
        self.name: str = player_name
        self.buffed_ids: set[str] = set()
        self.started: bool = False
        self.own_turns: int = 0
        self._last_turn: int = -1
        self._prev_draw_len: int = -1
        self._prev_tokens: int = 0
        self._spell_counts: dict[str, int] = {}
        self._spell_turn: int = -1
        self._spell_used: bool = False
        self._positions: dict[str, tuple[int, int]] = {}
        self._damage_seen: dict[str, int] = {}

    # ---------------- battle start ----------------

    def on_battle_start(self, gs: "GameState") -> None:
        self._apply_initial_hand(gs)
        self._prev_draw_len = len(gs.get_player(self.name).draw_pile)
        self._prev_tokens = gs.players_token.get(self.name, 0)

        luck = int(self.effects.get("luck_plus", 0))
        if luck:
            gs.players_luck[self.name] = max(0, min(100, BASE_LUCK + luck))

        penalty = int(self.effects.get("start_score_penalty", 0))
        if penalty:
            gs.score += penalty if self.name == "player1" else -penalty

        self.started = True

    def _apply_initial_hand(self, gs: "GameState") -> None:
        hand_plus = int(self.effects.get("hand_plus", 0))
        if not hand_plus:
            return
        player = gs.get_player(self.name)
        target = max(1, BASE_HAND_SIZE + hand_plus)
        while len(player.hand) < target:
            before = len(player.hand)
            player.draw_card(gs)
            if len(player.hand) == before:
                break
        while len(player.hand) > target:
            player.discard_pile.append(player.hand.pop())

    # ---------------- every tick ----------------

    def maintain(self, gs: "GameState") -> None:
        self._maintain_unit_buffs(gs)
        enchant_runtime.enforce(gs, self.name)
        if self.started:
            self._watch_reshuffle(gs)
            self._watch_spells(gs)
            self._watch_orbs(gs)
            self._watch_moves(gs)
            self._watch_growth(gs)

    def _maintain_unit_buffs(self, gs: "GameState") -> None:
        effects = self.effects
        hp_plus = effects.get("unit_hp_plus", 0)
        dmg_plus = effects.get("unit_damage_plus", 0)
        job_hp = effects.get("job_hp_plus", {})
        job_dmg = effects.get("job_damage_plus", {})
        first_hp = effects.get("first_unit_hp_plus", 0)
        first_dmg = effects.get("first_unit_damage_plus", 0)
        enchanted_dmg = effects.get("enchanted_damage_plus", 0)

        no_numb = effects.get("ap_no_numb")
        double_hit = int(effects.get("double_hit_damage", 0))

        if not (hp_plus or dmg_plus or job_hp or job_dmg
                or first_hp or first_dmg or enchanted_dmg or no_numb or double_hit):
            return

        for card in gs.get_player(self.name).on_board:
            if card.instance_id in self.buffed_ids:
                continue
            first = not self.buffed_ids
            if no_numb and card.job == "AP":
                _suppress_numbing(card)
            if double_hit:
                _punish_double_hits(card, double_hit)
            hp = hp_plus + job_hp.get(card.job, 0) + (first_hp if first else 0)
            dmg = dmg_plus + job_dmg.get(card.job, 0) + (first_dmg if first else 0)
            if enchanted_dmg and getattr(card, "tower_enchants", ()):
                dmg += enchanted_dmg
            if hp:
                card.health = max(1, card.health + hp)
                card.max_health = max(1, card.max_health + hp)
                card.display_health = card.health
            if dmg:
                card.damage = max(0, card.damage + dmg)
                card.original_damage = max(0, card.original_damage + dmg)
            self.buffed_ids.add(card.instance_id)

    def _watch_reshuffle(self, gs: "GameState") -> None:
        draw_len = len(gs.get_player(self.name).draw_pile)
        if draw_len > self._prev_draw_len:
            self._on_reshuffle(gs)
        self._prev_draw_len = draw_len

    def _on_reshuffle(self, gs: "GameState") -> None:
        draws = int(self.effects.get("draw_on_reshuffle", 0))
        if draws:
            gs.card_to_draw[self.name] = gs.card_to_draw.get(self.name, 0) + draws
        attacks = int(self.effects.get("attack_on_reshuffle", 0))
        if attacks:
            gs.number_of_attacks[self.name] = gs.number_of_attacks.get(self.name, 0) + attacks

    def _watch_orbs(self, gs: "GameState") -> None:
        """Blue Crystal Ball: an orb threshold firing stings a random enemy."""
        tokens = gs.players_token.get(self.name, 0)
        damage = int(self.effects.get("orb_trigger_damage", 0))
        if damage and tokens < self._prev_tokens:
            targets = [c for c in gs.get_opponent_cards(self.name) if c.health > 0]
            if targets:
                gs.judge.deal(damage, gs.rng.choice(targets), gs)
        self._prev_tokens = tokens

    def _watch_moves(self, gs: "GameState") -> None:
        """Razor Hat: any unit changing square draws blood from a random enemy."""
        damage = int(self.effects.get("damage_on_move", 0))
        moved = False
        positions: dict[str, tuple[int, int]] = {}
        for card in gs.get_both_player_cards():
            positions[card.instance_id] = (card.board_x, card.board_y)
            was = self._positions.get(card.instance_id)
            if was is not None and was != positions[card.instance_id]:
                moved = True
        self._positions = positions

        if damage and moved:
            targets = [c for c in gs.get_opponent_cards(self.name) if c.health > 0]
            if targets:
                gs.judge.deal(damage, gs.rng.choice(targets), gs)

    def _watch_growth(self, gs: "GameState") -> None:
        """Oni Mask: armor for every couple of points of damage a unit gains."""
        step = int(self.effects.get("armor_per_growth", 0))
        if not step:
            return
        for card in gs.get_player(self.name).on_board:
            grown = max(0, card.damage - card.original_damage)
            paid = self._damage_seen.get(card.instance_id, 0)
            awards = grown // step - paid // step
            if awards > 0:
                card.armor += awards
            self._damage_seen[card.instance_id] = grown

    def _watch_spells(self, gs: "GameState") -> None:
        if not self.effects.get("first_spell_draw") or self._spell_used:
            return
        counts: dict[str, int] = {}
        for code in gs.get_player(self.name).hand:
            plain = card_code.plain_code(code)
            if plain in MAGIC_CODES:
                counts[plain] = counts.get(plain, 0) + 1

        if self._spell_turn == gs.turn_number:
            played = sum(max(0, self._spell_counts.get(code, 0) - counts.get(code, 0))
                         for code in MAGIC_CODES)
            if played:
                self._spell_used = True
                gs.card_to_draw[self.name] = gs.card_to_draw.get(self.name, 0) + int(
                    self.effects["first_spell_draw"])

        self._spell_counts = counts
        self._spell_turn = gs.turn_number

    # ---------------- own turn start ----------------

    def on_turn_start(self, gs: "GameState") -> None:
        if gs.turn_number == self._last_turn:
            return
        self._last_turn = gs.turn_number
        self.own_turns += 1
        effects = self.effects

        enchant_runtime.turn_start(gs, self.name)

        tokens = int(effects.get("turn_start_tokens", 0))
        if tokens:
            enchant_runtime.gain_token(gs, self.name, tokens)

        coins = int(effects.get("turn_start_coins", 0))
        if coins:
            gs.players_coin[self.name] = gs.players_coin.get(self.name, 0) + coins

        draws = int(effects.get("turn_start_draw_plus", 0))
        if draws:
            gs.card_to_draw[self.name] = gs.card_to_draw.get(self.name, 0) + draws

        if effects.get("no_attack_gain"):
            gs.number_of_attacks[self.name] = 0
        else:
            bonus = int(effects.get("attacks_plus", 0))
            if effects.get("attacks_reset"):
                gs.number_of_attacks[self.name] = 1 + bonus
            elif bonus:
                gs.number_of_attacks[self.name] = (
                    gs.number_of_attacks.get(self.name, 0) + bonus)

        if effects.get("no_turn_start_draw"):
            gs.skip_turn_draw[self.name] = True

        totems = int(effects.get("turn_start_totem", 0))
        if totems:
            gs.players_totem[self.name] = gs.players_totem.get(self.name, 0) + totems

        move_turn = int(effects.get("move_spell_on_turn", 0))
        if move_turn and self.own_turns == move_turn:
            gs.get_player(self.name).hand.append("MOVE")

        every = int(effects.get("ghost_spell_every_n_turns", 0))
        if every and self.own_turns % every == 0:
            spell = gs.rng.choice(list(GHOST_SPELLS))
            gs.get_player(self.name).hand.append(
                card_code.add_enchant(spell, "ghost"))

    # ---------------- own turn end ----------------

    def on_turn_end(self, gs: "GameState") -> None:
        """Runs once when this side hands the turn over."""
        enchant_runtime.turn_end(gs, self.name)
        effects = self.effects

        shadow_damage = int(effects.get("shadow_damage", 0))
        if shadow_damage:
            shadows = {(c.board_x, c.board_y)
                       for c in gs.get_player(self.name).on_board
                       if c.job_and_color == "SHADOW"}
            for enemy in list(gs.get_opponent_cards(self.name)):
                if enemy.health > 0 and (enemy.board_x, enemy.board_y) in shadows:
                    gs.judge.deal(shadow_damage, enemy, gs)

        bonus = 0
        empty = int(effects.get("empty_board_score", 0))
        if empty and not [c for c in gs.get_player(self.name).on_board if c.health > 0]:
            bonus += empty

        per_totem = int(effects.get("score_per_totem", 0))
        if per_totem:
            bonus += gs.players_totem.get(self.name, 0) // per_totem

        if bonus:
            gs.score += -bonus if self.name == "player1" else bonus
