"""
Pipeline for loading and validating Vatican speech metadata.

This module connects database retrieval with date formatting and applies
historical validation logic to ensure data integrity.
"""

# ----------------------
# :: IMPORTS ::
# ----------------------
# local
from dc26_vatican_explorer.data_cleaning.query_speeches import fetch_speech_metadata
from dc26_vatican_explorer.data_cleaning import format_dates
from dc26_vatican_explorer.data_cleaning.data_objects import Speech, Pope

# other
from pathlib import Path

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def clean_dates(raw_data:list[dict]) -> dict[str, Pope]:
    """
    Groups speeches by Pope and applies date normalization and validation.

    Args:
        raw_data(list of dict): List of raw dictionaries fetched from the database.

    Returns:
        A dictionary of Pope objects, containing cleaned Speech metadata.
    """
    popes_data: dict[str, Pope] = {}

    for row in raw_data:
        pope_name = row['pope_name']
        if pope_name not in popes_data:
            # create Pope
            popes_data[pope_name] = Pope(
                pope_name=pope_name,
                papacy_began=format_dates.format_pontificate_date(row['pontificate_begin']),
            )
        current_pope = popes_data[pope_name]

        # reformat dates
        if row['date'] is not None:
            clean_date = format_dates.format_date_to_iso(row['date'])
        else:
            date_from_title = format_dates.extract_date_from_title(row['title'])
            clean_date = format_dates.format_date_to_iso(date_from_title)
        
        # validate: if speech given before papacy began, try to extract again
        if clean_date and clean_date < current_pope.papacy_began:
            date_from_title = format_dates.extract_date_from_title(row['title'])
            candidate_date = format_dates.format_date_to_iso(date_from_title)
            if candidate_date and candidate_date >= current_pope.papacy_began:
                clean_date = candidate_date
            else:
                clean_date = None
        
        # create Speech
        speech = Speech(
            title=row['title'],
            date=clean_date,
            category=row['section']
        )
        current_pope.texts.append(speech)
    return popes_data

def rearrange_pope_data(popes_data:dict[str,Pope]) -> dict[str,Pope]:
    """
    Sorts each Pope's texts chronologically, placing unknown dates at the end.

    Args:
        popes_data (dict): The nested dictionary of pope and speech data.

    Returns:
        The dictionary with sorted text lists.
    """
    for pdata in popes_data.values():
        pdata.texts.sort(key=lambda x: (x.date is None, x.date))
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
    return

if __name__ == "__main__":
    main()