# Plotting tools

This package contains reusable plotting helpers that are safe for scripts and
agents to call in headless environments. The helpers return Matplotlib
`(Figure, Axes)` objects so callers can keep customizing the chart before
saving it.

```python
from dc26_vatican_explorer.plotting_tools import (
    create_bar_chart,
    create_heatmap,
    create_ranked_bar_chart,
    save_figure,
)

fig, ax = create_ranked_bar_chart(
    values=[42, 17, 31],
    labels=["Francis", "Benedict", "Leo"],
    top_n=2,
    title="Example mentions",
    xlabel="Mentions",
    ylabel="Pope",
)
save_figure(fig, "outputs/example_plots/ranked_mentions.png")
```

## Generic helpers

- `create_scatterplot`
- `create_line_chart`
- `create_histogram`
- `create_box_plot`
- `create_heatmap`
- `create_bar_chart`
- `create_ranked_bar_chart`
- `save_figure`

All chart helpers validate common shape errors, apply optional labels, and use
Matplotlib's non-interactive `Agg` backend.

## Database examples

`create_example_plots.py` shows how to query the Vatican Explorer database,
transform query results into lists, call the generic helpers, save the figure,
and close it.

Run from the repo root:

```bash
uv run -m dc26_vatican_explorer.plotting_tools.create_example_plots
```

By default the script writes PNG files to `outputs/example_plots/`.
