# Testing Guide for DC26 Vatican Explorer

This directory contains unit tests for the Vatican Explorer project. The tests are written using [pytest](https://docs.pytest.org/), a powerful Python testing framework.

## Directory Structure

```
tests/
├── README.md                    # This file - your testing guide
├── __init__.py                  # Makes tests a Python package
├── conftest.py                  # Pytest configuration (handles imports)
└── test_pope_utilities.py       # Example: Tests for pope utility functions
```

**Note**: The `conftest.py` file is automatically loaded by pytest and configures the Python path so that imports work correctly. You don't need to modify it when adding new tests.

## Getting Started

### Prerequisites

Install pytest if you haven't already:

```bash
pip install pytest
```

### Running Tests

From the project root directory:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_pope_utilities.py

# Run a specific test class
pytest tests/test_pope_utilities.py::TestPapalNormalizeDisplayName

# Run a specific test
pytest tests/test_pope_utilities.py::TestPapalNormalizeDisplayName::test_normalize_simple_name

# Run with coverage report (requires pytest-cov)
pytest --cov=src --cov-report=html
```

## Writing Tests: Follow the Example

The file [test_pope_utilities.py](test_pope_utilities.py) demonstrates best practices for writing tests. Here's what to follow:

### 1. File Naming Convention

- Test files must start with `test_` (e.g., `test_database_utils.py`)
- Place test files in this `tests/` directory
- Name test files after the module they're testing

### 2. Test Structure

```python
"""
Module docstring explaining what is being tested.
"""

import pytest
from your_module import function_to_test


class TestFunctionName:
    """Group related tests into classes."""

    def test_basic_case(self):
        """Each test should have a clear docstring."""
        # Arrange: Set up test data
        input_data = "example"

        # Act: Call the function
        result = function_to_test(input_data)

        # Assert: Verify the result
        assert result == "expected output"
```

### 3. Test Naming

- Test methods must start with `test_`
- Use descriptive names: `test_function_does_something_specific`
- Good examples from [test_pope_utilities.py](test_pope_utilities.py):
  - ✅ `test_normalize_removes_leading_whitespace`
  - ✅ `test_find_case_insensitive`
  - ❌ `test_normalize` (too vague)
  - ❌ `test1` (not descriptive)

### 4. Test Class Organization

Group related tests into classes:

```python
class TestNormalization:
    """Tests for name normalization function."""

    def test_removes_whitespace(self):
        ...

    def test_handles_empty_string(self):
        ...


class TestValidation:
    """Tests for name validation function."""

    def test_accepts_valid_name(self):
        ...

    def test_rejects_invalid_name(self):
        ...
```

### 5. Test Coverage Checklist

For each function you test, include tests for:

- ✅ **Normal cases**: Typical valid inputs
- ✅ **Edge cases**: Empty strings, None, boundary values
- ✅ **Error cases**: Invalid inputs that should be handled gracefully
- ✅ **Multiple scenarios**: Different valid input patterns

**Example from test_pope_utilities.py:**

```python
def test_normalize_simple_name(self):           # Normal case
def test_normalize_empty_string(self):          # Edge case
def test_normalize_none_input(self):            # Error case
def test_normalize_collapses_multiple_spaces(): # Specific scenario
```

### 6. Using Fixtures

For shared test data, use pytest fixtures:

```python
class TestPapalFindByDisplayName:

    @pytest.fixture
    def sample_popes(self):
        """Fixture providing test data used across multiple tests."""
        return [
            {"display_name": "Francis", "slug": "francesco"},
            {"display_name": "Benedict XVI", "slug": "benedict-xvi"},
        ]

    def test_find_exact_match(self, sample_popes):
        # Use the fixture data
        result = papal_find_by_display_name(sample_popes, "Francis")
        assert result is not None
```

### 7. Assertion Best Practices

```python
# Use clear, specific assertions
assert result == expected_value                    # Equality
assert result is not None                          # None checks
assert len(result) == 3                           # Length checks
assert "key" in result                            # Membership
assert result > 0                                 # Comparisons

# Use pytest's special assertions for better error messages
with pytest.raises(ValueError):                   # Exception testing
    function_that_should_raise()
```

## Example: Testing a New Function

Let's say you want to test a function in `src/data/database_reader_example.py`:

### Step 1: Create a Test File

Create `tests/test_database_reader.py`:

```python
"""
Unit tests for database reader utility functions.
"""

import pytest
from data.database_reader_example import get_tables_in_database


class TestGetTablesInDatabase:
    """Tests for get_tables_in_database function."""

    def test_returns_list_of_table_names(self):
        """Should return a list of table name strings."""
        # Create a mock cursor or use a test database
        # This is a simplified example
        mock_cursor = MockCursor()
        result = get_tables_in_database(mock_cursor)

        assert isinstance(result, list)
        assert all(isinstance(name, str) for name in result)
```

### Step 2: Run Your Tests

```bash
pytest tests/test_database_reader.py -v
```

### Step 3: Iterate

- Start with simple tests
- Add more edge cases as you find issues
- Keep tests focused and independent

## Testing Tips

### DO:
- ✅ Write tests before or alongside your code
- ✅ Keep tests simple and focused
- ✅ Use descriptive names and docstrings
- ✅ Test one thing per test method
- ✅ Make tests independent (no dependencies between tests)
- ✅ Use fixtures for shared test data

### DON'T:
- ❌ Test implementation details (test behavior, not internal code)
- ❌ Write tests that depend on external services without mocking
- ❌ Write tests that depend on specific execution order
- ❌ Leave commented-out test code
- ❌ Skip writing tests for "simple" functions (they can still break!)

## Common Patterns

### Testing String Functions

See `TestPapalNormalizeDisplayName` in [test_pope_utilities.py](test_pope_utilities.py):
- Test empty strings
- Test whitespace handling
- Test None inputs
- Test special characters

### Testing Search/Filter Functions

See `TestPapalFindByDisplayName` in [test_pope_utilities.py](test_pope_utilities.py):
- Test exact matches
- Test case sensitivity
- Test not found cases
- Test empty collections

### Testing URL/Path Parsing

See `TestPapalExtractSlugFromContentUrl` in [test_pope_utilities.py](test_pope_utilities.py):
- Test valid URLs
- Test malformed URLs
- Test edge cases (empty, None, invalid format)

## Next Steps

1. Look at [test_pope_utilities.py](test_pope_utilities.py) to see real working examples
2. Choose a function from the codebase to test
3. Create a new `test_*.py` file following the patterns shown
4. Run your tests with `pytest -v`
5. Iterate and improve!

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Test-Driven Development (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)

## Questions or Issues?

If you have questions about testing or run into issues:
1. Review the example in [test_pope_utilities.py](test_pope_utilities.py)
2. Check the pytest documentation
3. Ask the team for help!

---

**Remember**: Good tests make refactoring safer and catch bugs before they reach production. Take the time to write clear, comprehensive tests!
