# Tests for plotting_functions.py

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")  # non-interactive backend; must be set before importing pyplot

from dc26_vatican_explorer.plotting_tools.plotting_functions import create_bar_chart, save_figure


@pytest.fixture(autouse=True)
def close_figures():
    """Close all matplotlib figures after each test to avoid resource leaks."""
    yield
    plt.close("all")


#########################################
# RETURN TYPES
#########################################


def test_returns_figure_and_axes():
    """create_bar_chart should return a (Figure, Axes) tuple."""
    fig, ax = create_bar_chart([1, 2, 3])
    assert isinstance(fig, plt.Figure)
    assert isinstance(ax, plt.Axes)


#########################################
# BAR COUNT
#########################################


def test_bar_count_matches_values():
    """Number of bars should equal the number of values."""
    values = [10, 20, 30, 40]
    fig, ax = create_bar_chart(values)
    assert len(ax.patches) == len(values)


#########################################
# LABELS
#########################################


def test_default_labels_are_integer_indices():
    """When no labels are given, x-ticks should be integer indices (vertical default)."""
    fig, ax = create_bar_chart([5, 10, 15])
    tick_labels = [t.get_text() for t in ax.get_xticklabels()]
    assert tick_labels == ["0", "1", "2"] or tick_labels == []


def test_custom_labels_applied():
    """Provided labels should appear on the category axis (x for vertical default)."""
    labels = ["alpha", "beta", "gamma"]
    fig, ax = create_bar_chart([1, 2, 3], labels=labels)
    tick_labels = [t.get_text() for t in ax.get_xticklabels()]
    assert tick_labels == labels


def test_vertical_labels_on_x_axis():
    """With orient='v', labels should appear on the x-axis."""
    labels = ["alpha", "beta", "gamma"]
    fig, ax = create_bar_chart([1, 2, 3], labels=labels, orient="v")
    tick_labels = [t.get_text() for t in ax.get_xticklabels()]
    assert tick_labels == labels


#########################################
# AXIS TITLES
#########################################


def test_title_is_set():
    """Chart title should match the provided title string."""
    fig, ax = create_bar_chart([1, 2], title="My Chart")
    assert ax.get_title() == "My Chart"


def test_no_title_when_not_provided():
    """No title should be set when the title argument is omitted."""
    fig, ax = create_bar_chart([1, 2])
    assert ax.get_title() == ""


def test_xlabel_is_set():
    """X-axis label should match the provided xlabel string."""
    fig, ax = create_bar_chart([1, 2], xlabel="Category")
    assert ax.get_xlabel() == "Category"


def test_ylabel_is_set():
    """Y-axis label should match the provided ylabel string."""
    fig, ax = create_bar_chart([1, 2], ylabel="Count")
    assert ax.get_ylabel() == "Count"


def test_no_xlabel_when_not_provided():
    """X-axis label should be empty when xlabel is omitted."""
    fig, ax = create_bar_chart([1, 2])
    assert ax.get_xlabel() == ""


def test_no_ylabel_when_not_provided():
    """Y-axis label should be empty when ylabel is omitted."""
    fig, ax = create_bar_chart([1, 2])
    assert ax.get_ylabel() == ""


#########################################
# FIGURE SIZE
#########################################


def test_custom_figsize():
    """Figure size should reflect the figsize argument."""
    fig, ax = create_bar_chart([1, 2, 3], figsize=(12, 6))
    width, height = fig.get_size_inches()
    assert width == pytest.approx(12)
    assert height == pytest.approx(6)


#########################################
# VALIDATION ERRORS
#########################################


def test_raises_on_empty_values():
    """Should raise ValueError when values list is empty."""
    with pytest.raises(ValueError, match="'values' must contain at least one element"):
        create_bar_chart([])


def test_raises_when_labels_length_mismatch():
    """Should raise ValueError when labels length != values length."""
    with pytest.raises(ValueError, match="'labels' length"):
        create_bar_chart([1, 2, 3], labels=["a", "b"])


def test_raises_when_hue_length_mismatch():
    """Should raise ValueError when hue length != values length."""
    with pytest.raises(ValueError, match="'hue' length"):
        create_bar_chart([1, 2, 3], hue=["g1", "g2"])


def test_raises_on_invalid_orient():
    """Should raise ValueError for orient values other than 'h' or 'v'."""
    with pytest.raises(ValueError, match="'orient' must be"):
        create_bar_chart([1, 2], orient="x")


#########################################
# ORIENT TESTS
#########################################


def test_default_orient_is_vertical():
    """Default chart should be vertical (numeric values on y-axis)."""
    fig, ax = create_bar_chart([10, 20], labels=["a", "b"])
    assert ax.get_ylim()[1] > 0


def test_horizontal_orient():
    """orient='h' should produce a horizontal bar chart (values on x-axis)."""
    fig, ax = create_bar_chart([10, 20], labels=["a", "b"], orient="h")
    assert ax.get_xlim()[1] > 0


#########################################
# HUE / LEGEND
#########################################


def test_hue_produces_legend():
    """When hue is provided, a legend should be present on the axes."""
    fig, ax = create_bar_chart(
        [3, 7, 2],
        labels=["a", "b", "c"],
        hue=["group1", "group2", "group1"],
    )
    assert ax.get_legend() is not None


def test_hue_legend_title():
    """When legend_title is set, the legend should use that title."""
    fig, ax = create_bar_chart(
        [3, 7],
        hue=["A", "B"],
        legend_title="Group",
    )
    assert ax.get_legend().get_title().get_text() == "Group"


#########################################
# save_figure TESTS
#########################################


def test_save_figure_creates_file(tmp_path):
    """save_figure should write a file at the specified path."""
    fig, ax = create_bar_chart([1, 2, 3])
    out = tmp_path / "test_output.png"
    result = save_figure(fig, out, fmt="png")
    assert result.exists()


def test_save_figure_returns_resolved_path(tmp_path):
    """save_figure should return the resolved absolute Path of the saved file."""
    fig, ax = create_bar_chart([1, 2])
    out = tmp_path / "chart.png"
    result = save_figure(fig, out)
    assert result == out.resolve()


def test_save_figure_appends_extension_when_missing(tmp_path):
    """save_figure should append the format as a suffix when filename has none."""
    fig, ax = create_bar_chart([4, 5])
    out = tmp_path / "no_ext"
    result = save_figure(fig, out, fmt="png")
    assert result.suffix == ".png"
    assert result.exists()


def test_save_figure_pdf_format(tmp_path):
    """save_figure should produce a PDF when fmt='pdf'."""
    fig, ax = create_bar_chart([1, 2])
    out = tmp_path / "chart.pdf"
    result = save_figure(fig, out, fmt="pdf")
    assert result.exists()
    # PDF files start with the %PDF magic bytes
    assert result.read_bytes()[:4] == b"%PDF"


def test_save_figure_creates_missing_parent_dirs(tmp_path):
    """save_figure should create intermediate directories if they don't exist."""
    fig, ax = create_bar_chart([1, 2])
    out = tmp_path / "subdir" / "deep" / "chart.png"
    result = save_figure(fig, out, fmt="png")
    assert result.exists()


def test_save_figure_raises_on_empty_fmt(tmp_path):
    """save_figure should raise ValueError when fmt is an empty string."""
    fig, ax = create_bar_chart([1, 2])
    with pytest.raises(ValueError, match="'fmt' must be a non-empty string"):
        save_figure(fig, tmp_path / "chart", fmt="")
