# ----------------------
# :: IMPORTS ::
# ----------------------
import pytest
from dc26_vatican_explorer.data_cleaning.cleaning_pipeline import clean_dates, rearrange_pope_data
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