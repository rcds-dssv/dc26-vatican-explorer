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

[Word Frequency](word-frequency.md) compares "love", "amore" and "Jesus" across
**five** pontificates back to Paul VI, as raw counts and as rates normalised by
document count. The headline: Francis says "Jesus" about 60% more often per
document than Benedict XVI or John Paul II, while Benedict leads on "love" —
and the English and Italian corpora, scraped independently, agree on the
ordering.

Those figures come from a wider corpus than the current build, which holds only
Francis and Leo XIV. Run `create_example_plots` against the reference database
today and you get the same charts with two bars:

```bash
uv run -m dc26_vatican_explorer.plotting_tools.create_example_plots
```

With two pontificates the comparison is thin — "love" appears 2.71 times per
English document under Francis against 2.37 under Leo XIV. Scraping the earlier
popes restores the five-way version.

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
