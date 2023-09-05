import plotly.graph_objects as go
import pandas as pd

# Function to generate basic bar chart
def bar_chart(data, x_axis, y_axis, title="", type='basic'):
    if type == 'basic':
        fig = go.Figure(data=[go.Bar(x=data[x_axis], y=data[y_axis])])
    elif type == 'stacked':
        traces = []
        for col in y_axis:
            traces.append(go.Bar(x=data[x_axis], y=data[col], name=col))
        fig = go.Figure(data=traces)
        fig.update_layout(barmode='stack')
    elif type == 'group':
        traces = []
        for col in y_axis:
            traces.append(go.Bar(x=data[x_axis], y=data[col], name=col))
        fig = go.Figure(data=traces)
        fig.update_layout(barmode='group')

    fig.update_layout(title=title)
    return fig



# Function to customize bar color
def customize_bar_color(fig, color_palette):
    for i, trace in enumerate(fig.data):
        trace.marker.color = color_palette[i % len(color_palette)]
    return fig

# Function to customize axis labels
def customize_axis_labels(fig, x_label, y_label):
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    return fig

# Function to customize chart title
def customize_title(fig, title):
    fig.update_layout(title=title)
    return fig

# Function to bundle all customizations
def customize_bar_chart(fig, color_palette=None, x_label=None, y_label=None, title=None):
    if color_palette:
        customize_bar_color(fig, color_palette)
    if x_label and y_label:
        customize_axis_labels(fig, x_label, y_label)
    if title:
        customize_title(fig, title)
    return fig