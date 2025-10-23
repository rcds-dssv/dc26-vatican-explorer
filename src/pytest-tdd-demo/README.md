# Pytest TDD Demo

A simple demonstration of Test-Driven Development (TDD) using pytest.

## What is TDD?

Test-Driven Development follows a simple cycle:

1. **Red**: Write a failing test
2. **Green**: Write code to make it pass
3. **Refactor**: Improve the code

## Setup

```bash
pip install pytest
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_calculator.py
```

## Examples Included

1. **Calculator** - Basic TDD example with arithmetic functions
2. **Shopping Cart** - Demonstrates building features incrementally with TDD
3. **String Utils** - Shows testing edge cases, parameterization, and **Google-style docstrings**

## Quick Example

```python
# 1. Write the test first (RED)
def test_add():
    assert add(2, 3) == 5

# 2. Run it - it fails (no add function yet)

# 3. Write minimal code (GREEN)
def add(a, b):
    return a + b

# 4. Run test - it passes!

# 5. Refactor if needed
```

## Project Structure

```
pytest-tdd-demo/
├── README.md                    # This file
├── DOCSTRING_GUIDE.md           # Guide to Google-style docstrings
├── PARAMETRIZE_GUIDE.md         # Guide to pytest parametrization
├── requirements.txt             # Python dependencies
├── calculator.py                # Simple calculator implementation
├── test_calculator.py           # Calculator tests (9 tests)
├── shopping_cart.py             # Shopping cart implementation
├── test_shopping_cart.py        # Shopping cart tests (6 tests)
├── string_utils.py              # String utilities with Google-style docstrings
├── test_string_utils.py         # String utilities tests (35 tests)
├── parametrize_examples.py      # Examples for parametrization
└── test_parametrize_examples.py # Parametrization tests (92 tests)
```

## Documentation

This demo includes comprehensive documentation:

- **DOCSTRING_GUIDE.md** - Complete guide to writing Google-style docstrings
- **PARAMETRIZE_GUIDE.md** - Complete guide to pytest parametrization
- **string_utils.py** - Example module with properly documented functions and classes
- **parametrize_examples.py** - 15+ examples of parametrization techniques

Learn how to write professional documentation and efficient tests for your Python code!
