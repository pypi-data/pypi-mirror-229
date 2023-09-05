import plotly.graph_objects as go

def draw_hierarchical_network_basic(data, custom_title="Hierarchical Network Chart (Basic)"):
    fig = go.Figure()

    fig.add_trace(go.Sunburst(
        ids=data['ids'],
        labels=data['labels'],
        parents=data['parents'],
        values=data['values'],
    ))

    fig.update_layout(
        title=custom_title
    )

    fig.show()


def draw_hierarchical_network_with_explicit_color(data, custom_title="Hierarchical Network Chart (With Explicit Color Mapping)"):
    fig = go.Figure()

    fig.add_trace(go.Sunburst(
        ids=data['ids'],
        labels=data['labels'],
        parents=data['parents'],
        values=data['values'],
        marker=dict(
            colors=data['colors'],
            colorscale='Viridis',
        )
    ))

    fig.update_layout(
        title=custom_title
    )

    fig.show()

# # Example data
# basic_data = {
#     'ids': ['Parent', 'Child 1', 'Child 2', 'Child 1.1', 'Child 1.2', 'Child 2.1'],
#     'labels': ['Parent', 'Child 1', 'Child 2', 'Child 1.1', 'Child 1.2', 'Child 2.1'],
#     'parents': ['', 'Parent', 'Parent', 'Child 1', 'Child 1', 'Child 2'],
#     'values': [10, 20, 30, 40, 50, 60]
# }

# explicit_color_data = {
#     'ids': ['Parent', 'Child 1', 'Child 2', 'Child 1.1', 'Child 1.2', 'Child 2.1'],
#     'labels': ['Parent', 'Child 1', 'Child 2', 'Child 1.1', 'Child 1.2', 'Child 2.1'],
#     'parents': ['', 'Parent', 'Parent', 'Child 1', 'Child 1', 'Child 2'],
#     'values': [10, 20, 30, 40, 50, 60],
#     'colors': ['#FFCC00', '#FF6600', '#FF3300', '#FF0000', '#FF3366', '#FF6699']
# }

# # Running the functions
# if __name__ == "__main__":
#     print("Displaying Hierarchical Network Chart (Basic)")
#     draw_hierarchical_network_basic(basic_data, custom_title="My Custom Title for Basic Chart")
    
#     print("Displaying Hierarchical Network Chart (With Explicit Color Mapping)")
#     draw_hierarchical_network_with_explicit_color(explicit_color_data, custom_title="My Custom Title for Color Mapped Chart")
