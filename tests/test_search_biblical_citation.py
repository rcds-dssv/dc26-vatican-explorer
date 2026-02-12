# Module with tests for search_biblical_citation.py

import pytest

from src.search.search_biblical_citation import (
    search_biblical_citations,
    search_biblical_citations_db,
    default_regex_pattern,
)

import src.search.search_biblical_citation as search_module

# TODO: go through the Vatican's website to find more complex examples to test--e.g.: https://www.vatican.va/content/francesco/en/angelus/2025/documents/20250302-angelus.html

#########################################
# SINGLE-CITATION TESTS
#########################################


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "It was her interpretation of the supreme statement of the New Testament: “God is love” (1 Jn 4:8.16).",
            ["1 Jn 4:8.16"],
        ),
        (
            "There, from his open side, he gave birth to the Church, his beloved bride, for which he gave his life (cf. Eph 5:25).",
            ["Eph 5:25"],
        ),
        (
            "She felt herself a sister to atheists, seated with them at table, like Jesus who sat with sinners (cf. Mt 9:10-13).",
            ["Mt 9:10-13"],
        ),
        (
            "Therese was conscious of the tragic reality of sin, yet she remained constantly immersed in the mystery of Christ, certain that “where sin increased, grace abounded all the more” ( Rom 5:20).",
            ["Rom 5:20"],
        ),
        (
            "As “greater” than faith and hope, charity will never pass away (cf. 1 Cor 13:8-13). It is the supreme gift of the Holy Spirit and “the mother and the root of all the virtues”.",
            ["1 Cor 13:8-13"],
        ),
    ],
)
def test_single_citations(text, expected):
    """Test detection of individual biblical citations in single-citation examples."""
    result = search_biblical_citations(text)
    citations = [c[0] for c in result]
    assert citations == expected


#########################################
# MULTIPLE-CITATION TEST
#########################################


def test_multiple_citations():
    """Test detection of multiple biblical citations within a long passage."""
    text = """Charity in truth, to which Jesus Christ bore witness by his earthly life and especially by his death and resurrection, is the principal driving force behind the authentic development of every person and of all humanity. Love — caritas — is an extraordinary force which leads people to opt for courageous and generous engagement in the field of justice and peace. It is a force that has its origin in God, Eternal Love and Absolute Truth. Each person finds his good by adherence to God's plan for him, in order to realize it fully: in this plan, he finds his truth, and through adherence to this truth he becomes free (cf. Jn 8:32). To defend the truth, to articulate it with humility and conviction, and to bear witness to it in life are therefore exacting and indispensable forms of charity. Charity, in fact, “rejoices in the truth” (1 Cor 13:6). All people feel the interior impulse to love authentically: love and truth never abandon them completely, because these are the vocation planted by God in the heart and mind of every human person. The search for love and truth is purified and liberated by Jesus Christ from the impoverishment that our humanity brings to it, and he reveals to us in all its fullness the initiative of love and the plan for true life that God has prepared for us. In Christ, charity in truth becomes the Face of his Person, a vocation for us to love our brothers and sisters in the truth of his plan. Indeed, he himself is the Truth (cf. Jn 14:6)."""
    expected = ["Jn 8:32", "1 Cor 13:6", "Jn 14:6"]
    result = search_biblical_citations(text)
    citations = [c[0] for c in result]
    assert citations == expected


#########################################
# NO-CITATION TEST
#########################################


def test_no_citations():
    """Test that function returns empty list when no biblical citations are present."""
    text = "No citations here."
    expected = []
    result = search_biblical_citations(text)
    assert result == expected


#########################################
# TESTS WITH PATTERN AND CONTEXT
#########################################


def test_custom_pattern_and_context():
    """Test detection with a custom regex pattern and context length."""
    text = "This doesn't need to be a biblical citation 123."
    pattern = r"\d{3}"
    context = 5
    expected = [("123", "tion 123.")]
    result = search_biblical_citations(text, context=context, pattern=pattern)
    assert result == expected


#########################################
# DATABASE SEARCH TESTS
#########################################


def test_search_biblical_citations_db_missing_texts_table(monkeypatch):
    """search_biblical_citations_db should raise if the 'texts' table is missing."""

    def fake_connect_to_database():
        return "conn", "cursor"

    def fake_register_regexp_function(conn):
        # no-op
        return None

    def fake_table_exists(cursor, table_name):
        assert table_name == "texts"
        return False  # simulate missing table

    # Patch dependencies in the module under test
    monkeypatch.setattr(search_module, "connect_to_database", fake_connect_to_database)
    monkeypatch.setattr(
        search_module, "register_regexp_function", fake_register_regexp_function
    )
    monkeypatch.setattr(search_module, "table_exists", fake_table_exists)

    with pytest.raises(
        ValueError, match="The 'texts' table does not exist in the database."
    ):
        search_biblical_citations_db()


def test_search_biblical_citations_db_invalid_schema(monkeypatch):
    """search_biblical_citations_db should raise if the 'texts' table schema is invalid."""

    def fake_connect_to_database():
        return "conn", "cursor"

    def fake_register_regexp_function(conn):
        return None

    def fake_table_exists(cursor, table_name):
        return True  # table exists

    def fake_check_texts_table_schema(cursor):
        return False  # but schema is wrong

    monkeypatch.setattr(search_module, "connect_to_database", fake_connect_to_database)
    monkeypatch.setattr(
        search_module, "register_regexp_function", fake_register_regexp_function
    )
    monkeypatch.setattr(search_module, "table_exists", fake_table_exists)
    monkeypatch.setattr(
        search_module, "check_texts_table_schema", fake_check_texts_table_schema
    )

    with pytest.raises(
        ValueError, match="The 'texts' table schema does not match the expected format."
    ):
        search_biblical_citations_db()


def test_search_biblical_citations_db_default_query_and_pattern(monkeypatch):
    """
    search_biblical_citations_db should use the default SQL query and default
    regex pattern when none are provided, and extract citations from row[9].
    """
    captured = {}

    def fake_connect_to_database():
        return "conn", "cursor"

    def fake_register_regexp_function(conn):
        return None

    def fake_table_exists(cursor, table_name):
        return True

    def fake_check_texts_table_schema(cursor):
        return True

    def fake_fetch_rows_by_regexp(cursor, sql, pattern):
        captured["sql"] = sql
        captured["pattern"] = pattern
        # row[0] = id, row[9] = text_content
        row = (
            1,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "This passage cites Jn 3:16 and 1 Cor 13:6 together.",
        )
        return [row]

    monkeypatch.setattr(search_module, "connect_to_database", fake_connect_to_database)
    monkeypatch.setattr(
        search_module, "register_regexp_function", fake_register_regexp_function
    )
    monkeypatch.setattr(search_module, "table_exists", fake_table_exists)
    monkeypatch.setattr(
        search_module, "check_texts_table_schema", fake_check_texts_table_schema
    )
    monkeypatch.setattr(
        search_module, "fetch_rows_by_regexp", fake_fetch_rows_by_regexp
    )

    results = search_biblical_citations_db()

    # Ensure default pattern was used
    assert captured["pattern"] == default_regex_pattern()

    # Ensure default query (whitespace-insensitive check)
    expected_default_query = """SELECT * FROM texts WHERE text_content REGEXP ?
    """
    assert captured["sql"].strip() == expected_default_query.strip()

    # Ensure citations were extracted from text_content at index 9
    assert len(results) == 1
    row_id, citations = results[0]
    assert row_id == 1
    citation_strings = [c[0] for c in citations]
    assert citation_strings == ["Jn 3:16", "1 Cor 13:6"]


def test_search_biblical_citations_db_custom_query_and_pattern(monkeypatch):
    """
    search_biblical_citations_db should forward a custom query and pattern to
    fetch_rows_by_regexp when provided.
    """
    captured = {}

    def fake_connect_to_database():
        return "conn", "cursor"

    def fake_register_regexp_function(conn):
        return None

    def fake_table_exists(cursor, table_name):
        return True

    def fake_check_texts_table_schema(cursor):
        return True

    def fake_fetch_rows_by_regexp(cursor, sql, pattern):
        captured["sql"] = sql
        captured["pattern"] = pattern
        return []  # no rows needed for this test

    monkeypatch.setattr(search_module, "connect_to_database", fake_connect_to_database)
    monkeypatch.setattr(
        search_module, "register_regexp_function", fake_register_regexp_function
    )
    monkeypatch.setattr(search_module, "table_exists", fake_table_exists)
    monkeypatch.setattr(
        search_module, "check_texts_table_schema", fake_check_texts_table_schema
    )
    monkeypatch.setattr(
        search_module, "fetch_rows_by_regexp", fake_fetch_rows_by_regexp
    )

    custom_pattern = r"CUSTOM_PATTERN"
    custom_query = "SELECT id, text_content FROM texts WHERE text_content REGEXP ?"

    results = search_biblical_citations_db(
        pattern=custom_pattern,
        query=custom_query,
    )

    assert results == []
    assert captured["sql"] == custom_query
    assert captured["pattern"] == custom_pattern
