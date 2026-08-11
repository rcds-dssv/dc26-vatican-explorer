# Vatican Explorer

![Vatican Explorer Logo](assets/logo.png)

**Vatican Explorer** is a data-science toolkit for scraping, cleaning, querying, and analyzing the full corpus of papal speeches published on the Vatican's official website (vatican.va). It enables quantitative comparison of rhetorical themes, biblical references, and speech patterns across popes, languages, and time periods.

## Overview

The project covers the full data pipeline:

1. **Scraping** — Systematically collects papal speeches by pope, year, section (e.g., homilies, addresses, angelus), and language (Italian, English, etc.) from vatican.va.
2. **Database** — Stores all collected content in a local SQLite database with tables for popes, speeches, and full text.
3. **Cleaning** — Normalizes dates, extracts metadata from titles, adds birthplace data, and validates the resulting dataset.
4. **Search** — Finds biblical citations within speech texts using regex patterns.
5. **Analysis** — Quantifies word-frequency themes (e.g., "love," "amore," "Jesus") per pope, compares speech volumes, and produces publication-ready visualizations.

## Example Analyses

Below are representative figures generated from the `plotting_tools` module. Each plot compares how different popes use specific words or phrases across their speeches.

### Speech Volume by Pope

How many English speeches did each pope deliver?

![Speech count per pope](assets/speech_count_EN_per_pope.png)

### "Love" in English Speeches

Total word count of "love" per pope (text content):

![Love text content per pope](assets/love_EN_text_content_per_pope.png)

Rate of "love" usage (normalized by total speech length):

![Love rate per pope](assets/love_EN_text_content_rate_per_pope.png)

### "Amore" in Italian Speeches

Total word count of "amore" per pope in Italian-language texts:

![Amore text content per pope](assets/amore_IT_text_content_per_pope.png)

Rate of "amore" usage in Italian:

![Amore rate per pope](assets/amore_IT_text_content_rate_per_pope.png)

### "Jesus" in English Speeches

Total word count of "Jesus" per pope in English texts:

![Jesus text content per pope](assets/Jesus_EN_text_content_per_pope.png)

### Biblical Citation Analysis

The toolkit can also search for specific biblical references across all speeches. For example, counting mentions of **1 John 4** by year and by pope reveals how different pontiffs engage with particular scriptural passages.

## Getting Started

```bash
# Install dependencies
uv sync

# Run the full scraping pipeline
uv run python -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline \
    --popes Benedict_XVI,Francis \
    --sections homilies,addresses,angelus \
    --langs Italian,English

# Clean and query speech metadata
uv run python -c "
from dc26_vatican_explorer.data_cleaning import get_clean_speech_metadata
data = get_clean_speech_metadata()
print(data)
"
```

## Project Structure

| Directory | Purpose |
|---|---|
| `src/dc26_vatican_explorer/vatican_scraper/` | Multi-step scraper (popes → years → speeches → text → DB) |
| `src/dc26_vatican_explorer/data_cleaning/` | Date normalization, birthplace enrichment, data validation |
| `src/dc26_vatican_explorer/database_utils/` | SQLite helpers, schema checks, query utilities |
| `src/dc26_vatican_explorer/search/` | Biblical citation search with regex patterns |
| `src/dc26_vatican_explorer/pope_comparison/` | Speech quantification and pope profiling |
| `analyses/` | Jupyter notebooks for exploratory analysis |
| `tests/` | Unit and integration tests |

## Documentation

- [Using Vatican Explorer](using-vatican-explorer.md) — How to set up and run the toolkit
- [Core API Reference](core-api.md) — Full function and class documentation

## Resources

- [Bible text conventions](resources/bible_text.md)
- [Dicastery communication guidelines](resources/communication_dicastery.md)

## About

Vatican Explorer is a **DSSV Data Conclave FY26** project by the RCDS team at [Northwestern University](https://www.northwestern.edu). The live documentation is hosted on GitHub Pages at [rcds-dssv.github.io/dc26-vatican-explorer](https://rcds-dssv.github.io/dc26-vatican-explorer/).
