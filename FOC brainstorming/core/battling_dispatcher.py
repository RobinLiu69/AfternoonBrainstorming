from typing import TYPE_CHECKING, Optional

from core.game_action import GameAction, ActionResult
from core.game_state import GameState


if TYPE_CHECKING:
    from core.network_layer import LANServer, LANClient
    from rendering.game_renderer import GameRenderer


class BattlingDispatcher:
    def __init__(self, game_state: GameState, mode: str = "local"):
        self.mode = mode
        self._network = None
        self._game_state: GameState = game_state
        self._game_renderer: Optional["GameRenderer"] = None

        self.pending_winner: Optional[str] = None

    def attach_renderer(self, renderer: "GameRenderer") -> None:
        self._game_renderer = renderer

    def attach_server(self, server: "LANServer") -> None:
        self._network = server
        server.on_action = self._on_remote_action
        server.on_client_connect = self._on_client_connect

    def attach_client(self, client: "LANClient") -> None:
        self._network = client
        client.on_state_update = self._client_apply_state

    def _on_client_connect(self) -> tuple[str, dict]:
        state = self._game_state.to_dict() if self._game_state else {}
        return "player2", state

    def _client_apply_state(self, state_dict: dict) -> None:
        if self._game_renderer is None:
            return
        self._game_state.apply_dict(state_dict, self._game_renderer)

    def dispatch(self, action: GameAction, game_state: GameState) -> ActionResult:
        self._game_state = game_state

        match self.mode:
            case "local":
                return self._execute(action, game_state)

            case "lan_client":
                self._send_to_server(action)
                return ActionResult(True, message="pending")

            case "lan_server":
                result = self._execute(action, game_state)
                if result.success:
                    self._broadcast_state(game_state)
                    if result.quit and result.message:
                        self._broadcast_game_over(result.message, game_state)
                        self.pending_winner = result.message
                return result

        return ActionResult(False, message=f"unknown mode: {self.mode}")

    def _on_remote_action(self, envelope: dict) -> None:
        """Background thread: a client sent us an action."""
        payload = {k: v for k, v in envelope.items() if k != "type"}
        try:
            action = GameAction(**payload)
        except TypeError as e:
            print(f"[BattlingDispatcher] Bad remote action payload: {e}")
            return

        result = self._execute(action, self._game_state)
        if result.success:
            self._broadcast_state(self._game_state)
            if result.quit and result.message:
                self._broadcast_game_over(result.message, self._game_state)
                self.pending_winner = result.message

    def _send_to_server(self, action: GameAction) -> None:
        from core.network_layer import LANClient
        if not isinstance(self._network, LANClient):
            print("[BattlingDispatcher] No network attached — cannot send action.")
            return
        self._network.send_action({
            "action_type": action.action_type,
            "player": action.player,
            "board_x": action.board_x,
            "board_y": action.board_y,
            "hand_index": action.hand_index,
        })

    def _broadcast_state(self, game_state: GameState) -> None:
        from core.network_layer import LANServer
        if not isinstance(self._network, LANServer):
            return
        print(f"[BattlingDispatcher] broadcast_state turn={game_state.turn_number} score={game_state.score}")
        self._network.broadcast_state(game_state.to_dict())

    def _broadcast_game_over(self, winner: str, game_state: GameState) -> None:
        from core.network_layer import LANServer
        if not isinstance(self._network, LANServer):
            return
        stats = {
            "export_for_charts": game_state.game_statistics.export_for_charts(),
            "score_history":     game_state.game_statistics.score_history,
        }
        self._network.broadcast_game_over(winner, stats)

    def _execute(self, action: GameAction, game_state: GameState) -> ActionResult:
        owned_actions = ("attack", "play_card", "move_to", "heal",
                         "spawn_cube", "toggle_upgrade", "end_turn")
        if action.action_type in owned_actions:
            current = "player1" if (game_state.turn_number % 2 == 0) else "player2"
            if action.player != current:
                return ActionResult(False, message="Not your turn")

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

            case "toggle_upgrade":
                if action.hand_index is None: return ActionResult(False, message="action missing: hand_index")
                player = game_state.get_player(action.player)
                if 0 <= action.hand_index < len(player.hand):
                    name = player.hand[action.hand_index]
                    if name.endswith(" (+)"):
                        player.hand[action.hand_index] = name[:-4]
                    elif name.endswith("C"):
                        player.hand[action.hand_index] = name + " (+)"
                return ActionResult(success=True)

            case "end_turn":
                game_state.turn_number += 1
                opponent = game_state.get_opponent_name(action.player)
                game_state.get_player(action.player).turn_end(game_state)
                game_state.game_statistics.add_score_record(game_state.score)
                if abs(game_state.score) >= 10:
                    winner = "player1" if game_state.score < 0 else "player2"
                    return ActionResult(True, message=winner, quit=True)
                game_state.get_player(opponent).turn_start(game_state)
                return ActionResult(True, end_turn=True)

            case "quit":
                return ActionResult(True, quit=True)

        return ActionResult(False, message=f"unknown action: {action.action_type}")