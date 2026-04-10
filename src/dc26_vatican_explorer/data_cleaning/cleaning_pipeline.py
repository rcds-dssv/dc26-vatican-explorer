"""
Pipeline for loading and validating Vatican speech metadata.

This module connects database retrieval with date formatting and applies
historical validation logic to ensure data integrity.
"""

# ----------------------
# :: IMPORTS ::
# ----------------------
from .query_speeches import fetch_speech_metadata
from . import format_dates
from pathlib import Path

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def clean_dates(raw_data:list[dict]) -> dict:
    """
    Groups speeches by Pope and applies date normalization and validation.

    Args:
        raw_data(list of dict): List of raw dictionaries fetched from the database.

    Returns:
        A dictionary keyed by pope name, containing cleaned speech metadata.
    
    TODO: clean this up:
    popes_data is a dict that looks like this:
    {
        "<pope_name>": {"pope_name": str,
                        "papacy_began": str,
                        "texts": [{ "title": str,
                                    "date": str | date,
                                    "category": str}, ...]
        },...}
    """
    popes_data = {}
    for row in raw_data:
        pope_name = row['pope_name']
        if pope_name not in popes_data:
            pontificate_began = format_dates.format_pontificate_date(row['pontificate_begin'])
            popes_data[pope_name] = {
                'pope_name': pope_name,
                'papacy_began': pontificate_began,
                'texts': []
            }
        pontificate_began = popes_data[pope_name]['papacy_began']
        # reformat dates
        if row['date'] is not None:
            new_date = format_dates.format_date_to_iso(row['date'])
        else:
            date_from_title = format_dates.extract_date_from_title(row['title'])
            new_date = format_dates.format_date_to_iso(date_from_title)
        # validate: if speech given before papacy began, try to extract again
        if new_date and new_date < pontificate_began:
            date_from_title = format_dates.extract_date_from_title(row['title'])
            candidate_date = format_dates.format_date_to_iso(date_from_title)
            if candidate_date and candidate_date >= pontificate_began:
                new_date = candidate_date
            else:
                new_date = None
        # fill in dictionary
        popes_data[pope_name]['texts'].append({
            'title': row["title"],
            'date': new_date,
            'category': row['section']
        })
    return popes_data

def rearrange_pope_data(popes_data:dict) -> dict:
    """
    Sorts each Pope's texts chronologically, placing unknown dates at the end.

    Args:
        popes_data (dict): The nested dictionary of pope and speech data.

    Returns:
        The dictionary with sorted text lists.
    """
    for pdata in popes_data.values():
        pdata['texts'].sort(key=lambda x: (x['date'] is None, x['date']))
    return popes_data

def get_clean_speech_metadata(db_path: str | Path) -> dict:
    """
    Executes the full loading and cleaning pipeline.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        The fully processed and sorted pope metadata dictionary.
    """
    raw_data = fetch_speech_metadata(db_path)
    pope_speech_metadata = clean_dates(raw_data)
    pope_speech_metadata = rearrange_pope_data(pope_speech_metadata)
    return pope_speech_metadata

def write_dates(popes_data, file_path):
    # create a file with all dates for easy debugging
    with open(file_path, 'w') as f:
        for pontiff, pontiff_data in popes_data.items():
            f.write(f"<<{pontiff}>>:\n\n")
            for text in pontiff_data['texts']:
                if text['date']:
                    f.write(text['date'] + '\n')
                else:
                    f.write('NONE FOUND\n')
            f.write('\n\n\n')
    return

# ----------------------
# :: MAIN ENTRYPOINT ::
# ----------------------

def main():
    write_for_debug = 0
    db_path = Path('data/vatican_texts.db')
    # load raw data
    raw_data = fetch_speech_metadata(db_path)
    # clean the data
    pope_speech_metadata = clean_dates(raw_data)
    pope_speech_metadata = rearrange_pope_data(pope_speech_metadata)
    print(pope_speech_metadata['Francis']['texts'][465])
    # write dates to file for debugging
    if write_for_debug:
        dates_file_path = Path('src/dc26_vatican_explorer/data_cleaning/playground/reformatted_dates.txt')
        write_dates(pope_speech_metadata, dates_file_path)
    return

if __name__ == "__main__":
    main()