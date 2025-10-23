"""
String utility functions demonstrating Google-style docstrings.

This module provides common string manipulation functions with comprehensive
documentation following Google's Python Style Guide.

Example:
    Basic usage of string utilities::

        >>> from string_utils import reverse_string, count_vowels
        >>> reverse_string("hello")
        'olleh'
        >>> count_vowels("beautiful")
        5

Attributes:
    VOWELS (str): String containing all vowels (lowercase and uppercase).
"""

VOWELS = "aeiouAEIOU"


def reverse_string(text):
    """Reverse a string.

    Args:
        text (str): The string to reverse.

    Returns:
        str: The reversed string.

    Example:
        >>> reverse_string("hello")
        'olleh'
        >>> reverse_string("Python")
        'nohtyP'
    """
    return text[::-1]


def count_vowels(text):
    """Count the number of vowels in a string.

    This function counts both lowercase and uppercase vowels (a, e, i, o, u).

    Args:
        text (str): The string to analyze.

    Returns:
        int: The number of vowels found in the string.

    Example:
        >>> count_vowels("hello")
        2
        >>> count_vowels("AEIOU")
        5
        >>> count_vowels("xyz")
        0
    """
    return sum(1 for char in text if char in VOWELS)


def is_palindrome(text):
    """Check if a string is a palindrome.

    A palindrome reads the same forwards and backwards, ignoring spaces
    and case.

    Args:
        text (str): The string to check.

    Returns:
        bool: True if the string is a palindrome, False otherwise.

    Example:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("A man a plan a canal Panama")
        True
        >>> is_palindrome("hello")
        False
    """
    cleaned = text.replace(" ", "").lower()
    return cleaned == cleaned[::-1]


def truncate_string(text, max_length, suffix="..."):
    """Truncate a string to a maximum length.

    If the string is longer than max_length, it will be truncated and
    a suffix will be added.

    Args:
        text (str): The string to truncate.
        max_length (int): Maximum length before truncation.
        suffix (str, optional): Suffix to add when truncated. Defaults to "...".

    Returns:
        str: The truncated string with suffix, or original if shorter than max_length.

    Raises:
        ValueError: If max_length is negative.
        TypeError: If text is not a string.

    Example:
        >>> truncate_string("Hello World", 5)
        'Hello...'
        >>> truncate_string("Hi", 10)
        'Hi'
        >>> truncate_string("Long text here", 8, suffix=" [more]")
        'Long tex [more]'
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if max_length < 0:
        raise ValueError("max_length must be positive")

    if len(text) <= max_length:
        return text

    return text[:max_length] + suffix


def word_frequency(text):
    """Calculate word frequency in a text.

    This function counts how many times each word appears in the given text.
    Words are case-insensitive and punctuation is ignored.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary where keys are words (lowercase) and values are
            their frequency counts.

    Example:
        >>> word_frequency("Hello world hello")
        {'hello': 2, 'world': 1}
        >>> word_frequency("The cat and the dog")
        {'the': 2, 'cat': 1, 'and': 1, 'dog': 1}
    """
    import re
    # Remove punctuation and convert to lowercase
    words = re.findall(r'\b\w+\b', text.lower())
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    return frequency


class StringProcessor:
    """A class for processing strings with various operations.

    This class provides methods for string manipulation and analysis,
    maintaining state about the operations performed.

    Attributes:
        text (str): The current text being processed.
        operations_count (int): Number of operations performed.

    Example:
        >>> processor = StringProcessor("Hello World")
        >>> processor.to_uppercase()
        'HELLO WORLD'
        >>> processor.operations_count
        1
    """

    def __init__(self, text):
        """Initialize the StringProcessor.

        Args:
            text (str): The initial text to process.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        self.text = text
        self.operations_count = 0

    def to_uppercase(self):
        """Convert text to uppercase.

        Returns:
            str: The text in uppercase.

        Example:
            >>> processor = StringProcessor("hello")
            >>> processor.to_uppercase()
            'HELLO'
        """
        self.operations_count += 1
        return self.text.upper()

    def to_lowercase(self):
        """Convert text to lowercase.

        Returns:
            str: The text in lowercase.

        Example:
            >>> processor = StringProcessor("HELLO")
            >>> processor.to_lowercase()
            'hello'
        """
        self.operations_count += 1
        return self.text.lower()

    def replace_substring(self, old, new):
        """Replace all occurrences of a substring.

        Args:
            old (str): The substring to replace.
            new (str): The replacement substring.

        Returns:
            str: The text with replacements made.

        Raises:
            ValueError: If old is an empty string.

        Example:
            >>> processor = StringProcessor("hello world")
            >>> processor.replace_substring("world", "universe")
            'hello universe'
        """
        if not old:
            raise ValueError("old substring cannot be empty")
        self.operations_count += 1
        return self.text.replace(old, new)

    def get_statistics(self):
        """Get statistics about the current text.

        Returns:
            dict: A dictionary containing:
                - length (int): Total character count
                - words (int): Word count
                - vowels (int): Vowel count
                - operations (int): Number of operations performed

        Example:
            >>> processor = StringProcessor("Hello World")
            >>> stats = processor.get_statistics()
            >>> stats['length']
            11
            >>> stats['words']
            2
        """
        return {
            'length': len(self.text),
            'words': len(self.text.split()),
            'vowels': count_vowels(self.text),
            'operations': self.operations_count
        }
