"""Reusable plotting helpers for Vatican Explorer analyses."""

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def create_scatterplot(
    x_values: list[float],
    y_values: list[float],
    plot_title: str | None = None,
    x_axis_title: str | None = None,
    y_axis_title: str | None = None,
) -> tuple[Figure, Axes]:
    """Create a scatterplot from x and y values.

    Args:
        x_values: Values to plot along the x-axis.
        y_values: Values to plot along the y-axis.
        plot_title: Optional title to display above the plot.
        x_axis_title: Optional title to display below the x-axis.
        y_axis_title: Optional title to display beside the y-axis.

    Returns:
        A tuple containing the matplotlib figure and axes objects.

    Raises:
        ValueError: If x_values and y_values do not contain the same number of
            values.
    """
    # Check that each x value has a matching y value.
    if len(x_values) != len(y_values):
        # Raise a clear error when the two input lists cannot form coordinate pairs.
        raise ValueError("x_values and y_values must have the same length.")

    # Create a matplotlib figure and axes for the scatterplot.
    fig, ax = plt.subplots()

    # Draw the x and y values as points on the axes using seaborn.
    sns.scatterplot(x=x_values, y=y_values, ax=ax)

    # Check whether the caller provided a plot title.
    if plot_title is not None:
        # Add the plot title above the axes.
        ax.set_title(plot_title)

    # Check whether the caller provided an x-axis title.
    if x_axis_title is not None:
        # Add the x-axis title below the axes.
        ax.set_xlabel(x_axis_title)

    # Check whether the caller provided a y-axis title.
    if y_axis_title is not None:
        # Add the y-axis title beside the axes.
        ax.set_ylabel(y_axis_title)

    # Return both matplotlib objects so another function can render or save them.
    return fig, ax
