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
