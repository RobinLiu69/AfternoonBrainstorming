import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.patches import Wedge
from matplotlib.text import Text
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import os, json, math
import numpy as np
from typing import cast

from type_hint import JobDictionary


__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))

with open(f"{__FOLDER_PATH}/setting/job_dictionary.json", "r", encoding="utf-8") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())

BLACK: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Black"].split(", "))))
WHITE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["White"].split(", "))))
BLUE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Blue"].split(", "))))
RED: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Red"].split(", "))))
GREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Green"].split(", "))))
ORANGE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Orange"].split(", "))))

COLORS_DICT: dict[str, tuple[float, float, float]] = dict(zip(JOB_DICTIONARY["colors_dict"].keys(), (cast(tuple[float, float, float], tuple(map(lambda RGB_color: float(RGB_color)/255, RGB_colors.split(", ")))) for RGB_colors in JOB_DICTIONARY["RGB_colors"].values())))

font_file_path = __FOLDER_PATH+"/fonts/8bitOperatorPlus-Bold.ttf"

output_folder = f"{__FOLDER_PATH}/output"



custom_font_prop = font_manager.FontProperties(fname=font_file_path)

def make_pie_chart(player_name: str, title_text: str, file_name: str, data: dict[str, int], fontsize: int=6, figsize: tuple[float, float]=(15, 15)) -> str:
    if len(data) > 0:
        labels: list[str] = list(map(lambda key: key.split("_")[-1], data.keys()))
        sorted_tags = sorted(COLORS_DICT.keys(), key=len, reverse=True)
        
        x: list[int] = list(data.values())
    
        colors: list[tuple[float, float, float] | str] = []
        for name in labels:
            for tag in sorted_tags:
                if name.endswith(tag):
                    colors.append(COLORS_DICT[tag])
                    break


        if not any(data.values()):
            title_text = "No Data"
            labels = ["No Data"]
            colors = ["gray"]
            x = [1]
        
        
    
        plt.figure(figsize=figsize, dpi=120)
        
        _, texts, _ = cast(tuple[list[Wedge], list[Text], list[Text]], plt.pie(x, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140, labeldistance=1.1, textprops={"color": "black", "fontproperties": custom_font_prop, "fontsize": fontsize*6}, wedgeprops={"linewidth": 5, "edgecolor": "gray"}))
        
        plt.axis("equal")
        for text in texts:
            text.set_color("white")
            text.set_fontsize(fontsize*7)
            
        plt.title(title_text, fontweight="bold", fontproperties=custom_font_prop, fontsize = fontsize*13, color = "white", loc="center", pad=30)
        plt.tight_layout()
        
        os.makedirs(output_folder, exist_ok=True)
        title_text = title_text.replace(" ", "_")
        plt.savefig(os.path.join(output_folder, player_name+"_pie_chart_"+title_text+".png"), transparent=True)
    return player_name+"_pie_chart_"+title_text+".png"

def make_bar_chart(player_name: str, title_text: str, datas: dict[str, dict[str, int]], turns: int, fontsize: int=6, figsize: tuple[float, float]=(15, 15)) -> str:
    '''
    title_text:
        1: 'KDA',
        2: 'Average Attack Damage',
        3: 'Attack Efficiency Index',
        4: 'Per Round Influence',
        5: 'Survival Index'
    
    'hit_count'
    'damage_dealt'
    'damage_taken_count'
    'damage_taken'
    'scored'
    'ability_count'
    'move_count'
    'killed_count'
    'death_count'
    'rounds_survived'
    '''
    if len(datas):
        labels: list[str] = list(datas.keys())
        
        sorted_tags = sorted(COLORS_DICT.keys(), key=len, reverse=True)

        colors: list[tuple[float, float, float] | str] = []
        for name in labels:
            for tag in sorted_tags:
                if name.endswith(tag):
                    colors.append(COLORS_DICT[tag])
                    break

        
        width: list[float] = [0]
        
        match title_text:
            case "KDA":
                width =  [datas[key]["killed_count"]/max(1, datas[key]["death_count"]) for key in datas.keys()]
            case "Average Attack Damage":
                width =  [datas[key]["damage_dealt"]/max(1, datas[key]["hit_count"]) for key in datas.keys()]
            case "Attack Efficiency Index":
                width =  [datas[key]["hit_count"]/max(1, datas[key]["damage_taken_count"]) for key in datas.keys()]
            case "Per Round Influence":
                width =  [datas[key]["damage_dealt"]*datas[key]["damage_taken"]/max(1, datas[key]["rounds_survived"]) for key in datas.keys()]
            case "Survival Index":
                width =  [((datas[key]["scored"]*5)+(datas[key]["damage_dealt"]/max(1, datas[key]["hit_count"])*2)+(datas[key]["damage_taken"]/max(1, datas[key]["damage_taken_count"])*2))/max(1, datas[key]["rounds_survived"]) for key in datas.keys()]

        for i in range(len(width)-1, -1, -1):
            if width[i] <= 0:
                width.pop(i)
                colors.pop(i)
                labels.pop(i)
        if not datas or not width:
            title_text = "No Data"
            labels = ["No Data"]
            colors = ["gray"]
            width = [1]
        
        fig, ax = cast(tuple[Figure, Axes], plt.subplots(figsize=figsize, dpi=120))
        ax.barh(labels, width, color=colors, linewidth=5, edgecolor="gray")
        ax.set_title(title_text, fontweight='bold', fontproperties=custom_font_prop, fontsize=fontsize * 12, color='white', loc='left', pad=30)
        
        
        categories = np.arange(math.ceil(max(width)+1))
        
        
        for label in plt.gca().get_yticklabels():
            label.set_fontproperties(custom_font_prop)
            label.set_color("white")
            label.set_fontsize(fontsize*9)
        for label in plt.gca().get_xticklabels():
            label.set_fontproperties(custom_font_prop)  
            label.set_color("white")
            label.set_fontsize(fontsize*8)
            
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)

        categories = categories[::max(1, 2*(len(categories)//10))]
        

        ax.set_xticks(categories)
        ax.set_xticklabels([str(cat) for cat in categories])
        
        plt.tight_layout()

        os.makedirs(output_folder, exist_ok=True)
        if title_text != "KDA":
            title_text = title_text.lower().replace(" ", "_")
        plt.savefig(os.path.join(output_folder, player_name+"_barchart_"+title_text+".png"), transparent=True)
        plt.close()
        return player_name+"_barchart_"+title_text+".png"
    else:
        return "None"


def make_plot_chart(data: list [int], fontsize: int=6, figsize: tuple[float, float]=(20, 8)) ->  str:
    if data:
        mean_value = float(np.mean(data))
        zero_value = 0
        title_text = "Score-Turns"
    else:
        zero_value = 0
        mean_value = 0
        x = [1]
        data = [1]
        title_text = "No Data"

    x = list(range(1, len(data)+1))
    plt.figure(figsize=figsize, dpi=120)
    plt.plot(x, data, marker=",", linestyle="-", color="white")
    plt.title( title_text, fontweight = "bold", fontproperties=custom_font_prop, fontsize=8*fontsize, color="white", loc="left", pad=30)
    plt.xlabel("Turns", fontproperties=custom_font_prop, fontsize=6*fontsize, color="white")
    plt.ylabel("Score", fontproperties=custom_font_prop, fontsize=6*fontsize, color="white")   
    plt.axhline(y=mean_value, color="white", linestyle="-.", linewidth=fontsize/2.5, label="Mean")
    plt.axhline(y=zero_value, color="darkgray", linestyle=":", linewidth=fontsize/2.5, label="Zero")
    for label in plt.gca().get_yticklabels():
        label.set_fontproperties(custom_font_prop)
        label.set_color("white")
        label.set_fontsize(9*fontsize)
    for label in plt.gca().get_xticklabels():
        label.set_fontproperties(custom_font_prop)
        label.set_color("white")
        label.set_fontsize(9*fontsize)

    plt.gca().yaxis.set_major_formatter("{:+.0f}".format)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["bottom"].set_visible(False)
    plt.gca().spines["left"].set_visible(False)
    plt.tick_params(axis = "x", colors = "white", labelsize=4*fontsize)
    plt.tick_params(axis = "y", colors = "white", labelsize=4*fontsize)
    plt.tight_layout()

    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, "plot_chart"+".png"), transparent=True)
    plt.close()
    return "plot_chart"+".png"
