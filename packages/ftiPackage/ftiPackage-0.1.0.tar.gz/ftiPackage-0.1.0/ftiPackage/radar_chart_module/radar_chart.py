import matplotlib.pyplot as plt
import numpy as np

def draw_basic_radar_chart(data, categories, **kwargs):
    # Number of variables we're plotting.
    num_vars = len(categories)

    # Split the circle into even parts and save the angles
    # so we know where to put each axis.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Plot data
    ax.fill(angles, data, color='blue', alpha=0.25)

    # Add labels for each category
    ax.set_yticklabels([])
    ax.set_xticks(angles)
    ax.set_xticklabels(categories)

    return fig, ax

def customize_radar_chart(fig, ax, custom_title=None, colors=None, axis_labels=None):
    if custom_title:
        ax.set_title(custom_title)
        
    if colors:
        for patch, color in zip(ax.patches, colors):
            patch.set_facecolor(color)
            
    if axis_labels:
        ax.set_xticklabels(axis_labels)


# data = [4, 5, 3, 2, 4]
# categories = ['A', 'B', 'C', 'D', 'E']

# fig, ax = draw_basic_radar_chart(data, categories)
# customize_radar_chart(fig, ax, custom_title="My Custom Radar Chart", colors=['red'], axis_labels=['X', 'Y', 'Z', 'P', 'Q'])
# plt.show()
