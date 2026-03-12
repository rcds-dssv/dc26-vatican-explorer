# Module with helper functions to work with the database

################################## IMPORT LIBRARIES ##################################

import sqlite3
from sqlite3 import Connection, Cursor

from src.config import _DB_PATH

import re

from pathlib import Path

################################## DEFINE FUNCTIONS ##################################

def connect_to_database() -> tuple[Connection, Cursor]:
    """Connects to the SQLite database.

    Returns:
        tuple[Connection, Cursor]: A tuple containing the active database
        connection and a cursor with foreign key enforcement enabled.
    """
    conn: Connection = sqlite3.connect(_DB_PATH)
    cursor: Cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    return conn, cursor

def get_tables_in_database(cursor: Cursor) -> list[str]:
    """Retrieves a list of tables in the database.

    Args:
        cursor: The active database cursor.

    Returns:
        list[str]: A list of table names in the database.
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [t[0] for t in tables]

def get_column_names_in_table(cursor: Cursor, table_name: str) -> list[str]:
    """Retrieves a list of column names in a specified table.

    Args:
        cursor: The active database cursor.
        table_name: The name of the table to inspect.

    Returns:
        list[str]: A list of column names in the specified table.
    """
    safe_table = sanitize_table_name(table_name)
    cursor.execute(f'PRAGMA table_info("{safe_table}")')  
    columns = cursor.fetchall()
    return [c[1] for c in columns]

def regexp(pattern: str, text: str | None) -> int:
    """Implements REGEXP operator for SQLite.

    Args:
        pattern: The regex pattern to search for.
        text: The text to search within.

    Returns:
        int: 1 if the pattern matches the text, 0 otherwise.
    """
    if text is None:
        return 0
    try:
        return 1 if re.search(pattern, text) else 0
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern {pattern!r}") from exc

def register_regexp_function(conn: Connection) -> None:
    """Registers the REGEXP function with the SQLite connection.

    Args:
        conn: The active database connection.

    Returns:
        None
    """
    conn.create_function("REGEXP", 2, regexp)

def table_exists(cursor: Cursor, table_name: str) -> bool:
    """Checks whether a given table exists in the database.

    Args:
        cursor: The active database cursor.
        table_name: The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1;",
        (table_name,),
    )
    return cursor.fetchone() is not None

def column_exists_in_table(cursor: Cursor, table_name: str, column_name: str) -> bool:
    """Checks whether a given column exists in the specified table.

    Args:
        cursor: The active database cursor.
        table_name: The name of the table to inspect.
        column_name: The name of the column to check.

    Returns:
        bool: True if the column exists in the table, False otherwise.
    """
    safe_table = sanitize_table_name(table_name)
    cursor.execute(f'PRAGMA table_info("{safe_table}")')
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def check_texts_table_schema(cursor: Cursor) -> bool:
    """Checks whether the 'texts' table has the expected columns in the correct order.

    Args:
        cursor: The active database cursor.

    Returns:
        bool: True if the 'texts' table contains exactly the expected columns
        in the correct order, False otherwise.
    """
    expected_columns = [
        "_texts_id",
        "pope_id",
        "section",
        "year",
        "date",
        "location",
        "title",
        "language",
        "url",
        "text_content",
        "entry_creation_date"
    ]

    actual_columns = get_column_names_in_table(cursor, "texts")
    return actual_columns == expected_columns

def fetch_rows_by_regexp(
    cursor: Cursor,
    query: str,
    pattern: str
) -> list:
    """
    Execute a SQL query using a regular-expression filter and return matching rows.

    Args:
        cursor:
            A database cursor object capable of executing SQL queries.
        query:
            A SQL query string that includes a placeholder for the regex
            pattern (typically in a `REGEXP ?` clause).
        pattern:
            A regular-expression pattern used to filter rows.

    Returns:
        A list of rows returned by the database driver.
    """
    cursor.execute(query, (pattern,))
    return cursor.fetchall()

def sanitize_table_name(table_name: str) -> str:
    """Sanitize a table name for safe use in SQL statements."""
    return table_name.replace('"', '""')

def speech_url_exists_in_db(db_path: Path, url: str) -> bool:
    """Checks whether a speech with the given URL exists in the database.

    This function queries the `speeches` table in the SQLite database located
    at `db_path` and determines whether at least one record exists with the
    specified URL.

    Args:
        db_path (Path): Path to the SQLite database file.
        url (str): The URL of the speech to look up.

    Returns:
        bool: True if a speech with the given URL exists in the database;
        False otherwise, including when an error occurs during the query.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM speeches WHERE url = ? LIMIT 1", (url,))
            return cur.fetchone() is not None
    except Exception:
        return False