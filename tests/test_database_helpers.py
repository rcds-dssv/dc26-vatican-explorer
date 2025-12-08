# Module with tests for database_helpers.py

import pytest

import sqlite3

import src.database_utils.database_helpers as db_module
from src.database_utils.database_helpers import (
    connect_to_database,
    get_tables_in_database,
    get_column_names_in_table,
    regexp,
    register_regexp_function,
    table_exists,
    column_exists_in_table,
    check_texts_table_schema,
    fetch_rows_by_regexp,
    sanitize_table_name
)

#########################################
# BASIC CONNECTION TEST
#########################################

def test_connect_to_database_returns_connection_and_cursor(tmp_path, monkeypatch):
    """Test that connect_to_database returns a valid SQLite connection and cursor."""
    test_db_path = tmp_path / "test.db"
    # Patch the module-level _DB_PATH that connect_to_database uses
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

#########################################
# get_tables_in_database
#########################################

def test_get_tables_in_database_returns_all_user_tables():
    """Test that get_tables_in_database returns the names of created tables."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY);")
        cursor.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY);")
        conn.commit()

        tables = get_tables_in_database(cursor)
        assert set(["users", "posts"]).issubset(set(tables))
    finally:
        conn.close()

def test_get_tables_in_database_on_empty_database_returns_empty_list():
    """Test that get_tables_in_database returns an empty list in a new database."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        tables = get_tables_in_database(cursor)
        assert tables == []
    finally:
        conn.close()

#########################################
# get_column_names_in_table
#########################################

def test_get_column_names_in_table_returns_all_columns_in_order():
    """Test that get_column_names_in_table returns column names in defined order."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT, age INTEGER);")
        conn.commit()

        columns = get_column_names_in_table(cursor, "test")
        assert columns == ["id", "name", "age"]
    finally:
        conn.close()

#########################################
# regexp
#########################################

def test_regexp_returns_1_when_pattern_matches_text():
    """Test that regexp returns 1 when the regex matches."""
    assert regexp(r"foo", "foobar") == 1

def test_regexp_returns_0_when_pattern_does_not_match_text():
    """Test that regexp returns 0 when the regex does not match."""
    assert regexp(r"foo", "bar") == 0

def test_regexp_returns_0_when_text_is_none():
    """Test that regexp safely handles None input."""
    assert regexp(r"foo", None) == 0

def test_regexp_raises_on_invalid_pattern():
    """Test that regexp raises a ValueError when given an invalid regex pattern."""
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        regexp(r"[", "foo")

#########################################
# register_regexp_function
#########################################

def test_register_regexp_function_makes_regexp_available_in_sql():
    """Test that register_regexp_function registers REGEXP as a usable SQL function."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        register_regexp_function(conn)

        match = cursor.execute("SELECT REGEXP(?, ?)", (r"foo", "foobar")).fetchone()[0]
        no_match = cursor.execute("SELECT REGEXP(?, ?)", (r"foo", "bar")).fetchone()[0]
        none_case = cursor.execute("SELECT REGEXP(?, ?)", (r"foo", None)).fetchone()[0]

        assert match == 1
        assert no_match == 0
        assert none_case == 0
    finally:
        conn.close()

#########################################
# table_exists
#########################################

def test_table_exists_identifies_existing_and_nonexisting_tables():
    """Test that table_exists correctly identifies whether a table exists."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE TABLE test_table (id INTEGER);")
        conn.commit()

        assert table_exists(cursor, "test_table") is True
        assert table_exists(cursor, "missing_table") is False
    finally:
        conn.close()

#########################################
# column_exists_in_table
#########################################

def test_column_exists_in_table_checks_correctly():
    """Test that column_exists_in_table detects existing and missing columns."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "CREATE TABLE users (id INTEGER, username TEXT, email TEXT);"
        )
        conn.commit()

        assert column_exists_in_table(cursor, "users", "id")
        assert column_exists_in_table(cursor, "users", "username")
        assert column_exists_in_table(cursor, "users", "email")
        assert not column_exists_in_table(cursor, "users", "age")
    finally:
        conn.close()

def test_column_exists_in_table_returns_false_when_table_does_not_exist():
    """Test that column_exists_in_table returns False if the table does not exist."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        assert not column_exists_in_table(cursor, "no_table", "col")
    finally:
        conn.close()

#########################################
# check_texts_table_schema
#########################################

EXPECTED_COLUMNS = [
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
    "entry_creation_date",
]

def create_texts_table(cursor, columns):
    """Create the 'texts' table with the specified column names (all TEXT type)."""
    col_defs = ", ".join(f"{col} TEXT" for col in columns)
    cursor.execute(f"CREATE TABLE texts ({col_defs});")

def test_check_texts_table_schema_returns_true_for_correct_schema():
    """
    Test that check_texts_table_schema returns True when the 'texts' table
    contains exactly the expected columns in the correct order.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        create_texts_table(cursor, EXPECTED_COLUMNS)
        conn.commit()

        assert check_texts_table_schema(cursor) is True
    finally:
        conn.close()

def test_check_texts_table_schema_returns_false_when_columns_out_of_order():
    """
    Test that check_texts_table_schema returns False when the columns exist
    but are not in the expected order.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        wrong_order = EXPECTED_COLUMNS.copy()
        wrong_order[0], wrong_order[1] = wrong_order[1], wrong_order[0]  # swap first two

        create_texts_table(cursor, wrong_order)
        conn.commit()

        assert check_texts_table_schema(cursor) is False
    finally:
        conn.close()

def test_check_texts_table_schema_returns_false_when_column_missing():
    """
    Test that check_texts_table_schema returns False when one or more expected
    columns are missing from the 'texts' table.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        missing_column = EXPECTED_COLUMNS[:-1]  # remove last expected column

        create_texts_table(cursor, missing_column)
        conn.commit()

        assert check_texts_table_schema(cursor) is False
    finally:
        conn.close()

def test_check_texts_table_schema_returns_false_when_extra_column_present():
    """
    Test that check_texts_table_schema returns False when the table contains
    all expected columns but also includes additional unwanted columns.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        extra_cols = EXPECTED_COLUMNS + ["extra_column"]

        create_texts_table(cursor, extra_cols)
        conn.commit()

        assert check_texts_table_schema(cursor) is False
    finally:
        conn.close()

def test_check_texts_table_schema_returns_false_when_table_missing():
    """
    Test that check_texts_table_schema returns False when the 'texts' table
    does not exist in the database.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        # No table created
        assert check_texts_table_schema(cursor) is False
    finally:
        conn.close()

#########################################
# fetch_rows_by_regexp
#########################################

def test_fetch_rows_by_regexp_returns_matching_rows():
    """
    Test that fetch_rows_by_regexp returns rows whose column values match
    the given regular-expression pattern.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        # Enable REGEXP in this connection
        register_regexp_function(conn)

        # Create a sample table and insert test data
        cursor.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);")
        cursor.executemany(
            "INSERT INTO items (name) VALUES (?);",
            [
                ("foo",),
                ("bar",),
                ("foobar",),
                ("baz",),
            ],
        )
        conn.commit()

        query = "SELECT name FROM items WHERE name REGEXP ? ORDER BY name;"
        pattern = r"foo"

        rows = fetch_rows_by_regexp(cursor, query, pattern)

        # Expect only names containing "foo"
        assert rows == [("foo",), ("foobar",)]
    finally:
        conn.close()

def test_fetch_rows_by_regexp_returns_empty_list_when_no_rows_match():
    """
    Test that fetch_rows_by_regexp returns an empty list when no rows
    match the provided regular-expression pattern.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        register_regexp_function(conn)

        cursor.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);")
        cursor.executemany(
            "INSERT INTO items (name) VALUES (?);",
            [
                ("alpha",),
                ("beta",),
                ("gamma",),
            ],
        )
        conn.commit()

        query = "SELECT name FROM items WHERE name REGEXP ?;"
        pattern = r"foo"  # no row contains "foo"

        rows = fetch_rows_by_regexp(cursor, query, pattern)

        assert rows == []
    finally:
        conn.close()

def test_fetch_rows_by_regexp_handles_multiple_column_selection():
    """
    Test that fetch_rows_by_regexp correctly returns full rows when the query
    selects multiple columns, not just one.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        register_regexp_function(conn)

        cursor.execute(
            "CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, city TEXT);"
        )
        cursor.executemany(
            "INSERT INTO people (name, city) VALUES (?, ?);",
            [
                ("Alice", "Rome"),
                ("Bob", "London"),
                ("Alicia", "Paris"),
            ],
        )
        conn.commit()

        query = "SELECT id, name, city FROM people WHERE name REGEXP ? ORDER BY id;"
        pattern = r"Ali"  # matches "Alice" and "Alicia"

        rows = fetch_rows_by_regexp(cursor, query, pattern)

        # Expect both rows with names starting with "Ali"
        assert rows == [
            (1, "Alice", "Rome"),
            (3, "Alicia", "Paris"),
        ]
    finally:
        conn.close()

#########################################
# sanitize_table_name
#########################################

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("users", "users"),                         # no quotes
        ('user"s', 'user""s'),                     # single quote
        ('"users"', '""users""'),                 # quotes at both ends
        ('user"name"with"quotes', 'user""name""with""quotes'),  # multiple quotes
        ("", ""),                                  # empty string
    ],
)
def test_sanitize_table_name_replaces_double_quotes(raw: str, expected: str) -> None:
    """
    Verify that `sanitize_table_name` safely escapes double-quote characters.

    SQLite requires double quotes inside identifiers to be escaped by doubling
    them. These tests ensure:

    - Unquoted table names remain unchanged.
    - Any occurrence of `"` is correctly replaced with `""`.
    - Edge cases such as empty strings or multiple embedded quotes behave as expected.
    """
    assert sanitize_table_name(raw) == expected