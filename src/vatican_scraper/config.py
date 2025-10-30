from pathlib import Path

_BASE = "https://www.vatican.va/"
_POPE_INDEX_RECENT_URL = "https://www.vatican.va/holy_father/index.htm"

_PKG_DIR = Path(__file__).resolve().parent  # .../src/vatican_scraper
_DB_PATH = _PKG_DIR / ".." / "data" / "vatican_speeches.db"