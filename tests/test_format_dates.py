# ----------------------
# :: IMPORTS ::
# ----------------------
import pytest
from src.dc26_vatican_explorer.data_cleaning.format_dates import (
    format_pontificate_date,
    format_date_to_iso,
    extract_date_from_title
)

# ----------------------
# :: TESTS ::
# ----------------------


# --- format_pontificate_date ---
@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("01,11.VII.2020", "2020-07-01"),
        ("1,11.VII.2020", "2020-07-01"),  # single digit day
        ("25,12.XII.1999", "1999-12-25"), # high month/day
    ]
)
def test_format_pontificate_date(input_date, expected):
    assert format_pontificate_date(input_date) == expected


# --- format_date_to_iso ---
@pytest.mark.parametrize(
    "date,expected",
    [
        ("January 5, 2020", "2020-01-05"),      # month dd, yyyy
        ("5 January 2020", "2020-01-05"),       # dd month yyyy
        ("5th January 2020", "2020-01-05"),     # ddth month yyyy
        ("5 gennaio 2020", "2020-01-05"),       # dd month-it yyyy,
        ("12 Octber 2022", "2022-10-12"),       # typo
        ("1 Jaunary 2021", "2021-01-01"),       # typo
        (None, None),                           # Edge case: None
        ('not a date', None),                   # Edge case: Not a date
    ],
)
def test_format_date_to_iso(date, expected):
    assert format_date_to_iso(date) == expected


# --- extract_date_from_title ---
@pytest.mark.parametrize(
    "title, expected",
    [
        ("Angelus (Rome, January 5, 2020)", "January 5, 2020"),
        ("Homily (Rome, 5 January 2020)", "5 January 2020"),
        ("Homily (5 January 2020)", "5 January 2020"),
        ("Angelus no date", None),
        ("Homily bad format (Jan 2020)", None),
    ]
)
def test_extract_date_from_title(title, expected):
    assert extract_date_from_title(title) == expected
