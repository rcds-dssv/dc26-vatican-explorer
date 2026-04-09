"""
Placeholder
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
    Fetch speech metadata from the SQLite database.
    Parameters
    ----------
    db_path : str | Path
        Path to the SQLite database file.
    Returns
    -------
    list[dict]
        A list of dictionaries, one per row returned by the query.
        Each dict contains at least the following keys:
        - "pope_name": str
        - "title": str
        - "date": str
        - "section": str
        - "pontificate_begin": str
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