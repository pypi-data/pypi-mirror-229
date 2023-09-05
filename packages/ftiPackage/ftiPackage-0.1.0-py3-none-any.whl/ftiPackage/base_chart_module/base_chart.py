import plotly.express as px

# base chart for bar charts
def basic_bar_chart(data, x, y):
    fig = px.bar(data, x=x, y=y)
    return fig

# base chart for scatter plots
def basic_scatter_plot(data, x_axis, y_axis):
    fig = px.scatter(data, x=x_axis, y=y_axis)
    return fig
