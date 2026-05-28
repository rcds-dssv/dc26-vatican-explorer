# create_example_plots.py
# Example analysis functions that query the database and produce figures.
#
# Run from the repo root:
#   uv run -m dc26_vatican_explorer.plotting_tools.create_example_plots

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from dc26_vatican_explorer.plotting_tools.plotting_functions import (
    create_bar_chart,
    save_figure,
)
from dc26_vatican_explorer.database_utils.database_helpers import (
    connect_to_database,
    register_regexp_function,
)
from dc26_vatican_explorer.search.search_biblical_citation import (
    search_biblical_citations_db,
)

# ── Column index of text_content in the texts table (schema-defined order) ──
_TEXT_CONTENT_COL = 9
# ── Extra columns appended by the JOIN query below ──
_POPE_NAME_COL = 11
_PONTIFICATE_BEGIN_COL = 12
_PONTIFICATE_END_COL = 13

# ── Allowed values for the search_field parameter ──
_VALID_SEARCH_FIELDS = {"text_content", "title"}

# ── Directory this module lives in (plotting_tools/) ──
_PLOTTING_TOOLS_DIR = Path(__file__).resolve().parent
_EXAMPLE_PLOTS_DIR = _PLOTTING_TOOLS_DIR / "example_plots"


def _extract_year(date_str: str | None) -> str | None:
    """Extract a 4-digit year from a date string."""
    if date_str is None:
        return None
    import re
    m = re.search(r"\d{4}", date_str)
    return m.group() if m else None


def _format_pope_label(pope_name: str, begin: str | None, end: str | None) -> str:
    """Return 'Pope Name (YYYY – YYYY)' or 'Pope Name (YYYY – present)'."""
    start_year = _extract_year(begin)
    if start_year is None:
        return pope_name
    end_year = _extract_year(end) or "present"
    return f"{pope_name} ({start_year} \u2013 {end_year})"


def _print_content_diagnostic() -> None:
    """Print text_content availability per pope per language (all languages)."""
    print("\n[DIAGNOSTIC] text_content status per pope per language (all languages)...")
    conn, cursor = connect_to_database()
    try:
        cursor.execute(
            """
            SELECT p.pope_name,
                   t.language,
                   COUNT(t._texts_id) AS total_texts,
                   SUM(CASE WHEN t.text_content IS NULL   THEN 1 ELSE 0 END) AS null_content,
                   SUM(CASE WHEN t.text_content = ''      THEN 1 ELSE 0 END) AS empty_content,
                   SUM(CASE WHEN t.text_content IS NOT NULL
                             AND t.text_content != ''     THEN 1 ELSE 0 END) AS texts_with_content
            FROM popes p
            LEFT JOIN texts t ON p._pope_id = t.pope_id
            GROUP BY p._pope_id, p.pope_name, t.language
            ORDER BY p.pontificate_begin, t.language
            """
        )
        for row in cursor.fetchall():
            print(
                f"  {row[0]} [{row[1]}]: total={row[2]}, "
                f"null={row[3]}, empty_string={row[4]}, has_content={row[5]}"
            )
    finally:
        conn.close()


def _fetch_word_counts(
    word: str,
    language: str,
    search_field: str = "text_content",
    count_speeches: bool = False,
) -> dict[str, tuple[int, str | None, str | None]]:
    """Query word counts per pope for the given language and field.

    Args:
        word: Word to search for (case-insensitive, whole-word match).
        language: Two-letter language code.
        search_field: DB column to search — ``"text_content"`` (default) or ``"title"``.
        count_speeches: If ``False`` (default), return the total number of regex matches
            across all speeches (can exceed speech count; used for rate).
            If ``True``, return the number of distinct speeches that contain the word
            at least once (always ≤ speech count; used for fraction).

    Returns:
        dict mapping pope_name to ``(count, pontificate_begin, pontificate_end)``.
    """
    if search_field not in _VALID_SEARCH_FIELDS:
        raise ValueError(
            f"Invalid search_field '{search_field}'. Must be one of {_VALID_SEARCH_FIELDS}."
        )
    pattern = rf"(?i)\b{word}\b"

    if count_speeches:
        print(f"Fetching speeches containing '{word}' in {search_field} [{language}]...")
        conn, cursor = connect_to_database()
        try:
            register_regexp_function(conn)
            cursor.execute(
                f"""
                SELECT p.pope_name, COUNT(t._texts_id) AS matching_speeches,
                       p.pontificate_begin, p.pontificate_end
                FROM texts t
                JOIN popes p ON t.pope_id = p._pope_id
                WHERE t.{search_field} REGEXP ?
                  AND t.language = ?
                GROUP BY p._pope_id, p.pope_name, p.pontificate_begin, p.pontificate_end
                """,
                (pattern, language),
            )
            rows = cursor.fetchall()
        finally:
            conn.close()
        return {row[0]: (row[1], row[2], row[3]) for row in rows}

    print(f"Fetching word counts for '{word}' in {search_field} [{language}]...")
    counts: dict[str, int] = defaultdict(int)
    pope_dates: dict[str, tuple[str | None, str | None]] = {}

    query = f"""
        SELECT t.*, p.pope_name, p.pontificate_begin, p.pontificate_end
        FROM texts t
        JOIN popes p ON t.pope_id = p._pope_id
        WHERE t.{search_field} REGEXP ?
          AND t.language = '{language}'
    """
    results = search_biblical_citations_db(
        pattern=pattern, query=query, search_field=search_field
    )
    for row, matches in results:
        pope_name = row[_POPE_NAME_COL]
        counts[pope_name] += len(matches)
        if pope_name not in pope_dates:
            pope_dates[pope_name] = (row[_PONTIFICATE_BEGIN_COL], row[_PONTIFICATE_END_COL])

    return {
        name: (counts[name], pope_dates[name][0], pope_dates[name][1])
        for name in counts
    }


def _fetch_speech_counts(
    language: str,
) -> dict[str, tuple[int, str | None, str | None]]:
    """Query speech counts per pope for the given language.

    Returns:
        dict mapping pope_name to ``(count, pontificate_begin, pontificate_end)``.
    """
    print(f"Fetching speech counts [{language}]...")
    conn, cursor = connect_to_database()
    try:
        cursor.execute(
            """
            SELECT p.pope_name, COUNT(t._texts_id) AS speech_count,
                   p.pontificate_begin, p.pontificate_end
            FROM popes p
            JOIN texts t ON p._pope_id = t.pope_id
            WHERE t.language = ?
            GROUP BY p._pope_id, p.pope_name, p.pontificate_begin, p.pontificate_end
            """,
            (language,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {row[0]: (row[1], row[2], row[3]) for row in rows}


def plot_word_count_per_pope(
    word: str = "love",
    language: str = "EN",
    search_field: str = "text_content",
    out_path: str | Path | None = None,
    title: str | None = None,
    palette: str = "Blues_d",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes, Path]:
    """Count word occurrences per pope across all DB texts and plot a bar chart.

    Uses :func:`search_biblical_citations_db` with a custom JOIN query so that
    pope names come back alongside the text rows, then tallies all regex matches
    per pope and renders a sorted bar chart.

    Args:
        word: The word to count (case-insensitive, whole-word match).
            Default is ``"love"``.
        out_path: Destination file path for the saved PNG. Defaults to
            ``<plotting_tools>/<word>_per_pope.png``. Intermediate
            directories are created if they do not exist.
        title: Chart title. Defaults to
            ``'Occurrences of "<word>" per pope'``.
        palette: Seaborn/matplotlib palette name for the bars. Default
            ``"Blues_d"``.
        figsize: ``(width, height)`` in inches.

    Returns:
        tuple[Figure, Axes, Path]: The figure, axes, and resolved path to the
        saved PNG file.

    """
    # Whole-word, case-insensitive regex for the target word
    pattern = rf"(?i)\b{word}\b"

    # Default save location: example_plots/<word>_<language>_<field>_per_pope.png
    if out_path is None:
        out_path = _EXAMPLE_PLOTS_DIR / f"{word}_{language}_{search_field}_per_pope.png"

    counts = _fetch_word_counts(word, language, search_field)

    print(f"\n[DIAGNOSTIC] Occurrences of '{word}' in {search_field} [{language}] per pope:")
    for pope, (count, begin, end) in sorted(
        counts.items(), key=lambda x: _extract_year(x[1][1]) or ""
    ):
        print(f"  {pope}: {count}")

    if not counts:
        raise ValueError(
            f"No occurrences of '{word}' found in the database. "
            "Check that the database is populated."
        )

    # Sort chronologically by pontificate start date
    sorted_popes = sorted(counts, key=lambda n: _extract_year(counts[n][1]) or "")
    sorted_values = [counts[p][0] for p in sorted_popes]
    sorted_labels = [
        _format_pope_label(p, counts[p][1], counts[p][2]) for p in sorted_popes
    ]

    print("Creating plot...")
    chart_title = title or f'Occurrences of "{word}" in {search_field} per pope [{language}]'

    fig, ax = create_bar_chart(
        values=sorted_values,
        labels=sorted_labels,
        title=chart_title,
        xlabel=f'Number of "{word}" occurrences',
        ylabel="Pope",
        palette=palette,
        figsize=figsize,
        x_rotation=0,
        orient="h",
    )

    saved_path = save_figure(fig, out_path, fmt="png")
    return fig, ax, saved_path


def plot_speech_count_per_pope(
    language: str = "EN",
    out_path: str | Path | None = None,
    title: str | None = None,
    palette: str = "Blues_d",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes, Path]:
    """Plot a bar chart showing the number of speeches per pope in the database.

    Args:
        out_path: Destination file path for the saved PNG. Defaults to
            ``<plotting_tools>/speech_count_per_pope.png``.
        title: Chart title. Defaults to ``'Number of speeches per pope'``.
        palette: Seaborn/matplotlib palette name. Default ``"Blues_d"``.
        figsize: ``(width, height)`` in inches.

    Returns:
        tuple[Figure, Axes, Path]: The figure, axes, and resolved path to the
        saved PNG file.

    """
    if out_path is None:
        out_path = _EXAMPLE_PLOTS_DIR / f"speech_count_{language}_per_pope.png"

    counts = _fetch_speech_counts(language)

    if not counts:
        raise ValueError(
            "No speech records found in the database. "
            "Check that the database is populated."
        )

    # Sort chronologically by pontificate start date
    sorted_popes = sorted(counts, key=lambda n: _extract_year(counts[n][1]) or "")
    sorted_labels = [
        _format_pope_label(p, counts[p][1], counts[p][2]) for p in sorted_popes
    ]
    sorted_values = [counts[p][0] for p in sorted_popes]

    print("Creating plot...")
    chart_title = title or f"Number of speeches per pope [{language}]"

    fig, ax = create_bar_chart(
        values=sorted_values,
        labels=sorted_labels,
        title=chart_title,
        xlabel="Number of speeches",
        ylabel="Pope",
        palette=palette,
        figsize=figsize,
        x_rotation=0,
        orient="h",
    )

    saved_path = save_figure(fig, out_path, fmt="png")
    return fig, ax, saved_path


def plot_word_rate_per_pope(
    word: str = "love",
    language: str = "EN",
    search_field: str = "text_content",
    mode: str = "rate",
    out_path: str | Path | None = None,
    title: str | None = None,
    palette: str = "Blues_d",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes, Path]:
    """Plot a normalised word metric per pope — either rate or fraction.

    Two modes are supported:

    - ``"rate"`` (default): total word occurrences ÷ speech count. Can exceed 1.
      Measures how intensely a word is used per speech.
    - ``"fraction"``: distinct speeches containing the word ÷ speech count.
      Always in [0, 1]. Measures how broadly a word is used across speeches.

    Args:
        word: Word to search for (case-insensitive, whole-word match). Default ``"love"``.
        language: Two-letter language code to filter texts. Default ``"EN"``.
        search_field: DB column to search — ``"text_content"`` (default) or ``"title"``.
        mode: ``"rate"`` or ``"fraction"`` (see above). Default ``"rate"``.
        out_path: Destination file path for the saved PNG. Defaults to
            ``<example_plots>/<word>_<language>_<field>_<mode>_per_pope.png``.
        title: Chart title. Auto-generated from ``word``, ``search_field``, ``language``,
            and ``mode`` if not provided.
        palette: Seaborn/matplotlib palette name. Default ``"Blues_d"``.
        figsize: ``(width, height)`` in inches.

    Returns:
        tuple[Figure, Axes, Path]: The figure, axes, and resolved path to the saved PNG.

    Raises:
        ValueError: If ``mode`` is not ``"rate"`` or ``"fraction"``.

    """
    if mode not in ("rate", "fraction"):
        raise ValueError(f"Invalid mode '{mode}'. Must be 'rate' or 'fraction'.")

    if out_path is None:
        out_path = _EXAMPLE_PLOTS_DIR / f"{word}_{language}_{search_field}_{mode}_per_pope.png"

    numerator_counts = _fetch_word_counts(word, language, search_field, count_speeches=(mode == "fraction"))

    speech_counts = _fetch_speech_counts(language)

    # Compute per-pope value; skip popes absent from either dataset
    values_map: dict[str, tuple[float, str | None, str | None]] = {}
    for pope, (n, begin, end) in numerator_counts.items():
        if pope in speech_counts and speech_counts[pope][0] > 0:
            values_map[pope] = (n / speech_counts[pope][0], begin, end)

    diag_label = "Rate" if mode == "rate" else "Fraction"
    print(f"\n[DIAGNOSTIC] {diag_label} of '{word}' in {search_field} [{language}] per pope:")
    for pope, (val, begin, end) in sorted(
        values_map.items(), key=lambda x: _extract_year(x[1][1]) or ""
    ):
        print(f"  {pope}: {val:.4f}")

    if not values_map:
        raise ValueError(
            f"No {mode} data available for '{word}' in {search_field} [{language}]. "
            "Check that the database is populated."
        )

    sorted_popes = sorted(values_map, key=lambda n: _extract_year(values_map[n][1]) or "")
    sorted_values = [values_map[p][0] for p in sorted_popes]
    sorted_labels = [
        _format_pope_label(p, values_map[p][1], values_map[p][2]) for p in sorted_popes
    ]

    print("Creating plot...")
    if mode == "rate":
        default_title = f'"{word}" in {search_field} per speech [{language}]'
        xlabel = f'"{word}" occurrences per speech'
    else:
        default_title = f'Fraction of speeches with "{word}" in {search_field} [{language}]'
        xlabel = f'Fraction of speeches containing "{word}"'
    chart_title = title or default_title

    fig, ax = create_bar_chart(
        values=sorted_values,
        labels=sorted_labels,
        title=chart_title,
        xlabel=xlabel,
        ylabel="Pope",
        palette=palette,
        figsize=figsize,
        x_rotation=0,
        orient="h",
    )

    saved_path = save_figure(fig, out_path, fmt="png")
    return fig, ax, saved_path


def main() -> None:

    # ── Diagnostics ───────────────────────────────────────────────────────────
    _print_content_diagnostic()
    # ─────────────────────────────────────────────────────────────────────────

    fig, ax, path = plot_speech_count_per_pope(language="EN")
    print(f"Saved speech count figure to: {path}")
    plt.close(fig)


    fig, ax, path = plot_word_count_per_pope(word="love", language="EN", search_field="title")
    print(f"Saved word count (title) figure to: {path}")
    plt.close(fig)
    fig, ax, path = plot_word_rate_per_pope(word="love", language="EN", search_field="title", mode="fraction")
    print(f"Saved word fraction (title) figure to: {path}")
    plt.close(fig)
    fig, ax, path = plot_word_count_per_pope(word="love", language="EN")
    print(f"Saved word count (text_content) figure to: {path}")
    plt.close(fig)
    fig, ax, path = plot_word_rate_per_pope(word="love", language="EN", mode="rate")
    print(f"Saved word rate figure to: {path}")
    plt.close(fig)

    fig, ax, path = plot_word_count_per_pope(word="Jesus", language="EN", search_field="title")
    print(f"Saved word count (title) figure to: {path}")
    plt.close(fig)
    fig, ax, path = plot_word_count_per_pope(word="Jesus", language="EN")
    print(f"Saved word count figure to: {path}")
    plt.close(fig)
    fig, ax, path = plot_word_rate_per_pope(word="Jesus", language="EN", mode="rate")
    print(f"Saved word rate figure to: {path}")
    plt.close(fig)

    # raises value error because no amore in titles
    # fig, ax, path = plot_word_count_per_pope(word="amore", language="IT", search_field="title")
    # print(f"Saved word count (title) figure to: {path}")
    # plt.close(fig)
    fig, ax, path = plot_word_count_per_pope(word="amore", language="IT")
    print(f"Saved word count figure to: {path}")
    plt.close(fig)
    fig, ax, path = plot_word_rate_per_pope(word="amore", language="IT", mode="rate")
    print(f"Saved word rate figure to: {path}")
    plt.close(fig)



if __name__ == "__main__":
    main()
