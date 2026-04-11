# ----------------------
# :: IMPORTS ::
# ----------------------
import pytest
from src.dc26_vatican_explorer.data_cleaning.format_dates import (
    extract_date_from_title, 
    format_date_to_iso
)

# ----------------------
# :: TESTS ::
# ----------------------


# -- normal pipeline --
def test_speech_metadata_to_iso_pipeline():
    # Simulate a raw title from your SQL query
    raw_title = "Homily of His Holiness (Rome, 15 Ottobre 2023)"
    
    # Step 1: Extract
    extracted = extract_date_from_title(raw_title)
    assert extracted == "15 Ottobre 2023"
    
    # Step 2: Convert
    iso_date = format_date_to_iso(extracted)
    
    # Final assertion
    assert iso_date == "2023-10-15"


# -- pipeline with bad title --
@pytest.mark.parametrize(
    "bad_title",
    [
        "Speech without date",
        None,
        "Incomplete date (Oct 2023)"
    ]
)
def test_pipeline_failure_modes(bad_title):
    extracted = extract_date_from_title(bad_title)
    iso_date = format_date_to_iso(extracted)
    assert iso_date is None