"""Tests for calculator functions."""
import pytest
from calculator import add, subtract, multiply, divide


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2


def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6


def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (5, 3, 8),
    (-1, -1, -2),
    (100, 200, 300),
])
def test_add_multiple(a, b, expected):
    assert add(a, b) == expected
