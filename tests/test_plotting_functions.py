"""Tests for plotting helper functions."""
# ruff: noqa: E402

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

import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure

from dc26_vatican_explorer.plotting_tools import create_bar_chart as exported_bar_chart
from dc26_vatican_explorer.plotting_tools import create_example_plots
from dc26_vatican_explorer.plotting_tools.plotting_functions import (
    create_bar_chart,
    create_box_plot,
    create_heatmap,
    create_histogram,
    create_line_chart,
    create_ranked_bar_chart,
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
        title="Speech Lengths",
        xlabel="Speech Number",
        ylabel="Word Count",
    )

    assert ax.get_title() == "Speech Lengths"
    assert ax.get_xlabel() == "Speech Number"
    assert ax.get_ylabel() == "Word Count"


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"x_values": [], "y_values": []}, "at least one"),
        ({"x_values": [1, 2], "y_values": [3]}, "must match"),
    ],
)
def test_create_scatterplot_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid scatterplot inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_scatterplot(**kwargs)


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
        ({"values": [1, 2], "color": ["red"]}, "'color' length"),
        ({"values": [1, 2], "orient": "diagonal"}, "'orient' must be"),
    ],
)
def test_create_bar_chart_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid bar chart inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_bar_chart(**kwargs)


def test_create_line_chart_returns_matplotlib_objects():
    """Confirm the line chart helper returns the figure and axes objects."""
    fig, ax = create_line_chart([2024, 2025], [10, 15])

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_line_chart_plots_values_and_titles():
    """Confirm line coordinates, labels, and tick rotation are applied."""
    _, ax = create_line_chart(
        [2024, 2025, 2026],
        [10, 15, 12],
        title="Speech Trend",
        xlabel="Year",
        ylabel="Speeches",
        x_rotation=45,
    )

    line = ax.lines[0]
    tick_rotations = [tick.get_rotation() for tick in ax.get_xticklabels()]

    assert line.get_xdata().tolist() == [2024, 2025, 2026]
    assert line.get_ydata().tolist() == [10, 15, 12]
    assert ax.get_title() == "Speech Trend"
    assert ax.get_xlabel() == "Year"
    assert ax.get_ylabel() == "Speeches"
    assert all(rotation == 45 for rotation in tick_rotations)


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"x_values": [], "y_values": []}, "at least one"),
        ({"x_values": [1, 2], "y_values": [3]}, "must match"),
    ],
)
def test_create_line_chart_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid line chart inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_line_chart(**kwargs)


def test_create_histogram_returns_matplotlib_objects():
    """Confirm the histogram helper returns the figure and axes objects."""
    fig, ax = create_histogram([1, 2, 3])

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_histogram_plots_requested_number_of_bins():
    """Confirm histogram bins and optional labels are applied."""
    _, ax = create_histogram(
        [1, 2, 3, 4],
        bins=2,
        title="Speech Lengths",
        xlabel="Words",
        ylabel="Frequency",
    )

    assert len(ax.patches) == 2
    assert ax.get_title() == "Speech Lengths"
    assert ax.get_xlabel() == "Words"
    assert ax.get_ylabel() == "Frequency"


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"values": []}, "at least one"),
        ({"values": [1, 2], "bins": 0}, "positive"),
    ],
)
def test_create_histogram_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid histogram inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_histogram(**kwargs)


def test_create_box_plot_returns_matplotlib_objects():
    """Confirm the box plot helper returns the figure and axes objects."""
    fig, ax = create_box_plot({"Francis": [1, 2], "Leo": [3, 4]})

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_box_plot_plots_group_labels_and_titles():
    """Confirm grouped data labels, titles, and tick rotation are applied."""
    _, ax = create_box_plot(
        {"Francis": [1, 2, 3], "Leo": [4, 5, 6]},
        title="Speech Length Distribution",
        xlabel="Pope",
        ylabel="Words",
        x_rotation=20,
    )

    tick_labels = [tick.get_text() for tick in ax.get_xticklabels()]
    tick_rotations = [tick.get_rotation() for tick in ax.get_xticklabels()]

    assert tick_labels == ["Francis", "Leo"]
    assert tick_rotations == [20, 20]
    assert ax.get_title() == "Speech Length Distribution"
    assert ax.get_xlabel() == "Pope"
    assert ax.get_ylabel() == "Words"


def test_create_box_plot_plots_horizontal_groups():
    """Confirm horizontal orientation puts group labels on the y-axis."""
    _, ax = create_box_plot(
        {"Homilies": [1, 2], "Audiences": [3, 4]},
        xlabel="Citation Count",
        ylabel="Section",
        orient="h",
    )

    tick_labels = [tick.get_text() for tick in ax.get_yticklabels()]

    assert tick_labels == ["Homilies", "Audiences"]
    assert ax.get_xlabel() == "Citation Count"
    assert ax.get_ylabel() == "Section"


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"values_by_group": {}}, "at least one group"),
        ({"values_by_group": {"Francis": []}}, "at least one value"),
        ({"values_by_group": {"Francis": [1]}, "orient": "diagonal"}, "'orient'"),
    ],
)
def test_create_box_plot_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid box plot inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_box_plot(**kwargs)


def test_create_heatmap_returns_matplotlib_objects():
    """Confirm the heatmap helper returns the figure and axes objects."""
    fig, ax = create_heatmap([[1, 2], [3, 4]], ["Love", "Hope"], ["Francis", "Leo"])

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_heatmap_plots_matrix_labels_and_titles():
    """Confirm heatmap dimensions, labels, titles, and annotations are applied."""
    _, ax = create_heatmap(
        [[1, 2], [3, 4]],
        x_labels=["Love", "Hope"],
        y_labels=["Francis", "Leo"],
        title="Theme Mentions",
        xlabel="Theme",
        ylabel="Pope",
    )

    heatmap_values = ax.collections[0].get_array()
    x_tick_labels = [tick.get_text() for tick in ax.get_xticklabels()]
    y_tick_labels = [tick.get_text() for tick in ax.get_yticklabels()]

    assert heatmap_values.shape == (2, 2)
    assert x_tick_labels == ["Love", "Hope"]
    assert y_tick_labels == ["Francis", "Leo"]
    assert len(ax.texts) == 4
    assert ax.get_title() == "Theme Mentions"
    assert ax.get_xlabel() == "Theme"
    assert ax.get_ylabel() == "Pope"


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"matrix": [], "x_labels": [], "y_labels": []}, "at least one row"),
        ({"matrix": [[1]], "x_labels": ["Love"], "y_labels": []}, "'y_labels'"),
        ({"matrix": [[]], "x_labels": [], "y_labels": ["Francis"]}, "row 0"),
        ({"matrix": [[1, 2]], "x_labels": ["Love"], "y_labels": ["Francis"]}, "'x_labels'"),
    ],
)
def test_create_heatmap_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid heatmap inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_heatmap(**kwargs)


def test_create_ranked_bar_chart_returns_matplotlib_objects():
    """Confirm the ranked bar chart helper returns the figure and axes objects."""
    fig, ax = create_ranked_bar_chart([1, 3, 2], ["A", "B", "C"])

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_create_ranked_bar_chart_sorts_and_limits_horizontal_bars():
    """Confirm ranked bars are sorted, limited, and plotted horizontally."""
    _, ax = create_ranked_bar_chart(
        [5, 9, 7],
        labels=["Francis", "Leo", "Benedict"],
        top_n=2,
        xlabel="Mentions",
        ylabel="Pope",
    )

    bar_widths = [patch.get_width() for patch in ax.patches]
    tick_labels = [tick.get_text() for tick in ax.get_yticklabels()]

    assert bar_widths == [9, 7]
    assert tick_labels == ["Leo", "Benedict"]
    assert ax.get_xlabel() == "Mentions"
    assert ax.get_ylabel() == "Pope"


def test_create_ranked_bar_chart_can_sort_ascending_vertically():
    """Confirm ascending ranked bars can be plotted vertically."""
    _, ax = create_ranked_bar_chart(
        [5, 9, 7],
        labels=["Francis", "Leo", "Benedict"],
        descending=False,
        orient="v",
    )

    bar_heights = [patch.get_height() for patch in ax.patches]
    tick_labels = [tick.get_text() for tick in ax.get_xticklabels()]

    assert bar_heights == [5, 7, 9]
    assert tick_labels == ["Francis", "Benedict", "Leo"]


@pytest.mark.parametrize(
    ("kwargs", "error_match"),
    [
        ({"values": [], "labels": []}, "at least one"),
        ({"values": [1, 2], "labels": ["Only one"]}, "'labels' length"),
        ({"values": [1, 2], "labels": ["A", "B"], "top_n": 0}, "positive"),
        ({"values": [1], "labels": ["A"], "orient": "diagonal"}, "'orient'"),
    ],
)
def test_create_ranked_bar_chart_rejects_invalid_inputs(kwargs, error_match):
    """Confirm invalid ranked bar chart inputs raise clear errors."""
    with pytest.raises(ValueError, match=error_match):
        create_ranked_bar_chart(**kwargs)


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


def test_save_figure_uses_existing_suffix_for_output_format(tmp_path):
    """Confirm an existing suffix controls the serialized file type."""
    fig, _ = create_bar_chart([1])
    output_file = tmp_path / "bar.svg"

    saved_path = save_figure(fig, output_file)

    assert saved_path == output_file.resolve()
    assert saved_path.read_text(encoding="utf-8").lstrip().startswith("<?xml")


def test_save_figure_rejects_empty_format(tmp_path):
    """Confirm an empty output format raises a clear error."""
    fig, _ = create_scatterplot([1], [2])

    with pytest.raises(ValueError, match="non-empty"):
        save_figure(fig, tmp_path / "plot", fmt="")


def test_plot_word_count_per_pope_includes_zero_match_popes(monkeypatch, tmp_path):
    """Confirm word count examples include searchable popes with zero matches."""

    def fake_fetch_word_counts(word, language, search_field, metric="occurrences"):
        return {"Francis": (2, "2013-03-13", None)}

    def fake_fetch_speech_counts(language, search_field=None):
        assert search_field == "title"
        return {
            "Francis": (10, "2013-03-13", None),
            "Leo XIV": (5, "2025-05-08", None),
        }

    monkeypatch.setattr(
        create_example_plots,
        "_fetch_word_counts",
        fake_fetch_word_counts,
    )
    monkeypatch.setattr(
        create_example_plots,
        "_fetch_speech_counts",
        fake_fetch_speech_counts,
    )

    fig, ax, _path = create_example_plots.plot_word_count_per_pope(
        word="love",
        language="EN",
        search_field="title",
        output_dir=tmp_path,
    )

    bar_widths = [patch.get_width() for patch in ax.patches]
    tick_labels = [tick.get_text() for tick in ax.get_yticklabels()]

    assert bar_widths == [2, 0]
    assert tick_labels == ["Francis (2013-present)", "Leo XIV (2025-present)"]
    plt.close(fig)


def test_plot_word_rate_per_pope_uses_searchable_denominator(monkeypatch, tmp_path):
    """Confirm rates divide by searchable records and include zero-match popes."""

    def fake_fetch_word_counts(word, language, search_field, metric="occurrences"):
        assert metric == "matching_speeches"
        return {"Francis": (2, "2013-03-13", None)}

    def fake_fetch_speech_counts(language, search_field=None):
        assert search_field == "text_content"
        return {
            "Francis": (4, "2013-03-13", None),
            "Leo XIV": (5, "2025-05-08", None),
        }

    monkeypatch.setattr(
        create_example_plots,
        "_fetch_word_counts",
        fake_fetch_word_counts,
    )
    monkeypatch.setattr(
        create_example_plots,
        "_fetch_speech_counts",
        fake_fetch_speech_counts,
    )

    fig, ax, _path = create_example_plots.plot_word_rate_per_pope(
        word="love",
        language="EN",
        search_field="text_content",
        mode="fraction",
        output_dir=tmp_path,
    )

    bar_widths = [patch.get_width() for patch in ax.patches]
    tick_labels = [tick.get_text() for tick in ax.get_yticklabels()]

    assert bar_widths == [0.5, 0]
    assert tick_labels == ["Francis (2013-present)", "Leo XIV (2025-present)"]
    plt.close(fig)


def test_plotting_tools_exports_public_helpers():
    """Confirm the package exposes the agent-facing plotting helpers."""
    assert exported_bar_chart is create_bar_chart
