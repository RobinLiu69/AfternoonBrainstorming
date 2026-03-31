from core.draft_state import DraftState
from screens.draft.draft_action import DraftAction
from dataclasses import dataclass

MAGIC_CARDS = ["CUBES", "MOVE", "MOVEO", "HEAL"]
MAX_DECK    = 12
MAX_UNIT    = 2
MAX_MAGIC   = 3

@dataclass
class DraftResult:
    success: bool
    phase_advanced: bool = False
    ready_to_start: bool = False
    message: str = ""


class DraftDispatcher:
    def __init__(self, mode: str = "local"):
        self.mode    = mode
        self._network = None

    def dispatch(self, action: DraftAction, draft_state: DraftState) -> DraftResult:
        match self.mode:
            case "local":
                return self._execute(action, draft_state)
            case "lan_client":
                return self._send_to_server(action)
            case "lan_server":
                result = self._execute(action, draft_state)
                self._broadcast(draft_state)
                return result
        return DraftResult(False, message=f"unknow mode: {self.mode}")
        
    def _execute(self, action: DraftAction, draft_state: DraftState) -> DraftResult:
        deck = (draft_state.player1_deck if action.player == "player1" else draft_state.player2_deck)

        if action.action_type in ("add_card", "remove_card", "remove_last_card"):
            if draft_state.current_editor() != action.player:
                return DraftResult(False, message="目前不是你的選牌階段")

        match action.action_type:
            case "add_card":
                if not action.card_name or action.card_name == "None":
                    return DraftResult(False)
                if len(deck) >= MAX_DECK:
                    return DraftResult(False, message="牌組已滿")
                is_magic = action.card_name in MAGIC_CARDS
                limit = MAX_MAGIC if is_magic else MAX_UNIT
                if deck.count(action.card_name) >= limit:
                    return DraftResult(False, message="超過攜帶上限")
                deck.append(action.card_name)
                return DraftResult(True)

            case "remove_card":
                if action.card_name and action.card_name in deck:
                    idx = len(deck) - 1 - deck[::-1].index(action.card_name)
                    deck.pop(idx)
                return DraftResult(True)

            case "remove_last_card":
                if deck:
                    deck.pop()
                return DraftResult(True)

            case "advance_phase":
                if not draft_state.can_advance():
                    return DraftResult(False)
                draft_state.advance_phase()
                if draft_state.phase == "done":
                    return DraftResult(True, phase_advanced=True)
                return DraftResult(True, phase_advanced=True)

            case "toggle_timer":
                draft_state.timer_mode = (
                    "countdown" if draft_state.timer_mode == "timer" else "timer"
                )
                return DraftResult(True)

            case "toggle_file_save":
                draft_state.file_auto_delete = not draft_state.file_auto_delete
                return DraftResult(True)

        return DraftResult(False, message=f"unknow action: {action.action_type}")

    def _send_to_server(self, action: DraftAction) -> DraftResult:
        raise NotImplementedError

    def _broadcast(self, draft_state: DraftState) -> None:
        raise NotImplementedError