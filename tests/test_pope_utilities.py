"""
Unit tests for pope name and URL utility functions.

This module tests the utility functions from vatican_scraper.step01_list_popes
that handle pope name normalization, validation, and URL parsing.
"""

import pytest
from vatican_scraper.step01_list_popes import (
    papal_normalize_display_name,
    papal_extract_slug_from_content_url,
    papal_find_by_display_name,
)


class TestPapalNormalizeDisplayName:
    """Tests for papal_normalize_display_name function."""

    def test_normalize_simple_name(self):
        """Should preserve single-word names without extra whitespace."""
        assert papal_normalize_display_name("Francis") == "Francis"

    def test_normalize_removes_leading_whitespace(self):
        """Should remove leading whitespace."""
        assert papal_normalize_display_name("  Francis") == "Francis"

    def test_normalize_removes_trailing_whitespace(self):
        """Should remove trailing whitespace."""
        assert papal_normalize_display_name("Francis  ") == "Francis"

    def test_normalize_collapses_multiple_spaces(self):
        """Should collapse multiple spaces into a single space."""
        assert papal_normalize_display_name("John    Paul    II") == "John Paul II"

    def test_normalize_handles_mixed_whitespace(self):
        """Should collapse tabs and newlines into single spaces."""
        assert papal_normalize_display_name("John\t\nPaul  II") == "John Paul II"

    def test_normalize_empty_string(self):
        """Should handle empty strings."""
        assert papal_normalize_display_name("") == ""

    def test_normalize_whitespace_only(self):
        """Should return empty string for whitespace-only input."""
        assert papal_normalize_display_name("   \t\n  ") == ""


class TestPapalExtractSlugFromContentUrl:
    """Tests for papal_extract_slug_from_content_url function."""

    def test_extract_slug_francesco(self):
        """Should extract slug from Francesco's URL."""
        url = "https://www.vatican.va/content/francesco/en.html"
        assert papal_extract_slug_from_content_url(url) == "francesco"

    def test_extract_slug_with_hyphens(self):
        """Should extract slug with hyphens (e.g., john-paul-i)."""
        url = "https://www.vatican.va/content/john-paul-i/en.htm"
        assert papal_extract_slug_from_content_url(url) == "john-paul-i"

    def test_extract_slug_benedict(self):
        """Should extract slug for Benedict XVI."""
        url = "https://www.vatican.va/content/benedict-xvi/en.html"
        assert papal_extract_slug_from_content_url(url) == "benedict-xvi"

    def test_extract_slug_john_paul_ii(self):
        """Should extract slug for John Paul II."""
        url = "https://www.vatican.va/content/john-paul-ii/en.html"
        assert papal_extract_slug_from_content_url(url) == "john-paul-ii"

    def test_extract_slug_invalid_url_no_content(self):
        """Should return None for URLs without /content/ path."""
        url = "https://www.vatican.va/holy_father/index.htm"
        assert papal_extract_slug_from_content_url(url) is None

    def test_extract_slug_invalid_url_too_short(self):
        """Should return None for URLs with insufficient path segments."""
        url = "https://www.vatican.va/content/"
        assert papal_extract_slug_from_content_url(url) is None

    def test_extract_slug_empty_string(self):
        """Should return None for empty string."""
        assert papal_extract_slug_from_content_url("") is None

    def test_extract_slug_malformed_url(self):
        """Should return None for malformed URLs."""
        assert papal_extract_slug_from_content_url("not a url") is None


class TestPapalFindByDisplayName:
    """Tests for papal_find_by_display_name function."""

    @pytest.fixture
    def sample_popes(self):
        """Fixture providing a sample list of pope dictionaries."""
        return [
            {
                "display_name": "Francis",
                "slug": "francesco",
                "url": "https://www.vatican.va/content/francesco/en.html",
            },
            {
                "display_name": "Benedict XVI",
                "slug": "benedict-xvi",
                "url": "https://www.vatican.va/content/benedict-xvi/en.html",
            },
            {
                "display_name": "John Paul II",
                "slug": "john-paul-ii",
                "url": "https://www.vatican.va/content/john-paul-ii/en.html",
            },
            {
                "display_name": "Paul VI",
                "slug": "paul-vi",
                "url": "https://www.vatican.va/content/paul-vi/en.html",
            },
        ]

    def test_find_exact_match(self, sample_popes):
        """Should find pope with exact name match."""
        result = papal_find_by_display_name(sample_popes, "Francis")
        assert result is not None
        assert result["display_name"] == "Francis"
        assert result["slug"] == "francesco"

    def test_find_case_insensitive(self, sample_popes):
        """Should find pope with case-insensitive matching."""
        result = papal_find_by_display_name(sample_popes, "francis")
        assert result is not None
        assert result["display_name"] == "Francis"

    def test_find_uppercase_input(self, sample_popes):
        """Should find pope when input is all uppercase."""
        result = papal_find_by_display_name(sample_popes, "FRANCIS")
        assert result is not None
        assert result["display_name"] == "Francis"

    def test_find_multi_word_name(self, sample_popes):
        """Should find popes with multi-word names."""
        result = papal_find_by_display_name(sample_popes, "John Paul II")
        assert result is not None
        assert result["display_name"] == "John Paul II"
        assert result["slug"] == "john-paul-ii"

    def test_find_with_extra_whitespace(self, sample_popes):
        """Should find pope even with extra whitespace in search."""
        result = papal_find_by_display_name(sample_popes, "  Francis  ")
        assert result is not None
        assert result["display_name"] == "Francis"

    def test_find_not_found(self, sample_popes):
        """Should return None when pope is not in the list."""
        result = papal_find_by_display_name(sample_popes, "Leo XIII")
        assert result is None

    def test_find_empty_list(self):
        """Should return None when searching empty list."""
        result = papal_find_by_display_name([], "Francis")
        assert result is None

    def test_find_empty_string(self, sample_popes):
        """Should return None when searching for empty string."""
        result = papal_find_by_display_name(sample_popes, "")
        assert result is None

    def test_find_returns_first_match(self):
        """Should return first match if there are duplicates."""
        duplicate_popes = [
            {"display_name": "Francis", "slug": "francesco-1", "url": "url1"},
            {"display_name": "Francis", "slug": "francesco-2", "url": "url2"},
        ]
        result = papal_find_by_display_name(duplicate_popes, "Francis")
        assert result is not None
        assert result["slug"] == "francesco-1"
