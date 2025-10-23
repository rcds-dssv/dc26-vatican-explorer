# step01_list_popes.py
from __future__ import annotations

import random
import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse


import requests
from bs4 import BeautifulSoup

POPE_INDEX_RECENT_URL = "https://www.vatican.va/holy_father/index.htm"
BASE = "https://www.vatican.va/"

# -------------------- tiny courtesy pause --------------------

def _papal_pause(min_s: float = 0.4, max_s: float = 1.2) -> None:
    """Sleep a small random amount to be polite."""
    time.sleep(random.uniform(min_s, max_s))

# -------------------- name/URL utilities --------------------

_ROMAN_RE = re.compile(r"^[IVXLCDM]+$", re.IGNORECASE)
_TITLE_RE = re.compile(r"^[A-Z][a-z]+$")

def _is_roman(token: str) -> bool:
    return bool(_ROMAN_RE.match(token or ""))

def _is_titlecase_word(token: str) -> bool:
    return bool(_TITLE_RE.match(token or ""))

def papal_normalize_display_name(text: str) -> str:
    """Collapse whitespace and trim display names."""
    return re.sub(r"\s+", " ", (text or "").strip())

def _looks_like_pope_display(name: str) -> bool:
    """
    Accept:
      - Single Title-case word (e.g., 'Francis')
      - N>=2 words where the last word is a Roman numeral
        and all preceding words are Title-case (e.g., 'John Paul II', 'Paul VI', 'John XXIII', 'Leo XIII').
    Reject everything else (e.g., 'ROMAN CURIA', 'Roman Curia', etc.).
    """
    name = papal_normalize_display_name(name)
    if not name:
        return False

    parts = name.split(" ")
    if len(parts) == 1:
        return _is_titlecase_word(parts[0])  # 'Francis'
    # last token must be roman numerals
    if not _is_roman(parts[-1]):
        return False
    # all preceding tokens must be Title-case words
    return all(_is_titlecase_word(p) for p in parts[:-1])

def papal_extract_slug_from_content_url(url: str) -> Optional[str]:
    """
    From URLs like:
      https://www.vatican.va/content/francesco/en.html -> 'francesco'
      https://www.vatican.va/content/john-paul-i/en.htm -> 'john-paul-i'
    """
    try:
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "content":
            return parts[1]
    except Exception:
        pass
    return None

# -------------------- core scraping --------------------

def _papal_collect_english_content_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Find anchors pointing to /content/<slug>/(en.html|en.htm),
    keep only those whose visible text looks like a papal name.
    Return [{'display_name','slug','url'}, ...].
    """
    items: List[Dict[str, str]] = []

    # More targeted selection within the main content area if present
    candidates = soup.select(
        "#corpo a[href*='/content/'][href$='en.html'], "
        "#corpo a[href*='/content/'][href$='en.htm']"
    )
    if not candidates:
        # Fallback if the page structure changes
        candidates = soup.find_all("a", href=True)

    for a in candidates:
        href = a.get("href", "")
        if "/content/" not in href:
            continue
        if not (href.endswith("en.html") or href.endswith("en.htm")):
            continue

        raw_name = a.get_text(strip=True)
        name = papal_normalize_display_name(raw_name)
        if not _looks_like_pope_display(name):
            continue  # filter out ROMAN CURIA and other non-papal entries

        url = urljoin(BASE, href)
        slug = papal_extract_slug_from_content_url(url)
        if not slug:
            continue

        items.append({"display_name": name, "slug": slug, "url": url})

    # Deduplicate by slug, preserving first occurrence
    seen, out = set(), []
    for it in items:
        if it["slug"] not in seen:
            seen.add(it["slug"])
            out.append(it)
    return out

# -------------------- public helpers (task-specific names) --------------------

def vatican_fetch_pope_directory_recent() -> List[Dict[str, str]]:
    """
    Scrape recent/current popes from https://www.vatican.va/holy_father/index.htm.
    Returns dicts: {'display_name', 'slug', 'url'} where 'url' is the English landing page
    (e.g., https://www.vatican.va/content/francesco/en.html).
    """
    _papal_pause()
    r = requests.get(POPE_INDEX_RECENT_URL, timeout=30)
    r.raise_for_status()
    _papal_pause()

    soup = BeautifulSoup(r.text, "html.parser")
    results = _papal_collect_english_content_links(soup)
    return results

def papal_find_by_display_name(popes: List[Dict[str, str]], name: str) -> Optional[Dict[str, str]]:
    """
    Case-insensitive exact match on display_name.
    Example: papal_find_by_display_name(popes, "Leo XIV") -> {...}
    """
    key = papal_normalize_display_name(name).lower()
    for p in popes:
        if papal_normalize_display_name(p["display_name"]).lower() == key:
            return p
    return None

# -------------------- optional quick test --------------------

if __name__ == "__main__":
    popes = vatican_fetch_pope_directory_recent()
    print(f"Found {len(popes)} entries")
    for d in popes:
        print(" -", d)