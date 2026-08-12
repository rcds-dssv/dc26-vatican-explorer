# Analyses

Exploratory work built on top of the speech database. Each analysis is a
notebook that can be re-run against your own copy of `vatican_texts.db`.

| Analysis | Question | Result |
|---|---|---|
| [1 John 4](first_john_4.ipynb) | How often do popes cite the "God is love" passage, and does that change by year and by pontificate? | 43 citations across 41 speeches, 2013–2026 |

## What 1 John 4 shows

Against the current [6,011-speech build](../data.md), the passage appears 43
times in 41 speeches — 34 by Francis, 9 by Leo XIV.

That gap is smaller than it looks. Francis's 34 citations are spread over
twelve years and 5,031 speeches; Leo XIV's 9 come from a single year and 980
speeches. Per speech, the newer pontificate cites the passage at several times
the rate. One year is a thin basis for a claim about a papacy, so this is a
hypothesis to revisit as the corpus grows, not a conclusion.

The notebooks are rendered here with their stored outputs — the build does not
execute them, because the database is deliberately not committed to the
repository. To run one yourself, [build the database](../data.md) first, then:

```bash
uv sync --group data-manipulation
uv run jupyter lab docs/analyses/
```

## Word frequency comparisons

The figures on the [home page](../index.md) compare word usage across popes —
"love" and "Jesus" in English, "amore" in Italian — both as raw counts and as
rates normalised by total speech length. Normalisation matters here: Francis
and John Paul II have very different corpus sizes, so raw counts mostly measure
how long someone was pope.

!!! note "Where the plotting code lives"
    The `plotting_tools` module that produced those figures is on the
    `agent-plotting-tools` branch and is not yet merged into `main`. The
    committed PNGs are the output of
    `dc26_vatican_explorer.plotting_tools.create_example_plots`.

## Biblical citation search

`search_biblical_citations` scans speech text for references such as `1 Jn 4:8`
using a regex over the book-abbreviation conventions listed in
`data/bible_books.csv`:

```python
from dc26_vatican_explorer.search.search_biblical_citation import (
    search_biblical_citations_db,
)

results = search_biblical_citations_db(r"1\s*(?:Jn\.?|John)\s*4")
```

Each result pairs the database row with the matched citations and the
surrounding context, so a hit can be read back in situ rather than trusted
blind.
