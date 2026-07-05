from __future__ import annotations
import copy
import types
from typing import TYPE_CHECKING, Optional

from campaign.ai_strategies.base import Strategy, PlacementChoice, AttackChoice
from campaign import ai_query, ai_evaluator
from campaign.config_loader import CAMPAIGN_SETTINGS
from core.game_action import GameAction

if TYPE_CHECKING:
    from core.game_state import GameState


class _NullLogger:
    def __getattr__(self, name):
        return self._noop

    @staticmethod
    def _noop(*args, **kwargs):
        return None


_NULL_LOGGER = _NullLogger()
_STUB = types.SimpleNamespace(
    dying_cards=[],
    card_renderer=types.SimpleNamespace(release=lambda iid: None),
)

_PLACE_MIN = float(CAMPAIGN_SETTINGS["thresholds"]["placement_min_score"])
_ATK_MIN = float(CAMPAIGN_SETTINGS["thresholds"]["attack_min_score"])
_LETHAL = float(CAMPAIGN_SETTINGS["thresholds"]["lethal_score_threshold"])
_PANIC = CAMPAIGN_SETTINGS["panic"]
_PANIC_MIN = float(_PANIC["min_panic_threshold"])
_PANIC_BELOW = int(_PANIC["deficit_no_drop_below"])
_PANIC_STEP = float(_PANIC["deficit_drop_per_step"])


def _atk_min_for(sim, who):
    deficit = -sim.score if who == "player2" else sim.score
    if deficit <= _PANIC_BELOW:
        return _ATK_MIN
    return max(_PANIC_MIN, _ATK_MIN - (deficit - _PANIC_BELOW) * _PANIC_STEP)

_TERMINAL = 1e6


class _Node:
    __slots__ = ("sim", "disp", "first", "ended", "outcome", "quick")

    def __init__(self, sim, disp, first, ended, outcome, quick):
        self.sim = sim
        self.disp = disp
        self.first = first
        self.ended = ended
        self.outcome = outcome
        self.quick = quick


class ClaudeStrategy(Strategy):

    placement_min_score = 1.0
    attack_min_score = 1.0

    beam_width = 10
    depth_cap = 8
    cells_per_card = 5
    max_place_cands = 10
    leaf_pool = 10
    opp_action_cap = 18
    my_action_cap = 12
    w_income = 2.4
    w_material = 0.10
    w_blade = 0.5

    def __init__(self):
        self._base = Strategy()
        self._cache_key = None
        self._cache_val = None
        self._opp_strat = self._base

    def _infer_opp_strategy(self, gs, opp):
        from campaign.ai_strategies.white import WhiteStrategy
        from campaign.ai_strategies.red import RedStrategy
        from campaign.ai_strategies.blue import BlueStrategy
        from campaign.ai_strategies.green import GreenStrategy
        from campaign.ai_strategies.orange import OrangeStrategy
        colors = {}
        p = gs.get_player(opp)
        cards = [c.job_and_color for c in p.on_board] + list(p.discard_pile) + list(getattr(p, "revealed_deck", []))
        for name in cards:
            job, color = ai_evaluator.parse_card_name(name)
            if color:
                colors[color] = colors.get(color, 0) + 1
        if not colors:
            return self._base
        top = max(colors, key=colors.get)
        mapping = {"White": WhiteStrategy, "Red": RedStrategy, "Blue": BlueStrategy,
                   "Green": GreenStrategy, "Orange": OrangeStrategy}
        cls = mapping.get(top)
        return cls() if cls else self._base

    def best_placement(self, gs: "GameState", owner: str) -> Optional[PlacementChoice]:
        plan = self._plan(gs, owner)
        if plan is None:
            return self._base.best_placement(gs, owner)
        return plan[0]

    def best_attack(self, gs: "GameState", owner: str) -> Optional[AttackChoice]:
        plan = self._plan(gs, owner)
        if plan is None:
            return self._base.best_attack(gs, owner)
        return plan[1]

    def _signature(self, gs, owner):
        cells = []
        for p in (gs.player1, gs.player2):
            for c in p.on_board:
                cells.append((c.owner, c.board_x, c.board_y, c.job_and_color,
                              c.health, c.armor, c.numbness))
        return (owner, gs.turn_number, gs.score,
                gs.number_of_attacks.get(owner, 0),
                tuple(gs.get_player(owner).hand), tuple(sorted(cells)))

    def _plan(self, gs, owner):
        key = self._signature(gs, owner)
        if key == self._cache_key:
            return self._cache_val
        try:
            result = self._search(gs, owner)
        except Exception:
            result = None
        self._cache_key = key
        self._cache_val = result
        return result

    def _clone(self, gs):
        return copy.deepcopy(gs, {id(gs.game_logger): _NULL_LOGGER})

    def _step(self, sim, disp, action):
        res = disp.dispatch(action, sim)
        sim.update()
        sim.player1.logic_update(sim, _STUB, False)
        sim.player2.logic_update(sim, _STUB, False)
        sim.neutral.update(sim, _STUB)
        _STUB.dying_cards.clear()
        sim.pending_combat_events.clear()
        sim.pending_attacks.clear()
        if res is not None and getattr(res, "quit", False):
            return getattr(res, "message", "") or "over"
        return None

    def _greedy_action(self, sim, who, strat=None):
        strat = strat or self._base
        attack = strat.best_attack(sim, who)
        play = strat.best_placement(sim, who)
        if attack is not None and attack.score >= _LETHAL:
            return GameAction(player=who, action_type="attack",
                              board_x=attack.x, board_y=attack.y)
        if play is not None and play.score >= _PLACE_MIN:
            return GameAction(player=who, action_type="play_card",
                              board_x=play.x, board_y=play.y, hand_index=play.hand_index)
        if attack is not None and attack.score >= _atk_min_for(sim, who):
            return GameAction(player=who, action_type="attack",
                              board_x=attack.x, board_y=attack.y)
        return None

    def _move_action(self, sim, who):
        movers = ai_query.units_with_pending_move(sim, who)
        if movers:
            selected = [m for m in movers if m.mouse_selected]
            if selected:
                unit = selected[0]
                dests = ai_query.move_destinations_for(sim, unit)
                if not dests:
                    return None
                best = max(dests, key=lambda d: ai_evaluator.score_move_destination(unit, d, sim))
                return GameAction(player=who, action_type="move_to",
                                  board_x=best[0], board_y=best[1])
            def uscore(u):
                dests = ai_query.move_destinations_for(sim, u)
                if not dests:
                    return float("-inf")
                return max(ai_evaluator.score_move_destination(u, d, sim) for d in dests)
            unit = max(movers, key=uscore)
            if uscore(unit) == float("-inf"):
                return None
            return GameAction(player=who, action_type="move_to",
                              board_x=unit.board_x, board_y=unit.board_y)
        if sim.number_of_movings.get(who, 0) > 0:
            on_board = sim.get_player(who).on_board
            if not any(c.moving for c in on_board):
                cands = [c for c in on_board if not c.numbness and c.health > 0]
                if cands:
                    def dscore(u):
                        dests = ai_query.move_destinations_for(sim, u)
                        if not dests:
                            return float("-inf")
                        return max(ai_evaluator.score_move_destination(u, d, sim) for d in dests)
                    unit = max(cands, key=dscore)
                    if dscore(unit) > 0:
                        return GameAction(player=who, action_type="move_to",
                                          board_x=unit.board_x, board_y=unit.board_y)
        hand = sim.get_player(who).hand
        if "MOVEO" in hand:
            movable = [c for c in sim.get_player(who).on_board
                       if not c.numbness and c.health > 0 and ai_query.move_destinations_for(sim, c)]
            if movable:
                return GameAction(player=who, action_type="play_card",
                                  board_x=0, board_y=0, hand_index=hand.index("MOVEO"))
        return None

    def _greedy_turn(self, sim, disp, who, cap, strat=None):
        for _ in range(cap):
            cur = "player1" if sim.turn_number % 2 == 0 else "player2"
            if cur != who:
                return None
            act = self._move_action(sim, who)
            if act is None:
                act = self._greedy_action(sim, who, strat)
            if act is None:
                act = GameAction(player=who, action_type="end_turn")
            over = self._step(sim, disp, act)
            if over:
                return over
            if act.action_type == "end_turn":
                return None
        return self._step(sim, disp, GameAction(player=who, action_type="end_turn"))

    def _value(self, sim, owner, opp):
        lead = sim.score if owner == "player2" else -sim.score
        inc = mat = 0.0
        for p, sign in ((sim.get_player(owner), 1.0), (sim.get_player(opp), -1.0)):
            for c in p.on_board:
                if c.health <= 0:
                    continue
                per = ai_evaluator.estimate_score_per_turn(c.job_and_color)
                inc += sign * (per * (0.5 if c.numbness else 1.0))
                mat += sign * ((c.health + max(0, c.armor)) * 0.5 + (c.damage + c.extra_damage) * 1.2)
        blades = sim.number_of_attacks.get(owner, 0)
        return lead + self.w_income * inc + self.w_material * mat + self.w_blade * blades

    def _leaf_value(self, node, owner, opp):
        if node.outcome:
            return _TERMINAL if node.outcome == owner else -_TERMINAL
        sim = self._clone(node.sim)
        from core.battling_dispatcher import BattlingDispatcher
        disp = BattlingDispatcher(sim, mode="local")
        over = self._greedy_turn(sim, disp, opp, self.opp_action_cap, self._opp_strat)
        if over:
            return _TERMINAL if over == owner else -_TERMINAL
        over = self._greedy_turn(sim, disp, owner, self.my_action_cap)
        if over:
            return _TERMINAL if over == owner else -_TERMINAL
        over = self._greedy_turn(sim, disp, opp, self.opp_action_cap, self._opp_strat)
        if over:
            return (_TERMINAL if over == owner else -_TERMINAL) * 0.9
        return self._value(sim, owner, opp)

    def _candidates(self, sim, owner):
        player = sim.get_player(owner)
        cands = [None]
        seen = set()
        placings = []
        empties = ai_query.empty_positions(sim)
        for hi, card_name in enumerate(player.hand):
            if card_name in seen or not ai_query.is_playable_unit_card(card_name):
                continue
            seen.add(card_name)
            real = card_name[:-4] if card_name.endswith(" (+)") else card_name
            ranked = sorted(empties, key=lambda xy: -ai_evaluator.evaluate_placement(real, xy, sim, owner))
            for (x, y) in ranked[: self.cells_per_card]:
                placings.append((ai_evaluator.evaluate_placement(real, (x, y), sim, owner),
                                 ("play_card", x, y, hi)))
        placings.sort(key=lambda t: -t[0])
        cands.extend(a for _, a in placings[: self.max_place_cands])
        if sim.number_of_attacks.get(owner, 0) > 0:
            for c in ai_query.friendly_cards(sim, owner):
                if c.numbness or c.health <= 0:
                    continue
                if not ai_query.attack_targets_at(sim, c):
                    continue
                cands.append(("attack", c.board_x, c.board_y, None))
        return cands

    def _search(self, gs, owner):
        opp = "player2" if owner == "player1" else "player1"
        self._opp_strat = self._infer_opp_strategy(gs, opp)
        from core.battling_dispatcher import BattlingDispatcher
        root = self._clone(gs)
        beam = [_Node(root, BattlingDispatcher(root, mode="local"), None, False, None,
                      self._value(root, owner, opp))]
        finished = []
        for _ in range(self.depth_cap):
            frontier = []
            for node in beam:
                if node.ended:
                    finished.append(node)
                    continue
                for cand in self._candidates(node.sim, owner):
                    sim = self._clone(node.sim)
                    disp = BattlingDispatcher(sim, mode="local")
                    if cand is None:
                        act = GameAction(player=owner, action_type="end_turn")
                    else:
                        act = GameAction(player=owner, action_type=cand[0],
                                         board_x=cand[1], board_y=cand[2],
                                         hand_index=cand[3])
                    over = self._step(sim, disp, act)
                    first = node.first if node.first is not None else (cand if cand is not None else "END")
                    ended = over is not None or cand is None
                    child = _Node(sim, disp, first, ended, over,
                                  self._value(sim, owner, opp))
                    if over:
                        child.quick = _TERMINAL if over == owner else -_TERMINAL
                    frontier.append(child)
            if not frontier:
                break
            frontier.sort(key=lambda n: -n.quick)
            beam = frontier[: self.beam_width]
        finished.extend(n for n in beam if n.ended)
        if not finished:
            finished = beam
        if not finished:
            return (None, None)
        finished.sort(key=lambda n: -n.quick)
        pool = finished[: self.leaf_pool]
        best = None
        best_v = -float("inf")
        for node in pool:
            v = self._leaf_value(node, owner, opp)
            if v > best_v:
                best_v = v
                best = node
        if best is None or best.first == "END" or best.first is None:
            return (None, None)
        first = best.first
        if first[0] == "play_card":
            hand = gs.get_player(owner).hand
            hi = first[3]
            if hi >= len(hand):
                return (None, None)
            return (PlacementChoice(hi, hand[hi], first[1], first[2], 50.0), None)
        return (None, AttackChoice(first[1], first[2], _LETHAL + 1.0))
