from core.game_action import GameAction, ActionResult
from core.game_state import GameState

class BattlingdDispatcher:
    def __init__(self, mode: str = "local"):
        mode = "local" #| "lan_client" | "lan_server"
        self.mode = mode
        self._network = None

    def dispatch(self, action: GameAction, game_state: GameState) -> ActionResult:
        match self.mode:
            case "local":
                return self._execute(action, game_state)
            case "lan_client":
                return self._send_to_server(action)
            case "lan_server":
                result = self._execute(action, game_state)
                self._broadcast_state(game_state)
                return result
        return ActionResult(False, message=f"unknow mode: {self.mode}")

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
                return ActionResult(False, message=f"action missing: board_x or board_y")
            case "heal":
                if action.board_x is not None and action.board_y is not None:
                    player.heal_card(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message=f"action missing: board_x or board_y")
            case "spawn_cube":
                if action.board_x is not None and action.board_y is not None:
                    player.spawn_cude(action.board_x, action.board_y, game_state)
                    return ActionResult(True)
                return ActionResult(False, message=f"action missing: board_x or board_y")
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
        return ActionResult(False, message=f"unknow action: {action.action_type}")

    def _send_to_server(self, action: GameAction) -> ActionResult:
        # self._network.send(action.to_json())
        # response = self._network.wait_response()
        # return ActionResult.from_json(response)
        raise NotImplementedError

    def _broadcast_state(self, game_state: GameState) -> None:
        raise NotImplementedError