from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.draft_state import DraftState
from core.network_layer import LANServer, LANClient
from screens.draft.draft_action import DraftAction

MAGIC_CARDS = ["CUBES", "MOVE", "MOVEO", "HEAL"]
MAX_DECK = 12
MAX_UNIT = 2
MAX_MAGIC = 3


@dataclass
class DraftResult:
    success: bool
    phase_advanced: bool = False
    ready_to_start: bool = False
    message: str = ""


class DraftDispatcher:
    def __init__(self, draft_state: DraftState, mode: str = "local"):
        self.mode = mode
        self._network = None
        self._draft_state: DraftState = draft_state

    def attach_server(self, server: "LANServer") -> None:
        """Call this before server.start() when running in lan_server mode."""
        self._network = server
        server.on_action = self._on_remote_action

    def attach_client(self, client: "LANClient") -> None:
        """Call this before client.connect() when running in lan_client mode."""
        self._network = client

    def dispatch(self, action: DraftAction, draft_state: DraftState) -> DraftResult:
        self._draft_state = draft_state

        match self.mode:
            case "local":
                return self._execute(action, draft_state)

            case "lan_client":
                result = self._execute(action, draft_state)
                if result.success:
                    self._send_to_server(action)
                return result

            case "lan_server":
                result = self._execute(action, draft_state)
                if result.success:
                    self._broadcast(draft_state)
                return result

        return DraftResult(False, message=f"unknown mode: {self.mode}")

    def _on_remote_action(self, action_dict: dict) -> None:
        """
        Server-side: called from the background accept thread when the remote
        client sends an action.  Executes it, then broadcasts the new state.
        """
        try:
            action = DraftAction(**action_dict)
        except TypeError as e:
            print(f"[DraftDispatcher] Bad remote action payload: {e}")
            return

        result = self._execute(action, self._draft_state)
        if result.success:
            self._broadcast(self._draft_state)

    def _send_to_server(self, action: DraftAction) -> None:
        """Client-side: serialise and send a DraftAction to the host."""
        if not isinstance(self._network, LANClient):
            print("[DraftDispatcher] No network attached — cannot send action.")
            return
        self._network.send_action({
            "action_type": action.action_type,
            "player":      action.player,
            "card_name":   action.card_name,
        })

    def _broadcast(self, draft_state: DraftState) -> None:
        """Server-side: push the full state to all connected clients."""
        if not isinstance(self._network, LANServer):
            return
        self._network.broadcast(draft_state.to_dict())


    def _execute(self, action: DraftAction, draft_state: DraftState) -> DraftResult:
        deck = (draft_state.player1_deck if action.player == "player1" else draft_state.player2_deck)

        if action.action_type in ("add_card", "remove_card", "remove_last_card"):
            if draft_state.current_editor() != action.player:
                return DraftResult(False, message="Its not your turn")

        match action.action_type:
            case "add_card":
                if not action.card_name or action.card_name == "None":
                    return DraftResult(False)
                if len(deck) >= MAX_DECK:
                    return DraftResult(False, message="Deck is full")
                is_magic = action.card_name in MAGIC_CARDS
                limit = MAX_MAGIC if is_magic else MAX_UNIT
                if deck.count(action.card_name) >= limit:
                    return DraftResult(False, message="Over limit")
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
                return DraftResult(True, phase_advanced=True)

            case "toggle_timer":
                draft_state.timer_mode = (
                    "countdown" if draft_state.timer_mode == "timer" else "timer"
                )
                return DraftResult(True)

            case "toggle_file_save":
                draft_state.file_auto_delete = not draft_state.file_auto_delete
                return DraftResult(True)

        return DraftResult(False, message=f"unknown action: {action.action_type}")