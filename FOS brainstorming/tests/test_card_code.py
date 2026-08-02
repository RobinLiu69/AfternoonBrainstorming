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

from shared import card_code


def test_plain_codes_round_trip_untouched():
    for name in ("TANKW", "ADCBR", "CUBES", "MOVEO"):
        assert card_code.base_code(name) == name
        assert card_code.plain_code(name) == name
        assert card_code.enchant_keys(name) == ()
        assert card_code.is_enchanted(name) is False


def test_upgrade_suffix_survives_enchanting():
    enchanted = card_code.add_enchant("APC (+)", "mana")
    assert enchanted == "APC*mana (+)"
    assert card_code.base_code(enchanted) == "APC (+)"
    assert card_code.plain_code(enchanted) == "APC"
    assert card_code.enchant_keys(enchanted) == ("mana",)


def test_multiple_enchants_keep_order_and_dedupe():
    name = card_code.add_enchant(card_code.add_enchant("TANKW", "sharp"), "fort")
    assert name == "TANKW*sharp.fort"
    assert card_code.add_enchant(name, "sharp") == name
    assert card_code.enchant_keys(name) == ("sharp", "fort")


def test_remove_enchants_returns_base():
    assert card_code.remove_enchants("TANKW*sharp.fort") == "TANKW"
    assert card_code.remove_enchants("APC*mana (+)") == "APC (+)"


def test_has_enchant():
    assert card_code.has_enchant("LFR*bleed", "bleed") is True
    assert card_code.has_enchant("LFR*bleed", "sharp") is False
