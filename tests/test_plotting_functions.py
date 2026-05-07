"""Tests for plotting helper functions."""

import os
from pathlib import Path
from tempfile import gettempdir

os.environ.setdefault("MPLBACKEND", "Agg")
matplotlib_cache_path = Path(gettempdir()) / "dc26-vatican-explorer-matplotlib"
matplotlib_cache_path.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache_path))

import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from dc26_vatican_explorer.plotting_tools.plotting_functions import (  # noqa: E402
    create_scatterplot,
)


@pytest.fixture(autouse=True)
def close_figures():
    """Close matplotlib figures after each test."""
    yield
    plt.close("all")


def test_create_scatterplot_returns_matplotlib_objects():
    """Confirm the helper returns the figure and axes objects."""
    fig, ax = create_scatterplot([1, 2], [3, 4])

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_scatterplot_plots_coordinates_with_seaborn():
    """Confirm the helper draws the expected coordinate pairs."""
    _, ax = create_scatterplot([1, 2], [3, 4])

    plotted_offsets = ax.collections[0].get_offsets().tolist()

    assert plotted_offsets == [[1.0, 3.0], [2.0, 4.0]]


def test_create_scatterplot_sets_optional_titles():
    """Confirm optional plot and axis titles are applied."""
    _, ax = create_scatterplot(
        [1, 2],
        [3, 4],
        plot_title="Speech Lengths",
        x_axis_title="Speech Number",
        y_axis_title="Word Count",
    )

    assert ax.get_title() == "Speech Lengths"
    assert ax.get_xlabel() == "Speech Number"
    assert ax.get_ylabel() == "Word Count"


def test_create_scatterplot_rejects_mismatched_list_lengths():
    """Confirm mismatched input lengths raise a clear error."""
    with pytest.raises(ValueError, match="same length"):
        create_scatterplot([1, 2], [3])
