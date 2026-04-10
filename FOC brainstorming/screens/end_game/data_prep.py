# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright 2024-2026 Robin Liu / FOC Studio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------


from typing import Callable, Optional

from core.game_state import GameStatistics
from core.game_screen import GameScreen, PIE_TITLE_TEXTS, KEYS_TO_CHECK
from utils.chart_make import make_plot_chart, make_pie_chart, make_bar_chart
from screens.end_game.chart import Chart


ProgressCallback = Callable[[int, int, str], None]


def init_datas(statistics: GameStatistics) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, dict[str, int]], list[list[int]], list[list[int]], list[str], list[str]]:
    player1_datas: dict[str, dict[str, int]] = statistics.export_player_stats("player1")
    player2_datas: dict[str, dict[str, int]]  = statistics.export_player_stats("player2")
    
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
    
    display_player1_data: list[list[int]] = []
    display_player1_name: list[str] = []
    display_player2_data: list[list[int]] = []
    display_player2_name: list[str] = []
    
    data_list: list[int] = []
    
    for i, (name, data) in enumerate(player1_profession_data.items()):
        data_list = []
        for key in KEYS_TO_CHECK:
            data_list.append(data[key])
        display_player1_data.append(data_list)
        display_player1_name.append(name)
    
    for i, (name, data) in enumerate(player2_profession_data.items()):
        data_list = []
        for key in KEYS_TO_CHECK:
            data_list.append(data[key])
        display_player2_data.append(data_list)
        display_player2_name.append(name)

    return (player1_datas, player2_datas, player1_profession_data, player2_profession_data,
            display_player1_data, display_player2_data, display_player1_name, display_player2_name)


def making_image(player1_datas: dict[str, dict[str, int]], player2_datas: dict[str, dict[str, int]],
                 player1_profession_data: dict[str, dict[str, int]], player2_profession_data: dict[str, dict[str, int]],
                 statistics: GameStatistics,
                 on_progress: Optional[ProgressCallback] = None) -> tuple[str, dict[str, list[str]], dict[str, list[str]]]:
    bar_title_texts = ["KDA", "Average Attack Damage", "Per Round Influence", "Survival Index"]

    bar_paths: dict[str, list[str]] = {"player1": [], "player2": []}
    pie_paths: dict[str, list[str]] = {"player1": [], "player2": []}

    total = len(bar_title_texts) * 2 + len(PIE_TITLE_TEXTS) * 2 + 1
    done = 0

    def _tick(label: str) -> None:
        nonlocal done
        done += 1
        if on_progress is not None:
            on_progress(done, total, label)

    for title_text in bar_title_texts:
        try:
            bar_paths["player1"].append(
                make_bar_chart("player1", title_text, player1_profession_data, len(statistics.score_history))
            )
        except Exception:
            pass
        _tick(f"Bar: P1 {title_text}")
        
        try:
            bar_paths["player2"].append(
                make_bar_chart("player2", title_text, player2_profession_data, len(statistics.score_history))
            )
        except Exception:
            pass
        _tick(f"Bar: P2 {title_text}")

    for key in PIE_TITLE_TEXTS:
        title_text = " ".join(map(lambda s: s.capitalize(), key.split("_")))
        try:
            pie_paths["player1"].append(make_pie_chart("player1", title_text, key, player1_datas[key]))
        except Exception as e:
            print(f"[pie {key}] {e}")
        _tick(f"Pie: P1 {title_text}")

        try:
            pie_paths["player2"].append(make_pie_chart("player2", title_text, key, player2_datas[key]))
        except Exception as e:
            print(f"[pie {key}] {e}")
        _tick(f"Pie: P2 {title_text}")

    plot_path = make_plot_chart(statistics.score_history)
    _tick("Score plot")

    return plot_path, pie_paths, bar_paths


def display_chart(pie_paths: dict[str, list[str]], bar_paths: dict[str, list[str]],
                  plot_path: str, game_screen: GameScreen) -> tuple[Chart, dict[str, dict[str, list[Chart]]]]:
    charts: dict[str, dict[str, list[Chart]]] = {"player1": {"pie": [], "bar": []}, "player2": {"pie": [], "bar": []}}
    for i, path in enumerate(pie_paths["player1"]):
        charts["player1"]["pie"].append(Chart(file_path=path,
                                              x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(pie_paths["player1"])/2+i*2.2))),
                                              y=int(game_screen.display_height/2-(game_screen.block_size*1.7)), width=int(game_screen.block_size*2),
                                              height=int(game_screen.block_size*2)))

    for i, path in enumerate(pie_paths["player2"]):
        charts["player2"]["pie"].append(Chart(file_path=path,
                                              x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(pie_paths["player2"])/2+i*2.2))),
                                              y=int(game_screen.display_height/2-(game_screen.block_size*1.7)), width=int(game_screen.block_size*2),
                                              height=int(game_screen.block_size*2)))
    
    for i, path in enumerate(bar_paths["player1"]):
        charts["player1"]["bar"].append(Chart(file_path=path,
                                              x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(bar_paths["player1"])/2+i*2.2))),
                                              y=int(game_screen.display_height/2+(game_screen.block_size*0.7)), width=int(game_screen.block_size*2),
                                              height=int(game_screen.block_size*2)))
    
    for i, path in enumerate(bar_paths["player2"]):
        charts["player2"]["bar"].append(Chart(file_path=path,
                                              x=int(game_screen.display_width/2+(game_screen.block_size*(-2.2*len(bar_paths["player2"])/2+i*2.2))),
                                              y=int(game_screen.display_height/2+(game_screen.block_size*0.7)), width=int(game_screen.block_size*2),
                                              height=int(game_screen.block_size*2)))
    
    score_chart = Chart(file_path=plot_path,
                        x=int(game_screen.display_width/2-(game_screen.block_size*3.75/1.1)),
                        y=int(game_screen.display_height/2+(game_screen.block_size*0.1)),
                        width=int(game_screen.block_size*7.5/1.1), height=int(game_screen.block_size*3/1.1))
    
    return score_chart, charts


def set_all_invisible(score_chart: Chart, charts: dict[str, dict[str, list[Chart]]]) -> None:
    score_chart.visible = False
    for player in charts:
        for chart_type in charts[player]:
            for chart in charts[player][chart_type]:
                chart.visible = False