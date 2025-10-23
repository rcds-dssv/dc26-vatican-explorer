# Google-Style Docstring Guide

This guide demonstrates how to write comprehensive docstrings following Google's Python Style Guide.

## Why Use Docstrings?

- **Documentation**: Explains what your code does
- **IDE Support**: Enables autocompletion and inline help
- **Auto-generation**: Tools like Sphinx can generate documentation
- **Testing**: Can be used with doctest for example-based testing

## Google Style vs Other Styles

**Google Style** - Clean, readable, widely used
```python
def function(arg1, arg2):
    """Summary line.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value
    """
```

**NumPy Style** - More detailed, common in scientific computing
```python
def function(arg1, arg2):
    """
    Summary line.

    Parameters
    ----------
    arg1 : type
        Description of arg1
    arg2 : type
        Description of arg2

    Returns
    -------
    type
        Description of return value
    """
```

**reStructuredText (Sphinx)** - More markup, very detailed
```python
def function(arg1, arg2):
    """
    Summary line.

    :param arg1: Description of arg1
    :type arg1: type
    :param arg2: Description of arg2
    :type arg2: type
    :returns: Description of return value
    :rtype: type
    """
```

## Google-Style Docstring Sections

### Module Docstring

```python
"""One-line summary of the module.

More detailed description of the module. This can span
multiple lines and paragraphs.

Example:
    How to use this module::

        >>> import my_module
        >>> my_module.do_something()

Attributes:
    MODULE_CONSTANT (type): Description of constant.
"""
```

### Function Docstring

```python
def function_name(param1, param2, param3=None):
    """One-line summary of function.

    More detailed description if needed. Explain what the
    function does, not how it does it.

    Args:
        param1 (type): Description of param1.
        param2 (type): Description of param2.
        param3 (type, optional): Description of param3. Defaults to None.

    Returns:
        type: Description of return value.

    Raises:
        ValueError: When the input is invalid.
        TypeError: When param1 is not a string.

    Example:
        >>> function_name("hello", 42)
        'result'
    """
```

### Class Docstring

```python
class MyClass:
    """One-line summary of class.

    More detailed description of the class.

    Attributes:
        attribute1 (type): Description of attribute1.
        attribute2 (type): Description of attribute2.

    Example:
        >>> obj = MyClass("value")
        >>> obj.method()
        'result'
    """

    def __init__(self, param):
        """Initialize MyClass.

        Args:
            param (type): Description of param.
        """
        self.attribute1 = param
```

### Method Docstring

```python
def method(self, param1):
    """One-line summary of method.

    Args:
        param1 (type): Description of param1.

    Returns:
        type: Description of return value.

    Note:
        Additional notes about the method.
    """
```

## Complete Example

See `string_utils.py` for a complete example with:

### 1. Module-level Docstring
```python
"""
String utility functions demonstrating Google-style docstrings.

This module provides common string manipulation functions with comprehensive
documentation following Google's Python Style Guide.

Example:
    Basic usage::

        >>> from string_utils import reverse_string
        >>> reverse_string("hello")
        'olleh'

Attributes:
    VOWELS (str): String containing all vowels.
"""
```

### 2. Simple Function
```python
def reverse_string(text):
    """Reverse a string.

    Args:
        text (str): The string to reverse.

    Returns:
        str: The reversed string.

    Example:
        >>> reverse_string("hello")
        'olleh'
    """
    return text[::-1]
```

### 3. Function with Multiple Parameters
```python
def truncate_string(text, max_length, suffix="..."):
    """Truncate a string to a maximum length.

    If the string is longer than max_length, it will be truncated and
    a suffix will be added.

    Args:
        text (str): The string to truncate.
        max_length (int): Maximum length before truncation.
        suffix (str, optional): Suffix to add when truncated. Defaults to "...".

    Returns:
        str: The truncated string with suffix, or original if shorter.

    Raises:
        ValueError: If max_length is negative.
        TypeError: If text is not a string.

    Example:
        >>> truncate_string("Hello World", 5)
        'Hello...'
    """
```

### 4. Class with Methods
```python
class StringProcessor:
    """A class for processing strings with various operations.

    Attributes:
        text (str): The current text being processed.
        operations_count (int): Number of operations performed.

    Example:
        >>> processor = StringProcessor("Hello")
        >>> processor.to_uppercase()
        'HELLO'
    """

    def __init__(self, text):
        """Initialize the StringProcessor.

        Args:
            text (str): The initial text to process.

        Raises:
            TypeError: If text is not a string.
        """
        self.text = text
        self.operations_count = 0
```

## Common Docstring Sections

| Section | Purpose | Required |
|---------|---------|----------|
| Summary | One-line description | Yes |
| Description | Detailed explanation | Optional |
| Args | Parameter descriptions | If parameters exist |
| Returns | Return value description | If returns value |
| Raises | Exceptions raised | If raises exceptions |
| Example | Usage examples | Recommended |
| Note | Additional notes | Optional |
| Warning | Important warnings | If applicable |
| See Also | Related functions/classes | Optional |

## Type Hints in Docstrings

You can include types in the docstring or use Python type hints:

**Docstring only:**
```python
def add(a, b):
    """Add two numbers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: Sum of a and b.
    """
    return a + b
```

**With type hints (Python 3.5+):**
```python
def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number.
        b: Second number.

    Returns:
        Sum of a and b.
    """
    return a + b
```

## Best Practices

1. **Keep it concise**: Write clear, brief descriptions
2. **Use active voice**: "Returns the sum" not "The sum is returned"
3. **Be consistent**: Use the same style throughout your project
4. **Include examples**: Especially for complex functions
5. **Document exceptions**: List all exceptions that can be raised
6. **Update regularly**: Keep docstrings in sync with code
7. **Use proper grammar**: Full sentences with punctuation
8. **Don't repeat yourself**: Docstring should add information, not duplicate code

## Tools for Docstrings

- **pydoc**: Built-in documentation generator
  ```bash
  python -m pydoc string_utils
  ```

- **Sphinx**: Professional documentation generator
  ```bash
  pip install sphinx
  sphinx-quickstart
  ```

- **pdoc**: Simple auto-documentation
  ```bash
  pip install pdoc3
  pdoc --html string_utils
  ```

- **IDE Support**: VS Code, PyCharm show docstrings on hover

## Testing with Doctest

Docstrings with examples can be tested:

```python
def add(a, b):
    """Add two numbers.

    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    """
    return a + b
```

Run with:
```bash
python -m doctest string_utils.py -v
```

## Quick Reference

**Minimal function docstring:**
```python
def func(arg):
    """Do something with arg."""
```

**Complete function docstring:**
```python
def func(arg1, arg2=None):
    """One-line summary.

    Longer description explaining the function's purpose.

    Args:
        arg1 (str): Description.
        arg2 (int, optional): Description. Defaults to None.

    Returns:
        bool: Description.

    Raises:
        ValueError: Description.

    Example:
        >>> func("test", 42)
        True
    """
```

## See Also

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)

For a complete working example, see `string_utils.py` in this directory.
