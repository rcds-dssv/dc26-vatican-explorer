"""
Examples demonstrating various pytest parametrization techniques.

This module contains practical examples of how to use @pytest.mark.parametrize
effectively in different scenarios.
"""


def validate_email(email):
    """
    Validate email format.

    Args:
        email (str): Email to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    if '@' not in email:
        return False

    # Split on @ and check we have exactly 2 parts
    parts = email.split('@')
    if len(parts) != 2:
        return False

    local, domain = parts
    # Local part (before @) must not be empty
    if not local:
        return False
    # Domain must contain a dot and have content after it
    return '.' in domain and len(domain.split('.')[-1]) > 0


def classify_number(num):
    """
    Classify a number as positive, negative, or zero.

    Args:
        num: Number to classify

    Returns:
        str: Classification ("positive", "negative", or "zero")

    Raises:
        TypeError: If num is not a number
    """
    if not isinstance(num, (int, float)):
        raise TypeError("Input must be a number")

    if num > 0:
        return "positive"
    elif num < 0:
        return "negative"
    else:
        return "zero"


def truncate_text(text, max_length, suffix="..."):
    """
    Truncate text to maximum length.

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def calculate_discount(price, discount_percent):
    """
    Calculate price after discount.

    Args:
        price (float): Original price
        discount_percent (int): Discount percentage (0-100)

    Returns:
        float: Price after discount

    Raises:
        ValueError: If discount is not between 0 and 100
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")

    return price * (1 - discount_percent / 100)


def get_grade(score):
    """
    Convert numeric score to letter grade.

    Args:
        score (int): Score from 0-100

    Returns:
        str: Letter grade (A, B, C, D, or F)
    """
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


class UserAccount:
    """Simple user account class for testing."""

    def __init__(self, username, age):
        """
        Initialize user account.

        Args:
            username (str): Username
            age (int): User's age

        Raises:
            ValueError: If age is negative or username is empty
        """
        if not username:
            raise ValueError("Username cannot be empty")
        if age < 0:
            raise ValueError("Age cannot be negative")

        self.username = username
        self.age = age

    def is_adult(self):
        """Check if user is an adult (18+)."""
        return self.age >= 18

    def get_category(self):
        """Get user age category."""
        if self.age < 13:
            return "child"
        elif self.age < 18:
            return "teen"
        elif self.age < 65:
            return "adult"
        else:
            return "senior"
