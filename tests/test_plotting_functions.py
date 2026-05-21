"""Tests for plotting helper functions."""

import os
from pathlib import Path
from tempfile import gettempdir

# Use Matplotlib's non-interactive Agg backend by default so plots can be rendered
# in headless environments like CI or test runs without opening a GUI window.
os.environ.setdefault("MPLBACKEND", "Agg")

# Create a project-specific temporary directory for Matplotlib's config/cache files.
matplotlib_cache_path = Path(gettempdir()) / "dc26-vatican-explorer-matplotlib"
matplotlib_cache_path.mkdir(exist_ok=True)

# Point Matplotlib at that writable temp config directory unless the caller already
# provided MPLCONFIGDIR, avoiding permission issues in locked-down environments.
os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache_path))

import matplotlib
import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.colors import to_rgba  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from dc26_vatican_explorer.plotting_tools.plotting_functions import (  # noqa: E402
    create_bar_chart,
    create_scatterplot,
    save_figure,
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


def test_create_bar_chart_returns_matplotlib_objects():
    """Confirm the bar chart helper returns the figure and axes objects."""
    fig, ax = create_bar_chart([3, 4])

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_bar_chart_plots_vertical_bars_with_labels_and_titles():
    """Confirm vertical bars, labels, titles, and tick rotation are applied."""
    _, ax = create_bar_chart(
        [3, 4],
        labels=["Francis", "Leo"],
        title="Speeches",
        xlabel="Pope",
        ylabel="Count",
        x_rotation=30,
    )

    bar_heights = [patch.get_height() for patch in ax.patches]
    tick_labels = [tick.get_text() for tick in ax.get_xticklabels()]
    tick_rotations = [tick.get_rotation() for tick in ax.get_xticklabels()]

    assert bar_heights == [3, 4]
    assert tick_labels == ["Francis", "Leo"]
    assert tick_rotations == [30, 30]
    assert ax.get_title() == "Speeches"
    assert ax.get_xlabel() == "Pope"
    assert ax.get_ylabel() == "Count"


def test_create_bar_chart_uses_indices_when_labels_are_omitted():
    """Confirm integer index labels are used when no labels are supplied."""
    _, ax = create_bar_chart([5, 6])

    tick_labels = [tick.get_text() for tick in ax.get_xticklabels()]

    assert tick_labels == ["0", "1"]


def test_create_bar_chart_plots_horizontal_bars():
    """Confirm horizontal orientation puts values on the x-axis."""
    _, ax = create_bar_chart(
        [7, 8],
        labels=["Homilies", "Audiences"],
        xlabel="Count",
        ylabel="Speech Type",
        orient="h",
    )

    bar_widths = [patch.get_width() for patch in ax.patches]
    tick_labels = [tick.get_text() for tick in ax.get_yticklabels()]

    assert bar_widths == [7, 8]
    assert tick_labels == ["Homilies", "Audiences"]
    assert ax.get_xlabel() == "Count"
    assert ax.get_ylabel() == "Speech Type"


def test_create_bar_chart_applies_single_color():
    """Confirm a single color can be applied to every bar."""
    _, ax = create_bar_chart([1, 2], color="black")

    assert [patch.get_facecolor() for patch in ax.patches] == [to_rgba("black")] * 2


def test_create_bar_chart_applies_per_bar_colors():
    """Confirm a list of colors can be applied one bar at a time."""
    _, ax = create_bar_chart([1, 2], color=["red", "blue"])

    assert [patch.get_facecolor() for patch in ax.patches] == [
        to_rgba("red"),
        to_rgba("blue"),
    ]


def test_create_bar_chart_adds_hue_legend_title():
    """Confirm hue groups create a legend with the requested title."""
    _, ax = create_bar_chart(
        [1, 2, 3],
        labels=["A", "B", "C"],
        hue=["Old", "New", "Old"],
        legend_title="Era",
    )

    legend = ax.get_legend()

    assert legend is not None
    assert legend.get_title().get_text() == "Era"


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"values": []}, "at least one"),
        ({"values": [1, 2], "labels": ["Only one"]}, "'labels' length"),
        ({"values": [1, 2], "hue": ["Only one"]}, "'hue' length"),
        ({"values": [1, 2], "orient": "diagonal"}, "'orient' must be"),
    ],
)
def test_create_bar_chart_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid bar chart inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_bar_chart(**kwargs)


def test_save_figure_appends_format_suffix_and_creates_parent_directory(tmp_path):
    """Confirm figures are saved with an added suffix when none is present."""
    fig, _ = create_scatterplot([1], [2])
    output_file = tmp_path / "plots" / "scatter"

    saved_path = save_figure(fig, output_file, fmt="png", dpi=72)

    assert saved_path == (tmp_path / "plots" / "scatter.png").resolve()
    assert saved_path.exists()
    assert saved_path.stat().st_size > 0


def test_save_figure_preserves_existing_suffix(tmp_path):
    """Confirm an existing filename suffix is not replaced."""
    fig, _ = create_bar_chart([1])
    output_file = tmp_path / "bar.svg"

    saved_path = save_figure(fig, output_file, fmt="svg")

    assert saved_path == output_file.resolve()
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8").lstrip().startswith("<?xml")


def test_save_figure_rejects_empty_format(tmp_path):
    """Confirm an empty output format raises a clear error."""
    fig, _ = create_scatterplot([1], [2])

    with pytest.raises(ValueError, match="non-empty"):
        save_figure(fig, tmp_path / "plot", fmt="")
