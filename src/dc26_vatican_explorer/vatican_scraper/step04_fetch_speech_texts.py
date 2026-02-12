# src/vatican_scraper/step04_fetch_speech_texts.py
from __future__ import annotations

import hashlib
import random
import re
import time
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString

from vatican_scraper.argparser import get_scraper_args
from config import _PKG_DIR, _DB_PATH
from vatican_scraper.database_utils.database_helpers import speech_url_exists_in_db

_SCRAPER_DIR = _PKG_DIR / "vatican_scaper"

try:
    import pandas as pd
except ImportError as e:
    raise SystemExit(
        "pandas is required. Install with: pip install pandas pyarrow"
    ) from e


from vatican_scraper.step01_list_popes import (
    vatican_fetch_pope_directory_recent,
    papal_find_by_display_name,
)
from vatican_scraper.step02_list_pope_year_links import (
    parse_years,
    fetch_pope_main_html,
    extract_year_links_from_main,
    extract_available_years_from_main,
    extract_pope_metadata_from_main,
    _sanitize_section,
)
from vatican_scraper.step03_list_speeches import extract_speeches_from_year_index


def _pause(min_s: float = 0.35, max_s: float = 1.1) -> None:
    time.sleep(random.uniform(min_s, max_s))


def fetch_html(url: str) -> str:
    _pause()
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    enc = (r.encoding or "").lower()
    if not enc or "8859" in enc or enc == "ascii":
        r.encoding = r.apparent_encoding or "utf-8"
    _pause()
    return r.text


def _maybe_fix_mojibake(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = s.replace("\xa0", " ")
    if "â" in s or "Ã" in s or "Â" in s:
        try:
            repaired = s.encode("latin1", errors="ignore").decode(
                "utf-8", errors="ignore"
            )
            if repaired and (repaired.count("�") <= s.count("�")):
                return repaired
        except Exception:
            pass
    return s


def _txt(el, sep: str = " ") -> Optional[str]:
    return el.get_text(sep, strip=True) if el is not None else None


_HAS_YEAR = re.compile(r"\b(19|20)\d{2}\b")


def _split_lines_on_br(el) -> List[str]:
    if el is None:
        return []
    has_br = el.find("br") is not None
    text = el.get_text("\n", strip=True)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines if has_br else ([text] if text else [])


def _clean(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = _maybe_fix_mojibake(s).replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip(" ,;·:—–-")
    return s or None


def _looks_reasonable_place(s: Optional[str]) -> bool:
    if not s:
        return False
    if sum(ch.isalpha() for ch in s) < 3 or len(s) > 120:
        return False
    if _HAS_YEAR.search(s):
        return False
    return True


def _find_location_in_abstract(soup: BeautifulSoup, debug: bool) -> Optional[str]:
    abstract = soup.select_one(".abstract")
    if not abstract:
        return None
    for p in abstract.find_all("p", recursive=False):
        lines = _split_lines_on_br(p)
        if debug:
            print(f"[loc:abstract] lines={lines!r}")
        if len(lines) >= 2 and _HAS_YEAR.search(lines[1]):
            loc = _clean(lines[0])
            if _looks_reasonable_place(loc):
                return loc
    return None


def _find_location_in_font_block(soup: BeautifulSoup, debug: bool) -> Optional[str]:
    for font in soup.select("div.text:nth-of-type(3) > font"):
        ps = font.find_all("p", recursive=False)
        for i, p in enumerate(ps):
            if i == 0:
                continue
            lines = _split_lines_on_br(p)
            if debug:
                print(f"[loc:font] p{i + 1} lines={lines!r}")
            if len(lines) >= 2 and _HAS_YEAR.search(lines[1]):
                loc = _clean(lines[0])
                if _looks_reasonable_place(loc):
                    return loc
    return None


def _find_location_in_text_block(soup: BeautifulSoup, debug: bool) -> Optional[str]:
    block = soup.select_one("div.text:nth-of-type(3)")
    if not block:
        return None
    ps = block.find_all("p", recursive=False)
    for i, p in enumerate(ps):
        if i == 0:
            continue
        lines = _split_lines_on_br(p)
        if debug:
            print(f"[loc:text3] p{i + 1} lines={lines!r}")
        if len(lines) >= 2 and _HAS_YEAR.search(lines[1]):
            loc = _clean(lines[0])
            if _looks_reasonable_place(loc):
                return loc
    return None


def _extract_location(soup: BeautifulSoup, debug: bool = False) -> Optional[str]:
    for fn in (
        _find_location_in_abstract,
        _find_location_in_font_block,
        _find_location_in_text_block,
    ):
        loc = fn(soup, debug)
        if loc:
            return loc
    return None


def _text_after_multimedia(text_el) -> Optional[str]:
    if text_el is None:
        return None
    a = text_el.select_one('a[href*="/content/vaticanevents/"]')
    if not a:
        return None
    node = a
    while node and node.parent is not None and node.parent != text_el:
        node = node.parent
    if node is None or node.parent != text_el:
        return None
    parts: List[str] = []
    for sib in node.next_siblings:
        if isinstance(sib, NavigableString):
            s = str(sib).strip()
            if s:
                parts.append(s)
        else:
            s = sib.get_text("\n", strip=True)
            if s:
                parts.append(s)
    out = "\n".join(p for p in parts if p).strip()
    return out or None


def extract_location_and_text(
    speech_html: str, debug_loc: bool = False
) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(speech_html, "html.parser")
    location = _extract_location(soup, debug=debug_loc)
    text_el = soup.select_one("div.text:nth-of-type(3)") or soup.select_one("div.text")
    text = _text_after_multimedia(text_el) or (
        text_el.get_text("\n", strip=True) if text_el else None
    )
    text = _maybe_fix_mojibake(text)
    return {"location": location, "text": text}


def find_translation_url(
    speech_html: str, speech_url: str, want_lang: str
) -> Optional[str]:
    soup = BeautifulSoup(speech_html, "html.parser")
    want = want_lang.strip().upper()
    for a in soup.select(".translation a[href]"):
        code = a.get_text(" ", strip=True).upper()
        if code == want:
            return urljoin(speech_url, a["href"])
    return None


_DATE_RE = re.compile(r"\b(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})\b")
_MONTHS_EN = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12",
}


def _normalize_date_yyyymmdd(date_text: Optional[str]) -> str:
    if not date_text:
        return "unknown"
    m = _DATE_RE.search(date_text)
    if not m:
        return "unknown"
    d, month, y = m.group(1), m.group(2), m.group(3)
    mm = _MONTHS_EN.get(month, "00")
    dd = d.zfill(2)
    return f"{y}{mm}{dd}"


def _slugify(text: str, maxlen: int = 40) -> str:
    text = (
        unicodedata.normalize("NFKD", text or "")
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text or "untitled")[:maxlen].rstrip("-")


def make_speech_id(
    pope_slug: str,
    section: str,
    date_text: Optional[str],
    title: Optional[str],
    url: str,
) -> str:
    ymd = _normalize_date_yyyymmdd(date_text)
    title_slug = _slugify(title or "")
    short = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    return f"{pope_slug}-{section}-{ymd}-{title_slug}-{short}"


def fetch_speeches_to_feather(
    pope: str,
    years_spec: str,
    lang: str = "EN",
    section: str = "angelus",
    out: Optional[str] = None,
    debug_loc: bool = False,
    max_n_speeches: int = None,
    save_to_file: bool = False,
) -> Tuple[Optional[Path], List[Dict[str, Optional[str]]]]:

    want_lang = lang.strip().upper()
    if not (len(want_lang) == 2 and want_lang.isalpha()):
        raise SystemExit(f"Bad --lang value: {lang}")

    section = _sanitize_section(section)
    years = set(parse_years(years_spec))
    if not years:
        raise SystemExit("No valid years parsed from --years.")

    popes = vatican_fetch_pope_directory_recent()
    rec = papal_find_by_display_name(popes, pope)
    if not rec:
        avail = ", ".join(p["display_name"] for p in popes)
        raise SystemExit(f'Pope "{pope}" not found. Available: {avail}')

    main_html = fetch_pope_main_html(rec["url"])
    pope_meta = extract_pope_metadata_from_main(main_html) or {}

    year_rows = extract_year_links_from_main(main_html, rec["slug"], years, section)
    if not year_rows:
        available = extract_available_years_from_main(main_html, rec["slug"], section)
        req_str = ", ".join(map(str, sorted(years)))
        avail_str = ", ".join(map(str, available)) if available else "none yet"
        raise SystemExit(
            f"No {section} year index pages found for {pope} in requested years [{req_str}]. "
            f"Available on page: {avail_str}."
        )

    rows: List[Dict[str, Optional[str]]] = []
    for row in year_rows:
        year = row["year"]
        idx_url = row["url"]
        idx_html = fetch_html(idx_url)
        speeches = extract_speeches_from_year_index(
            idx_html, idx_url, rec["slug"], section
        )
        if not speeches:
            continue
        if max_n_speeches is None:
            max_n_speeches = len(speeches)
        for si, s in enumerate(speeches):
            if si >= max_n_speeches:
                break

            base_url = s["url"]
            if speech_url_exists_in_db(_DB_PATH, base_url):
                print(f"[skip] Content already in database (by url): {base_url}")
                continue

            print(f"Fetching content from : {base_url}")

            base_html = fetch_html(base_url)
            final_url = base_url
            final_html = base_html
            served_lang = "EN"
            if want_lang != "EN":
                tr_url = find_translation_url(base_html, base_url, want_lang)
                if tr_url:
                    final_url = tr_url
                    final_html = fetch_html(tr_url)
                    served_lang = want_lang

            parsed = extract_location_and_text(
                final_html if served_lang == want_lang else base_html,
                debug_loc=debug_loc,
            )
            title_clean = _maybe_fix_mojibake(s.get("title"))
            text_value = (
                parsed.get("text")
                if served_lang == want_lang
                else "Not available in the requested language."
            )

            rows.append(
                {
                    "speech_id": make_speech_id(
                        rec["slug"], section, s.get("date"), title_clean, final_url
                    ),
                    "pope": rec["display_name"],
                    "pope_slug": rec["slug"],
                    "section": section,
                    "year": year,
                    "pope_number": pope_meta.get("pope_number"),
                    "pontificate_begin": pope_meta.get("pontificate_begin"),
                    "pontificate_end": pope_meta.get("pontificate_end"),
                    "secular_name": pope_meta.get("secular_name"),
                    "place_of_birth": pope_meta.get("place_of_birth"),
                    "date": s.get("date"),
                    "title": title_clean,
                    "lang_requested": want_lang,
                    "lang_available": served_lang if served_lang == want_lang else None,
                    "url": final_url if served_lang == want_lang else base_url,
                    "location": parsed.get("location"),
                    "text": text_value,
                }
            )

    if not rows:
        raise SystemExit("No speeches collected for the given filters.")

    out_path = None
    if save_to_file:
        df = pd.DataFrame.from_records(rows)

        base_dir = _SCRAPER_DIR / "scrape_result"
        print(base_dir)
        base_dir.mkdir(parents=True, exist_ok=True)

        if out:
            out_path = base_dir / Path(out).name
        else:
            years_sorted = sorted(int(y["year"]) for y in year_rows)
            yr_span = (
                f"{years_sorted[0]}-{years_sorted[-1]}"
                if len(set(years_sorted)) > 1
                else f"{years_sorted[0]}"
            )
            out_path = (
                base_dir
                / f"speeches_{rec['slug']}_{section}_{want_lang}_{yr_span}.feather"
            )

        try:
            df.to_feather(out_path)
        except Exception as e:
            if "pyarrow" in str(e).lower():
                raise SystemExit(
                    "Writing Feather requires pyarrow. Install with: pip install pyarrow"
                ) from e
            raise

        print(f"Wrote {len(df):,} rows to {out_path}")

    return out_path, rows


def main() -> None:
    p, args = get_scraper_args()

    # note that this will only take the first pope, since pope is now a list
    fetch_speeches_to_feather(
        pope=args.pope,
        years_spec=args.years,
        lang=args.lang,
        section=args.section,
        out=args.out,
        debug_loc=args.debug_loc,
    )


if __name__ == "__main__":
    main()
