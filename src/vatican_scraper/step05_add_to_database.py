# src/vatican_scraper/step05_add_to_database.py
# to run:
#
# from the root directory
# $ python -m vatican_scraper.step05_add_to_database

from vatican_scraper.step04_fetch_speech_texts import fetch_speeches_to_feather
from vatican_scraper.argparser import get_scraper_args
from config import _DB_PATH

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from pathlib import Path

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

CREATE TABLE IF NOT EXISTS texts (
    _texts_id INTEGER PRIMARY KEY,
    pope_id INTEGER,
    section TEXT,
    year TEXT,
    date TEXT,
    location TEXT,
    title TEXT,
    language TEXT,
    url TEXT,
    text_content TEXT,
    entry_creation_date TEXT,
    UNIQUE(pope_id, title, date),
    FOREIGN KEY (pope_id) REFERENCES popes(_pope_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
"""


def ensure_db_and_table(db_path: Path, table_schema: str = DEFAULT_TABLE_SCHEMA) -> None:
    """
    Create the sqlite database if it doesn't exist.
    
    Args:
        db_path: path to sqlite file (creates file if doesn't exist)
        table_schema: SQL schema

    Does not return content
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(table_schema)
        conn.commit()
    finally:
        conn.close()

def add_content_to_db(db_path: Path, record: Dict[str, Optional[str]], replace: bool = False) -> Tuple[int, int]:
    """
    Add a text record (dict) to the SQLite DB. Creates DB if needed.
    Update the popes database if needed.

    Args:
        db_path: path to sqlite database file (creates file if doesn't exist)
        record: dictionary with keys like 'pope','name','date','text', etc
        replace: if True, will REPLACE an existing row with the same (pope,name,date).
                 If False, will IGNORE duplicates (default).

    Returns:
        row id of inserted/updated (text, pope), or 0 if ignored.
    """

    ensure_db_and_table(db_path)

    # canonicalize keys and provide defaults
    pope_name = record.get("pope")
    pope_slug = record.get("pope_slug")
    pope_number = record.get("pope_number")
    secular_name = record.get("secular_name")
    place_of_birth = record.get("place_of_birth")
    section = record.get("section")
    year = record.get("year")
    pontificate_begin = record.get("pontificate_begin")
    pontificate_end = record.get("pontificate_end")
    date = record.get("date")
    location = record.get("location")
    title = record.get("title")
    language = record.get("language")
    text = record.get("text")
    url = record.get("url")
    entry_creation_date = datetime.now(timezone.utc).isoformat()  # store UTC timestamp


    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        cur = conn.cursor()
        # IGNORE will skip insertion if UNIQUE constraint conflict occurs
        sql_starter = "INSERT OR IGNORE INTO"
        if replace:
            # REPLACE will delete the existing row with conflicting unique key and insert a new one
            sql_starter = "INSERT OR REPLACE INTO"

        # update pope database
        sql_pope = sql_starter + """
            popes
                (pope_name, pope_slug, pope_number, secular_name, place_of_birth, pontificate_begin, pontificate_end, entry_creation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql_pope, (pope_name, pope_slug, pope_number, secular_name, place_of_birth, pontificate_begin, pontificate_end, entry_creation_date))
        conn.commit()

        # retrieve the pope_id (whether newly inserted or existing)
        cur.execute("SELECT _pope_id FROM popes WHERE pope_name = ? AND pope_number = ?", (pope_name, pope_number))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Pope {pope_name} (#{pope_number}) not found in database.")
        _pope_id = row[0]

        # update texts database
        sql_text = sql_starter + """
            texts
                (pope_id, section, year, date, location, title, language, url, text_content, entry_creation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql_text, (_pope_id, section, year, date, location, title, language, url, text, entry_creation_date))
        conn.commit()
        _text_id = cur.lastrowid or 0

        # If row was ignored, lastrowid will be 0; if replaced/inserted, lastrowid is the row id.
        return _text_id, _pope_id
    finally:
        conn.close()

def main() -> None:
    """
    Example of how to add a single text to the database.  This is not intended to be run on its own.
    Instead, the code above should be run as part of the overall scraping pipeline, as in step06_run_scraping_pipeline.py.
    """

    p, args = get_scraper_args()
        
    _, rows = fetch_speeches_to_feather(
        pope=args.pope,
        years_spec=args.years,
        lang=args.lang,
        section=args.section,
        out=args.out,
        debug_loc=args.debug_loc,
        max_n_speeches=1
    )


    for row in rows:
        print(row["url"])
        _text_id, _pope_id = add_content_to_db(_DB_PATH, row)

        if _text_id:
            print("Inserted text into database with id:", _text_id)
        else:
            print("Text record already exists (ignored).")
        if _pope_id:
            print("Inserted pope into database with id:", _pope_id)
        else:
            print("Pope record already exists (ignored).")


if __name__ == "__main__":
    main()

    