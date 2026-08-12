# dc26-vatican-explorer
DSSV Data Conclave project for FY26: Vatican Explorer

Our docs are live [here](https://rcds-dssv.github.io/dc26-vatican-explorer/) and are built on the `gh-pages` branch via an actions script `make_github_pages.yml` in the `main` branch, triggered automatically on push to `main`.  

The site is where the project is presented:

- **The Pipeline** — how speeches get from vatican.va into SQLite, and how to run it
- **The Data** — schema, coverage of the current build, and how to query it
- **Analyses** — notebooks, published with their outputs
- **API Reference** — generated from docstrings

The speech database itself is not in this repository (`data/*.db` is gitignored).
Build your own with the scraper, or ask the team for a copy.

```bash
uv sync --group scrape --group data-manipulation
uv run -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline \
    --pope Francis --years 2024 --section angelus --lang EN --max_n_speeches 5
```


[Github Project](https://github.com/orgs/rcds-dssv/projects/8)
