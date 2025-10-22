from vscraper import get_all_speech_links, get_speech_text

import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional

DEFAULT_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS speeches (
    id INTEGER PRIMARY KEY,
    pope TEXT,
    name TEXT,
    date TEXT,
    special TEXT,
    text TEXT,
    source_url TEXT,
    created_at TEXT,
    UNIQUE(pope, name, date)
);
"""

def ensure_db_and_table(db_path: str, table_schema: str = DEFAULT_TABLE_SCHEMA) -> None:
    """
    Create the sqlite file and the speeches table if they don't exist.
    
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

def add_speech_to_db(db_path: str, record: Dict[str, Optional[str]], replace: bool = False) -> int:
    """
    Add a speech record (dict) to the SQLite DB. Creates DB/table if needed.

    Args:
        db_path: path to sqlite file (creates file if doesn't exist)
        record: dictionary with keys like 'pope','name','date','special','text','source_url'
        replace: if True, will REPLACE an existing row with the same (pope,name,date).
                 If False, will IGNORE duplicates (default).

    Returns:
        row id of inserted/updated row, or 0 if ignored.
    """

    ensure_db_and_table(db_path)

    # canonicalize keys and provide defaults
    pope = record.get("pope")
    name = record.get("name")
    date = record.get("date")
    special = record.get("special")
    text = record.get("text")
    source_url = record.get("source_url")
    created_at = datetime.now(timezone.utc).isoformat()  # store UTC timestamp

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        if replace:
            # REPLACE will delete the existing row with conflicting unique key and insert a new one
            sql = """
            INSERT OR REPLACE INTO speeches
              (pope, name, date, special, text, source_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        else:
            # IGNORE will skip insertion if UNIQUE constraint conflict occurs
            sql = """
            INSERT OR IGNORE INTO speeches
              (pope, name, date, special, text, source_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

        cur.execute(sql, (pope, name, date, special, text, source_url, created_at))
        conn.commit()

        # If row was ignored, lastrowid will be 0; if replaced/inserted, lastrowid is the row id.
        return cur.lastrowid or 0
    finally:
        conn.close()

if __name__ == "__main__":
    url = "https://www.vatican.va/content/francesco/en/angelus/2025.index.html"
    links = get_all_speech_links(url)

    test_url = links[0]
    record = get_speech_text(test_url)
    print(record)

    database_path = os.path.join("..","data","speeches.db")
    print(database_path)

    row_id = add_speech_to_db(database_path, record)
    if row_id:
        print("Inserted row id:", row_id)
    else:
        print("Record already exists (ignored).")
    