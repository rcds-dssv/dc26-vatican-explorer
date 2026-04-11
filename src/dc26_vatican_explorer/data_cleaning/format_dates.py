"""
Date transformation utilities for Vatican text metadata.

This module provides functions to parse non-standard historical date formats
and normalize them into ISO 8601 strings.
"""

# ----------------------
# :: IMPORTS ::
# ----------------------
import re
from dateutil import parser as date_parser
from pathlib import Path
from datetime import datetime

# ----------------------
# :: GLOBAL CONSTANTS ::
# ----------------------
MONTH_MAP = {
    "gennaio": "January", "febbraio": "February", "marzo": "March", "aprile": "April",
    "maggio": "May", "giugno": "June", "luglio": "July", "agosto": "August",
    "settembre": "September", "ottobre": "October", "novembre": "November", "dicembre": "December",
    # also adding others that are typos or other languages:
    "agoo": "August", "Octber": "October", "Jaunary": "January", "Septembre": "September",
    "octobre": "October", "Novembrer": "November", "Febraury": "February"
}
MONTH_MAP = {k.lower():v.lower() for k, v in MONTH_MAP.items()}

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def format_pontificate_date(date_old_format:str) -> str | None:
    """
    Converts a papal election date from custom format to ISO.

    Args:
        date_old_format (str): String in format 'DD,HH.MMM.YYYY', where months are in Roman (e.g., '01,11.VII.2020').

    Returns:
        A date string in 'YYYY-MM-DD' format.
    """
    roman_map = {
        'I':'01', 'II':'02', 'III':'03', 'IV':'04', 'V':'05', 'VI':'06',
        'VII':'07', 'VIII':'08', 'IX':'09', 'X':'10', 'XI':'11', 'XII':'12'
    }
    date_parts = date_old_format.split(',')
    day = date_parts[0].zfill(2)
    month, year = date_parts[1].split('.')[1:]
    month = roman_map[month]
    new_date = f"{year}-{month}-{day}"
    return new_date

def format_date_to_iso(date:str) -> str | None:
    """
    Normalizes various date formats into ISO 8601 (YYYY-MM-DD).
    Supports: (Month DD, YYYY) OR (DD Month YYYY) OR (DD[nd, rd, st] Month YYYY)
    
    Args:
        date (str): A date string (e.g., 'June 14, 2014' or '14 giugno 2014').
        
    Returns:
        A string in YYYY-MM-DD format, or None if parsing fails or the year is missing.
    """
    # STEP 0 - date is none
    if date is None:
        return date
    
    # normalize
    date = date.lower()
    
    # STEP 1 - translate month
    for it_month, eng_month in MONTH_MAP.items():
        if it_month in date:
            date = date.replace(it_month, eng_month)
    
    # STEP 2 - try parser
    default_date = datetime(1, 1, 1)
    try:
        new_date = date_parser.parse(date, default=default_date, fuzzy=False)
        if new_date.year == 1:
            return None
        else:
            return new_date.strftime("%Y-%m-%d")
    except (date_parser.ParserError, ValueError) as e:
        return None

def extract_date_from_title(sentence:str) -> str | None:
    """
    Extracts a date string found within trailing parentheses of a title.
    Supports: (Month DD, YYYY) OR (DD Month YYYY) OR (DD[nd, rd, st] Month YYYY)

    Args:
        sentence (str): The full title of the text.

    Returns:
        The extracted date substring if a match is found, otherwise None.
    """
    if sentence is None:
        return None
    # pattern = r"\((?:.*,\s+)?([A-Z][a-z]+ \d{1,2}, \d{4}|\d{1,2}(?:st|nd|rd|th)? [A-Z][a-z]+ \d{4})\)$"
    pattern = r"""
        \(                # opening parenthesis
        (?:.*,\s+)?       # optional location and comma
        (                 # start capture group for date
            \w+\s+\d{1,2},\s+\d{4}     # Month DD, YYYY
            |                                  # OR
            \d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4} # DD Month YYYY
        )                 # end capture group
        \)                # closing parenthesis
        $                 # end of line
    """
    match = re.search(pattern, sentence.strip(), re.IGNORECASE | re.VERBOSE)
    if match:
        return match.group(1)  # returns the content inside the parentheses
    return None

# ----------------------
# :: MAIN ENTRYPOINT ::
# ----------------------
def main():
    base_path = Path('src/dc26_vatican_explorer/data_cleaning/playground')

    # test papacy dates
    papacy_date_test = '01,11.VII.2020'
    print(f"Papacy date old: {papacy_date_test}\nPapacy date new: {format_pontificate_date(papacy_date_test)}\n")

    # test date from title
    test_titles_path = base_path / 'test_titles.txt'
    with test_titles_path.open('r') as f:
        for ttl in f.readlines():
            tdt = extract_date_from_title(ttl)
            print(tdt)
            print(format_date_to_iso(tdt), '\n')
    
    # test other dates
    test_dates_path = base_path / 'test_dates.txt'
    with test_dates_path.open('r') as f:
        for tdt in f.readlines():
            print(tdt.rstrip('\n'))
            print(format_date_to_iso(tdt), '\n')
    return

if __name__ == "__main__":
    main()