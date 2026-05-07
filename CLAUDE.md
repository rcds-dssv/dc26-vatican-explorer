# CLAUDE.md — Vatican Explorer Codebase Guide

## Project Overview

**dc26-vatican-explorer** is a DSSV Data Conclave FY26 project that scrapes papal speeches from the Vatican website, stores them in a SQLite database, and provides analysis tools (biblical citation search, pope comparisons, etc.).

**Entry point CLI:** `vatican` (maps to `dc26_vatican_explorer.__main__:main` — currently just a stub)

---

## Repository Layout

```
dc26-vatican-explorer/
├── pyproject.toml              # build config, deps, ruff/deptry settings
├── data/
│   ├── vatican_texts.db        # SQLite DB (local only, not in git)
│   ├── bible_books.csv         # reference data
│   └── database_reader_example.py
├── src/dc26_vatican_explorer/
│   ├── config.py               # shared constants (_BASE, _DB_PATH, _PKG_DIR)
│   ├── __main__.py             # CLI stub
│   ├── vatican_scraper/        # web scraping pipeline (steps 01–06)
│   ├── database_utils/         # SQLite helpers
│   ├── data_cleaning/          # date normalization, speech metadata cleaning
│   ├── search/                 # biblical citation search
│   └── pope_comparison/        # analysis notebooks + dataclasses
├── tests/                      # pytest tests
└── analyses/                   # Jupyter notebooks
```

---

## Key Configuration (`config.py`)

```python
_BASE = "https://www.vatican.va/"
_POPE_INDEX_RECENT_URL = "https://www.vatican.va/holy_father/index.htm"
_PKG_DIR = Path(__file__).resolve().parent   # src/dc26_vatican_explorer/
_DB_PATH = (_PKG_DIR.parent.parent / "data" / "vatican_texts.db").resolve()
# resolves to: <repo_root>/data/vatican_texts.db
```

**Important:** The scraper modules (`step0*.py`) import `config` directly (not as `dc26_vatican_explorer.config`) using the bare name `from config import ...`. This works because `src/dc26_vatican_explorer/` is on `sys.path` when running as a module from the repo root.

---

## Database Schema

Two tables in `data/vatican_texts.db` (SQLite):

```sql
CREATE TABLE popes (
    _pope_id          INTEGER PRIMARY KEY,
    pope_name         TEXT NOT NULL,
    pope_slug         TEXT,           -- URL slug e.g. 'francesco'
    pope_number       TEXT,
    secular_name      TEXT,
    place_of_birth    TEXT,
    pontificate_begin TEXT,           -- format: 'DD,HH.MMM.YYYY' (roman month)
    pontificate_end   TEXT,
    entry_creation_date TEXT,
    UNIQUE(pope_name, pope_number)
);

CREATE TABLE texts (
    _texts_id         INTEGER PRIMARY KEY,
    pope_id           INTEGER NOT NULL,
    section           TEXT,           -- e.g. 'angelus', 'audiences', 'speeches'
    year              TEXT,
    date              TEXT,           -- ISO 8601 after cleaning
    location          TEXT,
    title             TEXT,
    language          TEXT,
    url               TEXT NOT NULL UNIQUE,
    text_content      TEXT,
    entry_creation_date TEXT,
    FOREIGN KEY (pope_id) REFERENCES popes(_pope_id) ON UPDATE CASCADE ON DELETE CASCADE
);
```

Known popes in DB (from `adding_birthplace.py`):
- Benedict XVI (`_pope_id=1`) — Marktl, Germany
- John Paul II (`_pope_id=2`) — Wadowice, Poland
- Paul VI (`_pope_id=3`) — Concesio, Italy
- Francis (`_pope_id=4`) — Buenos Aires, Argentina
- Leo XIV (`_pope_id=5`) — Chicago, Illinois

`pontificate_begin` is stored in the raw Vatican format `DD,HH.MMM.YYYY` (Roman-numeral month) and must be parsed with `date_cleaning.format_pontificate_date()`.

---

## Scraping Pipeline (`vatican_scraper/`)

Run the full pipeline from the repo root:
```bash
python -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline \
    --pope "Francis" --years "2025" --section "angelus"
```

| Step | File | Purpose |
|------|------|---------|
| 01 | `step01_list_popes.py` | Scrape pope list from Vatican index; extract slugs |
| 02 | `step02_list_pope_year_links.py` | Get available years and metadata from a pope's main page |
| 03 | `step03_list_speeches.py` | List all speech URLs for a given year index page |
| 04 | `step04_fetch_speech_texts.py` | Fetch speech HTML, extract text, save to `.feather` file |
| 05 | `step05_add_to_database.py` | Load feather rows into the SQLite DB |
| 06 | `step06_run_scraping_pipeline.py` | Orchestrates steps 04+05 for one or more popes |

CLI args (step06 / argparser):
- `--pope "Francis"` (repeatable) or `--popes "Francis,Benedict XVI"` (comma-separated)
- `--years "2025"` or `"2019,2021-2023"` or `"2021-2023"`
- `--section` — `angelus` | `audiences` | `speeches` (default: `angelus`)
- `--lang EN` — two-letter language code
- `--max_n_speeches INT` — limit for debugging
- `--debug-loc` — flag for debug output

The scraper uses polite random delays (`_papal_pause()`) and a shared `requests.Session` with retry logic (6 retries, exponential backoff, respects `Retry-After`).

---

## Database Utilities (`database_utils/database_helpers.py`)

Key functions:
- `connect_to_database()` → `(Connection, Cursor)` — connects to `_DB_PATH`, enables foreign keys
- `register_regexp_function(conn)` — registers Python `re.search` as SQLite `REGEXP`
- `fetch_rows_by_regexp(cursor, query, pattern)` — runs a REGEXP query
- `table_exists(cursor, table_name)` → `bool`
- `column_exists_in_table(cursor, table_name, column_name)` → `bool`
- `check_texts_table_schema(cursor)` → `bool` — validates exact column order
- `sanitize_table_name(table_name)` — escapes double-quotes for safe SQL interpolation
- `speech_url_exists_in_db(db_path, url)` → `bool` — dedup check during scraping

---

## Biblical Citation Search (`search/search_biblical_citation.py`)

```python
from dc26_vatican_explorer.search.search_biblical_citation import (
    search_biblical_citations,       # search a single text string
    search_biblical_citations_db,    # search all texts in the DB
    default_regex_pattern,           # returns the default citation regex
)
```

Default regex: `r'\b(?:[1-3]\s+)?[A-Za-z]{2,4}\s+\d{1,3}:\d{1,3}(?:[-.]\d{1,3})?\b'`

- Matches: `Jn 8:32`, `1 Cor 13:6`, `Mt 9:10-13`, `1 Jn 4:8.16`
- `search_biblical_citations(text, context=100, pattern=None)` → `list[tuple[citation, surrounding_text]]`
- `search_biblical_citations_db(pattern=None, query=None)` → `list[tuple[db_row, citations]]`
  - `db_row` is a tuple with columns in schema order; `text_content` is at index 9

---

## Data Cleaning (`data_cleaning/`)

| File | Purpose |
|------|---------|
| `date_cleaning.py` | `format_pontificate_date()`, `format_date_to_iso()`, `extract_date_from_title()` |
| `query_speeches.py` | `fetch_speech_metadata(db_path)` — JOIN query returning pope+text metadata |
| `cleaning_pipeline.py` | `get_clean_speech_metadata(db_path)` — full pipeline: query → clean dates → sort |
| `adding_birthplace.py` | `add_birthplace_to_db(db_path)` — one-time UPDATE using hardcoded `BIRTH_MAPS` |

Date cleaning notes:
- `format_pontificate_date` parses Vatican's `DD,HH.MMM.YYYY` (Roman-numeral month) format
- `format_date_to_iso` handles Italian month names, typos, and common format variants
- Known bug: dates in titles referencing past events (e.g., John Paul II in 1986) can be extracted incorrectly

---

## Pope Comparison (`pope_comparison/`)

- `speech_quantification.py` — contains `BibleRef` and `PopeSpeech` dataclasses (work in progress)
- `speech_quantification.ipynb` — notebook for analysis
- `pope_profile.ipynb` — notebook for pope profiles

---

## Testing

```bash
# From repo root
pytest tests/
```

`tests/conftest.py` adds `src/` to `sys.path` so tests can import `dc26_vatican_explorer` and `vatican_scraper`.

Test files:
- `test_database_helpers.py` — unit tests for all DB helper functions using in-memory SQLite and `monkeypatch`
- `test_search_biblical_citation.py` — parametrized tests for citation regex matching; DB search tests with mocked dependencies
- `test_pope_utilities.py` — tests for pope name normalization, slug extraction, and name lookup

---

## Import Conventions

- Main package code uses: `from dc26_vatican_explorer.config import _DB_PATH`
- Scraper step modules (run as `python -m dc26_vatican_explorer.vatican_scraper.stepNN`) use: `from config import ...` and `from vatican_scraper.xxx import ...`
- The `pyproject.toml` `[tool.deptry]` section declares `config` and `vatican_scraper` as known first-party to suppress false positive dependency warnings

---

## Dev Commands

```bash
# Install (with uv)
uv sync

# Run a scrape
python -m dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline --pope "Francis" --years "2025"

# Add birthplaces to DB
python -m dc26_vatican_explorer.data_cleaning.adding_birthplace

# Run tests
pytest tests/

# Lint
ruff check src/
deptry src/

# Read from database (example)
python -m data.database_reader_example
```

---

## Notes & Known Issues

- `__main__.py` is a stub — `vatican` CLI does nothing yet
- `speech_quantification.py` dataclasses (`BibleRef`, `PopeSpeech`) are stubs
- `cleaning_pipeline.py` docstring says "PLACEHOLDER"
- The `data/vatican_texts.db` is not committed to git; obtain it separately or generate with the scraper
- Date extraction can misfire on titles that reference historical events (known bug in `date_cleaning.py`)
