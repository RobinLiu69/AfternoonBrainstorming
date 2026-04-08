from core.game_screen import GameScreen
from core.game_state import GameState
from rendering.card_renderer import CardRenderer
from rendering.board_renderer import BoardRenderer
from rendering.ui_renderer import UIRenderer


class GameRenderer:
    def __init__(self, game_screen: GameScreen):
        self.game_screen = game_screen
        
        self.card_renderer = CardRenderer(game_screen)
        self.board_renderer = BoardRenderer(game_screen)
        self.ui_renderer = UIRenderer(game_screen)
    
    def render_frame(self, controller: str, mouse_x: int, mouse_y: int,
                     mouse_board_x: int | None, mouse_board_y: int | None, game_state: GameState, hint_on: bool = False) -> None:
        self.game_screen.render()

        for card in game_state.neutral.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
        for card in game_state.player1.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
        for card in game_state.player2.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
    
        self.board_renderer.render_all(game_state)

        if mouse_board_x is not None and mouse_board_y is not None:
            self.board_renderer.render_attack_highlight(
                mouse_board_x, mouse_board_y, controller, game_state
            )

        self.ui_renderer.render_score(controller, game_state)
        self.ui_renderer.render_controller_label(controller)
        self.ui_renderer.render_hands(game_state)
        self.ui_renderer.render_attack_counts(game_state)
        self.ui_renderer.render_tokens(game_state)
        self.ui_renderer.render_luck(game_state)
        self.ui_renderer.render_totems(game_state)
        self.ui_renderer.render_coins(game_state)
        self.ui_renderer.render_deck_info(game_state)
        self.ui_renderer.render_timers(game_state)

        self._render_hint(mouse_x, mouse_y, mouse_board_x, mouse_board_y, game_state, hint_on)

    def _render_hint(self, mouse_x: int, mouse_y: int,
                     mouse_board_x: int | None, mouse_board_y: int | None, game_state: GameState, hint_on: bool) -> None:
        self.ui_renderer._hint_box.turn_on = hint_on
        if not hint_on:
            return
        
        if mouse_x < self.game_screen.display_width / 2 - self.game_screen.block_size * 2:
            name, _ = game_state.player1.get_hand_name_by_mouse_pos(mouse_x, mouse_y, self.game_screen)
            print(name)
            if name != "None":
                self.ui_renderer.render_hint(mouse_x, mouse_y, name)

        elif mouse_x > self.game_screen.display_width / 2 + self.game_screen.block_size * 2:
            name, _ = game_state.player2.get_hand_name_by_mouse_pos(mouse_x, mouse_y, self.game_screen)
            if name != "None":
                self.ui_renderer.render_hint(mouse_x, mouse_y, name)

        if mouse_board_x is not None and mouse_board_y is not None:
            for card in game_state.get_all_cards():
                if card.board_x == mouse_board_x and card.board_y == mouse_board_y:
                    self.ui_renderer.render_hint(mouse_x, mouse_y, card)
                    return
    
    def _render_boards(self, game_state: GameState) -> None:
        for board in game_state.board_dict.values():
            self.board_renderer.render(board)
    
    def _render_neutral_cards(self, game_state: GameState) -> None:
        for card in game_state.neutral.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
    
    def _render_player_cards(self, game_state: GameState) -> None:
        for card in game_state.player1.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)
        for card in game_state.player2.on_board:
            for render_object in card.get_render_data():
                self.card_renderer.render(render_object)