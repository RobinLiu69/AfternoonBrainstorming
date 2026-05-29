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


TOKEN_VALUE: float = 4.0
"""Per-token value used in attack and placement scoring. 1 token ≈ 1/3 of a free
draw (3 → draw trigger) plus partial HFB ramp and ADCB token_draw value;
empirically tuned so APB's +2 tokens / hit clearly outweighs ADCB's chip swing
in the attack-comparison branch."""


def expected_tokens_from_attack(attacker, gs) -> int:
    """How many tokens the AI will likely net from `attacker` swinging right now.

    Maps each blue attacker's token-yield trigger to the targets currently in
    range. Ability-triggered yields (APB, LFB) scale by the number of damage
    events; kill-triggered yields (ADCB, ASSB) only count targets we can
    actually one-shot.
    """
    targets = ai_query.attack_targets_at(gs, attacker)
    if not targets:
        return 0
    name = attacker.job_and_color
    if name == "APB":
        return len(targets) * 2  # ability: +2 tokens per damage event
    if name == "LFB":
        return len(targets)      # ability: +1 token per damage event
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
    """Token-tempo faction. The win-condition pipeline:

    1. TANKB / APB / APTB sit front-line, eat damage, churn tokens passively.
    2. **SPB is the damage core** — on deploy hits N random enemies where
       N = on_board + discard_pile size. Late-game deploy = mass damage finisher.
       In attack: 5 damage / farthest pattern, highest single-shot in the faction.
    3. **LFB / ASSB are token harvesters held in hand** until conditions ripen:
       - LFB ability fires per damage event (chip many → many tokens).
       - ASSB needs the kill to give +2 tokens; held until a lethal setup exists
         (covered by `lethal_placement_bonus` triggering on its deploy).
    4. **HFB** consumes tokens: `extra_damage = current tokens`. Hold until tokens
       are accumulated; then it hits like a freight train.
    5. **ADCB on board at the moment tokens reach 3** → `token_draw` clears its
       numbness or enqueues an extra attack. Deploy BEFORE the threshold.

    The Strategy here teaches the AI to respect that ordering — early plays
    should be front-line + token producers, mid/late plays should be the
    payoff units (SPB / HFB) and the token-draw beneficiary (ADCB).
    """

    def attack_bonus(self, attacker, gs, base_score: float) -> float:
        tokens = gs.players_token.get(attacker.owner, 0)
        bonus = 0.0

        # Approaching 3 tokens — next damage event triggers a free draw.
        if tokens == 2:
            bonus += 16.0
        elif tokens == 1:
            bonus += 6.0

        # SPB is the dedicated damage core: 5 dmg, farthest pattern, prioritized.
        if attacker.job_and_color == "SPB":
            bonus += 12.0

        # HFB damage scales with current tokens. Pay attention to projected damage.
        if attacker.job_and_color == "HFB" and tokens >= 1:
            targets = ai_query.attack_targets_at(gs, attacker)
            for t in targets:
                effective = (attacker.damage + tokens) - max(0, t.armor)
                if effective > 0 and t.health <= effective:
                    bonus += 20.0
                    break
                bonus += min(effective, t.health) * 1.5
            bonus = min(bonus, 70.0)

        # LFB ability fires once per damage event — multi-target hit = multi-token.
        if attacker.job_and_color == "LFB":
            targets = ai_query.attack_targets_at(gs, attacker)
            bonus += len(targets) * 4.0

        # ADCB / ASSB generate tokens from kills (covered partly by base kill scoring;
        # add a small swing-encourage bonus).
        if attacker.job_and_color in ("ADCB", "ASSB"):
            bonus += 4.0

        # Token-yield maximization: weigh same-damage attack choices by expected
        # token income. Two attackers with the same kill potential should split
        # on token yield — APB hit (+2 tokens) beats ADCB chip (+0), LFB multi
        # (+1/target) shines on wide patterns.
        expected = expected_tokens_from_attack(attacker, gs)
        bonus += expected * TOKEN_VALUE

        # token_draw chain: if this attack crosses the threshold AND a non-numb
        # ADCB sits on the board, draw fires → ADCB enqueues a free attack.
        # Encourage the trigger swing.
        threshold = gs.how_many_token_to_draw_a_card
        if tokens + expected >= threshold:
            has_armed_adcb = any(
                c.job_and_color == "ADCB" and not c.numbness and c.health > 0
                for c in gs.get_player(attacker.owner).on_board
            )
            if has_armed_adcb:
                bonus += 12.0

        return base_score + bonus

    def placement_bonus(self, card_name, position, gs, owner, base_score: float) -> float:
        tokens = gs.players_token.get(owner, 0)
        x, y = position
        bonus = 0.0

        if card_name == "TANKB":
            # TANKB gets tokens when attacked. Closer to enemies = more incoming hits.
            dist = ai_query.nearest_enemy_distance(gs, owner, x, y)
            if dist <= 1:
                bonus += 12.0
            elif dist <= 2:
                bonus += 5.0

        if card_name == "SPB":
            # SPB is spell-like: the deploy effect IS the reason to place it.
            # Deploy hits N random enemies where N = my on_board + discard_pile.
            # Without enemies on board the deploy fires into the void; SPB then
            # just sits with 1 HP waiting to die. Heavy penalty when there's
            # nothing to deploy-damage, heavy bonus when the board is rich.
            my_units = (
                len(gs.get_player(owner).on_board) + len(gs.get_player(owner).discard_pile)
            )
            enemies = ai_query.enemy_cards(gs, owner)
            if not enemies:
                bonus -= 20.0  # save SPB for later
            else:
                effective_hits = min(my_units, len(enemies) * 2)
                bonus += effective_hits * 4.5
                if len(enemies) >= 3:
                    bonus += 8.0  # mass-clear payoff
                # Sequencing: every OTHER unit we can place first grows on_board,
                # so SPB hits one more enemy on its deploy. Defer SPB by
                # discounting once per pending unit-playable in hand.
                other_unit_playables = sum(
                    1 for c in gs.get_player(owner).hand
                    if c != "SPB" and ai_query.is_playable_unit_card(c)
                )
                bonus -= other_unit_playables * 5.0

        if card_name == "ADCB":
            # ADCB.token_draw:
            #   - if numb → clear numbness (first event after placement)
            #   - else    → enqueue a free attack
            # On board means: catch every subsequent token-draw event this turn AND
            # the next turns until ADCB dies. The more token engines we have, the
            # more free attacks ADCB nets.
            if tokens == 2:
                bonus += 18.0  # immediate token draw will arm ADCB
            elif tokens == 1:
                bonus += 6.0
            # Every on-board blue token generator = expected token cycle that
            # ADCB will cash in on a later turn.
            engines = sum(
                1 for c in gs.get_player(owner).on_board
                if c.health > 0 and c.job_and_color in (
                    "APB", "LFB", "ASSB", "TANKB", "APTB",
                )
            )
            bonus += engines * 4.0

        if card_name == "HFB":
            # HFB without tokens is a vanilla 2-damage HF. Hold for token loading.
            if tokens == 0:
                bonus -= 6.0
            elif tokens >= 2:
                bonus += 10.0

        if card_name == "APB":
            # AP gives +2 tokens per ability + numbs target. Always strong tempo.
            bonus += 5.0

        if card_name == "LFB":
            # LFB ability per damage = 1 token. Want many enemies in attack range so
            # subsequent attacks rake in tokens. Hold when the board is sparse.
            enemies = ai_query.enemy_cards(gs, owner)
            in_range_targets = ai_query.attack_targets_from_pos(
                gs, owner, x, y, "small_cross",  # blue LF attack pattern
            )
            if len(in_range_targets) >= 2:
                bonus += 8.0
            elif len(enemies) >= 2:
                bonus += 2.0  # board is target-rich but our position lacks reach
            else:
                bonus -= 6.0  # hold for a richer board

        # ASSB: hand_threat_penalty -20 already discourages random deployment; only
        # lethal_placement_bonus (deploy-kill) or defensive_placement_bonus brings it
        # out, which is exactly the user-described pattern.

        if card_name == "APTB":
            # APTB converts armor → tokens via after_token, accumulates armor itself.
            bonus += 3.0

        return base_score + bonus
