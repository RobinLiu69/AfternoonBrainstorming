import matplotlib.pyplot as plt
import numpy as np

# 提供的職業數據
data = {
    'ASSR': {'hit_count': 5, 'damage_dealt': 14, 'damage_taken_count': 1, 'damage_taken': 2, 'scored': 2, 'ability_count': 5, 'killed_count': 2, 'death_count': 1, 'move_count': 0},
    'ADCO': {'hit_count': 7, 'damage_dealt': 27, 'damage_taken_count': 5, 'damage_taken': 17, 'scored': 7, 'ability_count': 7, 'move_count': 5, 'killed_count': 2, 'death_count': 3},
    'APTR': {'hit_count': 8, 'damage_dealt': 27, 'damage_taken_count': 7, 'damage_taken': 25, 'scored': 13, 'ability_count': 8, 'move_count': 1, 'killed_count': 5, 'death_count': 2},
    'ASSO': {'hit_count': 6, 'damage_dealt': 18, 'damage_taken_count': 1, 'damage_taken': 2, 'scored': 5, 'ability_count': 6, 'move_count': 8, 'killed_count': 5, 'death_count': 1},
    'TANKG': {'damage_taken_count': 5, 'damage_taken': 17, 'scored': 11, 'hit_count': 0, 'damage_dealt': 0, 'ability_count': 0, 'move_count': 0, 'killed_count': 0, 'death_count': 0},
    'TANKO': {'damage_taken_count': 9, 'damage_taken': 37, 'scored': 6, 'death_count': 2, 'hit_count': 0, 'damage_dealt': 0, 'ability_count': 0, 'move_count': 0, 'killed_count': 0},
    'TANKR': {'damage_taken_count': 5, 'damage_taken': 18, 'scored': 2, 'death_count': 2, 'hit_count': 0, 'damage_dealt': 0, 'ability_count': 0, 'move_count': 0, 'killed_count': 0},
}

categories = ['hit_count', 'damage_dealt', 'damage_taken_count', 'damage_taken', 'scored', 'ability_count', 'move_count', 'killed_count', 'death_count']

# Preparation for Radar Chart
def radar_chart_fixed(data, categories):
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    labels = list(data.keys())
    values = [list(d.values()) for d in data.values()]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合雷达图形

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    ax.set_rlabel_position(0)
    plt.xticks(angles[:-1], categories)
    
    for i, (label, value) in enumerate(zip(labels, values)):
        value += value[:1]  # 闭合数据点
        ax.plot(angles, value, linewidth=1, linestyle='solid', label=label)
        ax.fill(angles, value, alpha=0.2)

    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('Radar Chart for Player Professions', size=16)
    plt.show()


# Preparation for Stacked Bar Chart
def stacked_bar_chart(data, categories):
    labels = list(data.keys())
    values = [list(d.values()) for d in data.values()]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    bottom = np.zeros(len(labels))
    
    for i, category in enumerate(categories):
        cat_values = [d[category] for d in data.values()]
        ax.bar(labels, cat_values, label=category, bottom=bottom)
        bottom += np.array(cat_values)
    
    ax.set_xlabel('Professions')
    ax.set_ylabel('Values')
    ax.set_title('Stacked Bar Chart for Professions')
    ax.legend()
    plt.show()

# Preparation for Box Plot
def box_plot(data, categories):
    values = [list(d.values()) for d in data.values()]
    fig, ax = plt.subplots(figsize=(10, 7))
    
    ax.boxplot(values, labels=data.keys())
    ax.set_title('Box Plot for Professions')
    ax.set_ylabel('Values')
    plt.show()

# Preparation for Bubble Chart
def bubble_chart(data, categories):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    labels = list(data.keys())
    x = np.arange(len(labels))
    y = [sum(d.values()) for d in data.values()]
    bubble_size = [sum(d.values()) * 10 for d in data.values()]
    
    ax.scatter(x, y, s=bubble_size, alpha=0.5)
    
    ax.set_xlabel('Professions')
    ax.set_ylabel('Total Values')
    ax.set_title('Bubble Chart for Professions')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.show()

# Preparation for Heatmap
def heatmap(data, categories):
    values = np.array([[d[cat] for cat in categories] for d in data.values()])
    print([[d[cat] for cat in categories] for d in data.values()])
    fig, ax = plt.subplots(figsize=(10, 7))
    
    cax = ax.matshow(values, cmap='coolwarm')
    fig.colorbar(cax)
    
    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(len(data)))
    ax.set_xticklabels(categories)
    ax.set_yticklabels(data.keys())
    
    plt.title('Heatmap for Professions')
    plt.show()

# Generate all the charts
# radar_chart_fixed(data, categories)
# stacked_bar_chart(data, categories)
# box_plot(data, categories)
# bubble_chart(data, categories)
heatmap(data, categories)
