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

import re
from pathlib import Path

from cards.card_white import Tank as WhiteTank
from core.game_state import GameState
from core.game_statistics import StatType
from tests.helpers import make_game_state, place_card, do_attack


def labels(game_state: GameState) -> list[str]:
    return [event.text for event in game_state.pending_combat_events
            if event.kind == "float" and event.text]


def kinds_at(game_state: GameState, x: int, y: int) -> set[str]:
    return {event.kind for event in game_state.pending_combat_events
            if (event.board_x, event.board_y) == (x, y)}


class TestStatAdjustAnimates:
    def test_a_buff_floats_one_green_label_for_every_stat_it_touched(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, armor=3, damage=3)

        assert labels(gs) == ["+3 SHIELD +3 ATK"]
        assert all(event.good for event in gs.pending_combat_events if event.text)
        assert (card.armor, card.damage) == (3, WhiteTank("player1", 0, 0).damage + 3)

    def test_a_debuff_floats_a_red_label(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, damage=-1)

        assert labels(gs) == ["-1 ATK"]
        assert not any(event.good for event in gs.pending_combat_events if event.text)

    def test_losing_health_plays_a_hurt_and_a_damage_number(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        before = card.health
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, health=-2)

        assert card.health == before - 2
        assert kinds_at(gs, 1, 1) == {"hurt", "float"}
        assert [e.damage for e in gs.pending_combat_events if e.kind == "float"] == [2]

    def test_losing_the_last_health_also_plays_a_death(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        card.health = 1
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, health=-3)

        assert card.health == 0
        assert card.pending_death is True
        assert "death" in kinds_at(gs, 1, 1)

    def test_a_lethal_adjustment_runs_the_victims_death_hook(self) -> None:
        from cards.card_cyan import Hf as CyanHf

        gs = make_game_state()
        card = place_card(gs, CyanHf, "player2", 1, 1)
        card.upgrade = True
        card.health = 1
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, health=-1)

        assert card.anger is True
        assert card.pending_death is False
        assert "death" not in kinds_at(gs, 1, 1)

    def test_a_lethal_adjustment_credits_the_source_with_the_kill(self) -> None:
        gs = make_game_state()
        killer = place_card(gs, WhiteTank, "player1", 0, 0)
        victim = place_card(gs, WhiteTank, "player2", 1, 1)
        victim.health = 1
        gs.pending_combat_events.clear()

        victim.adjust_stats(gs, health=-1, source=killer)

        assert gs.game_statistics.get(StatType.KILLED, killer.get_uid()) == 1
        assert gs.game_statistics.get(StatType.DEATH, victim.get_uid()) == 1

    def test_a_lethal_adjustment_without_a_source_still_records_the_death(self) -> None:
        gs = make_game_state()
        victim = place_card(gs, WhiteTank, "player2", 1, 1)
        victim.health = 1
        gs.pending_combat_events.clear()

        victim.adjust_stats(gs, health=-1)

        assert gs.game_statistics.get(StatType.DEATH, victim.get_uid()) == 1
        assert victim.pending_death is True

    def test_a_mixed_adjustment_never_reads_as_a_buff(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        card.armor = 2
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, armor=-2, damage=3)

        assert labels(gs) == ["-2 SHIELD +3 ATK"]
        assert not any(event.good for event in gs.pending_combat_events if event.text)

    def test_a_healing_adjustment_respects_the_health_cap(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        card.health = card.max_health - 1
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, health=5)

        assert card.health == card.max_health
        assert labels(gs) == ["+5 HP"]

    def test_stats_never_go_below_zero(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        card.damage = 0
        card.armor = 1
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, damage=-5, armor=-5, extra_damage=-5)

        assert (card.damage, card.armor, card.extra_damage) == (0, 0, 0)

    def test_touching_nothing_animates_nothing(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs)

        assert gs.pending_combat_events == []

    def test_the_caller_can_hold_the_label_back(self) -> None:
        gs = make_game_state()
        card = place_card(gs, WhiteTank, "player1", 1, 1)
        gs.pending_combat_events.clear()

        card.adjust_stats(gs, damage=1, anim_delay=0.5)

        assert [event.delay for event in gs.pending_combat_events] == [0.5]


class TestEveryFactionRoutesThroughTheInterface:
    STAT_WRITE = re.compile(
        r"(?P<owner>\w+)\.(?P<stat>health|damage|armor|extra_damage)\s*(=(?!=)|\+=|-=|\*=|//=|%=)")
    SHIELD_WRITE = re.compile(
        r"\w+\.(armor|extra_damage)\s*(=(?!=)|\+=|-=|\*=|//=|%=)")
    DERIVED_REFRESH = ("self", "extra_damage")

    def _scan(self, pattern: re.Pattern, allow_derived: bool, *globs: str) -> list[str]:
        root = Path(__file__).resolve().parent.parent
        found: list[str] = []
        for glob in globs:
            for path in sorted(root.glob(glob)):
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    match = pattern.search(line)
                    if not match:
                        continue
                    if allow_derived and (match.group("owner"), match.group("stat")) == self.DERIVED_REFRESH:
                        continue
                    found.append(f"{path.name}:{number}: {line.strip()}")
        return found

    def test_no_faction_file_adjusts_a_stat_by_hand(self) -> None:
        assert self._scan(self.STAT_WRITE, True, "cards/card_*.py") == []

    def test_the_guard_still_sees_a_plain_assignment(self) -> None:
        assert self.STAT_WRITE.search("target.armor = 0")
        assert self.STAT_WRITE.search("self.health = 0")
        assert self.STAT_WRITE.search("card.armor += awards")
        assert not self.STAT_WRITE.search("if target.health == 0:")

    def test_nothing_outside_the_cards_hands_out_a_shield_by_itself(self) -> None:
        assert self._scan(self.SHIELD_WRITE, False, "tower/*.py", "campaign/*.py",
                          "campaign/ai_strategies/*.py", "endless/*.py") == []


class TestFactionBuffsAnnounce:
    def _labels(self, game_state: GameState) -> list[str]:
        return [event.text for event in game_state.pending_combat_events
                if event.kind == "float" and event.text]

    def test_a_white_shield_buff_floats_on_every_card_it_touched(self) -> None:
        from cards.card_white import Apt as WhiteApt

        gs = make_game_state()
        apt = place_card(gs, WhiteApt, "player1", 0, 0)
        place_card(gs, WhiteTank, "player1", 1, 0)
        place_card(gs, WhiteTank, "player2", 0, 1)

        do_attack(apt, gs)

        assert self._labels(gs) == [f"+{apt.damage} SHIELD"] * 2

    def test_a_red_snowball_floats_once_per_card_it_buffed(self) -> None:
        from cards.card_red import Apt as RedApt, Sp as RedSp

        gs = make_game_state()
        apt = place_card(gs, RedApt, "player1", 0, 0)
        place_card(gs, RedSp, "player1", 1, 0)
        place_card(gs, WhiteTank, "player2", 0, 1)

        do_attack(apt, gs)

        assert len(self._labels(gs)) == 3
        assert all("SHIELD" in label and "ATK" in label for label in self._labels(gs))

    def test_a_purple_strip_reports_what_it_took(self) -> None:
        from cards.card_purple import Ap as PurpleAp

        gs = make_game_state()
        mage = place_card(gs, PurpleAp, "player1", 0, 0)
        victim = place_card(gs, WhiteTank, "player2", 0, 1)
        victim.armor = 4
        victim.damage = victim.original_damage + 3
        gs.pending_combat_events.clear()

        do_attack(mage, gs)

        assert victim.nullify is True
        assert victim.armor == 0
        assert victim.damage == victim.original_damage
        assert self._labels(gs) == ["-4 SHIELD -3 ATK"]


class TestGreenKeepsItsOwnWording:
    def _labels(self, game_state: GameState) -> list[str]:
        return [event.text for event in game_state.pending_combat_events
                if event.kind == "float" and event.text]

    def test_a_fortune_roll_never_adds_a_generic_label(self) -> None:
        from cards.card_green import GreenCard

        descriptive = {"+4 ARMOR", "ATK x2", "FREE STRIKE", "FREE MOVE", "SPAWN BLOCKS",
                       "ARMOR GONE", "NUMBED", "HP HALVED", "ATK HALVED", "-2 HP", "NO EFFECT"}
        for seed in range(120):
            gs = make_game_state(rng_seed=seed)
            target = place_card(gs, WhiteTank, "player2", 1, 1)
            target.armor = 3
            gs.pending_combat_events.clear()

            GreenCard.lucky_effects(target, gs)

            assert set(self._labels(gs)) <= descriptive

    def test_halving_the_last_health_point_now_plays_a_death(self) -> None:
        from cards.card_green import GreenCard

        for seed in range(200):
            gs = make_game_state(rng_seed=seed)
            target = place_card(gs, WhiteTank, "player2", 1, 1)
            target.health = 1
            gs.pending_combat_events.clear()

            GreenCard.lucky_effects(target, gs)
            if "HP HALVED" in self._labels(gs):
                assert target.health == 0
                assert target.pending_death is True
                assert "death" in {event.kind for event in gs.pending_combat_events}
                return

        raise AssertionError("no seed rolled the halving jinx")
