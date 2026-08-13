# The Data

Everything downstream — search, word frequencies, the notebooks — reads from a
single SQLite file, `data/vatican_texts.db`.

!!! warning "The database is not in the repository"
    `data/*.db` is gitignored. The speech texts remain the property of the Holy
    See; see the [Dicastery for Communication legal notice](resources/communication_dicastery.md)
    before redistributing anything beyond aggregate counts. Build your own copy
    with the [pipeline](pipeline.md), or ask the team for one.

## Schema

Two tables. `texts` holds one row per speech per language; `popes` holds one
row per pontiff.

=== "popes"

    | Column | Type | Notes |
    |---|---|---|
    | `_pope_id` | INTEGER | Primary key. |
    | `pope_name` | TEXT | Display name, e.g. `Francis`. |
    | `pope_slug` | TEXT | URL segment on vatican.va, e.g. `francesco`. |
    | `pope_number` | TEXT | Regnal number where applicable. |
    | `secular_name` | TEXT | Birth name. |
    | `place_of_birth` | TEXT | Populated by `add_birthplace_to_db`, not by the scraper. |
    | `pontificate_begin` | TEXT | ISO date. Used to reject implausible speech dates. |
    | `pontificate_end` | TEXT | ISO date, null for a reigning pope. |
    | `entry_creation_date` | TEXT | When the row was written. |

    Unique on `(pope_name, pope_number)`.

=== "texts"

    | Column | Type | Notes |
    |---|---|---|
    | `_texts_id` | INTEGER | Primary key. |
    | `pope_id` | INTEGER | Foreign key to `popes._pope_id`, cascading. |
    | `section` | TEXT | `angelus`, `homilies`, `speeches`, … |
    | `year` | TEXT | Year the speech is filed under on the site. |
    | `date` | TEXT | Raw date; normalised by the cleaning pipeline. |
    | `location` | TEXT | Extracted heuristically from the page. |
    | `title` | TEXT | Speech title. |
    | `language` | TEXT | `EN`, `IT`, … |
    | `url` | TEXT | Source page. |
    | `text_content` | TEXT | Body text. May be null if extraction failed. |
    | `entry_creation_date` | TEXT | When the row was written. |

    Unique on `(pope_id, title, date)` — this is what makes re-running a scrape
    idempotent.

The `year` and `date` columns are stored as TEXT and are not guaranteed to
agree: `year` comes from the index page a speech was listed under, `date` from
the page itself. Where they conflict, the cleaning pipeline trusts the date and
falls back to parsing the title.

## Coverage

Check what your database actually contains — counts of speeches per pope, per
language, per section, and how many are missing body text:

```bash
uv run -m dc26_vatican_explorer.database_utils.print_database_diagnostics
```

The reference build covers **7,808 speeches** across two pontificates, in
English and Italian. Every row has body text — text extraction currently fails
on none of them.

| Pope | Language | Section | Speeches | Missing text |
|---|---|---:|---:|---:|
| Francis | EN | angelus | 688 | 0 |
| Francis | EN | homilies | 550 | 0 |
| Francis | EN | speeches | 2177 | 0 |
| Francis | IT | angelus | 688 | 0 |
| Francis | IT | homilies | 549 | 0 |
| Francis | IT | speeches | 2176 | 0 |
| Leo XIV | EN | angelus | 71 | 0 |
| Leo XIV | EN | homilies | 93 | 0 |
| Leo XIV | EN | speeches | 326 | 0 |
| Leo XIV | IT | angelus | 71 | 0 |
| Leo XIV | IT | homilies | 93 | 0 |
| Leo XIV | IT | speeches | 326 | 0 |

Francis spans 2013–2025 (6,828 speeches); Leo XIV spans 2025–2026 (980).

!!! danger "This corpus was 30% smaller until the per-year cap was fixed"
    An earlier build stored exactly 47 angelus, 44 homilies and 126 speeches
    for *every* Francis year, because `max_n_speeches` leaked across years in
    `step04`. Month indexes are walked newest-first, so the truncation deleted
    January–April from most years — Lent and Easter included. If you have a
    database built before that fix, re-run the pipeline: existing rows are
    kept and the missing documents are filled in. See
    [Findings §5](findings.md#5-what-the-data-could-not-say-last-week).

!!! info "The EN and IT counts are close but not identical"
    Homilies differ by one — 550 English against 549 Italian. The two languages
    are scraped as separate passes over separate index pages, so a document
    published in one language and not the other shows up as exactly this kind
    of gap. Treat cross-language comparisons as approximate unless you join on
    URL.

Earlier pontificates (Benedict XVI, John Paul II, Paul VI) are supported by the
scraper but are not in this build. Add them by re-running the pipeline with
`--popes "Benedict XVI,John Paul II"` and the appropriate year range.

Add `--show-missing-urls` to list the specific pages whose text extraction came
back empty. Those are usually PDF-only documents or pages using an unusual
template, and are worth re-checking before treating a zero count as a real
absence.

## Querying

Filter the `texts` table without writing SQL:

```bash
uv run -m dc26_vatican_explorer.database_utils.check_texts \
    --pope Francis --section angelus --years 2020-2024 --lang EN --first
```

From Python, `query_texts` takes the same filters, and `query_missing_fields`
reports rows with null or empty values in any of `text_content`, `date`,
`location`, `title`, `language`, `place_of_birth`, `secular_name`,
`pontificate_begin`, `pontificate_end`:

```python
from dc26_vatican_explorer.database_utils.database_helpers import (
    query_texts,
    query_missing_fields,
)

rows = query_texts(pope_name="Francis", section="angelus", years="2020-2024")
gaps = query_missing_fields(fields=["text_content", "date"])
```

For cleaned, date-normalised metadata grouped by pope, use the cleaning
pipeline instead — it returns `Pope` objects holding sorted `Speech` lists:

```python
from dc26_vatican_explorer.data_cleaning import get_clean_speech_metadata

popes = get_clean_speech_metadata(pope_name="Francis", include_text=False)
```

## Reference data

`data/bible_books.csv` maps the 72 books of the canon to their group,
testament, and accepted abbreviations — the vocabulary behind the citation
regex in [`search_biblical_citation`](using-vatican-explorer.md).

| book | group | testament | abbreviations |
|---|---|---|---|
| Genesis | Pentateuch | old | Gen |
| Exodus | Pentateuch | old | Ex., Exo., Exod. |
| … | | | |
| Apocalypse | Revelations | new | Rev |
