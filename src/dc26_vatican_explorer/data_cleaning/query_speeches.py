"""
Database interaction layer for fetching Vatican speech metadata.

This module handles connection management and raw data retrieval from the 
SQLite database containing Pope and Text records.

TODO: Decide if I want to turn the dictionary into a dataclass instead, this may make it easy for dependents
"""

# ----------------------
# :: IMPORTS ::
# ----------------------
from contextlib import closing
import sqlite3
from pathlib import Path

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def fetch_speech_metadata(db_path:str | Path) -> list[dict]:
    """
    Fetch raw speech and pontificate metadata from the SQLite database.
    
    Args:
        db_path (str or Path): Path to the SQLite database file.
    
    Returns
        A list of dictionaries, one per row returned by the query. Each dict contains:
            - pope_name (str): The name of the pope.
            - title (str): The speech title.
            - date (str): The date of the speech.
            - section (str): The type of speech.
            - pontificate_begin (str): The start date of the pontificate.
    """
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.row_factory = sqlite3.Row
            query = (
                """
                SELECT p.pope_name, t.title, t.date, t.section, p.pontificate_begin
                FROM popes p
                JOIN texts t ON p._pope_id = t.pope_id
                ORDER BY p.pontificate_begin, t.date
                """
            )
            query_results =  [dict(row) for row in connection.execute(query)]

    return query_results

# ----------------------
# :: MAIN ENTRYPOINT ::
# ----------------------
def main():
    db_path = Path('data/vatican_texts.db')
    query_results = fetch_speech_metadata(db_path)
    print(query_results[0])
    return

if __name__ == "__main__":
    main()