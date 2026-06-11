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
import json
import os

from shared.setting import FOLDER_PATH


_DEFAULTS: dict = {
    "ai_delay_ms": {
        "turn_start": 900,
        "action": 650,
        "attack": 500,
        "busy_recheck": 120,
    },
    "thresholds": {
        "placement_min_score": 1.0,
        "attack_min_score": 15.0,
        "lethal_score_threshold": 100.0,
    },
    "scoring": {
        "kill_bonus_base": 100.0,
        "kill_bonus_per_threat": 10.0,
        "score_income_multiplier": 8.0,
        "hand_threat_value": {"ASS": 20.0},
    },
    "threat_model": {
        "ass_threat_damage": 5,
        "incoming_kill_penalty": 30.0,
        "incoming_chip_penalty_per_damage": 1.5,
    },
    "faction_overrides": {
        "white": {"attack_min_score": 10.0},
        "red": {"attack_min_score": 12.0},
        "blue": {"attack_min_score": 13.0},
        "orange": {"attack_min_score": 12.0},
        "boss": {"attack_min_score": 13.0},
    },
    "heal": {
        "amount": 6,
        "min_amount": 3,
        "min_score": 12.0,
        "low_ratio_threshold": 0.4,
        "low_ratio_bonus": 10.0,
        "save_from_lethal_base": 30.0,
        "save_from_lethal_damage_mult": 3.0,
        "score_income_mult": 4.0,
        "damage_mult": 1.5,
    },
    "panic": {
        "min_panic_threshold": 8.0,
        "deficit_no_drop_below": 2,
        "deficit_drop_per_step": 3.5,
    },
    "stage_buffs": {
        "green":  {"initial_luck": 65},
        "orange": {"free_moving_every_n_turns": 3},
        "boss":   {"unit_hp_plus": 1, "initial_hand_size": 4, "free_heal_every_n_turns": 5},
    },
    "stage_buff_text_templates": {
        "initial_luck":              "AI starts with {value}% luck",
        "initial_hand_size":         "AI starts with {value} cards",
        "unit_hp_plus":              "AI units +{value} HP",
        "free_moving_every_n_turns": "AI gains +1 movement every {value} turns",
        "free_heal_every_n_turns":   "AI gains +1 heal every {value} turns",
    },
    "strategy_bonuses": {
        "red": {
            "damage_grown_per_stack": 6.0,
            "hfr_baseline": 8.0,
            "hfr_anger_bonus": 20.0,
            "adcr_baseline": 5.0,
            "apr_baseline": 7.0,
            "apr_target_damage_mult": 1.5,
            "placement": {"LFR": 5.0, "SPR": 4.0, "HFR": 3.0},
        },
        "blue": {
            "token_value": 4.0,
            "tokens_at_2": 16.0,
            "tokens_at_1": 6.0,
            "spb_baseline": 12.0,
            "hfb_kill_bonus": 20.0,
            "hfb_chip_mult": 1.5,
            "hfb_cap": 70.0,
            "lfb_per_target": 4.0,
            "adcb_assb_baseline": 4.0,
            "token_draw_chain": 12.0,
            "placement": {
                "tankb_close": 12.0,
                "tankb_mid": 5.0,
                "spb_no_enemy_penalty": -20.0,
                "spb_hit_value": 4.5,
                "spb_mass_clear": 8.0,
                "spb_other_unit_discount": 5.0,
                "adcb_token_2": 18.0,
                "adcb_token_1": 6.0,
                "adcb_per_engine": 4.0,
                "hfb_no_token_penalty": -6.0,
                "hfb_high_token": 10.0,
                "apb": 5.0,
                "lfb_multi_target": 8.0,
                "lfb_target_rich": 2.0,
                "lfb_sparse_penalty": -6.0,
                "aptb": 3.0,
            },
        },
        "green": {
            "lfg_per_block": 45.0,
            "hfg_per_block": 30.0,
            "adcg_per_empty_cell": 2.0,
            "adcg_cap": 8.0,
            "placement": {
                "aptg_yield_mult": 8.0,
                "aptg_baseline": 6.0,
                "lfg_adj_block": 18.0,
                "lfg_adj_apt": 10.0,
                "hfg_adj_block": 14.0,
                "hfg_adj_apt": 8.0,
                "spg_cap": 20.0,
                "spg_luck_mult": 0.4,
            },
        },
        "orange": {
            "adco_score_mult": 0.4,
            "adco_reach_mult": 2.0,
            "lfo_baseline": 8.0,
            "hfo_baseline": 12.0,
            "hfo_extra_damage_mult": 6.0,
            "hfo_multi_target_bonus": 5.0,
            "asso_anger_bonus": 25.0,
            "asso_setup_bonus": 4.0,
            "placement": {
                "mover_openness_mult": 2.0,
                "tanko_front_line": 8.0,
                "spo_per_mover": 4.0,
                "apto_per_friendly": 2.5,
                "apto_cap": 12.0,
            },
        },
        "boss": {
            "tank_vs_heavy_dmg": 5.0,
            "ass_vs_beefy": 6.0,
            "trailing_attack_bonus": 5.0,
            "heavy_dmg_threshold": 4,
            "beefy_hp_threshold": 6,
            "trailing_threshold": -2,
        },
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_campaign_settings() -> dict:
    path = os.path.join(FOLDER_PATH, "config", "campaign_setting.json")
    if not os.path.isfile(path):
        return _DEFAULTS
    try:
        with open(path, "r", encoding="utf-8") as f:
            user = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _DEFAULTS
    return _deep_merge(_DEFAULTS, user)


CAMPAIGN_SETTINGS: dict = load_campaign_settings()
