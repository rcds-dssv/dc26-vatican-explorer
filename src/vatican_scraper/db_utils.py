from pathlib import Path
import sqlite3


def speech_url_exists_in_db(db_path: Path, url: str) -> bool:
    """
    Check if a speech with the given URL exists in the database.
    """
    
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM speeches WHERE url = ? LIMIT 1", (url,))
            return cur.fetchone() is not None
    except Exception:
        return False