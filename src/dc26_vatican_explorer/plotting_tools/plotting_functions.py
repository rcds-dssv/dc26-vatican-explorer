"""Reusable plotting helpers for Vatican Explorer analyses."""
# ruff: noqa: I001

from __future__ import annotations

from pathlib import Path

import pandas as pd

import matplotlib

matplotlib.use("Agg")  # non-interactive backend; must be set before pyplot import
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import seaborn as sns


def _set_optional_labels(
    ax: Axes,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> None:
    """Apply optional title and axis labels to an axes object."""
    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)


def create_scatterplot(
    x_values: list[float],
    y_values: list[float],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    color: str | None = None,
    figsize: tuple[float, float] = (8, 5),
) -> tuple[Figure, Axes]:
    """Create a scatterplot from x and y values.

    Args:
        x_values: Values to plot along the x-axis.
        y_values: Values to plot along the y-axis.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        color: Optional point color.
        figsize: ``(width, height)`` in inches for the figure.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If ``x_values``/``y_values`` are empty or have different
            lengths.

    """
    if len(x_values) == 0:
        raise ValueError("'x_values' must contain at least one element.")

    if len(x_values) != len(y_values):
        raise ValueError(
            f"'x_values' length ({len(x_values)}) must match "
            f"'y_values' length ({len(y_values)})."
        )

    fig, ax = plt.subplots(figsize=figsize)
    sns.scatterplot(x=x_values, y=y_values, color=color, ax=ax)

    _set_optional_labels(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    fig.tight_layout()

    return fig, ax


def create_line_chart(
    x_values: list[str | int | float],
    y_values: list[int | float],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    color: str | None = None,
    marker: str | None = "o",
    figsize: tuple[float, float] = (8, 5),
    x_rotation: float = 0,
) -> tuple[Figure, Axes]:
    """Create a line chart from x and y values.

    Args:
        x_values: Values to plot along the x-axis.
        y_values: Numeric values to plot along the y-axis.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        color: Optional line color.
        marker: Optional marker style for each point. Use None for no markers.
        figsize: ``(width, height)`` in inches for the figure.
        x_rotation: Rotation angle in degrees for x-axis tick labels.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If ``x_values``/``y_values`` are empty or have different
            lengths.

    """
    if len(x_values) == 0:
        raise ValueError("'x_values' must contain at least one element.")

    if len(x_values) != len(y_values):
        raise ValueError(
            f"'x_values' length ({len(x_values)}) must match "
            f"'y_values' length ({len(y_values)})."
        )

    fig, ax = plt.subplots(figsize=figsize)
    sns.lineplot(x=x_values, y=y_values, color=color, marker=marker, ax=ax)

    _set_optional_labels(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    ax.tick_params(axis="x", rotation=x_rotation)
    fig.tight_layout()

    return fig, ax


def create_histogram(
    values: list[int | float],
    bins: int = 10,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    color: str | None = None,
    figsize: tuple[float, float] = (8, 5),
    kde: bool = False,
) -> tuple[Figure, Axes]:
    """Create a histogram for a numeric distribution.

    Args:
        values: Numeric values to bin.
        bins: Number of bins to use. Default is 10.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        color: Optional bar color.
        figsize: ``(width, height)`` in inches for the figure.
        kde: Whether to overlay a kernel density estimate.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If ``values`` is empty or ``bins`` is not positive.

    """
    if len(values) == 0:
        raise ValueError("'values' must contain at least one element.")

    if bins <= 0:
        raise ValueError("'bins' must be a positive integer.")

    fig, ax = plt.subplots(figsize=figsize)
    sns.histplot(values, bins=bins, color=color, kde=kde, ax=ax)

    _set_optional_labels(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    fig.tight_layout()

    return fig, ax


def create_box_plot(
    values_by_group: dict[str, list[int | float]],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    color: str | None = None,
    palette: str | None = None,
    figsize: tuple[float, float] = (8, 5),
    x_rotation: float = 0,
    orient: str = "v",
) -> tuple[Figure, Axes]:
    """Create a box plot from grouped numeric values.

    Args:
        values_by_group: Mapping of group labels to numeric values.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        color: Single color string for all boxes. Ignored when ``palette`` is set.
        palette: Seaborn/matplotlib palette name.
        figsize: ``(width, height)`` in inches for the figure.
        x_rotation: Rotation angle in degrees for x-axis tick labels.
        orient: Box orientation, ``"v"`` for vertical or ``"h"`` for horizontal.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If no groups are provided, any group has no values, or
            ``orient`` is not ``"h"`` or ``"v"``.

    """
    if len(values_by_group) == 0:
        raise ValueError("'values_by_group' must contain at least one group.")

    if orient not in ("h", "v"):
        raise ValueError(f"'orient' must be 'h' or 'v', got {orient!r}.")

    rows: list[dict[str, str | int | float]] = []
    for group, values in values_by_group.items():
        if len(values) == 0:
            raise ValueError(f"Group {group!r} must contain at least one value.")
        rows.extend({"group": group, "value": value} for value in values)

    df = pd.DataFrame(rows)
    horizontal = orient == "h"
    x_column = "value" if horizontal else "group"
    y_column = "group" if horizontal else "value"

    fig, ax = plt.subplots(figsize=figsize)
    sns.boxplot(
        data=df,
        x=x_column,
        y=y_column,
        color=color if palette is None else None,
        palette=palette,
        orient=orient,
        ax=ax,
    )

    _set_optional_labels(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    ax.tick_params(axis="x", rotation=x_rotation)
    fig.tight_layout()

    return fig, ax


def create_heatmap(
    matrix: list[list[int | float]],
    x_labels: list[str],
    y_labels: list[str],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "viridis",
    figsize: tuple[float, float] = (8, 5),
    annotate: bool = True,
    annotation_format: str = ".2g",
) -> tuple[Figure, Axes]:
    """Create a heatmap from a two-dimensional numeric matrix.

    Args:
        matrix: Two-dimensional numeric values to plot.
        x_labels: Labels for matrix columns.
        y_labels: Labels for matrix rows.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        palette: Matplotlib/seaborn color map name.
        figsize: ``(width, height)`` in inches for the figure.
        annotate: Whether to write values inside heatmap cells.
        annotation_format: Format string for annotations.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If ``matrix`` is empty, has empty rows, or its dimensions do
            not match the provided labels.

    """
    if len(matrix) == 0:
        raise ValueError("'matrix' must contain at least one row.")

    if len(y_labels) != len(matrix):
        raise ValueError(
            f"'y_labels' length ({len(y_labels)}) must match "
            f"'matrix' row count ({len(matrix)})."
        )

    for row_index, row in enumerate(matrix):
        if len(row) == 0:
            raise ValueError(f"Matrix row {row_index} must contain at least one value.")
        if len(row) != len(x_labels):
            raise ValueError(
                f"Matrix row {row_index} length ({len(row)}) must match "
                f"'x_labels' length ({len(x_labels)})."
            )

    data = pd.DataFrame(matrix, index=y_labels, columns=x_labels)

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(data, annot=annotate, fmt=annotation_format, cmap=palette, ax=ax)

    _set_optional_labels(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    fig.tight_layout()

    return fig, ax


def create_bar_chart(
    values: list[int | float],
    labels: list[str] | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    color: str | list[str] | None = None,
    palette: str | None = None,
    figsize: tuple[float, float] = (8, 5),
    x_rotation: float = 0,
    hue: list[str] | None = None,
    legend_title: str | None = None,
    orient: str = "v",
) -> tuple[Figure, Axes]:
    """Create a bar chart from a list of values using seaborn.

    Args:
        values: Numeric values for each bar.
        labels: Category label for each bar. If None, integer indices are used.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        color: Single color string or list of per-bar color strings.
            Ignored when ``palette`` is set.
        palette: Seaborn/matplotlib palette name (e.g. ``"Blues_d"``).
            Applied when ``hue`` is provided; otherwise used as a color cycle.
        figsize: ``(width, height)`` in inches for the figure.
        x_rotation: Rotation angle in degrees for x-axis tick labels.
        hue: Optional grouping variable — list of group names, one per bar.
            When provided, bars are colored by group and a legend is shown.
        legend_title: Title for the legend (only used when ``hue`` is provided).
        orient: Bar orientation — ``"v"`` for vertical (default) or ``"h"``
            for horizontal. In horizontal mode the numeric axis is x and the
            category axis is y.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If ``values`` is empty, ``labels``/``hue`` lengths do not
            match ``values``, or ``orient`` is not ``"h"`` or ``"v"``.

    """
    if len(values) == 0:
        raise ValueError("'values' must contain at least one element.")

    if labels is not None and len(labels) != len(values):
        raise ValueError(
            f"'labels' length ({len(labels)}) must match 'values' length ({len(values)})."
        )

    if hue is not None and len(hue) != len(values):
        raise ValueError(
            f"'hue' length ({len(hue)}) must match 'values' length ({len(values)})."
        )

    if isinstance(color, list) and len(color) != len(values):
        raise ValueError(
            f"'color' length ({len(color)}) must match 'values' length ({len(values)})."
        )

    if orient not in ("h", "v"):
        raise ValueError(f"'orient' must be 'h' or 'v', got {orient!r}.")

    cats = labels if labels is not None else list(range(len(values)))
    horizontal = orient == "h"

    # For horizontal bars, numeric values go on x and categories go on y.
    x_data = values if horizontal else cats
    y_data = cats if horizontal else values

    fig, ax = plt.subplots(figsize=figsize)

    if hue is not None:
        df = pd.DataFrame({"x": x_data, "y": y_data, "hue": hue})
        sns.barplot(
            data=df,
            x="x",
            y="y",
            hue="hue",
            palette=palette,
            orient=orient,
            ax=ax,
        )
        if legend_title is not None:
            ax.legend(title=legend_title)
    else:
        bar_color = color if color is not None else None
        palette_hue = None
        if palette is not None and bar_color is None:
            palette_hue = y_data if horizontal else x_data

        sns.barplot(
            x=x_data,
            y=y_data,
            hue=palette_hue,
            palette=palette if bar_color is None else None,
            color=bar_color if isinstance(bar_color, str) else None,
            orient=orient,
            legend=False,
            ax=ax,
        )
        if isinstance(color, list):
            for bar, c in zip(ax.patches, color, strict=False):
                bar.set_facecolor(c)

    _set_optional_labels(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    ax.tick_params(axis="x", rotation=x_rotation)

    fig.tight_layout()

    return fig, ax


def create_ranked_bar_chart(
    values: list[int | float],
    labels: list[str],
    top_n: int | None = None,
    descending: bool = True,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    color: str | list[str] | None = None,
    palette: str | None = None,
    figsize: tuple[float, float] = (8, 5),
    x_rotation: float = 0,
    orient: str = "h",
) -> tuple[Figure, Axes]:
    """Create a sorted bar chart for ranked comparisons.

    Args:
        values: Numeric values for each bar.
        labels: Category label for each bar.
        top_n: Optional maximum number of ranked bars to show.
        descending: Sort largest-to-smallest when True. Sort smallest-to-largest
            when False.
        title: Chart title. If None, no title is added.
        xlabel: Label for the x-axis. If None, no label is added.
        ylabel: Label for the y-axis. If None, no label is added.
        color: Single color string or list of per-bar color strings.
        palette: Seaborn/matplotlib palette name.
        figsize: ``(width, height)`` in inches for the figure.
        x_rotation: Rotation angle in degrees for x-axis tick labels.
        orient: Bar orientation, ``"v"`` for vertical or ``"h"`` for horizontal.

    Returns:
        tuple[Figure, Axes]: The matplotlib Figure and Axes objects.

    Raises:
        ValueError: If input lengths are invalid, ``top_n`` is not positive, or
            ``orient`` is not ``"h"`` or ``"v"``.

    """
    if len(values) == 0:
        raise ValueError("'values' must contain at least one element.")

    if len(labels) != len(values):
        raise ValueError(
            f"'labels' length ({len(labels)}) must match 'values' length ({len(values)})."
        )

    if top_n is not None and top_n <= 0:
        raise ValueError("'top_n' must be a positive integer.")

    ranked_pairs = sorted(
        zip(labels, values, strict=True),
        key=lambda pair: pair[1],
        reverse=descending,
    )

    if top_n is not None:
        ranked_pairs = ranked_pairs[:top_n]

    ranked_labels = [label for label, _ in ranked_pairs]
    ranked_values = [value for _, value in ranked_pairs]

    return create_bar_chart(
        values=ranked_values,
        labels=ranked_labels,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        color=color,
        palette=palette,
        figsize=figsize,
        x_rotation=x_rotation,
        orient=orient,
    )


def save_figure(
    fig: plt.Figure,
    filename: str | Path,
    fmt: str = "png",
    dpi: int = 150,
) -> Path:
    """Save a matplotlib figure to a file.

    Args:
        fig: The matplotlib Figure object to save.
        filename: Destination file path (with or without extension). If the
            path has no suffix, ``fmt`` is appended automatically.
        fmt: Output format understood by matplotlib, e.g. ``"png"``,
            ``"pdf"``, ``"svg"``, ``"jpg"``. Default is ``"png"``.
        dpi: Resolution in dots per inch. Default is 150.

    Returns:
        Path: The resolved path to the saved file.

    Raises:
        ValueError: If ``fmt`` is an empty string.

    """
    if not fmt:
        raise ValueError("'fmt' must be a non-empty string.")

    out = Path(filename)
    if not out.suffix:
        out = out.with_suffix(f".{fmt}")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=fmt, dpi=dpi, bbox_inches="tight")
    return out.resolve()
