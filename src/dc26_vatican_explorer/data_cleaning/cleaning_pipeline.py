"""
PLACEHOLDER
"""

# ----------------------
# :: IMPORTS ::
# ----------------------
from .query_speeches import fetch_speech_metadata
from . import date_cleaning
from pathlib import Path

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def clean_dates(raw_data:list[dict]) -> dict:
    """
    placeholder
    """
    popes_data = {}
    for row in raw_data:
        pope_name = row['pope_name']
        if pope_name not in popes_data:
            pontificate_began = date_cleaning.format_pontificate_date(row['pontificate_begin'])
            popes_data[pope_name] = {
                'pope_name': pope_name,
                'papacy_began': pontificate_began,
                'texts': []
            }
        pontificate_began = popes_data[pope_name]['papacy_began']
        # reformat dates
        if row['date'] is not None:
            new_date = date_cleaning.format_date_to_iso(row['date'])
        else:
            date_from_title = date_cleaning.extract_date_from_title(row['title'])
            new_date = date_cleaning.format_date_to_iso(date_from_title)
        # validate: if speech given before papacy began, try to extract again
        if new_date and new_date < pontificate_began:
            date_from_title = date_cleaning.extract_date_from_title(row['title'])
            candidate_date = date_cleaning.format_date_to_iso(date_from_title)
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

def rearrange_pope_data(popes_data):
    for pdata in popes_data.values():
        pdata['texts'].sort(key=lambda x: (x['date'] is None, x['date']))
    return popes_data

def get_clean_speech_metadata(db_path):
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