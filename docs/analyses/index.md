# Analyses

Exploratory work built on top of the speech database. Each analysis is a
notebook that can be re-run against your own copy of `vatican_texts.db`.

| Analysis | Question | Result |
|---|---|---|
| [1 John 4](first_john_4.ipynb) | How often do popes cite the "God is love" passage, and does that change by year and by pontificate? | 52 citations across 49 speeches, 2013–2026 |

See also [Findings](../findings.md) for the corpus-wide results.

## What 1 John 4 shows

Against the current [7,808-speech build](../data.md), the passage appears 52
times in 49 speeches — 43 by Francis, 9 by Leo XIV.

That gap is smaller than it looks. Francis's 43 citations are spread over
twelve years and 6,828 speeches; Leo XIV's 9 come from a single year and 980
speeches. Per speech, the newer pontificate cites the passage at several times
the rate. One year is a thin basis for a claim about a papacy, so this is a
hypothesis to revisit as the corpus grows, not a conclusion.

!!! note "These numbers moved once already"
    An earlier build reported 43 citations across 41 speeches. The difference
    is not a change in method — it is the 1,797 documents recovered by fixing
    the per-year scraper cap. Counts quoted here are only as complete as the
    corpus underneath them.

The notebooks are rendered here with their stored outputs — the build does not
execute them, because the database is deliberately not committed to the
repository. To run one yourself, [build the database](../data.md) first, then:

```bash
uv sync --group data-manipulation
uv run jupyter lab docs/analyses/
```

## Word frequency comparisons

`plotting_tools.create_example_plots` compares word usage across popes — "love"
and "Jesus" in English, "amore" in Italian — as raw counts and as rates
normalised by speech length:

```bash
uv run -m dc26_vatican_explorer.plotting_tools.create_example_plots
```

It writes to `outputs/example_plots/` (gitignored). These charts are not on the
site, because with two pontificates in the corpus every one of them is a
two-bar comparison, and the two bars are close: "love" appears 2.71 times per
English document under Francis against 2.37 under Leo XIV. That difference is
not worth a figure. The framing becomes useful once earlier pontificates are
collected.

!!! warning "Earlier versions of this site showed richer per-pope charts"
    Those PNGs were generated from a corpus containing John Paul II, Benedict
    XVI and Paul VI, none of which this build contains, so they could not be
    reproduced from the shipped pipeline. They have been removed in favour of
    the [Findings](../findings.md) figures, which regenerate from the current
    database.

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
