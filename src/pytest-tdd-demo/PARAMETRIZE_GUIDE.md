# Pytest Parametrize Guide

Complete guide to using `@pytest.mark.parametrize` for efficient testing.

## What is Parametrization?

Parametrization allows you to run the same test with different inputs, reducing code duplication and making your test suite more maintainable.

**Without parametrization:**
```python
def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0
```

**With parametrization:**
```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, -1, -2),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

## Basic Syntax

### Single Parameter

```python
import pytest

@pytest.mark.parametrize("number", [1, 2, 3, 4, 5])
def test_is_positive(number):
    """Test that numbers are positive."""
    assert number > 0
```

This creates 5 separate test cases, one for each number.

### Multiple Parameters

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (10, 20, 30),
])
def test_addition(a, b, expected):
    """Test addition with multiple inputs."""
    assert a + b == expected
```

### Alternative Syntax (Tuple of Parameter Names)

```python
@pytest.mark.parametrize(("a", "b", "expected"), [
    (1, 1, 2),
    (2, 3, 5),
    (10, 20, 30),
])
def test_addition(a, b, expected):
    assert a + b == expected
```

## Common Use Cases

### 1. Testing Multiple Valid Inputs

```python
@pytest.mark.parametrize("email", [
    "test@example.com",
    "user@domain.org",
    "name@subdomain.domain.com",
    "user+tag@example.com",
])
def test_valid_email_formats(email):
    """Test that various email formats are valid."""
    assert is_valid_email(email) is True
```

### 2. Testing Edge Cases

```python
@pytest.mark.parametrize("value,expected", [
    (0, "zero"),
    (-1, "negative"),
    (1, "positive"),
    (None, "none"),
    ("", "empty"),
])
def test_classify_value(value, expected):
    """Test value classification with edge cases."""
    assert classify(value) == expected
```

### 3. Testing Error Conditions

```python
@pytest.mark.parametrize("invalid_input", [
    "",
    " ",
    "123",
    "user@",
    "@domain.com",
    "nodomain",
])
def test_invalid_email_raises_error(invalid_input):
    """Test that invalid emails raise ValueError."""
    with pytest.raises(ValueError):
        validate_email(invalid_input)
```

### 4. Testing String Operations

```python
@pytest.mark.parametrize("text,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("MiXeD", "MIXED"),
    ("", ""),
])
def test_to_uppercase(text, expected):
    """Test converting strings to uppercase."""
    assert text.upper() == expected
```

### 5. Testing with Different Types

```python
@pytest.mark.parametrize("value,type_name", [
    (42, "int"),
    (3.14, "float"),
    ("hello", "str"),
    ([1, 2, 3], "list"),
    ({"key": "value"}, "dict"),
])
def test_type_detection(value, type_name):
    """Test type detection for various inputs."""
    assert get_type_name(value) == type_name
```

## Advanced Parametrization

### 1. Using pytest.param for Test IDs

```python
@pytest.mark.parametrize("a,b,expected", [
    pytest.param(2, 3, 5, id="positive"),
    pytest.param(-1, -1, -2, id="negative"),
    pytest.param(0, 0, 0, id="zero"),
])
def test_add_with_ids(a, b, expected):
    """Test addition with custom test IDs."""
    assert add(a, b) == expected
```

Output:
```
test_add_with_ids[positive] PASSED
test_add_with_ids[negative] PASSED
test_add_with_ids[zero] PASSED
```

### 2. Marking Individual Parameters

```python
@pytest.mark.parametrize("number,expected", [
    (5, 120),
    (10, 3628800),
    pytest.param(20, 2432902008176640000, marks=pytest.mark.slow),
])
def test_factorial(number, expected):
    """Test factorial calculation."""
    assert factorial(number) == expected
```

### 3. Using ids Function

```python
def idfn(val):
    """Custom ID function."""
    if isinstance(val, str):
        return f"string:{val}"
    return repr(val)

@pytest.mark.parametrize("text", ["hello", "world", "test"], ids=idfn)
def test_with_id_function(text):
    assert len(text) > 0
```

### 4. Multiple Parametrize Decorators (Cartesian Product)

```python
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_cartesian(x, y):
    """Test with cartesian product of parameters."""
    # Creates 4 tests: (0,2), (0,3), (1,2), (1,3)
    assert x < y
```

### 5. Indirect Parametrization (with Fixtures)

```python
@pytest.fixture
def user(request):
    """Fixture that creates a user based on parameter."""
    username = request.param
    return User(username)

@pytest.mark.parametrize("user", ["alice", "bob", "charlie"], indirect=True)
def test_user_creation(user):
    """Test user creation through fixture."""
    assert user.username in ["alice", "bob", "charlie"]
```

### 6. Parametrizing Fixtures

```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """Fixture with built-in parametrization."""
    return request.param

def test_with_fixture(number):
    """Test will run 3 times with values 1, 2, 3."""
    assert number > 0
```

## Real-World Examples

### Example 1: Email Validation

```python
@pytest.mark.parametrize("email,expected", [
    # Valid emails
    ("user@example.com", True),
    ("name.surname@domain.co.uk", True),
    ("user+tag@example.com", True),

    # Invalid emails
    ("invalid", False),
    ("@example.com", False),
    ("user@", False),
    ("user @example.com", False),
    ("", False),
])
def test_email_validation(email, expected):
    """Test email validation with various inputs."""
    assert is_valid_email(email) == expected
```

### Example 2: String Manipulation

```python
@pytest.mark.parametrize("text,max_len,suffix,expected", [
    ("Hello World", 5, "...", "Hello..."),
    ("Hi", 10, "...", "Hi"),
    ("Long text here", 8, " [more]", "Long tex [more]"),
    ("Exact", 5, "...", "Exact"),
])
def test_truncate_string(text, max_len, suffix, expected):
    """Test string truncation with various parameters."""
    assert truncate_string(text, max_len, suffix) == expected
```

### Example 3: Mathematical Operations

```python
@pytest.mark.parametrize("operation,a,b,expected", [
    ("add", 2, 3, 5),
    ("subtract", 5, 3, 2),
    ("multiply", 4, 5, 20),
    ("divide", 10, 2, 5),
])
def test_calculator_operations(operation, a, b, expected):
    """Test calculator with different operations."""
    calc = Calculator()
    result = getattr(calc, operation)(a, b)
    assert result == expected
```

### Example 4: HTTP Status Codes

```python
@pytest.mark.parametrize("status_code,is_success", [
    (200, True),  # OK
    (201, True),  # Created
    (204, True),  # No Content
    (400, False), # Bad Request
    (404, False), # Not Found
    (500, False), # Server Error
])
def test_http_status_classification(status_code, is_success):
    """Test HTTP status code classification."""
    assert is_successful_status(status_code) == is_success
```

### Example 5: File Extensions

```python
@pytest.mark.parametrize("filename,expected_ext", [
    ("document.pdf", "pdf"),
    ("image.PNG", "png"),
    ("archive.tar.gz", "gz"),
    ("noextension", ""),
    ("multiple.dots.txt", "txt"),
])
def test_get_file_extension(filename, expected_ext):
    """Test extracting file extensions."""
    assert get_extension(filename) == expected_ext
```

## Organizing Parametrize Data

### 1. Using Constants

```python
VALID_EMAILS = [
    "user@example.com",
    "test@domain.org",
    "name@subdomain.example.com",
]

@pytest.mark.parametrize("email", VALID_EMAILS)
def test_valid_emails(email):
    assert is_valid_email(email)
```

### 2. Using External Data

```python
import json

def load_test_data():
    with open('test_data.json') as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_test_data())
def test_from_file(test_case):
    assert process(test_case['input']) == test_case['expected']
```

### 3. Using Fixtures to Generate Parameters

```python
def pytest_generate_tests(metafunc):
    """Dynamically generate test parameters."""
    if "number" in metafunc.fixturenames:
        metafunc.parametrize("number", range(1, 6))

def test_with_generated_params(number):
    assert number > 0
```

## Best Practices

### 1. Use Descriptive IDs

```python
# Good - clear test names
@pytest.mark.parametrize("email,expected", [
    pytest.param("valid@example.com", True, id="valid_email"),
    pytest.param("invalid", False, id="invalid_email"),
])
def test_email(email, expected):
    assert is_valid_email(email) == expected
```

### 2. Keep Test Cases Readable

```python
# Good - easy to read
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (10, 20, 30),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### 3. Group Related Tests

```python
class TestEmailValidation:
    """Group all email validation tests."""

    @pytest.mark.parametrize("email", [
        "valid@example.com",
        "test@domain.org",
    ])
    def test_valid_emails(self, email):
        assert is_valid_email(email)

    @pytest.mark.parametrize("email", [
        "invalid",
        "@example.com",
    ])
    def test_invalid_emails(self, email):
        assert not is_valid_email(email)
```

### 4. Use Comments for Complex Cases

```python
@pytest.mark.parametrize("input,expected", [
    # Edge case: empty string
    ("", 0),
    # Normal case: single word
    ("hello", 5),
    # Edge case: only spaces
    ("   ", 3),
])
def test_string_length(input, expected):
    assert len(input) == expected
```

## Common Patterns

### Testing Both Success and Failure

```python
@pytest.mark.parametrize("value,should_raise", [
    (5, False),
    (0, True),
    (-5, True),
])
def test_positive_validation(value, should_raise):
    """Test validation for positive numbers."""
    if should_raise:
        with pytest.raises(ValueError):
            validate_positive(value)
    else:
        validate_positive(value)  # Should not raise
```

### Testing String Transformations

```python
@pytest.mark.parametrize("input,output", [
    ("hello", "HELLO"),
    ("WORLD", "world"),
    ("MiXeD", "mixed"),
])
def test_transformations(input, output):
    processor = StringProcessor(input)
    assert processor.to_lowercase() == output.lower()
    assert processor.to_uppercase() == output.upper()
```

## Running Parametrized Tests

```bash
# Run all tests
pytest test_file.py -v

# Run specific parametrized test
pytest test_file.py::test_name[param_id] -v

# Run all tests with specific parameter value
pytest -k "positive" -v

# Show parameter values in output
pytest -v --tb=short
```

## Complete Working Example

See `test_string_utils.py` and `test_calculator.py` in this repository for complete examples of parametrization in action!

```python
# From test_calculator.py
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (5, 3, 8),
    (-1, -1, -2),
    (100, 200, 300),
])
def test_add_multiple(a, b, expected):
    """Example of parametrization from our demo."""
    assert add(a, b) == expected
```

## Key Takeaways

1. **Reduce duplication** - Write one test, test many cases
2. **Better coverage** - Easy to add more test cases
3. **Clear output** - Each parameter combination is a separate test
4. **Maintainable** - Update test logic in one place
5. **Readable** - Test data clearly separated from test logic

## Resources

- [Pytest Parametrize Documentation](https://docs.pytest.org/en/latest/how-to/parametrize.html)
- [Pytest Examples](https://docs.pytest.org/en/latest/example/parametrize.html)
- See `test_calculator.py` and `test_string_utils.py` for working examples
