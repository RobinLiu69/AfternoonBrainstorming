from typing import TYPE_CHECKING
from cards.card import Card, GameScreen
from core.board_block import Board
import cards.card_white as white
import cards.card_red as red
import cards.card_green as green
import cards.card_blue as blue
import cards.card_orange as orange
import cards.card_purple as purple
import cards.card_dark_green as darkgreen
import cards.card_cyan as cyan
import cards.card_fuchsia as fuchsia

if TYPE_CHECKING:
    from core.player import Player
    from core.neutral import Neutral


def spawn_card(board_x: int, board_y: int, card_name: str, owner: str, player1: Player, player2: Player, neutral: Neutral, board_dict: dict[str, Board], game_screen: GameScreen) -> bool:
    if spawn_check(board_x, board_y, board_dict):
        on_board = player1.on_board if owner == "player1" else player2.on_board
        match card_name:
            case "CUBE":
                neutral.on_board.append(white.Cube(owner, board_x, board_y))
            case "ADCW":
                on_board.append(white.Adc(owner, board_x, board_y))
            case "APW":
                on_board.append(white.Ap(owner, board_x, board_y))
            case "TANKW":
                on_board.append(white.Tank(owner, board_x, board_y))
            case "HFW":
                on_board.append(white.Hf(owner, board_x, board_y))
            case "LFW":
                on_board.append(white.Lf(owner, board_x, board_y))
            case "ASSW":
                on_board.append(white.Ass(owner, board_x, board_y))
            case "APTW":
                on_board.append(white.Apt(owner, board_x, board_y))
            case "SPW":
                on_board.append(white.Sp(owner, board_x, board_y))
            
            case "ADCR":
                on_board.append(red.Adc(owner, board_x, board_y))
            case "APR":
                on_board.append(red.Ap(owner, board_x, board_y))
            case "TANKR":
                on_board.append(red.Tank(owner, board_x, board_y))
            case "HFR":
                on_board.append(red.Hf(owner, board_x, board_y))
            case "LFR":
                on_board.append(red.Lf(owner, board_x, board_y))
            case "ASSR":
                on_board.append(red.Ass(owner, board_x, board_y))
            case "APTR":
                on_board.append(red.Apt(owner, board_x, board_y))
            case "SPR":
                on_board.append(red.Sp(owner, board_x, board_y))
            
            case "ADCG":
                on_board.append(green.Adc(owner, board_x, board_y))
            case "APG":
                on_board.append(green.Ap(owner, board_x, board_y))
            case "TANKG":
                on_board.append(green.Tank(owner, board_x, board_y))
            case "HFG":
                on_board.append(green.Hf(owner, board_x, board_y))
            case "LFG":
                on_board.append(green.Lf(owner, board_x, board_y))
            case "ASSG":
                on_board.append(green.Ass(owner, board_x, board_y))
            case "APTG":
                on_board.append(green.Apt(owner, board_x, board_y))
            case "SPG":
                on_board.append(green.Sp(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            case "ADCB":
                on_board.append(blue.Adc(owner, board_x, board_y))
            case "APB":
                on_board.append(blue.Ap(owner, board_x, board_y))
            case "TANKB":
                on_board.append(blue.Tank(owner, board_x, board_y))
            case "HFB":
                on_board.append(blue.Hf(owner, board_x, board_y))
            case "LFB":
                on_board.append(blue.Lf(owner, board_x, board_y))
            case "ASSB":
                on_board.append(blue.Ass(owner, board_x, board_y))
            case "APTB":
                on_board.append(blue.Apt(owner, board_x, board_y))
            case "SPB":
                on_board.append(blue.Sp(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            
            case "ADCO":
                on_board.append(orange.Adc(owner, board_x, board_y))
            case "APO":
                on_board.append(orange.Ap(owner, board_x, board_y))
            case "TANKO":
                on_board.append(orange.Tank(owner, board_x, board_y))
            case "HFO":
                on_board.append(orange.Hf(owner, board_x, board_y))
            case "LFO":
                on_board.append(orange.Lf(owner, board_x, board_y))
            case "ASSO":
                on_board.append(orange.Ass(owner, board_x, board_y))
            case "APTO":
                on_board.append(orange.Apt(owner, board_x, board_y))
            case "SPO":
                on_board.append(orange.Sp(owner, board_x, board_y))
            
            case "ADCP":
                on_board.append(purple.Adc(owner, board_x, board_y))
            case "APP":
                on_board.append(purple.Ap(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            case "TANKP":
                on_board.append(purple.Tank(owner, board_x, board_y))
            case "HFP":
                on_board.append(purple.Hf(owner, board_x, board_y))
            case "LFP":
                on_board.append(purple.Lf(owner, board_x, board_y))
            case "ASSP":
                on_board.append(purple.Ass(owner, board_x, board_y))
            case "APTP":
                on_board.append(purple.Apt(owner, board_x, board_y))
            case "SPP":
                on_board.append(purple.Sp(owner, board_x, board_y))
            
            case "ADCDKG":
                on_board.append(darkgreen.Adc(owner, board_x, board_y))
            case "APDKG":
                on_board.append(darkgreen.Ap(owner, board_x, board_y))
            case "TANKDKG":
                on_board.append(darkgreen.Tank(owner, board_x, board_y))
            case "HFDKG":
                on_board.append(darkgreen.Hf(owner, board_x, board_y))
            case "LFDKG":
                on_board.append(darkgreen.Lf(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            case "ASSDKG":
                on_board.append(darkgreen.Ass(owner, board_x, board_y))
            case "APTDKG":
                on_board.append(darkgreen.Apt(owner, board_x, board_y))
            case "SPDKG":
                on_board.append(darkgreen.Sp(owner, board_x, board_y))
            
            case "ADCC":
                on_board.append(cyan.Adc(owner, board_x, board_y))
            case "APC":
                on_board.append(cyan.Ap(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            case "TANKC":
                on_board.append(cyan.Tank(owner, board_x, board_y))
            case "HFC":
                on_board.append(cyan.Hf(owner, board_x, board_y))
            case "LFC":
                on_board.append(cyan.Lf(owner, board_x, board_y))
            case "ASSC":
                on_board.append(cyan.Ass(owner, board_x, board_y))
            case "APTC":
                on_board.append(cyan.Apt(owner, board_x, board_y))
            case "SPC":
                on_board.append(cyan.Sp(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            
            case "ADCC (+)":
                if cyan.Adc.price_check(owner, "ADC", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Adc(owner, board_x, board_y, True))
                else:
                    return False
            case "APC (+)":
                if cyan.Ap.price_check(owner, "AP", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Ap(owner, board_x, board_y, True).deploy(player1, player2, neutral, board_dict, game_screen))
                else:
                    return False
            case "TANKC (+)":
                if cyan.Tank.price_check(owner, "TANK", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Tank(owner, board_x, board_y, True))
                else:
                    return False
            case "HFC (+)":
                if cyan.Hf.price_check(owner, "HF", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Hf(owner, board_x, board_y, True))
                else:
                    return False
            case "LFC (+)":
                if cyan.Lf.price_check(owner, "LF", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Lf(owner, board_x, board_y, True))
                else:
                    return False
            case "ASSC (+)":
                if cyan.Ass.price_check(owner, "ASS", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Ass(owner, board_x, board_y, True))
                else:
                    return False
            case "APTC (+)":
                if cyan.Apt.price_check(owner, "APT", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Apt(owner, board_x, board_y, True))
                else:
                    return False
            case "SPC (+)":
                if cyan.Sp.price_check(owner, "SP", player1.on_board, player2.on_board, game_screen):
                    on_board.append(cyan.Sp(owner, board_x, board_y, True).deploy(player1, player2, neutral, board_dict, game_screen))
                else:
                    return False
            
            case "ADCF":
                on_board.append(fuchsia.Adc(owner, board_x, board_y))
            case "APF":
                on_board.append(fuchsia.Ap(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            case "TANKF":
                on_board.append(fuchsia.Tank(owner, board_x, board_y))
            case "HFF":
                on_board.append(fuchsia.Hf(owner, board_x, board_y))
            case "LFF":
                on_board.append(fuchsia.Lf(owner, board_x, board_y))
            case "ASSF":
                on_board.append(fuchsia.Ass(owner, board_x, board_y))
            case "APTF":
                on_board.append(fuchsia.Apt(owner, board_x, board_y))
            case "SPF":
                on_board.append(fuchsia.Sp(owner, board_x, board_y).deploy(player1, player2, neutral, board_dict, game_screen))
            
            case _:
                return False
            
        board_dict[str(board_x)+"-"+str(board_y)].occupy = True
        return True
    else:
        return False

def spawn_check(board_x: int, board_y: int, board_dict: dict[str, Board]) -> bool:
    return (str(board_x)+"-"+str(board_y)) in board_dict and not board_dict[str(board_x)+"-"+str(board_y)].occupy
