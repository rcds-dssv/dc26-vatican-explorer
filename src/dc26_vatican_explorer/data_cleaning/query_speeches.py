"""
Database interaction layer for fetching Vatican speech metadata.

This module handles connection management and raw data retrieval from the 
SQLite database containing Pope and Text records.
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
def fetch_speech_metadata(
    db_path: str | Path,
    include_text: bool = False,
    limit: int | None = None,
    random_sample: bool = False,
    pope_name: str | None = None
) -> list[dict]:
    """
    Fetch raw speech and pontificate metadata from the SQLite database.
    
    Args:
        db_path (str or Path): Path to the SQLite database file.
        include_text (bool): Whether to include the raw speech text content.
        limit (int, optional): Maximum number of speeches to retrieve.
        random_sample (bool): Whether to return a random sample of speeches.
        pope_name (str, optional): Name of a specific Pope to filter by.
    
    Returns
        A list of dictionaries, one per row returned by the query. Each dict contains:
            - pope_name (str): The name of the pope.
            - title (str): The speech title.
            - date (str): The date of the speech.
            - section (str): The type of speech.
            - pontificate_begin (str): The start date of the pontificate.
            - text_content (str, optional): The raw text of the speech (if include_text is True).
    """
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            connection.row_factory = sqlite3.Row
            
            # Select columns dynamically
            columns = "p.pope_name, t.title, t.date, t.section, p.pontificate_begin"
            if include_text:
                columns += ", t.text_content"
                
            query_parts = [f"SELECT {columns}", "FROM popes p", "JOIN texts t ON p._pope_id = t.pope_id"]
            parameters = []
            
            # Filter by Pope Name
            if pope_name is not None:
                query_parts.append("WHERE LOWER(p.pope_name) = LOWER(?)")
                parameters.append(pope_name)
                
            # Order By clause
            if random_sample:
                query_parts.append("ORDER BY RANDOM()")
            else:
                query_parts.append("ORDER BY p.pontificate_begin, t.date")
                
            # Limit clause
            if limit is not None:
                query_parts.append("LIMIT ?")
                parameters.append(limit)
                
            query = "\n".join(query_parts)
            query_results =  [dict(row) for row in connection.execute(query, parameters)]

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