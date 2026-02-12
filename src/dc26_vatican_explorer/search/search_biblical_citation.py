# Module to implement biblical citation search

######################################### IMPORT LIBRARIES #########################################
from re import finditer

from src.database_utils.database_helpers import (
    connect_to_database,
    register_regexp_function,
    table_exists,
    check_texts_table_schema,
    fetch_rows_by_regexp,
)

######################################### DEFINE FUNCTIONS #########################################


def default_regex_pattern() -> str:
    """Function to return the default regex pattern for biblical citations.

    Args:
        None

    Returns:
        str: The default regex pattern for biblical citations.
    """
    return r"\b(?:[1-3]\s+)?[A-Za-z]{2,4}\s+\d{1,3}:\d{1,3}(?:[-.]\d{1,3})?\b"


def search_biblical_citations(
    text: str, context: int = 100, pattern: str | None = None
) -> list[tuple[str, str]]:
    """Function to search for biblical citations in a given text.

    Args:
        text: The input text to search for biblical citations.
        context: The number of characters to include before and after the citation for context.
        pattern: The regex pattern to use for searching. If None, a default pattern is used.

    Returns:
        list of tuples: Each tuple contains the found citation and its surrounding context.
    """
    # Check that the input text is a string
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")

    # Check that context is an integer
    if not isinstance(context, int):
        raise ValueError("Context must be an integer.")

    # Check that pattern is a string if provided
    if pattern is not None and not isinstance(pattern, str):
        raise ValueError("Pattern must be a string.")

    # Default regex pattern for biblical citations if none provided
    if pattern is None:
        pattern = default_regex_pattern()

    # Search for citations using regex
    matches = finditer(pattern, text)

    # Initialize results list
    results = []

    # Iterate over matches
    for match in matches:
        # Extract citation
        citation = match.group()

        # Get start and end indices of the match
        start, end = match.span()

        # Calculate context boundaries
        context_start = max(0, start - context)
        context_end = min(len(text), end + context)

        # Extract context
        surrounding_text = text[context_start:context_end]

        # Append citation and context to results
        results.append((citation, surrounding_text))

    # Return results
    return results


def search_biblical_citations_db(
    pattern: str | None = None, query: str | None = None
) -> list[tuple[int, list[tuple[str, str]]]]:
    """Search database texts for biblical citations matching a regex pattern.

    This function connects to the database, validates the schema, executes a
    regex-based SQL query, and extracts biblical citations from each row's
    text content.

    Args:
        pattern:
            Optional regex pattern used when searching within the `text_content`
            column. If not provided, the default biblical citation pattern is
            used via `default_regex_pattern()`.
        query:
            Optional SQL query override. If not provided, a default query is
            used that searches the `text_content` column with a REGEXP clause.
            The query must contain exactly one positional placeholder (?) for
            the regex pattern. The query must return all columns from the `texts`
            table in the same order as the schema.

    Returns:
        A list of tuples containing the row ID and the extracted citations.

    Raises:
        ValueError: If required tables, columns, or schema definitions are
            missing or incorrect.
    """
    conn = None
    cursor = None
    try:
        # Connect to the database
        conn, cursor = connect_to_database()

        # Register REGEXP function (SQLite compatibility)
        register_regexp_function(conn)

        # Validate table
        if not table_exists(cursor, "texts"):
            raise ValueError("The 'texts' table does not exist in the database.")

        # Validate schema format
        if not check_texts_table_schema(cursor):
            raise ValueError(
                "The 'texts' table schema does not match the expected format."
            )

        # Default SQL query
        default_query = """SELECT * FROM texts WHERE text_content REGEXP ?
        """

        # Use default query if none provided
        sql = query or default_query

        # Use default regex pattern if none provided
        if pattern is None:
            pattern = default_regex_pattern()

        # Fetch rows matching the regex pattern
        rows = fetch_rows_by_regexp(cursor, sql, pattern)

        results = []

        # Extract citations from each row's text content
        for row in rows:
            row_id = row[0]
            text_content = row[9]
            if not isinstance(text_content, str):
                citations = []
            else:
                citations = search_biblical_citations(text_content, pattern=pattern)
            results.append((row_id, citations))

        return results
    finally:
        if conn is not None and hasattr(conn, "close"):
            conn.close()
