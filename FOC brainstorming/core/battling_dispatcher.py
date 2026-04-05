from typing import TYPE_CHECKING

from core.game_action import GameAction, ActionResult
from core.game_state import GameState

if TYPE_CHECKING:
    from network_layer import LANServer, LANClient


class BattlingDispatcher:
    def __init__(self, mode: str = "local"):
        self.mode = mode
        self._network = None
        self._game_state: GameState | None = None

    def attach_server(self, server: "LANServer") -> None:
        """Call before server.start() when running in lan_server mode."""
        self._network = server
        server.on_action = self._on_remote_action

    def attach_client(self, client: "LANClient") -> None:
        """Call before client.connect() when running in lan_client mode."""
        self._network = client

    def dispatch(self, action: GameAction, game_state: GameState) -> ActionResult:
        self._game_state = game_state

        match self.mode:
            case "local":
                return self._execute(action, game_state)

            case "lan_client":
                # Optimistic local execution for instant feedback;
                # server is authoritative and will broadcast the real state.
                result = self._execute(action, game_state)
                if result.success:
                    self._send_to_server(action)
                return result

            case "lan_server":
                result = self._execute(action, game_state)
                if result.success:
                    self._broadcast_state(game_state)
                return result

        return ActionResult(False, message=f"unknown mode: {self.mode}")

    def _on_remote_action(self, action_dict: dict) -> None:
        """
        Server-side: called from the background thread when the remote
        client sends an action.  Executes it, then broadcasts the new state.
        """
        if self._game_state is None:
            return
        try:
            action = GameAction(**action_dict)
        except TypeError as e:
            print(f"[BattlingDispatcher] Bad remote action payload: {e}")
            return

        result = self._execute(action, self._game_state)
        if result.success:
            self._broadcast_state(self._game_state)

    def _send_to_server(self, action: GameAction) -> None:
        """Client-side: serialise and send a GameAction to the host."""
        if not isinstance(self._network, LANClient):
            print("[BattlingDispatcher] No network attached — cannot send action.")
            return
        self._network.send_action({
            "action_type": action.action_type,
            "player":      action.player,
            "board_x":     action.board_x,
            "board_y":     action.board_y,
            "hand_index":  action.hand_index,
        })

    def _broadcast_state(self, game_state: GameState) -> None:
        """Server-side: push the full state to all connected clients."""
        if not isinstance(self._network, LANServer):
            return
        self._network.broadcast(game_state.to_dict())

    def _execute(self, action: GameAction, game_state: GameState) -> ActionResult:
        player = game_state.get_player(action.player)

        match action.action_type:
            case "attack":
                if action.board_x is None or action.board_y is None:
                    return ActionResult(False, message="需要棋盤座標")
                if game_state.number_of_attacks[action.player] <= 0:
                    return ActionResult(False, message="攻擊次數不足")
                player.attack(action.board_x, action.board_y, game_state)
                return ActionResult(True)

            case "play_card":
                if action.hand_index is None:
                    return ActionResult(False)
                if action.board_x is None or action.board_y is None:
                    return ActionResult(False)
                player.play_card(action.board_x, action.board_y, action.hand_index, game_state)
                return ActionResult(True)

            case "move_to":
                if action.board_x is not None and action.board_y is not None:
                    player.move_card(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message="action missing: board_x or board_y")

            case "heal":
                if action.board_x is not None and action.board_y is not None:
                    player.heal_card(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message="action missing: board_x or board_y")

            case "spawn_cube":
                if action.board_x is not None and action.board_y is not None:
                    player.spawn_cube(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message="action missing: board_x or board_y")

            case "end_turn":
                game_state.turn_number += 1
                opponent = game_state.get_opponent_name(action.player)
                game_state.get_player(action.player).turn_end(game_state)
                if abs(game_state.score) >= 10:
                    return ActionResult(True, message=action.player, quit=True)
                game_state.get_player(opponent).turn_start(game_state)
                game_state.game_statistics.add_score_record(game_state.score)
                return ActionResult(True, end_turn=True)

            case "quit":
                return ActionResult(True, quit=True)

        return ActionResult(False, message=f"unknown action: {action.action_type}")