"""Figures for the Findings page.

Each function answers one question and writes one PNG. Run the module to
regenerate every figure into ``docs/assets``:

    uv run -m dc26_vatican_explorer.plotting_tools.story_plots

Unlike ``create_example_plots``, nothing here is framed "per pope": the corpus
currently holds two pontificates of very different lengths, so a two-bar
comparison of raw totals would say more about how long someone reigned than
about anything they said. Where popes are compared, the comparison is either
rate-based or restricted to equivalent windows.
"""

from __future__ import annotations

import csv
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from dc26_vatican_explorer.config import _DB_PATH, _PKG_DIR
from dc26_vatican_explorer.data_cleaning.format_dates import (
    format_date_to_iso,
    format_pontificate_date,
)
from dc26_vatican_explorer.plotting_tools import (
    create_bar_chart,
    create_box_plot,
    create_heatmap,
    create_line_chart,
    save_figure,
)
from dc26_vatican_explorer.search.search_biblical_citation import (
    search_biblical_citations,
)

_REPO_ROOT = _PKG_DIR.parent.parent
_ASSETS_DIR = _REPO_ROOT / "docs" / "assets"
_BIBLE_BOOKS_CSV = _REPO_ROOT / "data" / "bible_books.csv"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# The shipped default pattern only accepts 2-4 letter abbreviations, which drops
# every citation written out in full ("Matthew 5:9", "Genesis 1:1"). Book-level
# analysis needs the longer form, so widen the token and reuse the same search.
BOOK_CITATION_PATTERN = r"\b((?:[1-3]\s+)?[A-Za-z]{2,12})\s+\d{1,3}:\d{1,3}"


def load_bible_books(csv_path: Path = _BIBLE_BOOKS_CSV) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """Read ``bible_books.csv`` into lookup tables.

    Args:
        csv_path: Path to the reference CSV.

    Returns:
        tuple: ``(abbreviation -> book, book -> (group, testament))``. Lookup
        keys are lowercased with any trailing period removed.

    """
    abbrev_to_book: dict[str, str] = {}
    book_to_group: dict[str, tuple[str, str]] = {}

    with open(csv_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            book = row["book"]
            book_to_group[book] = (row["group"], row["testament"])
            for alias in [book, *row["abbreviations"].split(",")]:
                key = alias.strip().rstrip(".").lower()
                if key:
                    abbrev_to_book.setdefault(key, book)

    return abbrev_to_book, book_to_group


def _connect(db_path: Path = _DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def _month_index(iso_date: str) -> int:
    """Return the 1-12 month number of an ISO date string."""
    return int(iso_date[5:7])


def plot_covid_rupture(db_path: Path = _DB_PATH, output_dir: Path = _ASSETS_DIR) -> Path:
    """Monthly English output through 2019-2022, audiences against the Angelus.

    The pandemic emptied the audience halls but not the Sunday window, so the
    two lines separate sharply in 2020 and rejoin later.
    """
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT t.section, t.date
            FROM texts t JOIN popes p ON p._pope_id = t.pope_id
            WHERE p.pope_name = 'Francis' AND t.language = 'EN'
              AND t.date IS NOT NULL AND t.year BETWEEN '2019' AND '2022'
            """
        ).fetchall()
    finally:
        conn.close()

    addresses: Counter[str] = Counter()
    angelus: Counter[str] = Counter()
    for section, raw_date in rows:
        iso = format_date_to_iso(raw_date)
        if not iso:
            continue
        key = iso[:7]
        if section == "angelus":
            angelus[key] += 1
        else:
            addresses[key] += 1

    months = [f"{y}-{m:02d}" for y in range(2019, 2023) for m in range(1, 13)]
    fig, ax = create_line_chart(
        x_values=months,
        y_values=[addresses.get(m, 0) for m in months],
        title="The audiences stopped; the Angelus did not (Francis, English)",
        xlabel="Month",
        ylabel="Documents published",
        marker=None,
        figsize=(11, 5),
        x_rotation=90,
    )
    ax.plot(months, [angelus.get(m, 0) for m in months], marker=None, label="Angelus")
    ax.lines[0].set_label("Speeches & homilies")
    ax.axvspan("2020-03", "2020-08", alpha=0.12, color="red")
    ax.annotate(
        "first lockdown",
        xy=("2020-05", ax.get_ylim()[1] * 0.92),
        ha="center",
        fontsize=9,
    )
    ax.legend()
    # Keep the axis readable: one tick per quarter rather than all 48 months.
    ax.set_xticks([m for i, m in enumerate(months) if i % 3 == 0])
    fig.tight_layout()

    return save_figure(fig, output_dir / "covid_rupture.png")


def plot_first_year_comparison(db_path: Path = _DB_PATH, output_dir: Path = _ASSETS_DIR) -> Path:
    """Compare each pope's first twelve months, month by month.

    Raw career totals are meaningless across a twelve-year and a one-year
    pontificate. Aligning on months-since-election is the like-for-like view.
    """
    conn = _connect(db_path)
    try:
        begins = {
            name: format_pontificate_date(begin)
            for name, begin in conn.execute("SELECT pope_name, pontificate_begin FROM popes")
        }
        rows = conn.execute(
            """
            SELECT p.pope_name, t.date
            FROM texts t JOIN popes p ON p._pope_id = t.pope_id
            WHERE t.language = 'EN' AND t.date IS NOT NULL
            """
        ).fetchall()
    finally:
        conn.close()

    per_pope: dict[str, Counter[int]] = defaultdict(Counter)
    for pope, raw_date in rows:
        begin = begins.get(pope)
        iso = format_date_to_iso(raw_date)
        if not begin or not iso:
            continue
        offset = (int(iso[:4]) - int(begin[:4])) * 12 + (_month_index(iso) - _month_index(begin))
        if 0 <= offset < 12:
            per_pope[pope][offset] += 1

    popes = sorted(per_pope, key=lambda name: begins[name] or "")
    values: list[int] = []
    labels: list[str] = []
    hue: list[str] = []
    for pope in popes:
        for offset in range(12):
            values.append(per_pope[pope].get(offset, 0))
            labels.append(str(offset + 1))
            hue.append(f"{pope} (from {begins[pope]})")

    totals = ", ".join(f"{p}: {sum(per_pope[p].values())}" for p in popes)
    fig, _ax = create_bar_chart(
        values=values,
        labels=labels,
        hue=hue,
        title=f"First twelve months of each pontificate, English documents ({totals})",
        xlabel="Month since election",
        ylabel="Documents published",
        legend_title="Pope",
        figsize=(11, 5),
    )
    return save_figure(fig, output_dir / "first_year_comparison.png")


def _citation_counts_by_pope(db_path: Path) -> tuple[dict[str, Counter[str]], Counter[str]]:
    """Count scripture citations per book per pope, plus documents per pope."""
    abbrev_to_book, _groups = load_bible_books()
    token = re.compile(BOOK_CITATION_PATTERN)

    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT p.pope_name, t.text_content
            FROM texts t JOIN popes p ON p._pope_id = t.pope_id
            WHERE t.language = 'EN' AND t.text_content IS NOT NULL
            """
        ).fetchall()
    finally:
        conn.close()

    by_pope: dict[str, Counter[str]] = defaultdict(Counter)
    documents: Counter[str] = Counter()
    for pope, text in rows:
        documents[pope] += 1
        for citation, _context in search_biblical_citations(text, context=0, pattern=BOOK_CITATION_PATTERN):
            match = token.match(citation)
            if not match:
                continue
            key = re.sub(r"\s+", " ", match.group(1).lower()).rstrip(".")
            book = abbrev_to_book.get(key)
            if book:
                by_pope[pope][book] += 1

    return by_pope, documents


def plot_scripture_heatmap(
    db_path: Path = _DB_PATH, output_dir: Path = _ASSETS_DIR, top_n: int = 12
) -> Path:
    """Which books each pope reaches for, as citations per 100 documents.

    Normalising by document count is what makes the two pontificates
    comparable at all.
    """
    by_pope, documents = _citation_counts_by_pope(db_path)

    overall: Counter[str] = Counter()
    for counts in by_pope.values():
        overall.update(counts)
    books = [book for book, _n in overall.most_common(top_n)]

    popes = sorted(by_pope, key=lambda name: -documents[name])
    matrix = [
        [round(100 * by_pope[pope].get(book, 0) / documents[pope], 1) for book in books]
        for pope in popes
    ]

    fig, _ax = create_heatmap(
        matrix=matrix,
        x_labels=books,
        y_labels=[f"{p}\n(n={documents[p]})" for p in popes],
        title="Scripture citations per 100 English documents",
        annotation_format=".1f",
        palette="rocket_r",
        figsize=(12, 3.2),
    )
    return save_figure(fig, output_dir / "scripture_heatmap.png")


def plot_length_by_section(db_path: Path = _DB_PATH, output_dir: Path = _ASSETS_DIR) -> Path:
    """Word-count distribution per section, showing how distinct the genres are."""
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT t.section, t.text_content
            FROM texts t
            WHERE t.language = 'EN' AND t.text_content IS NOT NULL
            """
        ).fetchall()
    finally:
        conn.close()

    lengths: dict[str, list[int]] = defaultdict(list)
    for section, text in rows:
        lengths[section].append(len(text.split()))

    ordered = {
        f"{section}\n(n={len(values)})": values
        for section, values in sorted(lengths.items(), key=lambda kv: -len(kv[1]))
    }

    fig, ax = create_box_plot(
        values_by_group=ordered,
        title="A fixed form and a free one: word counts by section (English)",
        xlabel="Section",
        ylabel="Words per document (log scale)",
        palette="crest",
        figsize=(9, 5),
    )
    # A handful of addresses run past 10,000 words while the Angelus never
    # clears 1,600. On a linear axis the outliers flatten every box into a line.
    ax.set_yscale("log")
    fig.tight_layout()
    return save_figure(fig, output_dir / "length_by_section.png")


def main() -> None:
    """Regenerate every Findings figure."""
    _ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for builder in (
        plot_covid_rupture,
        plot_first_year_comparison,
        plot_scripture_heatmap,
        plot_length_by_section,
    ):
        path = builder()
        print(f"wrote {path}")
        plt.close("all")


if __name__ == "__main__":
    main()
