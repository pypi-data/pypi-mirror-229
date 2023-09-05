import plotly.express as px

# scatter_plot_customization
# Function to customize the color of scatter plot points
def customize_scatter_color(fig, color_palette):
    fig.update_traces(marker=dict(color=color_palette))
    return fig

# Function to customize the size of scatter plot points
def customize_scatter_size(fig, size_factor):
    fig.update_traces(marker=dict(size=size_factor))
    return fig

# Function to customize the axis labels of scatter plot
def customize_scatter_axes_labels(fig, x_label, y_label):
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label
    )
    return fig

# Function to customize the title of scatter plot
def customize_scatter_title(fig, title):
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(
                size=24
            )
        )
    )
    return fig

# Function to assemble all customizations into one
def full_customize_scatter(fig, color_palette=None, size_factor=None, x_label=None, y_label=None, title=None):
    if color_palette:
        fig = customize_scatter_color(fig, color_palette)
    if size_factor:
        fig = customize_scatter_size(fig, size_factor)
    if x_label and y_label:
        fig = customize_scatter_axes_labels(fig, x_label, y_label)
    if title:
        fig = customize_scatter_title(fig, title)
    return fig


