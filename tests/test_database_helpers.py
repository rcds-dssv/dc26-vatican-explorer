# Module with tests for database_helpers.py

import sqlite3

import src.database_utils.database_helpers as db_module
from src.database_utils.database_helpers import connect_to_database

#########################################
# BASIC CONNECTION TEST
#########################################

def test_connect_to_database_returns_connection_and_cursor(tmp_path, monkeypatch):
    """Test that connect_to_database returns a valid SQLite connection and cursor."""
    test_db_path = tmp_path / "test.db"
    monkeypatch.setattr(db_module, "_DB_PATH", str(test_db_path))

    conn, cursor = connect_to_database()

    try:
        # Types are correct
        assert isinstance(conn, sqlite3.Connection)
        assert isinstance(cursor, sqlite3.Cursor)

        # Database file is created
        assert test_db_path.exists()

        # Foreign key enforcement is actually enabled
        fk_status = cursor.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_status == 1, "Foreign key enforcement should be enabled."
    finally:
        conn.close()
