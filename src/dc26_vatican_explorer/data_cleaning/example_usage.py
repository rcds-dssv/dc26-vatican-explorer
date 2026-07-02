from dc26_vatican_explorer import get_clean_speech_metadata
from pathlib import Path

db_path = Path('data/vatican_texts.db')
pope_speech_metadata = get_clean_speech_metadata(db_path)
print(pope_speech_metadata['Francis'].texts[465])