import pygame, shutil
from dataclasses import dataclass, field
from typing import cast, Generator


from game_screen import GameScreen, os, draw_text, __FOLDER_PATH, PIE_TITLE_TEXTS, KEYS_TO_CHECK, KETYS_TO_DISPLAY, BLACK, WHITE
from chart_make import make_plot_chart, make_pie_chart, make_bar_chart
from controls import key_pressed


folder_path = __FOLDER_PATH

@dataclass(kw_only=True)
class Chart:
    file_path: str
    x: int
    y: int
    width: int
    height: int
    visible: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        file_path = folder_path+"/output/"+self.file_path
        
        self.image: pygame.surface.Surface | None = None
        if os.path.exists(file_path):
            self.image = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), (self.width, self.height))

    def display(self, game_screen: GameScreen) -> None:
        if self.visible == True and self.image is not None:
            game_screen.surface.blit(self.image, (self.x, self.y))

def making_image(player1_datas: dict[str, dict[str, int]], player2_datas: dict[str, dict[str, int]], player1_profession_data: dict[str, dict[str, int]], player2_profession_data: dict[str, dict[str, int]], game_screen: GameScreen) -> tuple[str, dict[str, list[str]], dict[str, list[str]]]:
    bar_title_texts = ["KDA", "Average Attack Damage", "Per Round Influence", "Survival Index"]
    
    bar_paths: dict[str, list[str]] = {"player1": [], "player2": []}
    pie_paths: dict[str, list[str]] = {"player1": [], "player2": []}
    
    
    for title_text in bar_title_texts:
        bar_paths["player1"].append(make_bar_chart("player1", title_text, player1_profession_data, len(game_screen.data.score_records)))
        bar_paths["player2"].append(make_bar_chart("player2", title_text, player2_profession_data, len(game_screen.data.score_records)))
        
    for key in PIE_TITLE_TEXTS:
        title_text = " ".join(map(lambda string: string.capitalize(), key.split("_")))
        pie_paths["player1"].append(make_pie_chart("player1", title_text, key, player1_datas[key]))
        pie_paths["player2"].append(make_pie_chart("player2", title_text, key, player2_datas[key]))
        
    plot_path = make_plot_chart(game_screen.data.score_records)
    
    
    return plot_path, pie_paths, bar_paths

def display_chart(pie_paths: dict[str, list[str]], bar_paths: dict[str, list[str]], plot_path: str, game_screen: GameScreen) -> tuple[Chart, dict[str, dict[str, list[Chart]]]]:
    charts: dict[str, dict[str, list[Chart]]] = {"player1": {"pie": [], "bar": []}, "player2": {"pie": [], "bar": []}}

    for i, path in enumerate(pie_paths["player1"]):
        charts["player1"]["pie"].append(Chart(file_path=path, x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(pie_paths["player1"])/2+i*2.2))), y=int(game_screen.display_height/2-(game_screen.block_size*1.7)), width=int(game_screen.block_size*2), height=int(game_screen.block_size*2)))

    for i, path in enumerate(pie_paths["player2"]):
        charts["player2"]["pie"].append(Chart(file_path=path, x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(pie_paths["player2"])/2+i*2.2))), y=int(game_screen.display_height/2-(game_screen.block_size*1.7)), width=int(game_screen.block_size*2), height=int(game_screen.block_size*2)))
    
    for i, path in enumerate(bar_paths["player1"]):
        charts["player1"]["bar"].append(Chart(file_path=path, x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(bar_paths["player1"])/2+i*2.2))), y=int(game_screen.display_height/2+(game_screen.block_size*0.7)), width=int(game_screen.block_size*2), height=int(game_screen.block_size*2)))
    
    for i, path in enumerate(bar_paths["player2"]):
        charts["player2"]["bar"].append(Chart(file_path=path, x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(bar_paths["player2"])/2+i*2.2))), y=int(game_screen.display_height/2+(game_screen.block_size*0.7)), width=int(game_screen.block_size*2), height=int(game_screen.block_size*2)))
    
    score_chart = Chart(file_path=plot_path, x=int(game_screen.display_width/2-(game_screen.block_size*3.75/1.1)), y=int(game_screen.display_height/2+(game_screen.block_size*0.1)), width=int(game_screen.block_size*7.5/1.1), height=int(game_screen.block_size*3/1.1))
    
    return score_chart, charts

def init_datas(game_screen: GameScreen) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    player1_datas: dict[str, dict[str, int]] = dict(zip(game_screen.data.data_dicts.keys(), ((cast(dict[str, int], dict((key, value) for (key, value) in datas.items() if key.startswith("player1")))) for datas in game_screen.data.data_dicts.values())))
    player2_datas: dict[str, dict[str, int]]  = dict(zip(game_screen.data.data_dicts.keys(), ((cast(dict[str, int], dict((key, value) for (key, value) in datas.items() if key.startswith("player2")))) for datas in game_screen.data.data_dicts.values())))
    
    player1_profession_data: dict[str, dict[str, int]] = {}
    player2_profession_data: dict[str, dict[str, int]] = {}
    
    for key, value in player1_datas.items():
        for player_key, player_value in value.items():
            if player_key.startswith('player1_'):
                profession = player_key.split('_')[1]
                
                if profession not in player1_profession_data:
                    player1_profession_data[profession] = {}
            
                player1_profession_data[profession][key] = player_value
    

    for key in player1_profession_data.keys():
        for sub_key in KEYS_TO_CHECK:
            if sub_key not in player1_profession_data[key]:
                player1_profession_data[key][sub_key] = 0


    for key, value in player2_datas.items():
        for player_key, player_value in value.items():
            if player_key.startswith('player2_'):
                profession = player_key.split('_')[1]
                
                if profession not in player2_profession_data:
                    player2_profession_data[profession] = {}
        
                player2_profession_data[profession][key] = player_value
    
    
    for key in player2_profession_data.keys():
        for sub_key in KEYS_TO_CHECK:
            if sub_key not in player2_profession_data[key]:
                player2_profession_data[key][sub_key] = 0
    
    
    return player1_datas, player2_datas, player1_profession_data, player2_profession_data

def set_all_invisible(score_chart: Chart, charts: dict[str, dict[str, list[Chart]]]) -> None:
    score_chart.visible = False
    for player in charts:
        for chart_type in charts[player]:
            for chart in charts[player][chart_type]:
                chart.visible = False

def loading_screen(game_screen: GameScreen) -> None:
    game_screen.surface.fill(BLACK)
    draw_text("Loading...", game_screen.big_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*0.425, game_screen.display_height/2-game_screen.block_size*0.3, game_screen.surface)
    pygame.display.update()

def display_raw_data(player1_profession_data: dict[str, dict[str, int]], player2_profession_data: dict[str, dict[str, int]], game_screen: GameScreen) -> None:
    display_player1_data = [[profession[cat] for cat in profession] for profession in player1_profession_data.values()]
    display_player2_data = [[profession[cat] for cat in profession] for profession in player2_profession_data.values()]

    for i in range(len(KEYS_TO_CHECK)):
        draw_text(KETYS_TO_DISPLAY[i], game_screen.mid_text_font, WHITE, game_screen.display_width/2+game_screen.block_size*(-3.3+0.75*i), game_screen.display_height/2+game_screen.block_size*(-2.25), game_screen.surface)
    
    for i in range(len(display_player1_data)):
        for j in range(len(display_player1_data[i])):
            draw_text(str(display_player1_data[i][j]), game_screen.mid_text_font, WHITE, game_screen.display_width/2+game_screen.block_size*(-3.2+0.75*j), game_screen.display_height/2+game_screen.block_size*(-2+0.2*i), game_screen.surface)
    
        draw_text(tuple(player1_profession_data.keys())[i], game_screen.mid_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*4, game_screen.display_height/2+game_screen.block_size*(-2+0.2*i), game_screen.surface)
    
    
    for i in range(len(display_player2_data)):
        for j in range(len(display_player2_data[i])):
            draw_text(str(display_player2_data[i][j]), game_screen.mid_text_font, WHITE, game_screen.display_width/2+game_screen.block_size*(-3.2+0.75*j), game_screen.display_height/2+game_screen.block_size*(0.25+0.2*i), game_screen.surface)
    
        draw_text(tuple(player2_profession_data.keys())[i], game_screen.mid_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*4, game_screen.display_height/2+game_screen.block_size*(0.25+0.2*i), game_screen.surface)


def display_end_game_data(winner: str, game_screen: GameScreen):
    draw_text(f"Winner: {winner.capitalize()}!!", game_screen.title_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*1.5, game_screen.display_height/2-game_screen.block_size*2, game_screen.surface)
    draw_text(f"Total Turns: {len(game_screen.data.score_records)}", game_screen.big_text_font, WHITE, game_screen.display_width/2-game_screen.block_size*3.75/1.1, game_screen.display_height/2-game_screen.block_size*0.4, game_screen.surface)
    draw_text(f"Player1 Timer: {game_screen.player_timer["player1"]},   Player2 Timer: {game_screen.player_timer["player2"]}", game_screen.text_font, WHITE, game_screen.display_width/2-game_screen.block_size*3.75/1.1, game_screen.display_height/2-game_screen.block_size*0.2, game_screen.surface)
    
    

def main(winner: str, game_screen: GameScreen) -> None:
    player1_datas, player2_datas, player1_profession_data, player2_profession_data = init_datas(game_screen)
    loading_screen(game_screen)
    plot_path, pie_paths, bar_paths = making_image(player1_datas, player2_datas, player1_profession_data, player2_profession_data, game_screen)
    print(pie_paths)
    score_chart, charts = display_chart(pie_paths, bar_paths, plot_path, game_screen)
    
    display_state: str = "mid"
    score_chart.visible = True
    
    running = True

    
    while running:
        game_screen.update()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_board_x = int((mouse_x-(game_screen.display_width/2-game_screen.block_size*2))/game_screen.block_size) if mouse_x > game_screen.display_width/2-game_screen.block_size*2 else None
        mouse_board_y = int((mouse_y-(game_screen.display_height/2-game_screen.block_size*1.65))/game_screen.block_size) if mouse_y > game_screen.display_height/2-game_screen.block_size*1.65 else None
        
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                match key_pressed(keys):
                    case pygame.K_ESCAPE:
                        running = False
                    case pygame.K_TAB:
                        match display_state:
                            case "raw":
                                display_state = "mid"
                                set_all_invisible(score_chart, charts)
                                score_chart.visible = True
                            case _:
                                display_state = "raw"
                                set_all_invisible(score_chart, charts)
                    case pygame.K_SPACE:
                        match display_state:
                            case "mid":
                                display_state = "player1"
                                set_all_invisible(score_chart, charts)
                                for chart in charts["player1"]["pie"]:
                                    chart.visible = True
                                for chart in charts["player1"]["bar"]:
                                    chart.visible = True
                            case "player1":
                                display_state = "player2"
                                set_all_invisible(score_chart, charts)
                                for chart in charts["player2"]["pie"]:
                                    chart.visible = True
                                for chart in charts["player2"]["bar"]:
                                    chart.visible = True
                            case "player2":
                                display_state = "mid"
                                set_all_invisible(score_chart, charts)
                                score_chart.visible = True
                    case pygame.K_1:
                        match display_state:
                            case "player1":
                                display_state = "mid"
                                set_all_invisible(score_chart, charts)
                                score_chart.visible = True
                            case _:
                                display_state = "player1"
                                set_all_invisible(score_chart, charts)
                                for chart in charts["player1"]["pie"]:
                                    chart.visible = True
                                for chart in charts["player1"]["bar"]:
                                    chart.visible = True
                    case pygame.K_2:
                        match display_state:
                            case "player2":
                                display_state = "mid"
                                set_all_invisible(score_chart, charts)
                                score_chart.visible = True
                            case _:
                                display_state = "player2"
                                set_all_invisible(score_chart, charts)
                                for chart in charts["player2"]["pie"]:
                                    chart.visible = True
                                for chart in charts["player2"]["bar"]:
                                    chart.visible = True
            if event.type == pygame.QUIT:
                running = False
        
        for player_charts in charts.values():
            for value in player_charts.values():
                for chart in value:
                    chart.display(game_screen)
        
        if display_state == "raw":
            display_raw_data(player1_profession_data, player2_profession_data, game_screen)
        elif display_state == "mid":
            display_end_game_data(winner, game_screen)
        
        score_chart.display(game_screen)

        pygame.display.update()
        game_screen.clock.tick(60)
    
    file_path = __FOLDER_PATH+"/output"
    try:
        if game_screen.file_auto_delet:
            shutil.rmtree(file_path)
    except FileNotFoundError:
        pass