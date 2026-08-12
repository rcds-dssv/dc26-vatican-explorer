"""Checks for the citation-resolution logic behind the Findings figures.

The plots themselves are not asserted on; the part that can silently go wrong
is mapping a citation token like ``1 Cor`` back to a book of the Bible.
"""

import re

from dc26_vatican_explorer.plotting_tools.story_plots import (
    BOOK_CITATION_PATTERN,
    load_bible_books,
)
from dc26_vatican_explorer.search.search_biblical_citation import search_biblical_citations


def _resolve(text: str) -> list[str]:
    """Run the Findings pipeline over a snippet and return the books matched."""
    abbrev_to_book, _groups = load_bible_books()
    token = re.compile(BOOK_CITATION_PATTERN)

    books = []
    for citation, _context in search_biblical_citations(text, context=0, pattern=BOOK_CITATION_PATTERN):
        match = token.match(citation)
        key = re.sub(r"\s+", " ", match.group(1).lower()).rstrip(".")
        if key in abbrev_to_book:
            books.append(abbrev_to_book[key])
    return books


def test_bible_books_csv_loads_with_aliases():
    abbrev_to_book, book_to_group = load_bible_books()

    assert book_to_group["John"] == ("Gospel", "new")
    assert book_to_group["Genesis"] == ("Pentateuch", "old")
    # Full names, short forms and the numbered books all resolve.
    assert abbrev_to_book["jn"] == "John"
    assert abbrev_to_book["john"] == "John"
    assert abbrev_to_book["1 cor"] == "1 Corinthians"
    # Regression: the CSV shipped "Pslams" as the book name.
    assert abbrev_to_book["ps"] == "Psalms"


def test_pattern_resolves_both_abbreviated_and_spelled_out_citations():
    """The shipped default pattern caps tokens at 4 letters and loses these."""
    found = _resolve(
        "As Jn 3:16 says, and Matthew 5:9, and 1 Cor 13:6, and Genesis 1:1, and Rm 8:28."
    )

    assert found == ["John", "Matthew", "1 Corinthians", "Genesis", "Romans"]


def test_plain_prose_yields_no_citations():
    assert _resolve("The Holy Father greeted the pilgrims at 10:30 in the square.") == []
