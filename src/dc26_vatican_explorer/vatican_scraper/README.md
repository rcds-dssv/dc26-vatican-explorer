This directory contains code for scraping the Vatican website and generating the sqlite database. 

To retrieve the first 20 speeches from the default pope and year, run the code from the `src` directory with:

```
python -m vatican_scraper.step06_run_scraping_pipeline --max_n_speeches 20
```

You can also use the `--help` flag to see all the other options.


## Running the Vatican scraper pipeline

### Setup

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install requests beautifulsoup4 pandas pyarrow

PYTHONPATH=src python3 -c "from config import _DB_PATH; from vatican_scraper.step05_add_to_database import ensure_db_and_table; ensure_db_and_table(_DB_PATH); print('DB initialized at', _DB_PATH)"

# Optionally start from a clean data base:
rm -f data/vatican_texts.db
PYTHONPATH=src python3 -c "from config import _DB_PATH; from vatican_scraper.step05_add_to_database import ensure_db_and_table; ensure_db_and_table(_DB_PATH); print('DB initialized at', _DB_PATH)"

popes="Paul VI,John Paul I,John Paul II,Benedict XVI,Francis,Leo XIV"
years="1963-2026"

# then run the pipeline; example: (Paul VI → Leo XIV, EN + IT; homilies/audiences/speeches)

for lang in EN IT; do
  for section in homilies audiences speeches; do
    echo "=== RUN: lang=$lang section=$section ==="
    PYTHONPATH=src PYTHONUNBUFFERED=1 python3 -u -m vatican_scraper.step06_run_scraping_pipeline \
      --popes "$popes" \
      --section "$section" \
      --years "$years" \
      --lang "$lang" \
      2>&1 | tee "run_${lang}_${section}.log"
  done
done
