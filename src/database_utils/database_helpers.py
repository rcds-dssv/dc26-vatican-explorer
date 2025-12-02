# Module with helper functions to work with the database

################################## IMPORT LIBRARIES ##################################

import sqlite3
from sqlite3 import Connection, Cursor

from src.config import _DB_PATH

from typing import Any

################################## DEFINE FUNCTIONS ##################################

def connect_to_database() -> tuple[Connection, Cursor]:
    """Connects to the SQLite database.

    Returns:
        tuple[Connection, Cursor]: A tuple containing the active database
        connection and a cursor with foreign key enforcement enabled.
    """
    conn: Connection = sqlite3.connect(_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor: Cursor = conn.cursor()
    return conn, cursor

def fetch_table_subset(
    table: str,
    columns: list[str] | None = None,
    filters: dict[str, Any] | None = None,
) -> list[tuple]:
    """Return a subset of rows from a table.

    Args:
        table: Name of the table to query.
        columns: Optional list of column names to return. If None, all
            columns are selected.
        filters: Optional mapping of {column_name: value} used to build the
            WHERE clause. All filters are combined with AND. If a value is
            None, an `IS NULL` condition is used instead of `=`.

    Returns:
        A list of rows (each row is a tuple).
    """
    conn, cursor = connect_to_database()

    try:
        # Columns to select
        if columns:
            col_clause = ", ".join(f'"{col}"' for col in columns)
        else:
            col_clause = "*"

        # Base query
        query = f'SELECT {col_clause} FROM "{table}"'

        # WHERE clause
        params: list[Any] = []
        if filters:
            conditions: list[str] = []
            for col, value in filters.items():
                if value is None:
                    conditions.append(f'"{col}" IS NULL')
                else:
                    conditions.append(f'"{col}" = ?')
                    params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows

    finally:
        conn.close()