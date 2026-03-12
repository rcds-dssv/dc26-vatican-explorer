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
    popes_data is a dict that looks like this:
    {
        "<pope_name>": {"pope_name": str,
                        "papacy_began": str,
                        "texts": [{ "title": str,
                                    "date": str | date,
                                    "category": str}, ...]
        },...}
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