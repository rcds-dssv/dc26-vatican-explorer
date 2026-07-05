"""Example database-backed plots built with ``plotting_functions.py``.

Run from the repo root:

    uv run -m dc26_vatican_explorer.plotting_tools.create_example_plots

The functions in this module are intentionally domain-specific examples. The
generic plotting API lives in ``plotting_functions.py`` and is re-exported from
``dc26_vatican_explorer.plotting_tools``.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt

from dc26_vatican_explorer.database_utils.database_helpers import (
    connect_to_database,
    register_regexp_function,
)
from dc26_vatican_explorer.plotting_tools import create_bar_chart, save_figure

SearchField = Literal["text_content", "title"]
WordMetric = Literal["occurrences", "matching_speeches"]
RateMode = Literal["rate", "fraction"]

_VALID_SEARCH_FIELDS: set[SearchField] = {"text_content", "title"}
_DEFAULT_OUTPUT_DIR = Path("outputs") / "example_plots"


def _extract_year(date_str: str | None) -> str | None:
    """Extract the first four-digit year from a date string."""
    if date_str is None:
        return None
    match = re.search(r"\d{4}", date_str)
    return match.group() if match else None


def _format_pope_label(pope_name: str, begin: str | None, end: str | None) -> str:
    """Return a chart label with pontificate years when available."""
    start_year = _extract_year(begin)
    if start_year is None:
        return pope_name

    end_year = _extract_year(end) or "present"
    return f"{pope_name} ({start_year}-{end_year})"


def _word_pattern(word: str) -> str:
    """Build a case-insensitive whole-word regex for a literal word."""
    return rf"(?i)\b{re.escape(word)}\b"


def _validate_search_field(search_field: str) -> SearchField:
    """Return a typed search field after checking it against the allowlist."""
    if search_field not in _VALID_SEARCH_FIELDS:
        valid_values = ", ".join(sorted(_VALID_SEARCH_FIELDS))
        raise ValueError(
            f"Invalid search_field {search_field!r}. Expected one of: {valid_values}."
        )
    return search_field  # type: ignore[return-value]


def _default_output_path(name: str, output_dir: str | Path | None = None) -> Path:
    """Return a default output path outside the source package tree."""
    directory = Path(output_dir) if output_dir is not None else _DEFAULT_OUTPUT_DIR
    return directory / name


def _print_content_diagnostic() -> None:
    """Print text_content availability per pope and language."""
    print("\n[diagnostic] text_content availability per pope/language")
    conn, cursor = connect_to_database()
    try:
        cursor.execute(
            """
            SELECT p.pope_name,
                   t.language,
                   COUNT(t._texts_id) AS total_texts,
                   SUM(CASE WHEN t.text_content IS NULL THEN 1 ELSE 0 END) AS null_content,
                   SUM(CASE WHEN t.text_content = '' THEN 1 ELSE 0 END) AS empty_content,
                   SUM(CASE WHEN t.text_content IS NOT NULL
                             AND t.text_content != '' THEN 1 ELSE 0 END) AS texts_with_content
            FROM popes p
            LEFT JOIN texts t ON p._pope_id = t.pope_id
            GROUP BY p._pope_id, p.pope_name, t.language
            ORDER BY p.pontificate_begin, t.language
            """
        )
        for pope_name, language, total, nulls, empty, with_content in cursor.fetchall():
            print(
                f"  {pope_name} [{language}]: total={total}, null={nulls}, "
                f"empty={empty}, has_content={with_content}"
            )
    finally:
        conn.close()


def _fetch_speech_counts(
    language: str,
    search_field: str | None = None,
) -> dict[str, tuple[int, str | None, str | None]]:
    """Query speech counts per pope for a given language."""
    field_filter = ""
    if search_field is not None:
        field = _validate_search_field(search_field)
        field_filter = f"AND t.{field} IS NOT NULL AND t.{field} != ''"

    conn, cursor = connect_to_database()
    try:
        cursor.execute(
            f"""
            SELECT p.pope_name,
                   COUNT(t._texts_id) AS speech_count,
                   p.pontificate_begin,
                   p.pontificate_end
            FROM popes p
            JOIN texts t ON p._pope_id = t.pope_id
            WHERE t.language = ?
              {field_filter}
            GROUP BY p._pope_id, p.pope_name, p.pontificate_begin, p.pontificate_end
            """,
            (language,),
        )
        return {
            pope_name: (speech_count, begin, end)
            for pope_name, speech_count, begin, end in cursor.fetchall()
        }
    finally:
        conn.close()


def _fetch_word_counts(
    word: str,
    language: str,
    search_field: str = "text_content",
    metric: WordMetric = "occurrences",
) -> dict[str, tuple[int, str | None, str | None]]:
    """Query word counts per pope for a given language and searchable field."""
    field = _validate_search_field(search_field)
    pattern = _word_pattern(word)

    conn, cursor = connect_to_database()
    try:
        register_regexp_function(conn)
        cursor.execute(
            f"""
            SELECT p.pope_name,
                   p.pontificate_begin,
                   p.pontificate_end,
                   t.{field}
            FROM texts t
            JOIN popes p ON t.pope_id = p._pope_id
            WHERE t.{field} REGEXP ?
              AND t.language = ?
            """,
            (pattern, language),
        )

        counts: dict[str, int] = defaultdict(int)
        pope_dates: dict[str, tuple[str | None, str | None]] = {}
        for pope_name, begin, end, field_value in cursor.fetchall():
            if metric == "matching_speeches":
                match_count = 1
            elif isinstance(field_value, str):
                match_count = len(re.findall(pattern, field_value))
            else:
                match_count = 0

            counts[pope_name] += match_count
            pope_dates.setdefault(pope_name, (begin, end))

        return {
            pope_name: (count, pope_dates[pope_name][0], pope_dates[pope_name][1])
            for pope_name, count in counts.items()
        }
    finally:
        conn.close()


def _sorted_labels_and_values(
    values_by_pope: dict[str, tuple[int | float, str | None, str | None]],
) -> tuple[list[str], list[int | float]]:
    """Return labels and values sorted by pontificate start year."""
    sorted_popes = sorted(
        values_by_pope,
        key=lambda pope_name: _extract_year(values_by_pope[pope_name][1]) or "",
    )
    labels = [
        _format_pope_label(
            pope_name,
            values_by_pope[pope_name][1],
            values_by_pope[pope_name][2],
        )
        for pope_name in sorted_popes
    ]
    values = [values_by_pope[pope_name][0] for pope_name in sorted_popes]
    return labels, values


def plot_speech_count_per_pope(
    language: str = "EN",
    out_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    title: str | None = None,
    palette: str = "Blues_d",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes, Path]:
    """Plot the number of speeches per pope for a given language."""
    if out_path is None:
        out_path = _default_output_path(
            f"speech_count_{language}_per_pope.png",
            output_dir=output_dir,
        )

    counts = _fetch_speech_counts(language)
    if not counts:
        raise ValueError(
            f"No speech records found for language {language!r}. "
            "Check that the database is populated."
        )

    labels, values = _sorted_labels_and_values(counts)
    fig, ax = create_bar_chart(
        values=values,
        labels=labels,
        title=title or f"Number of speeches per pope [{language}]",
        xlabel="Number of speeches",
        ylabel="Pope",
        palette=palette,
        figsize=figsize,
        orient="h",
    )

    return fig, ax, save_figure(fig, out_path, fmt="png")


def plot_word_count_per_pope(
    word: str = "love",
    language: str = "EN",
    search_field: str = "text_content",
    out_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    title: str | None = None,
    palette: str = "Blues_d",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes, Path]:
    """Plot literal word occurrences per pope for a database field."""
    field = _validate_search_field(search_field)
    if out_path is None:
        out_path = _default_output_path(
            f"{word}_{language}_{field}_per_pope.png",
            output_dir=output_dir,
        )

    counts = _fetch_word_counts(word, language, field)
    searchable_counts = _fetch_speech_counts(language, field)
    if not searchable_counts:
        raise ValueError(
            f"No searchable {field} records found for language {language!r}."
        )

    if not any(count > 0 for count, _begin, _end in counts.values()):
        raise ValueError(
            f"No occurrences of {word!r} found in {field} for language {language!r}."
        )

    values_by_pope = {
        pope_name: (
            counts.get(pope_name, (0, begin, end))[0],
            begin,
            end,
        )
        for pope_name, (_speech_count, begin, end) in searchable_counts.items()
    }

    labels, values = _sorted_labels_and_values(values_by_pope)
    fig, ax = create_bar_chart(
        values=values,
        labels=labels,
        title=title or f'Occurrences of "{word}" in {field} per pope [{language}]',
        xlabel=f'Number of "{word}" occurrences',
        ylabel="Pope",
        palette=palette,
        figsize=figsize,
        orient="h",
    )

    return fig, ax, save_figure(fig, out_path, fmt="png")


def plot_word_rate_per_pope(
    word: str = "love",
    language: str = "EN",
    search_field: str = "text_content",
    mode: str = "rate",
    out_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    title: str | None = None,
    palette: str = "Blues_d",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes, Path]:
    """Plot word occurrences per speech or share of speeches containing a word."""
    if mode not in ("rate", "fraction"):
        raise ValueError(f"Invalid mode {mode!r}. Expected 'rate' or 'fraction'.")

    field = _validate_search_field(search_field)
    if out_path is None:
        out_path = _default_output_path(
            f"{word}_{language}_{field}_{mode}_per_pope.png",
            output_dir=output_dir,
        )

    metric: WordMetric = "matching_speeches" if mode == "fraction" else "occurrences"
    numerator_counts = _fetch_word_counts(word, language, field, metric=metric)
    searchable_counts = _fetch_speech_counts(language, field)

    values_by_pope: dict[str, tuple[float, str | None, str | None]] = {}
    for pope_name, (speech_count, begin, end) in searchable_counts.items():
        if speech_count > 0:
            numerator = numerator_counts.get(pope_name, (0, begin, end))[0]
            values_by_pope[pope_name] = (numerator / speech_count, begin, end)

    if not values_by_pope:
        raise ValueError(
            f"No searchable {field} records available for {word!r} "
            f"for language {language!r}."
        )

    labels, values = _sorted_labels_and_values(values_by_pope)
    if mode == "rate":
        chart_title = title or f'"{word}" in {field} per speech [{language}]'
        xlabel = f'"{word}" occurrences per speech'
    else:
        chart_title = title or f'Fraction of speeches with "{word}" in {field} [{language}]'
        xlabel = f'Fraction of speeches containing "{word}"'

    fig, ax = create_bar_chart(
        values=values,
        labels=labels,
        title=chart_title,
        xlabel=xlabel,
        ylabel="Pope",
        palette=palette,
        figsize=figsize,
        orient="h",
    )

    return fig, ax, save_figure(fig, out_path, fmt="png")


def main() -> None:
    """Create a small gallery of example plots."""
    _print_content_diagnostic()

    examples = [
        (plot_speech_count_per_pope, {"language": "EN"}),
        (plot_word_count_per_pope, {"word": "love", "language": "EN", "search_field": "title"}),
        (
            plot_word_rate_per_pope,
            {"word": "love", "language": "EN", "search_field": "title", "mode": "fraction"},
        ),
        (plot_word_count_per_pope, {"word": "love", "language": "EN"}),
        (plot_word_rate_per_pope, {"word": "love", "language": "EN", "mode": "rate"}),
        (plot_word_count_per_pope, {"word": "Jesus", "language": "EN", "search_field": "title"}),
        (plot_word_count_per_pope, {"word": "Jesus", "language": "EN"}),
        (plot_word_rate_per_pope, {"word": "Jesus", "language": "EN", "mode": "rate"}),
        (plot_word_count_per_pope, {"word": "amore", "language": "IT"}),
        (plot_word_rate_per_pope, {"word": "amore", "language": "IT", "mode": "rate"}),
    ]

    for plot_function, kwargs in examples:
        fig, _ax, path = plot_function(**kwargs)
        print(f"Saved {plot_function.__name__} to: {path}")
        plt.close(fig)


if __name__ == "__main__":
    main()
