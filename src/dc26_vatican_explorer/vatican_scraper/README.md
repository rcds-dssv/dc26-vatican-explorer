This directory contains code for scraping the Vatican website and generating the sqlite database. 

To retrieve the first 20 speeches from the default pope and year, run the code from the repo root with:

```
uv run -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline --max_n_speeches 20
```

You can also use the `--help` flag to see all the other options.


## Running the Vatican scraper pipeline

From repo root:

```bash
# initial setup
uv venv
source .venv/bin/activate
uv pip install -e ".[scrape,data-manipulation]"

# This is the command we used to populate the database
uv run -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline \
  --popes "Paul VI,John Paul I,John Paul II,Benedict XVI,Francis,Leo XIV" \
  --section "homilies,audiences,speeches" \
  --years "1963-2026" \
  --lang "EN,IT" \
  2>&1 | tee "run_all.log"
```
