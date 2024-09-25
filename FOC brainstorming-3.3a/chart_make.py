import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os, json
import numpy as np
from typing import cast

from type_hint import JobDictionary


__FOLDER_PATH: str = os.path.realpath(os.path.dirname(__file__))

with open(f"{__FOLDER_PATH}/job_dictionary.json", "r") as file:
    JOB_DICTIONARY: JobDictionary = json.loads(file.read())
        
BLACK: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Black"].split(", "))))
WHITE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["White"].split(", "))))
BLUE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Blue"].split(", "))))
RED: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Red"].split(", "))))
GREEN: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Green"].split(", "))))
ORANGE: tuple[int, int, int] = cast(tuple[int, int, int], tuple(map(int, JOB_DICTIONARY["RGB_colors"]["Orange"].split(", "))))

COLORS_DICT: dict[str, tuple[float, float, float]] = dict(zip(JOB_DICTIONARY["RGB_colors"].keys(), (cast(tuple[float, float, float], tuple(map(lambda RGB_color: float(RGB_color)/255, RGB_colors.split(", ")))) for RGB_colors in JOB_DICTIONARY["RGB_colors"].values())))

font_file_path = os.path.join(__FOLDER_PATH,"fonts/8bitOperatorPlus-Bold.ttf")

output_folder = "./output"


custom_font_prop = font_manager.FontProperties(fname=font_file_path)

# def make_pie_chart(player_name: str, title_text: str, data: dict[str, int]):
#     # "攻擊次數": "Number of Attacks"(NoA)
#     # "造成傷害": "Damage Dealt"(DD)
#     # "受到傷害次數": "Number of Hits Taken"(NoHT)
#     # "受到傷害": "Hits Taken"(HT)
#     # "得分數": "Score"(Score)
#     if len(data)> 0:
#         labels: list[str] = list(data.keys())
#         print(COLORS_DICT)
#         my_list = {
#                 1: "Damage Dealt",
#                 2: "Hit Taken",
#                 3: "Scored"
#             }
#         sorted_tags = sorted(colors_dict.keys(), key=len, reverse=True)

#         colors = []
#         for name in labels:
#             for tag in sorted_tags:
#                 if name.endswith(tag):
#                     colors.append(colors_dict[tag])
#                     break

#         sizes = [data[i] for i in range(1,len(data))]

#         for i in range(len(sizes)):
#             if sizes[i] > 0:
#                 break
#         else:
#             title_text = "No Data"
#             labels = ["No Data"]
#             colors = ["gray"]
#             sizes = [1]
#     else:
#         return False
    
#     for i in range(len(sizes)-1,-1,-1):
#         if sizes[i] == 0: #sizes[i] <= max_value*0.05 or 
#             sizes.pop(i)
#             labels.pop(i)
#             colors.pop(i)
    
#     plt.figure(figsize=(15, 15), dpi=120)
    
#     _, texts, _ = plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140, labeldistance=1.1, textprops={"color": "black", "fontproperties": custom_font_prop, "fontsize": 30}, wedgeprops={"linewidth": 5, "edgecolor": "gray"})
#     plt.axis("equal")
#     for text in texts:
#         text.set_color("white")
#         text.set_fontsize(35)
#     plt.title(title_text, fontweight="bold", fontproperties=custom_font_prop, fontsize = 65, color = "white", loc="center", pad=30)
#     plt.tight_layout()
    
#     os.makedirs(output_folder, exist_ok=True)
#     plt.savefig(os.path.join(output_folder, player_name+"_"+str(title_text)+"_pie_chart"+".png"), transparent=True)
#     return True


def make_plot_chart(data: list [int], fontsize: int=5, figsize: tuple[float, float]=(20, 8)): 
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
    return True
