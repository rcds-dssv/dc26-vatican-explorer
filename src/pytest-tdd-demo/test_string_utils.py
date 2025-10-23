"""Tests for string utilities with Google-style docstrings."""
import pytest
from string_utils import (
    reverse_string,
    count_vowels,
    is_palindrome,
    truncate_string,
    word_frequency,
    StringProcessor,
)


class TestReverseString:
    """Test suite for reverse_string function."""

    def test_reverse_simple_string(self):
        """Test reversing a simple string."""
        assert reverse_string("hello") == "olleh"

    def test_reverse_empty_string(self):
        """Test reversing an empty string."""
        assert reverse_string("") == ""

    def test_reverse_single_character(self):
        """Test reversing a single character."""
        assert reverse_string("a") == "a"


class TestCountVowels:
    """Test suite for count_vowels function."""

    def test_count_vowels_lowercase(self):
        """Test counting vowels in lowercase text."""
        assert count_vowels("hello") == 2

    def test_count_vowels_uppercase(self):
        """Test counting vowels in uppercase text."""
        assert count_vowels("AEIOU") == 5

    def test_count_vowels_no_vowels(self):
        """Test text with no vowels."""
        assert count_vowels("xyz") == 0

    def test_count_vowels_empty_string(self):
        """Test empty string."""
        assert count_vowels("") == 0


class TestIsPalindrome:
    """Test suite for is_palindrome function."""

    def test_simple_palindrome(self):
        """Test a simple palindrome."""
        assert is_palindrome("racecar") is True

    def test_not_palindrome(self):
        """Test a non-palindrome."""
        assert is_palindrome("hello") is False

    def test_palindrome_with_spaces(self):
        """Test palindrome with spaces."""
        assert is_palindrome("A man a plan a canal Panama") is True

    def test_empty_string_is_palindrome(self):
        """Test that empty string is a palindrome."""
        assert is_palindrome("") is True


class TestTruncateString:
    """Test suite for truncate_string function."""

    def test_truncate_long_string(self):
        """Test truncating a string longer than max_length."""
        assert truncate_string("Hello World", 5) == "Hello..."

    def test_truncate_short_string(self):
        """Test that short strings are not truncated."""
        assert truncate_string("Hi", 10) == "Hi"

    def test_truncate_custom_suffix(self):
        """Test truncation with custom suffix."""
        assert truncate_string("Hello World", 5, suffix=" [more]") == "Hello [more]"

    def test_truncate_negative_length_raises_error(self):
        """Test that negative max_length raises ValueError."""
        with pytest.raises(ValueError, match="max_length must be positive"):
            truncate_string("Hello", -1)

    def test_truncate_non_string_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="text must be a string"):
            truncate_string(123, 5)


class TestWordFrequency:
    """Test suite for word_frequency function."""

    def test_word_frequency_simple(self):
        """Test word frequency with simple text."""
        result = word_frequency("hello world hello")
        assert result == {"hello": 2, "world": 1}

    def test_word_frequency_case_insensitive(self):
        """Test that word frequency is case-insensitive."""
        result = word_frequency("The cat and the dog")
        assert result["the"] == 2

    def test_word_frequency_empty_string(self):
        """Test word frequency with empty string."""
        result = word_frequency("")
        assert result == {}


class TestStringProcessor:
    """Test suite for StringProcessor class."""

    def test_processor_initialization(self):
        """Test creating a StringProcessor instance."""
        processor = StringProcessor("Hello")
        assert processor.text == "Hello"
        assert processor.operations_count == 0

    def test_processor_initialization_with_non_string(self):
        """Test that initialization with non-string raises TypeError."""
        with pytest.raises(TypeError, match="text must be a string"):
            StringProcessor(123)

    def test_to_uppercase(self):
        """Test converting text to uppercase."""
        processor = StringProcessor("hello")
        result = processor.to_uppercase()
        assert result == "HELLO"
        assert processor.operations_count == 1

    def test_to_lowercase(self):
        """Test converting text to lowercase."""
        processor = StringProcessor("HELLO")
        result = processor.to_lowercase()
        assert result == "hello"
        assert processor.operations_count == 1

    def test_replace_substring(self):
        """Test replacing a substring."""
        processor = StringProcessor("hello world")
        result = processor.replace_substring("world", "universe")
        assert result == "hello universe"
        assert processor.operations_count == 1

    def test_replace_empty_substring_raises_error(self):
        """Test that replacing empty substring raises ValueError."""
        processor = StringProcessor("hello")
        with pytest.raises(ValueError, match="old substring cannot be empty"):
            processor.replace_substring("", "x")

    def test_get_statistics(self):
        """Test getting text statistics."""
        processor = StringProcessor("Hello World")
        stats = processor.get_statistics()
        assert stats["length"] == 11
        assert stats["words"] == 2
        assert stats["vowels"] == 3
        assert stats["operations"] == 0

    def test_operations_count_increments(self):
        """Test that operations count increments correctly."""
        processor = StringProcessor("test")
        processor.to_uppercase()
        processor.to_lowercase()
        processor.replace_substring("t", "T")
        assert processor.operations_count == 3


@pytest.mark.parametrize("text,expected", [
    ("hello", "olleh"),
    ("Python", "nohtyP"),
    ("12345", "54321"),
    ("", ""),
])
def test_reverse_string_parameterized(text, expected):
    """Test reverse_string with multiple inputs using parameterization."""
    assert reverse_string(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("hello", 2),
    ("AEIOU", 5),
    ("xyz", 0),
    ("Beautiful", 5),
])
def test_count_vowels_parameterized(text, expected):
    """Test count_vowels with multiple inputs using parameterization."""
    assert count_vowels(text) == expected
