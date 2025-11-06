# Data Directory

This folder serves as a repository for our data. Not all data is on GitHub, but when working locally, place your `.db` here. The data files we should have are:

**Reference Data**
- `bible_books.csv`

**Working Data**
- (local) `vatican_speeches.db` (This is available by request, and can also be created using the `src/vatican_scraper` pipeline.)


This database has the following format :

```
DEFAULT_TABLE_SCHEMA = """

CREATE TABLE IF NOT EXISTS popes (
    _pope_id INTEGER PRIMARY KEY,
    pope_name TEXT,
    pope_slug TEXT,
    pope_number TEXT,
    secular_name TEXT,
    place_of_birth TEXT,
    pontificate_begin TEXT,
    pontificate_end TEXT,
    entry_creation_date TEXT,
    UNIQUE(pope_name, pope_number)
);

CREATE TABLE IF NOT EXISTS speeches (
    _speech_id INTEGER PRIMARY KEY,
    pope_name TEXT,
    section TEXT,
    year TEXT,
    date TEXT,
    location TEXT,
    title TEXT,
    language TEXT,
    url TEXT,
    text TEXT,
    entry_creation_date TEXT,
    UNIQUE(pope_name, title, date)
);
"""
```

I also included an example python file to test reading from the database.  You can run this from the root directory with:

```
python -m data.database_reader_example

```