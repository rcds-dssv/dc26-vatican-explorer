"""
Comprehensive tests demonstrating various pytest parametrization techniques.

This test file showcases different ways to use @pytest.mark.parametrize
for efficient and maintainable testing.
"""
import pytest
from parametrize_examples import (
    validate_email,
    classify_number,
    truncate_text,
    calculate_discount,
    get_grade,
    UserAccount,
)


# =============================================================================
# EXAMPLE 1: Basic Parametrization - Single Parameter
# =============================================================================

@pytest.mark.parametrize("email", [
    "user@example.com",
    "test@domain.org",
    "name@subdomain.example.com",
    "user+tag@example.com",
])
def test_valid_emails(email):
    """Test valid email formats."""
    assert validate_email(email) is True


# =============================================================================
# EXAMPLE 2: Multiple Parameters
# =============================================================================

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("test@domain.org", True),
    ("invalid", False),
    ("@example.com", False),
    ("user@", False),
    ("", False),
])
def test_email_validation(email, expected):
    """Test email validation with various inputs."""
    assert validate_email(email) == expected


# =============================================================================
# EXAMPLE 3: Using pytest.param with IDs
# =============================================================================

@pytest.mark.parametrize("number,expected", [
    pytest.param(5, "positive", id="positive_number"),
    pytest.param(-3, "negative", id="negative_number"),
    pytest.param(0, "zero", id="zero_value"),
])
def test_classify_number_with_ids(number, expected):
    """Test number classification with custom test IDs."""
    assert classify_number(number) == expected


# =============================================================================
# EXAMPLE 4: Testing Multiple Scenarios
# =============================================================================

@pytest.mark.parametrize("text,max_len,suffix,expected", [
    ("Hello World", 5, "...", "Hello..."),
    ("Hi", 10, "...", "Hi"),
    ("Long text here", 8, " [more]", "Long tex [more]"),
    ("Exact", 5, "...", "Exact"),
    ("", 5, "...", ""),
])
def test_truncate_text(text, max_len, suffix, expected):
    """Test text truncation with various parameters."""
    assert truncate_text(text, max_len, suffix) == expected


# =============================================================================
# EXAMPLE 5: Testing Exception Cases
# =============================================================================

@pytest.mark.parametrize("invalid_input", [
    None,
    "123",  # String, not a number
    [],
    {},
])
def test_classify_number_with_invalid_type(invalid_input):
    """Test that invalid types raise TypeError."""
    with pytest.raises(TypeError, match="Input must be a number"):
        classify_number(invalid_input)


@pytest.mark.parametrize("discount", [
    -10,
    101,
    150,
    -1,
])
def test_invalid_discount_raises_error(discount):
    """Test that invalid discount percentages raise ValueError."""
    with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
        calculate_discount(100.0, discount)


# =============================================================================
# EXAMPLE 6: Testing Boundary Conditions
# =============================================================================

@pytest.mark.parametrize("price,discount,expected", [
    (100.0, 0, 100.0),      # No discount
    (100.0, 100, 0.0),      # Full discount
    (100.0, 50, 50.0),      # Half discount
    (50.0, 20, 40.0),       # 20% off
    (75.0, 10, 67.5),       # 10% off
])
def test_calculate_discount(price, discount, expected):
    """Test discount calculation with various inputs."""
    result = calculate_discount(price, discount)
    assert result == pytest.approx(expected, rel=0.01)


# =============================================================================
# EXAMPLE 7: Testing Grade Ranges
# =============================================================================

@pytest.mark.parametrize("score,expected_grade", [
    # A range (90-100)
    (100, "A"),
    (95, "A"),
    (90, "A"),
    # B range (80-89)
    (89, "B"),
    (85, "B"),
    (80, "B"),
    # C range (70-79)
    (79, "C"),
    (75, "C"),
    (70, "C"),
    # D range (60-69)
    (69, "D"),
    (65, "D"),
    (60, "D"),
    # F range (0-59)
    (59, "F"),
    (50, "F"),
    (0, "F"),
])
def test_get_grade(score, expected_grade):
    """Test grade calculation for various scores."""
    assert get_grade(score) == expected_grade


# =============================================================================
# EXAMPLE 8: Testing Class Methods
# =============================================================================

@pytest.mark.parametrize("username,age,is_adult", [
    ("alice", 25, True),
    ("bob", 18, True),
    ("charlie", 17, False),
    ("dave", 10, False),
])
def test_user_is_adult(username, age, is_adult):
    """Test adult status for various user ages."""
    user = UserAccount(username, age)
    assert user.is_adult() == is_adult


@pytest.mark.parametrize("age,expected_category", [
    (5, "child"),
    (12, "child"),
    (13, "teen"),
    (17, "teen"),
    (18, "adult"),
    (64, "adult"),
    (65, "senior"),
    (80, "senior"),
])
def test_user_category(age, expected_category):
    """Test user age category classification."""
    user = UserAccount("testuser", age)
    assert user.get_category() == expected_category


# =============================================================================
# EXAMPLE 9: Testing Invalid User Creation
# =============================================================================

@pytest.mark.parametrize("username,age,error_match", [
    ("", 25, "Username cannot be empty"),
    ("alice", -1, "Age cannot be negative"),
    ("", -5, "Username cannot be empty"),  # Username checked first
])
def test_invalid_user_creation(username, age, error_match):
    """Test that invalid user data raises ValueError."""
    with pytest.raises(ValueError, match=error_match):
        UserAccount(username, age)


# =============================================================================
# EXAMPLE 10: Multiple Parametrize Decorators (Cartesian Product)
# =============================================================================

@pytest.mark.parametrize("base", [10, 20, 30])
@pytest.mark.parametrize("discount", [10, 20])
def test_discount_combinations(base, discount):
    """Test discount with cartesian product of parameters.

    This creates 6 tests (3 bases × 2 discounts):
    - base=10, discount=10 → result=9.0
    - base=10, discount=20 → result=8.0
    - base=20, discount=10 → result=18.0
    - base=20, discount=20 → result=16.0
    - base=30, discount=10 → result=27.0
    - base=30, discount=20 → result=24.0
    """
    result = calculate_discount(float(base), discount)
    expected = base * (1 - discount / 100)
    assert result == pytest.approx(expected)


# =============================================================================
# EXAMPLE 11: Using Constants for Test Data
# =============================================================================

VALID_EMAILS = [
    "user@example.com",
    "test@domain.org",
    "admin@company.co.uk",
]

INVALID_EMAILS = [
    "invalid",
    "@example.com",
    "user@",
    "",
    "no-at-sign.com",
]

@pytest.mark.parametrize("email", VALID_EMAILS)
def test_valid_emails_from_constant(email):
    """Test valid emails using a constant list."""
    assert validate_email(email) is True


@pytest.mark.parametrize("email", INVALID_EMAILS)
def test_invalid_emails_from_constant(email):
    """Test invalid emails using a constant list."""
    assert validate_email(email) is False


# =============================================================================
# EXAMPLE 12: Complex Test Scenarios with IDs
# =============================================================================

@pytest.mark.parametrize("username,age,expected_category,expected_adult", [
    pytest.param("child1", 8, "child", False, id="young_child"),
    pytest.param("teen1", 15, "teen", False, id="teenager"),
    pytest.param("adult1", 30, "adult", True, id="young_adult"),
    pytest.param("senior1", 70, "senior", True, id="elderly"),
])
def test_user_full_profile(username, age, expected_category, expected_adult):
    """Test multiple user properties simultaneously."""
    user = UserAccount(username, age)
    assert user.get_category() == expected_category
    assert user.is_adult() == expected_adult


# =============================================================================
# EXAMPLE 13: Edge Cases and Boundary Testing
# =============================================================================

@pytest.mark.parametrize("text,max_len", [
    ("", 0),           # Empty string, zero length
    ("a", 1),          # Single char, exact length
    ("ab", 1),         # Needs truncation
    ("test", 100),     # Way longer than needed
])
def test_truncate_edge_cases(text, max_len):
    """Test text truncation edge cases."""
    result = truncate_text(text, max_len)
    # Result should never be longer than max_len + suffix length
    assert len(result) <= max_len + 3  # 3 for "..."


# =============================================================================
# EXAMPLE 14: Class-based Parametrized Tests
# =============================================================================

class TestEmailValidation:
    """Group related parametrized tests in a class."""

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test@domain.org",
    ])
    def test_valid_formats(self, email):
        """Test valid email formats."""
        assert validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "invalid",
        "@example.com",
        "user@",
    ])
    def test_invalid_formats(self, email):
        """Test invalid email formats."""
        assert validate_email(email) is False


# =============================================================================
# EXAMPLE 15: Marked Parameters for Special Cases
# =============================================================================

@pytest.mark.parametrize("score,grade", [
    (95, "A"),
    (85, "B"),
    (75, "C"),
    pytest.param(55, "F", marks=pytest.mark.xfail(reason="Known grading bug")),
])
def test_grades_with_marks(score, grade):
    """Test grades with some marked as expected failures."""
    assert get_grade(score) == grade


# =============================================================================
# Running Information
# =============================================================================

"""
To run these tests:

1. All tests:
   pytest test_parametrize_examples.py -v

2. Specific test with parameter:
   pytest test_parametrize_examples.py::test_email_validation -v

3. Tests matching a keyword:
   pytest test_parametrize_examples.py -k "valid" -v

4. Show test IDs:
   pytest test_parametrize_examples.py --collect-only

5. Run with specific ID:
   pytest test_parametrize_examples.py::test_classify_number_with_ids[positive_number] -v
"""
