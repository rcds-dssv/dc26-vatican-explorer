# ----------------------
# :: IMPORTS ::
# ----------------------
import pytest
import sqlite3
from dc26_vatican_explorer.data_cleaning.cleaning_pipeline import (
    clean_dates,
    rearrange_pope_data,
    get_clean_speech_metadata
)
from dc26_vatican_explorer.data_cleaning.query_speeches import fetch_speech_metadata
from dc26_vatican_explorer.data_cleaning.data_objects import Pope, Speech

# ----------------------
# :: TESTS ::
# ----------------------
@pytest.fixture
def sample_raw_data():
    """Provides a mix of standard, messy, and 'impossible' dates."""
    return [
        # Standard case
        {
            "pope_name": "Francis",
            "title": "Standard Speech",
            "date": "January 5, 2020",
            "section": "Angelus",
            "pontificate_begin": "01,13.III.2013"
        },
        # Date is None, must extract from title
        {
            "pope_name": "Francis",
            "title": "Speech from Title (10 January 2020)",
            "date": None,
            "section": "Homily",
            "pontificate_begin": "01,13.III.2013"
        },
        # Conflict: Date is before papacy began, but title has the correct one
        {
            "pope_name": "Benedict XVI",
            "title": "Correct Date in Title (15 April 2005)",
            "date": "10 January 1990", # Previous error
            "section": "Message",
            "pontificate_begin": "01,19.IV.2005"
        }
    ]


# -- clean date from dictionary --
def test_clean_dates_logic(sample_raw_data):
    # Execute
    result = clean_dates(sample_raw_data)

    # Verify Structure
    assert "Francis" in result
    assert "Benedict XVI" in result
    
    # Verify Date Extraction from Title
    francis_texts = result["Francis"].texts
    # The one with None date should now have "2020-01-10"
    assert any(t.date == "2020-01-10" for t in francis_texts)

    # Verify Validation Logic (The "Candidate Date" check)
    benedict_texts = result["Benedict XVI"].texts
    # 1990 is before 2005, so it should have tried the title and found April 15
    assert benedict_texts[0].date == "2005-04-15"

# --  sorting by date --
def test_rearrange_pope_data_sorting():
    # Setup out-of-order data
    unsorted = {
        "Francis": Pope(
            pope_name='Francis',
            papacy_began='somewhen',
            texts=[
                Speech(date="2023-01-01", title="Newer", category='Homily'),
                Speech(date="2020-01-01", title="Older", category='Homily'),
                Speech(date=None, title="Unknown", category='Homily')
            ]
        )
    }
    
    sorted_data = rearrange_pope_data(unsorted)
    dates = [t.date for t in sorted_data["Francis"].texts]
    
    # Expected order: Oldest first, Nones at the end
    assert dates == ["2020-01-01", "2023-01-01", None]


# -- speech text inclusion and filtering --
def test_clean_dates_with_text_inclusion(sample_raw_data):
    # Add text content to sample raw data
    for item in sample_raw_data:
        item["text_content"] = "This is a test speech content."
    
    # Execute with include_text=True
    result = clean_dates(sample_raw_data, include_text=True)
    
    # Verify text is populated
    francis_texts = result["Francis"].texts
    assert all(t.text_content == "This is a test speech content." for t in francis_texts)
    return


def test_clean_dates_without_text_inclusion(sample_raw_data):
    # Add text content to sample raw data
    for item in sample_raw_data:
        item["text_content"] = "This is a test speech content."
    
    # Execute with include_text=False
    result = clean_dates(sample_raw_data, include_text=False)
    
    # Verify text is not populated (should be None)
    francis_texts = result["Francis"].texts
    assert all(t.text_content is None for t in francis_texts)
    return


# def test_fetch_speech_metadata_options(tmp_path):
#     # Setup test DB
#     db_path = tmp_path / "test_speeches.db"
#     with sqlite3.connect(db_path) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE popes (
#                 _pope_id INTEGER PRIMARY KEY,
#                 pope_name TEXT,
#                 pontificate_begin TEXT
#             );
#         """)
#         cursor.execute("""
#             CREATE TABLE texts (
#                 _texts_id INTEGER PRIMARY KEY,
#                 pope_id INTEGER,
#                 title TEXT,
#                 date TEXT,
#                 section TEXT,
#                 text_content TEXT
#             );
#         """)
        
#         # Insert Popes
#         cursor.execute("INSERT INTO popes VALUES (1, 'Francis', '01,13.III.2013')")
#         cursor.execute("INSERT INTO popes VALUES (2, 'Benedict XVI', '01,19.IV.2005')")
        
#         # Insert Texts
#         cursor.execute("INSERT INTO texts VALUES (1, 1, 'Francis Speech 1', 'January 5, 2020', 'Angelus', 'Text of Francis Speech 1')")
#         cursor.execute("INSERT INTO texts VALUES (2, 1, 'Francis Speech 2', 'January 10, 2020', 'Homily', 'Text of Francis Speech 2')")
#         cursor.execute("INSERT INTO texts VALUES (3, 2, 'Benedict Speech 1', 'April 15, 2005', 'Message', 'Text of Benedict Speech 1')")
#         conn.commit()

#     # 1. Test basic fetch metadata without text
#     results = fetch_speech_metadata(db_path)
#     assert len(results) == 3
#     assert "text_content" not in results[0]
    
#     # 2. Test fetch with text inclusion
#     results_with_text = fetch_speech_metadata(db_path, include_text=True)
#     assert len(results_with_text) == 3
#     # Benedict before Francis (sorted by pontificate_begin, t.date)
#     assert results_with_text[0]["text_content"] == "Text of Benedict Speech 1"
    
#     # 3. Test filtering by Pope name
#     results_francis = fetch_speech_metadata(db_path, pope_name="Francis")
#     assert len(results_francis) == 2
#     assert all(r["pope_name"] == "Francis" for r in results_francis)
    
#     # 4. Test limiting
#     results_limit = fetch_speech_metadata(db_path, limit=1)
#     assert len(results_limit) == 1
    
#     # 5. Test pipeline integration with text
#     pipeline_res = get_clean_speech_metadata(db_path, include_text=True)
#     assert "Francis" in pipeline_res
#     assert "Benedict XVI" in pipeline_res
#     assert pipeline_res["Francis"].texts[0].text_content == "Text of Francis Speech 1"
#     return