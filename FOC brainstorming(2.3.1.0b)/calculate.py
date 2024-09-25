from variable import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.font_manager as font_manager


code_path = os.getcwd()
relative_font_path = os.path.join(code_path,'8bitOperatorPlus-Bold.ttf')
custom_font_prop = font_manager.FontProperties(fname=relative_font_path)



def search_character(character,owner):
    if owner =="player1":
        for row in range(1, len(P1matrix)):
            if P1matrix[row][0] == character:
                return row
        return -1
    if owner =="player2":
        for row in range(1, len(P2matrix)):
            if P2matrix[row][0] == character:
                return row
        return -1
    return False

def update_data(self, owner, type, data):
    row = search_character(self,owner)
    if owner =="player1":
        if row == -1:
            P1matrix.append([self] +[0] * (len(P1matrix[0]) - 1))
            row = search_character(self,owner)
        if type =='攻擊次數':
            P1matrix[row][1] += data
            return True
        if type =='造成傷害':
            P1matrix[row][2] += data
            return True
        if type =='受到傷害次數':
            P1matrix[row][3] += data
            return True
        if type =='受到傷害':
            P1matrix[row][4] += data
            return True
        if type =='得分數':
            P1matrix[row][5] += data
            return True
    if owner =="player2":
        if row == -1:
            P2matrix.append([self] +[0] * (len(P2matrix[0]) - 1))
            row = search_character(self,owner)
        if type =='攻擊次數':
            P2matrix[row][1] += data
            return True
        if type =='造成傷害':
            P2matrix[row][2] += data
            return True
        if type =='受到傷害次數':
            P2matrix[row][3] += data
            return True
        if type =='受到傷害':
            P2matrix[row][4] += data
            return True
        if type =='得分數':
            P2matrix[row][5] += data
    return False

def makepiechart(data, parts, whose): 
    # 1='攻擊次數', 2='造成傷害', 3='受到傷害次數', 4='受到傷害' , 5='得分數'
    # '攻擊次數': 'Number of Attacks'(NoA)
    # '造成傷害': 'Damage Dealt'(DD)
    # '受到傷害次數': 'Number of Hits Taken'(NoHT)
    # '受到傷害': 'Hits Taken'(HT)
    # '得分數': 'Score'(Score)
    if len(data)> 0:
        labels = [data[i][0] for i in range(1,len(data))]
        colors_dict = {'B': (60/255, 100/255, 225/255), 'R': (255/255, 0/255, 0/255), 'G': (51/255, 255/255, 51/255), 'W': (255/255, 255/255, 255/255), 'O': (255/255, 69/255, 0/255), 'P': (128/255, 0/255, 255/255), 'DKG': (85/255, 107/255, 47/255)}
        my_list = {
                1: 'NoA',
                2: 'DD',
                3: 'NoHT',
                4: 'HT',
                5: 'Score'
            }
        title_text=my_list[parts]
        sorted_tags = sorted(colors_dict.keys(), key=len, reverse=True)

        colors = []
        for name in labels:
            for tag in sorted_tags:
                if name.endswith(tag):
                    colors.append(colors_dict[tag])
                    break

        sizes =  [data[i][parts] for i in range(1,len(data))]
        tag=False
        for i in range(len(sizes)):
            if sizes[i] > 0:
                tag=True
                break
        if tag==False:
            title_text = "No Data"
            labels = ["No Data"]
            colors = ["gray"]
            sizes = [1]
    else:
        return False
    max_value = max(sizes)
    for i in range(len(sizes)-1,-1,-1):
        if sizes[i] == 0: #sizes[i] <= max_value*0.05 or 
            sizes.pop(i)
            labels.pop(i)
            colors.pop(i)
    plt.figure(figsize=(15, 15), dpi=120)
    _, texts, _ = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, labeldistance=1.1, textprops={'color': 'black', 'fontproperties': custom_font_prop, 'fontsize': 30}, wedgeprops={'linewidth': 5, 'edgecolor': 'gray'})
    plt.axis('equal')
    for text in texts:
        text.set_color('white')
        text.set_fontsize(35)
    plt.title(title_text, fontweight='bold', fontproperties=custom_font_prop, fontsize = 65, color = 'white', loc='center', pad=30)
    plt.tight_layout()
    output_folder = './output'
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, whose+str(parts)+"piechart"+".png"), transparent=True)
    return True


def makebarchart(data, parts, whose):  
    # 1='攻擊次數', 2='造成傷害', 3='受到傷害次數', 4='受到傷害' , 5='得分數'
    # '攻擊次數': 'Number of Attacks'(NoA)
    # '造成傷害': 'Damage Dealt'(DD)
    # '受到傷害次數': 'Number of Hits Taken'(NoHT)
    # '受到傷害': 'Hits Taken'(HT)
    # '得分數': 'Score'(Score)
    if len(data)> 0:
        labels = [data[i][0] for i in range(1,len(data))]
        colors_dict = {'B': (60/255, 100/255, 225/255), 'R': (255/255, 0/255, 0/255), 'G': (51/255, 255/255, 51/255), 'W': (255/255, 255/255, 255/255), 'O': (255/255, 69/255, 0/255), 'P': (128/255, 0/255, 255/255), 'DKG': (85/255, 107/255, 47/255)}
        my_list = {
                1: 'DD/NoA',#平均攻擊傷害
                2: 'NoA/NoHT',#攻擊效率指數
                3: 'DD*HT/Score',#每回合影響力
                4: '((Score*5)+(DD/NoA)+(HT/NoHT*2))/Turns'#生存指數
            }
        my_titlelist = {
                1: 'Average Attack Damage',
                2: 'Attack Efficiency Index',
                3: 'Per Round Influence',
                4: 'Survival Index'
            }
        title_text=my_titlelist[parts]
        sorted_tags = sorted(colors_dict.keys(), key=len, reverse=True)

        colors = []
        for name in labels:
            for tag in sorted_tags:
                if name.endswith(tag):
                    colors.append(colors_dict[tag])
                    break 
    # 1='攻擊次數', 2='造成傷害', 3='受到傷害次數', 4='受到傷害' , 5='得分數'
    # '攻擊次數': 'Number of Attacks'(NoA)
    # '造成傷害': 'Damage Dealt'(DD)
    # '受到傷害次數': 'Number of Hits Taken'(NoHT)
    # '受到傷害': 'Hits Taken'(HT)
    # '得分數': 'Score'(Score)
        tag=False
        if parts == 1:
            # 'DD/NoA',平均攻擊傷害
            sizes =  [data[i][2]/(data[i][1]+1) for i in range(1,len(data))]
        if parts == 2:
            # 'NoA/NoHT',攻擊效率指數
            sizes =  [data[i][1]/(data[i][3]+1) for i in range(1,len(data))]
        if parts == 3:
            # 'DD*HT/Score',每回合影響力
            sizes =  [data[i][2]*data[i][4]/(data[i][5]+1) for i in range(1,len(data))]
        if parts == 4:
            # '((Score*5)+(DD/NoA*2)+(HT/NoHT*2))/Turns'#生存指數
            sizes =  [((data[i][5]*5)+(data[i][2]/(data[i][1]+1)*2)+(data[i][4]/(data[i][3]+1)*2))/Turns[0] for i in range(1,len(data))]

        for i in range(len(sizes)):
            if sizes[i] > 0:
                tag=True
                max_value = max(sizes)
                for i in range(len(sizes)-1,-1,-1):
                    if sizes[i] == 0: #sizes[i] <= max_value*0.05 or 
                        sizes.pop(i)
                        labels.pop(i)
                        colors.pop(i)
                break
        if tag==False:
            title_text = "No Data"
            labels = ["No Data"]
            colors = ["gray"]
            sizes = [1]
    else:
        return False
    
    plt.figure(figsize=(20, 20), dpi=120) #導致pygame視窗改變
    plt.barh(labels, sizes, color = colors, linewidth = 5, edgecolor = "gray")
    plt.title(title_text, fontweight = 'bold', fontproperties=custom_font_prop, fontsize = 60, color = 'white', loc='Left', pad=30)
    
    for label in plt.gca().get_yticklabels():
        label.set_fontproperties(custom_font_prop)
        label.set_color("white")
        label.set_fontsize(45)
    for label in plt.gca().get_xticklabels():
        label.set_fontproperties(custom_font_prop)
        label.set_color("white")
        label.set_fontsize(45)
        
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)

    plt.tight_layout()

    output_folder = './output'
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, whose+str(parts)+"barchart"+".png"), transparent=True)
    plt.close()
    return True

def makeplot(data) -> bool:
    if data != []:      
        mean_value = np.mean(data)
        zero_value = 0
        title_text = "Score-Turns"
    else:
        zero_value = 0
        mean_value = 0
        x = [1]
        data = [1]
        title_text = "No Data"

    x = range(1, len(data)+1)
    plt.figure(figsize=(20, 8), dpi=120)
    plt.plot(x, data, marker=',', linestyle='-', color='white')
    plt.title( title_text, fontweight = 'bold', fontproperties=custom_font_prop, fontsize = 40, color = 'white', loc='Left', pad=30)
    plt.xlabel('Turns', fontproperties=custom_font_prop, fontsize = 30, color = 'white')
    plt.ylabel('Score', fontproperties=custom_font_prop, fontsize = 30, color = 'white')   
    plt.axhline(y=mean_value, color='white', linestyle='-.', linewidth=2, label='Mean')
    plt.axhline(y=zero_value, color='darkgray', linestyle=':', linewidth=2, label='Zero')
    for label in plt.gca().get_yticklabels():
        label.set_fontproperties(custom_font_prop)
        label.set_color("white")
        label.set_fontsize(45)
    for label in plt.gca().get_xticklabels():
        label.set_fontproperties(custom_font_prop)
        label.set_color("white")
        label.set_fontsize(45)

    plt.gca().yaxis.set_major_formatter('{:+.0f}'.format)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.tick_params(axis = 'x', colors = "white", labelsize=20)
    plt.tick_params(axis = 'y', colors = "white", labelsize=20)
    plt.tight_layout()

    output_folder = './output'
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, "plotchart"+".png"), transparent=True)
    plt.close()
    return True