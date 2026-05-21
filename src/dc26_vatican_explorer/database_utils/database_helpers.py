# Module with helper functions to work with the database

################################## IMPORT LIBRARIES ##################################

import argparse
import re
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor

from dc26_vatican_explorer.config import _DB_PATH

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
    """Execute a SQL query using a regular-expression filter and return matching rows.

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

def speech_url_exists_in_db(db_path: Path, url: str, require_content: bool = False) -> bool:
    """Checks whether a speech with the given URL exists in the database.

    This function queries the `texts` table in the SQLite database located
    at `db_path` and determines whether at least one record exists with the
    specified URL.

    Args:
        db_path (Path): Path to the SQLite database file.
        url (str): The URL of the speech to look up.
        require_content (bool): If True, only return True when the row exists
            AND has non-empty text_content. Defaults to False.

    Returns:
        bool: True if a matching speech record is found; False otherwise,
        including when an error occurs during the query.

    """
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            if require_content:
                cur.execute(
                    "SELECT 1 FROM texts WHERE url = ? "
                    "AND text_content IS NOT NULL AND TRIM(text_content) != '' LIMIT 1",
                    (url,)
                )
            else:
                cur.execute("SELECT 1 FROM texts WHERE url = ? LIMIT 1", (url,))
            return cur.fetchone() is not None
    except Exception:
        return False


def get_speech_text_by_url(db_path: Path, url: str) -> str | None:
    """Return the stored text_content for a given URL, or None if not found."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT text_content FROM texts WHERE url = ? LIMIT 1", (url,))
            row = cur.fetchone()
            return row[0] if row is not None else None
    except Exception:
        return None


def query_texts(
    db_path: Path = _DB_PATH,
    pope_name: str | None = None,
    section: str | None = None,
    years: str | None = None,
    language: str | None = None,
) -> list[dict]:
    """Query the texts table by any combination of pope name, section, year range, and language.

    Args:
        db_path: Path to the SQLite database file.
        pope_name: Pope display name, e.g. ``"John Paul II"``.
        section: Content section, e.g. ``"homilies"``.
        years: Year or year range string, e.g. ``"1977"``, ``"1977-1978"``,
            or ``"1977,1979-1981"``.
        language: Two-letter language code, e.g. ``"EN"``.

    Returns:
        A list of dicts, one per matching row, with keys matching the
        ``texts`` table columns joined with ``pope_name`` from ``popes``.

    Example::

        rows = query_texts(_DB_PATH, pope_name="John Paul II",
                           section="homilies", years="1977-1978", language="EN")
        for r in rows:
            print(r["date"], r["title"], r["url"])

    """
    # Parse years spec into a flat list of year strings
    year_list: list[str] = []
    if years:
        for part in (p.strip() for p in years.split(",")):
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                if a.isdigit() and b.isdigit():
                    year_list.extend(str(y) for y in range(int(a), int(b) + 1))
            elif part.isdigit():
                year_list.append(part)

    conditions: list[str] = []
    params: list = []

    if pope_name:
        conditions.append("p.pope_name = ?")
        params.append(pope_name)
    if section:
        conditions.append("t.section = ?")
        params.append(section)
    if year_list:
        placeholders = ",".join("?" * len(year_list))
        conditions.append(f"t.year IN ({placeholders})")
        params.extend(year_list)
    if language:
        conditions.append("t.language = ?")
        params.append(language)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"""
        SELECT t._texts_id, p.pope_name, t.section, t.year, t.date,
               t.location, t.title, t.language, t.url, t.text_content,
               t.entry_creation_date
        FROM texts t
        JOIN popes p ON t.pope_id = p._pope_id
        {where}
        ORDER BY t.year, t.date
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


# Columns that can be checked for missing values, mapped to their table.
_TEXTS_FIELDS = {"text_content", "date", "location", "title", "language"}
_POPES_FIELDS = {"place_of_birth", "secular_name", "pontificate_begin", "pontificate_end"}
_ALL_CHECKABLE_FIELDS = _TEXTS_FIELDS | _POPES_FIELDS


def query_missing_fields(
    db_path: Path = _DB_PATH,
    fields: list[str] | None = None,
    pope_name: str | None = None,
    section: str | None = None,
    years: str | None = None,
    language: str | None = None,
) -> dict[str, list[dict]]:
    """Return rows that have NULL or empty values for the requested fields.

    Args:
        db_path: Path to the SQLite database file.
        fields: List of column names to check. Defaults to
            ``["text_content", "date", "location", "place_of_birth"]``.
            Valid values: ``text_content``, ``date``, ``location``, ``title``,
            ``language`` (from ``texts``), and ``place_of_birth``,
            ``secular_name``, ``pontificate_begin``, ``pontificate_end``
            (from ``popes``).
        pope_name: Optional filter by pope display name.
        section: Optional filter by section.
        years: Optional year or range string, e.g. ``"1977-1978"``.
        language: Optional two-letter language code.

    Returns:
        A dict mapping each requested field name to a list of row dicts that
        are missing that field.  Rows from ``popes`` checks include only pope
        columns; rows from ``texts`` checks include all columns plus
        ``pope_name``.

    Example::

        missing = query_missing_fields(fields=["text_content", "date", "place_of_birth"])
        for field, rows in missing.items():
            print(f"{field}: {len(rows)} records missing")

    """
    if fields is None:
        fields = ["text_content", "date", "location", "place_of_birth"]

    unknown = [f for f in fields if f not in _ALL_CHECKABLE_FIELDS]
    if unknown:
        raise ValueError(f"Unknown field(s): {unknown}. Valid: {sorted(_ALL_CHECKABLE_FIELDS)}")

    # Parse years into a list of year strings
    year_list: list[str] = []
    if years:
        for part in (p.strip() for p in years.split(",")):
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                if a.isdigit() and b.isdigit():
                    year_list.extend(str(y) for y in range(int(a), int(b) + 1))
            elif part.isdigit():
                year_list.append(part)

    results: dict[str, list[dict]] = {}

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        for field in fields:
            if field in _TEXTS_FIELDS:
                conds = [f"(t.{field} IS NULL OR TRIM(t.{field}) = '')"]
                params: list = []
                if pope_name:
                    conds.append("p.pope_name = ?")
                    params.append(pope_name)
                if section:
                    conds.append("t.section = ?")
                    params.append(section)
                if year_list:
                    conds.append(f"t.year IN ({','.join('?' * len(year_list))})")
                    params.extend(year_list)
                if language:
                    conds.append("t.language = ?")
                    params.append(language)
                sql = (
                    "SELECT t._texts_id, p.pope_name, t.section, t.year, t.date, "
                    "t.location, t.title, t.language, t.url, t.text_content, "
                    "t.entry_creation_date "
                    "FROM texts t JOIN popes p ON t.pope_id = p._pope_id "
                    f"WHERE {' AND '.join(conds)} ORDER BY t.year, t.date"
                )
                cur.execute(sql, params)
            else:  # popes field
                conds = [f"(p.{field} IS NULL OR TRIM(p.{field}) = '')"]
                params = []
                if pope_name:
                    conds.append("p.pope_name = ?")
                    params.append(pope_name)
                sql = (
                    "SELECT p._pope_id, p.pope_name, p.pope_slug, p.pope_number, "
                    "p.secular_name, p.place_of_birth, p.pontificate_begin, "
                    "p.pontificate_end, p.entry_creation_date "
                    "FROM popes p "
                    f"WHERE {' AND '.join(conds)} ORDER BY p.pope_name"
                )
                cur.execute(sql, params)

            results[field] = [dict(r) for r in cur.fetchall()]

    return results



    p = argparse.ArgumentParser(description="Query speech texts from the Vatican database.")
    p.add_argument("--pope", default=None, help='Pope display name, e.g. "John Paul II"')
    p.add_argument("--section", default=None, help='Section, e.g. "homilies"')
    p.add_argument("--years", default=None, help='Year or range, e.g. "1977-1978"')
    p.add_argument("--lang", default=None, help='Two-letter language code, e.g. "EN"')
    p.add_argument("--field", default="text_content", help='Row field to print (default: text_content)')
    p.add_argument("--first", action="store_true", help="Print only the first result")
    args = p.parse_args()

    rows = query_texts(pope_name=args.pope, section=args.section, years=args.years, language=args.lang)
    if not rows:
        print("No results found.")
        return
    target = rows[:1] if args.first else rows
    for row in target:
        print(row.get(args.field, f"(field '{args.field}' not found)"))


if __name__ == "__main__":
    main()
