# Vatican Explorer

[![Deploy Docs](https://github.com/rcds-dssv/dc26-vatican-explorer/actions/workflows/make_github_pages.yml/badge.svg)](https://github.com/rcds-dssv/dc26-vatican-explorer/actions/workflows/make_github_pages.yml)
[![Docs](https://img.shields.io/badge/docs-live-blue)](https://rcds-dssv.github.io/dc26-vatican-explorer/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

**Vatican Explorer** is a data-science toolkit for scraping, cleaning, querying, and analyzing the full corpus of papal speeches published on the Vatican's official website ([vatican.va](https://www.vatican.va)). It turns decades of angeluses, audiences, and addresses into a structured, queryable dataset — enabling quantitative comparison of rhetorical themes, biblical references, and speech patterns across popes, languages, and time periods.

This is a **DSSV Data Conclave FY26** project built by the [RCDS](https://www.it.northwestern.edu/departments/it-services-support/research/) team at Northwestern University.

![Monthly output through the pandemic](docs/assets/covid_rupture.png)

Between March and August 2020 Francis's speeches and homilies fell 89%, while the Sunday Angelus went *up* by two. See [Findings](https://rcds-dssv.github.io/dc26-vatican-explorer/findings/).

## What it does

The project covers the full pipeline from raw web page to publication-ready chart:

1. **Scrape** — Systematically collect papal speeches by pope, year, section (angelus, audiences, speeches), and language directly from vatican.va, with polite rate-limiting and retry logic.
2. **Store** — Load everything into a local SQLite database, with tables for popes and texts linked by foreign key.
3. **Clean** — Normalize inconsistent date formats (including Vatican's Roman-numeral dates), extract metadata from titles, and enrich records with biographical data.
4. **Search** — Find and extract biblical citations (e.g., `Jn 8:32`, `1 Cor 13:6`) anywhere in the speech corpus using regex-based search.
5. **Analyze & visualize** — Compare word usage, speech volume, and scriptural references across popes, languages, and eras with a reusable set of charting helpers.

## Quick start

```bash
# Install dependencies (requires uv: https://docs.astral.sh/uv/)
# Scraping and dataframe support live in opt-in groups
uv sync --group scrape --group data-manipulation

# Scrape a pope's speeches for a given year and section
uv run python -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline \
    --pope "Francis" --years "2025" --section "angelus"

# Generate the figures behind the Findings page
uv run python -m dc26_vatican_explorer.plotting_tools.story_plots

# Generate example per-pope comparison plots
uv run python -m dc26_vatican_explorer.plotting_tools.create_example_plots

# Run the test suite
uv run pytest tests/
```

The speech database is **not** in this repository (`data/*.db` is gitignored) —
the texts remain the property of the Holy See. Build your own with the scraper
above, or ask the team for a copy.

## Project layout

| Path | Purpose |
|---|---|
| [`src/dc26_vatican_explorer/vatican_scraper/`](src/dc26_vatican_explorer/vatican_scraper/) | Multi-step scraper: popes → years → speeches → text → database |
| [`src/dc26_vatican_explorer/database_utils/`](src/dc26_vatican_explorer/database_utils/) | SQLite connection, schema, and query helpers |
| [`src/dc26_vatican_explorer/data_cleaning/`](src/dc26_vatican_explorer/data_cleaning/) | Date normalization, metadata extraction, birthplace enrichment |
| [`src/dc26_vatican_explorer/search/`](src/dc26_vatican_explorer/search/) | Biblical citation search over the speech corpus |
| [`src/dc26_vatican_explorer/plotting_tools/`](src/dc26_vatican_explorer/plotting_tools/) | Reusable chart helpers and example database-driven analyses |
| [`src/dc26_vatican_explorer/pope_comparison/`](src/dc26_vatican_explorer/pope_comparison/) | Cross-pope speech quantification and profiling |
| [`docs/analyses/`](docs/analyses/) | Jupyter notebooks for exploratory analysis, published on the docs site |
| [`data/`](data/) | Reference data (`bible_books.csv`); the local, gitignored `vatican_texts.db` lives here too |
| [`tests/`](tests/) | Unit and integration test suite |

## Documentation

Full setup instructions, database schema, CLI reference, and API documentation are published at:

**[rcds-dssv.github.io/dc26-vatican-explorer](https://rcds-dssv.github.io/dc26-vatican-explorer/)**

| Page | Contents |
|---|---|
| [Findings](https://rcds-dssv.github.io/dc26-vatican-explorer/findings/) | What the corpus shows, with caveats |
| [The Pipeline](https://rcds-dssv.github.io/dc26-vatican-explorer/pipeline/) | How speeches get from vatican.va into SQLite |
| [The Data](https://rcds-dssv.github.io/dc26-vatican-explorer/data/) | Schema, coverage, and query recipes |
| [Analyses](https://rcds-dssv.github.io/dc26-vatican-explorer/analyses/) | Notebooks and word-frequency comparisons |
| [API Reference](https://rcds-dssv.github.io/dc26-vatican-explorer/using-vatican-explorer/) | Generated from docstrings |

Docs are built with MkDocs from the [`docs/`](docs/) folder and deployed automatically to the `gh-pages` branch on every push to `main` via [`make_github_pages.yml`](.github/workflows/make_github_pages.yml).

## Project tracking

Active work is tracked on the [GitHub Project board](https://github.com/orgs/rcds-dssv/projects/8).

## License

This project is licensed under [CC BY-NC 4.0](LICENSE) — free to use and adapt for non-commercial purposes with attribution.
