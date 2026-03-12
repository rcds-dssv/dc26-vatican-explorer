"""
Docstring Placeholder
TODO:
!! Not perfect, I'm getting a 1986 from Francis (see first one after rearranging).
'To the National Confederation ... on the occasion of ... John Paul II on 14 June 1986 (14 June 2014)'
'date': '1986-06-14'
"""

# ----------------------
# :: IMPORTS ::
# ----------------------
import re
from dateutil import parser as date_parser
from pathlib import Path
from datetime import datetime

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def format_pontificate_date(date_old_format:str):
    """
    Converting from the following format: DD,HH.MMM.YYYY, but months are in roman
    """
    roman_map = {
        'I':'01', 'II':'02', 'III':'03', 'IV':'04', 'V':'05', 'VI':'06',
        'VII':'07', 'VIII':'08', 'IX':'09', 'X':'10', 'XI':'11', 'XII':'12'
    }
    temp = date_old_format.split(',')
    day = temp[0]
    if len(day) == 1:
        day = '0' + day
    month, year = temp[1].split('.')[1:]
    month = roman_map[month]
    new_date = f"{year}-{month}-{day}"
    return new_date

def format_date_to_iso(date:str):
    """
    Turns date from a given format to YYYY-MM-DD
    Supports: (Month DD, YYYY) OR (DD Month YYYY) OR (DD[nd, rd, st] Month YYYY)
    """
    month_map = {
        "gennaio": "January", "febbraio": "February", "marzo": "March", "aprile": "April",
        "maggio": "May", "giugno": "June", "luglio": "July", "agosto": "August",
        "settembre": "September", "ottobre": "October", "novembre": "November", "dicembre": "December",
        # also adding others that are typos or other languages:
        "agoo": "August", "Octber": "October", "Jaunary": "January", "Septembre": "September",
        "octobre": "October", "Novembrer": "November", "Febraury": "February"
    }
    # STEP 0 - date is none
    if date is None:
        return date
    
    # STEP 1 - translate month
    date = date.lower()
    for it_month, eng_month in month_map.items():
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

def extract_date_from_title(sentence:str):
    """
    obtains the date from the end of a sentence.
    Supports: (Month DD, YYYY) OR (DD Month YYYY) OR (DD[nd, rd, st] Month YYYY)
        - TODO: Month characters from [A-Z][a-z], some languages may use others so could change to \w+?
    """
    # pattern = r"\((?:.*,\s+)?([A-Z][a-z]+ \d{1,2}, \d{4}|\d{1,2}(?:st|nd|rd|th)? [A-Z][a-z]+ \d{4})\)$"
    pattern = r"""
        \(                # opening parenthesis
        (?:.*,\s+)?       # optional location and comma
        (                 # start capture group for date
            [A-Z][a-z]+\s+\d{1,2},\s+\d{4}     # Month DD, YYYY
            |                                  # OR
            \d{1,2}(?:st|nd|rd|th)?\s+[A-Z][a-z]+\s+\d{4} # DD Month YYYY
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
    # test papacy dates
    papacy_date_test = '01,11.VII.2020'
    print(f"Papacy date old: {papacy_date_test}\nPapacy date new: {format_pontificate_date(papacy_date_test)}\n")

    # test date from title
    test_titles_path = Path('src/data_cleaning/playground/test_titles.txt')
    with test_titles_path.open('r') as f:
        for ttl in f.readlines():
            tdt = extract_date_from_title(ttl)
            print(tdt)
            print(format_date_to_iso(tdt), '\n')
    
    # test other dates
    test_dates_path = Path('src/data_cleaning/playground/test_dates.txt')
    with test_dates_path.open('r') as f:
        for tdt in f.readlines():
            print(tdt.rstrip('\n'))
            print(format_date_to_iso(tdt), '\n')
    return

if __name__ == "__main__":
    main()