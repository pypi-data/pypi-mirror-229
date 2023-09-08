# Generating colors for each unique value in the data
import matplotlib.pyplot as plt
import pandas as pd

def get_color_map(data):
    items = np.unique(data)
    item_colors = {}
    colors_item = {}
    for item in items:
        new_color = np.random.randint(0, items.__len__() + 1)
        while new_color in colors_item:
            new_color = np.random.randint(0, items.__len__() + 1)
        item_colors[item] = new_color
        colors_item[new_color] = item

    data_item_colors = []
    for i in data:
        data_item_colors.append(item_colors[i])
    return data_item_colors, colors_item

# Returns the label for the color
def get_color_label(color_dict, label):
    return color_dict[int(label[label.index('{') + 1: label.index('}')])]

def scatter(df: pd.DataFrame, x_column, y_column, color_column):
    # Getting the colors
    colors, colors_dict = get_color_map(df[color_column])
    # Displaying Age vs Gender
    scatter = plt.scatter(df[x_column], df[y_column], c = colors)
    plt.title(f'{x_column} vs {y_column}')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    colors, labels = scatter.legend_elements()
    plt.legend(colors, [get_color_label(colors_dict, d) for d in labels], loc = 'upper right', title = color_column)

def scatter_plots(df: pd.DataFrame, columns: list, color_column):
    # Getting the colors
    colors, colors_dict = get_color_map(df[color_column])
    charts_per_row = 2
    rows = math.ceil(columns.__len__() / float(charts_per_row))
    fig, axs = plt.subplots(rows, charts_per_row, figsize=(16, 10), constrained_layout=True)
    data_index = 0
    # Displaying Age vs Gender
    for i in range(rows):
        for j in range(charts_per_row):

            if data_index >= columns.__len__():
                break

            x_column = columns[data_index][0]
            y_column = columns[data_index][1]
            ax = None
            if rows > 1:
                ax = axs[i, j]
            else:
                ax = axs[j]
            scatter = ax.scatter(df[x_column], df[y_column], c = colors)
            ax.title.set_text(f'{x_column} vs {y_column}')
            plt.setp(ax, xlabel=x_column, ylabel= y_column)
            scatter_colors, labels = scatter.legend_elements()
            ax.legend(scatter_colors, [get_color_label(colors_dict, d) for d in labels], loc = 'upper right', title = color_column)
            data_index += 1
    plt.subplots_adjust(left=1,
                    bottom=0.1,
                    right=1,
                    top=1,
                    wspace=1,
                    hspace=1)
 