This directory contains code for scraping the Vatican website and generating the sqlite database. 

To retrieve the first 20 speeches from the default pope and year, run the code from the repo root with:

```
uv run -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline --max_n_speeches 20
```

You can also use the `--help` flag to see all the other options.


## Running the Vatican scraper pipeline

### Setup

From repo root:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[scrape,data-manipulation]"

uv run -c "from dc26_vatican_explorer.config import _DB_PATH; from dc26_vatican_explorer.vatican_scraper.step05_add_to_database import ensure_db_and_table; ensure_db_and_table(_DB_PATH); print('DB initialized at', _DB_PATH)"

# Optionally start from a clean data base:
rm -f data/vatican_texts.db
uv run -c "from dc26_vatican_explorer.config import _DB_PATH; from dc26_vatican_explorer.vatican_scraper.step05_add_to_database import ensure_db_and_table; ensure_db_and_table(_DB_PATH); print('DB initialized at', _DB_PATH)"

popes="Paul VI,John Paul I,John Paul II,Benedict XVI,Francis,Leo XIV"
years="1963-2026"

# then run the pipeline; example: (Paul VI → Leo XIV, EN + IT; homilies/audiences/speeches)

for lang in EN IT; do
  for section in homilies audiences speeches; do
    echo "=== RUN: lang=$lang section=$section ==="
    uv run -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline \
      --popes "$popes" \
      --section "$section" \
      --years "$years" \
      --lang "$lang" \
      2>&1 | tee "run_${lang}_${section}.log"
  done
done
