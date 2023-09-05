import circlify
import matplotlib.pyplot as plt
import pandas as pd

def draw_basic_circle_packing(df):
    # Create just a figure and only one subplot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Title
    ax.set_title('Basic circular packing')

    # Remove axes
    ax.axis('off')

    # Generate circles
    circles = circlify.circlify(
        df['Value'].tolist(),
        show_enclosure=False
    )

    # Find axis boundaries
    lim = max(
        max(
            abs(circle.x) + circle.r,
            abs(circle.y) + circle.r
        )
        for circle in circles
    )
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)

    # List of labels
    labels = df['Name']

    # Print circles
    for circle, label in zip(circles, labels):
        x, y, r = circle
        ax.add_patch(plt.Circle((x, y), r, alpha=0.2, linewidth=2))
        plt.annotate(
            label,
            (x, y),
            va='center',
            ha='center'
        )

    plt.show()


# # Create a sample dataframe
# df = pd.DataFrame({
#     'Name': ['A', 'B', 'C', 'D', 'E', 'F'],
#     'Value': [10, 2, 23, 87, 12, 65]
# })

# # Call the function
# draw_basic_circle_packing(df)
