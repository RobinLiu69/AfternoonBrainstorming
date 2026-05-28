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


WHITE_DECK: list[str] = [
    "ADCW", "ADCW", "APW",
    "TANKW", "TANKW",
    "HFW", "HFW", "LFW",
    "ASSW", "ASSW", "APTW", "SPW",
]

RED_DECK: list[str] = [
    "ADCR", "ADCR", "APR",
    "TANKR", "TANKR",
    "HFR", "HFR", "LFR", "LFR",
    "ASSR", "ASSR", "SPR",
]

BLUE_DECK: list[str] = [
    "ADCB", "ADCB", "APB",
    "TANKB", "TANKB",
    "HFB", "LFB", "LFB",
    "ASSB", "ASSB", "APTB", "SPB",
]

GREEN_DECK: list[str] = [
    "ADCG", "ADCG", "APG",
    "TANKG", "TANKG",
    "HFG", "HFG", "LFG", "LFG",
    "ASSG", "APTG", "SPG",
]

ORANGE_DECK: list[str] = [
    "ADCO", "ADCO", "APO",
    "TANKO", "TANKO",
    "HFO", "HFO", "LFO", "LFO",
    "ASSO", "ASSO", "SPO",
]

BOSS_DECK: list[str] = [
    "ADCW", "ADCR",
    "TANKB", "TANKW",
    "LFO", "LFR",
    "ASSB", "ASSO",
    "HFO", "HFR",
    "SPR", "APTB",
]


STAGE_AI_DECKS: dict[str, list[str]] = {
    "white":  WHITE_DECK,
    "red":    RED_DECK,
    "blue":   BLUE_DECK,
    "green":  GREEN_DECK,
    "orange": ORANGE_DECK,
    "boss":   BOSS_DECK,
}

STAGE_PLAYER_DECKS: dict[str, list[str]] = {
    "white":  WHITE_DECK,
    "red":    WHITE_DECK,
    "blue":   WHITE_DECK,
    "green":  WHITE_DECK,
    "orange": WHITE_DECK,
    "boss":   WHITE_DECK,
}
"""Phase 1: player always uses a baseline white deck. Phase 4 may add deck-builder UI."""

STAGE_ORDER: list[str] = ["white", "red", "blue", "green", "orange", "boss"]

STAGE_DIFFICULTY: dict[str, str] = {
    "white":  "easy",
    "red":    "normal",
    "blue":   "normal",
    "green":  "hard",
    "orange": "hard",
    "boss":   "boss",
}

STAGE_LABELS: dict[str, str] = {
    "white":  "1. White  -  Tutorial",
    "red":    "2. Red    -  Damage Snowball",
    "blue":   "3. Blue   -  Token Tempo",
    "green":  "4. Green  -  Lucky Chaos",
    "orange": "5. Orange -  Mobile Counter",
    "boss":   "B. Boss   -  Mixed Elite",
}
