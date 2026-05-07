# Module with reusable plotting functions for Vatican Explorer analysis

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.use("Agg")  # non-interactive backend; safe for agent/script use


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
) -> tuple[plt.Figure, plt.Axes]:
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

    if orient not in ("h", "v"):
        raise ValueError(f"'orient' must be 'h' or 'v', got {orient!r}.")

    cats = labels if labels is not None else list(range(len(values)))
    horizontal = orient == "h"

    # seaborn barplot: for horizontal, numeric values → x, categories → y
    x_data = values if horizontal else cats
    y_data = cats if horizontal else values

    fig, ax = plt.subplots(figsize=figsize)

    if hue is not None:
        import pandas as pd

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
        sns.barplot(
            x=x_data,
            y=y_data,
            hue=y_data if (palette is not None and bar_color is None and horizontal) else (
                x_data if (palette is not None and bar_color is None) else None
            ),
            palette=palette if bar_color is None else None,
            color=bar_color if isinstance(bar_color, str) else None,
            orient=orient,
            legend=False,
            ax=ax,
        )
        # Apply per-bar colors when a list is supplied
        if isinstance(color, list):
            for bar, c in zip(ax.patches, color):
                bar.set_facecolor(c)

    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    ax.tick_params(axis="x", rotation=x_rotation)

    fig.tight_layout()

    return fig, ax


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
