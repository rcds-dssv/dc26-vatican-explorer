# Module to implement biblical citation search

######################################### IMPORT LIBRARIES #########################################
from re import finditer
from typing import Any

from dc26_vatican_explorer.database_utils.database_helpers import (
    check_texts_table_schema,
    connect_to_database,
    fetch_rows_by_regexp,
    register_regexp_function,
    table_exists,
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
) -> list[tuple[tuple[Any, ...], list[tuple[str, str]]]]:
    """Search database texts for biblical citations using a regex pattern.

    This function queries the `texts` table for rows whose `text_content`
    column matches a regular expression. For each matching row, it extracts
    biblical citations from the text content.

    Args:
        pattern (str | None):
            Regular expression used to search the `text_content` column.
            If None, the default biblical citation regex from
            `default_regex_pattern()` is used.

        query (str | None):
            Optional SQL query override. If not provided, the function uses
            a default query that searches `text_content` using a REGEXP clause.

            The query must:
            - Contain exactly one positional placeholder (?) for the regex.
            - Return all columns from the `texts` table in the same order
              defined in the schema.

    Returns:
        list[tuple[tuple, list[tuple[str, str]]]]:
            A list of tuples where each item contains:
            - The full database row (all columns from `texts`)
            - A list of extracted biblical citations as (citation, surrounding_text) tuples,
              where `citation` is the matched citation string and `surrounding_text` is the
              surrounding context from the source text.

    Raises:
        ValueError:
            If the `texts` table does not exist or its schema does not match
            the expected structure.

    """
    # Initialize database connection and cursor placeholders
    conn = None
    cursor = None

    try:
        # Connect to the SQLite database and obtain a cursor
        conn, cursor = connect_to_database()

        # Register a Python REGEXP function for SQLite compatibility
        register_regexp_function(conn)

        # Verify that the required table exists in the database
        if not table_exists(cursor, "texts"):
            raise ValueError("The 'texts' table does not exist in the database.")

        # Validate that the table schema matches the expected format
        if not check_texts_table_schema(cursor):
            raise ValueError(
                "The 'texts' table schema does not match the expected format."
            )

        # Define the default SQL query used to search the text content
        default_query = """SELECT * FROM texts WHERE text_content REGEXP ?"""

        # Use the user-supplied query if provided, otherwise use the default
        sql = query or default_query

        # If no regex pattern was provided, use the default citation pattern
        if pattern is None:
            pattern = default_regex_pattern()

        # Execute the SQL query and fetch rows whose text matches the regex
        rows = fetch_rows_by_regexp(cursor, sql, pattern)

        # Initialize a list to store the final results
        results = []

        # Iterate through each returned row from the database
        for row in rows:
            # Extract the text_content column (index 9 based on schema)
            text_content = row[9]

            # If the text content is not a string, no citations can be extracted
            if not isinstance(text_content, str):
                citations = []

            # Otherwise, search the text for biblical citations
            else:
                citations = search_biblical_citations(text_content, pattern=pattern)

            # Store the full row along with the extracted citations
            results.append((row, citations))

        # Return the list of rows and their extracted citations
        return results

    finally:
        # Ensure the database connection is safely closed
        if conn is not None and hasattr(conn, "close"):
            conn.close()
