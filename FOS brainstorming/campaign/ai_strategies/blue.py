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

from __future__ import annotations

from campaign.ai_strategies.base import Strategy
from campaign import ai_query
from campaign.config_loader import CAMPAIGN_SETTINGS

_B = CAMPAIGN_SETTINGS["strategy_bonuses"]["blue"]
_P = _B["placement"]
TOKEN_VALUE: float = float(_B["token_value"])


def expected_tokens_from_attack(attacker, gs) -> int:
    targets = ai_query.attack_targets_at(gs, attacker)
    if not targets:
        return 0
    name = attacker.job_and_color
    if name == "APB":
        return len(targets) * 2
    if name == "LFB":
        return len(targets)
    effective = attacker.damage + attacker.extra_damage
    if name == "ADCB":
        return sum(
            1 for t in targets if t.health <= effective - max(0, t.armor)
        )
    if name == "ASSB":
        return sum(
            2 for t in targets if t.health <= effective - max(0, t.armor)
        )
    return 0


class BlueStrategy(Strategy):

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        tokens = gs.players_token.get(attacker.owner, 0)
        bonus = 0.0

        if tokens == 2:
            bonus += _B["tokens_at_2"]
        elif tokens == 1:
            bonus += _B["tokens_at_1"]

        if attacker.job_and_color == "SPB":
            bonus += _B["spb_baseline"]

        if attacker.job_and_color == "HFB" and tokens >= 1:
            targets = ai_query.attack_targets_at(gs, attacker)
            for t in targets:
                effective = (attacker.damage + tokens) - max(0, t.armor)
                if effective > 0 and t.health <= effective:
                    bonus += _B["hfb_kill_bonus"]
                    break
                bonus += min(effective, t.health) * _B["hfb_chip_mult"]
            bonus = min(bonus, _B["hfb_cap"])

        if attacker.job_and_color == "LFB":
            targets = ai_query.attack_targets_at(gs, attacker)
            bonus += len(targets) * _B["lfb_per_target"]

        if attacker.job_and_color in ("ADCB", "ASSB"):
            bonus += _B["adcb_assb_baseline"]

        expected = expected_tokens_from_attack(attacker, gs)
        bonus += expected * TOKEN_VALUE

        threshold = gs.tokens_to_draw_a_card
        if tokens + expected >= threshold:
            has_armed_adcb = any(
                c.job_and_color == "ADCB" and not c.numbness and c.health > 0
                for c in gs.get_player(attacker.owner).on_board
            )
            if has_armed_adcb:
                bonus += _B["token_draw_chain"]

        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        tokens = gs.players_token.get(owner, 0)
        x, y = position
        bonus = 0.0

        if card_name == "TANKB":
            dist = ai_query.nearest_enemy_distance(gs, owner, x, y)
            if dist <= 1:
                bonus += _P["tankb_close"]
            elif dist <= 2:
                bonus += _P["tankb_mid"]

        if card_name == "SPB":
            my_units = (
                len(gs.get_player(owner).on_board) + len(gs.get_player(owner).discard_pile)
            )
            enemies = ai_query.enemy_cards(gs, owner)
            if not enemies:
                bonus += _P["spb_no_enemy_penalty"]
            else:
                effective_hits = min(my_units, len(enemies) * 2)
                bonus += effective_hits * _P["spb_hit_value"]
                if len(enemies) >= 3:
                    bonus += _P["spb_mass_clear"]
                other_unit_playables = sum(
                    1 for c in gs.get_player(owner).hand
                    if c != "SPB" and ai_query.is_playable_unit_card(c)
                )
                bonus -= other_unit_playables * _P["spb_other_unit_discount"]

        if card_name == "ADCB":
            if tokens == 2:
                bonus += _P["adcb_token_2"]
            elif tokens == 1:
                bonus += _P["adcb_token_1"]
            engines = sum(
                1 for c in gs.get_player(owner).on_board
                if c.health > 0 and c.job_and_color in (
                    "APB", "LFB", "ASSB", "TANKB", "APTB",
                )
            )
            bonus += engines * _P["adcb_per_engine"]

        if card_name == "HFB":
            if tokens == 0:
                bonus += _P["hfb_no_token_penalty"]
            elif tokens >= 2:
                bonus += _P["hfb_high_token"]

        if card_name == "APB":
            bonus += _P["apb"]

        if card_name == "LFB":
            enemies = ai_query.enemy_cards(gs, owner)
            in_range_targets = ai_query.attack_targets_from_pos(
                gs, owner, x, y, "small_cross",
            )
            if len(in_range_targets) >= 2:
                bonus += _P["lfb_multi_target"]
            elif len(enemies) >= 2:
                bonus += _P["lfb_target_rich"]
            else:
                bonus += _P["lfb_sparse_penalty"]

        if card_name == "APTB":
            bonus += _P["aptb"]

        return base_score + bonus
