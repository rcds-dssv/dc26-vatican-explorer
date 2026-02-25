# src/vatican_scraper/step04_fetch_speech_texts.py
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import time
import unicodedata
import difflib
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urldefrag

import requests
from bs4 import BeautifulSoup, NavigableString

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from vatican_scraper.argparser import get_scraper_args
from config import _PKG_DIR, _DB_PATH
from vatican_scraper.db_utils import speech_url_exists_in_db

_SCRAPER_DIR = _PKG_DIR / "vatican_scraper"

try:
    import pandas as pd
except ImportError as e:
    raise SystemExit("pandas is required. Install with: pip install pandas pyarrow") from e



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
from vatican_scraper.step03_list_speeches import collect_speeches_for_year_index

def _pause(min_s: float = 0.35, max_s: float = 1.1) -> None:
    time.sleep(random.uniform(min_s, max_s))

_SESSION = None

def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is not None:
        return _SESSION

    s = requests.Session()
    s.headers.update({
        "User-Agent": "dc26_vatican_explorer/1.0 (+https://www.vatican.va) python-requests"
    })

    retry = Retry(
        total=6,
        connect=6,
        read=6,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    _SESSION = s
    return s


def fetch_html(url: str, *, timeout=(10, 120)) -> str:
    """
    timeout = (connect_timeout_seconds, read_timeout_seconds)
    """
    # light throttling to reduce timeouts / rate-limits
    time.sleep(random.uniform(0.3, 0.9))

    s = _get_session()
    r = s.get(url, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text

def fetch_html_with_final_url(url: str, *, timeout=(10, 120)) -> Tuple[str, str]:
    """
    Like fetch_html, but also returns the final URL after redirects.
    This is critical for language handling because /it/ pages sometimes redirect to /en/.
    """
    time.sleep(random.uniform(0.3, 0.9))
    s = _get_session()
    r = s.get(url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return (r.url, r.text)


def _norm_text_for_compare(t: Optional[str]) -> str:
    if not t:
        return ""
    t = _maybe_fix_mojibake(t)
    t = t.replace("\xa0", " ")
    t = t.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t

DEBUG_LANG = os.getenv("VATICAN_DEBUG_LANG", "0") == "1"

def _snippet(s: Optional[str], n: int = 220) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return (s[:n] + "…") if len(s) > n else s

def _is_effectively_same_text(a: Optional[str], b: Optional[str]) -> bool:
    """
    Language-agnostic: if the 'translated' page is basically the same as the EN page,
    treat it as NOT translated.
    """
    aa = _norm_text_for_compare(a)
    bb = _norm_text_for_compare(b)
    if not aa or not bb:
        return False
    # avoid false positives on tiny pages
    if min(len(aa), len(bb)) < 300:
        return False
    ratio = difflib.SequenceMatcher(None, aa, bb).ratio()
    return ratio >= 0.995

def _maybe_fix_mojibake(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = s.replace("\xa0", " ")
    if "â" in s or "Ã" in s or "Â" in s:
        try:
            repaired = s.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
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
                print(f"[loc:font] p{i+1} lines={lines!r}")
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
            print(f"[loc:text3] p{i+1} lines={lines!r}")
        if len(lines) >= 2 and _HAS_YEAR.search(lines[1]):
            loc = _clean(lines[0])
            if _looks_reasonable_place(loc):
                return loc
    return None

def _extract_location(soup: BeautifulSoup, debug: bool = False) -> Optional[str]:
    for fn in (_find_location_in_abstract, _find_location_in_font_block, _find_location_in_text_block):
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

def extract_links_from_container(container, base_url: str) -> List[str]:
    """
    Extract unique, normalized hrefs from <a> tags within the speech text container.
    """
    links: List[str] = []
    seen: Set[str] = set()

    if container is None:
        return links

    for a in container.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        if href.startswith(("mailto:", "javascript:", "tel:")):
            continue

        abs_url = urljoin(base_url, href)
        abs_url, _ = urldefrag(abs_url)  # drop #fragment

        if abs_url not in seen:
            seen.add(abs_url)
            links.append(abs_url)

    return links


def extract_location_and_text(
    speech_html: str,
    speech_url: str,
    debug_loc: bool = False
) -> Dict[str, Optional[object]]:
    soup = BeautifulSoup(speech_html, "html.parser")
    location = _extract_location(soup, debug=debug_loc)

    text_el = soup.select_one("div.text:nth-of-type(3)") or soup.select_one("div.text")

    embedded_links = extract_links_from_container(text_el, base_url=speech_url)

    text = _text_after_multimedia(text_el) or (text_el.get_text("\n", strip=True) if text_el else None)
    text = _maybe_fix_mojibake(text)

    return {"location": location, "text": text, "embedded_links": embedded_links}

_LANG_IN_URL_RE = re.compile(r"/content/[^/]+/([a-z]{2})(?:/|$)", re.IGNORECASE)

def _lang_from_url(url: str) -> Optional[str]:
    m = _LANG_IN_URL_RE.search(url or "")
    return m.group(1).upper() if m else None

def _lang_from_html(html: str) -> Optional[str]:
    try:
        soup = BeautifulSoup(html, "html.parser")
        h = soup.find("html")
        if h and h.get("lang"):
            return (h.get("lang") or "").split("-")[0].upper()
    except Exception:
        pass
    return None

def _rewrite_lang_in_url(url: str, want_lang: str) -> Optional[str]:
    """
    Turn .../content/<slug>/en/... into .../content/<slug>/<want>/...
    Only rewrites if it matches the Vatican /content/<slug>/<lang>/ pattern.
    """
    want = want_lang.strip().lower()
    m = re.search(r"(/content/[^/]+/)([a-z]{2})(/)", url, flags=re.IGNORECASE)
    if not m:
        return None
    prefix, _cur, slash = m.group(1), m.group(2), m.group(3)
    return re.sub(r"(/content/[^/]+/)([a-z]{2})(/)", rf"\1{want}\3", url, count=1, flags=re.IGNORECASE)

def _looks_like_it(text: str) -> bool:
    """
    Crude heuristic: count common Italian function words in the first chunk of text.
    Avoid external dependencies.
    """
    if not text:
        return False
    t = re.sub(r"\s+", " ", text).lower()
    sample = t[:2000]
    it_words = [" il ", " lo ", " la ", " gli ", " le ", " che ", " e ", " di ", " del ", " della ", " per ", " con ", " non ", " una ", " un "]
    en_words = [" the ", " and ", " to ", " of ", " in ", " for ", " that ", " with ", " not "]
    it_score = sum(sample.count(w) for w in it_words)
    en_score = sum(sample.count(w) for w in en_words)
    # require a minimal signal and that IT beats EN
    return it_score >= 8 and it_score > en_score

def find_translation_url(speech_html: str, speech_url: str, want_lang: str) -> Optional[str]:
    soup = BeautifulSoup(speech_html, "html.parser")
    want = want_lang.strip().upper()

    selectors = ".translation a[href], .lingua a[href], #lingua a[href], .lingue a[href]"
    for a in soup.select(selectors):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        abs_url = urljoin(speech_url, href)
        abs_url, _ = urldefrag(abs_url)
        if _lang_from_url(abs_url) == want:
            return abs_url

    # Fallback: visible code match, but still require URL-lang to match.
    for a in soup.select(selectors):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        code = a.get_text(" ", strip=True).upper()
        if code != want:
            continue
        abs_url = urljoin(speech_url, href)
        abs_url, _ = urldefrag(abs_url)
        if _lang_from_url(abs_url) == want:
            return abs_url

    return None

_DATE_RE = re.compile(r"\b(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})\b")
_MONTHS_EN = {
    "January": "01","February": "02","March": "03","April": "04","May": "05","June": "06",
    "July": "07","August": "08","September": "09","October": "10","November": "11","December": "12",
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
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text or "untitled")[:maxlen].rstrip("-")

def make_speech_id(pope_slug: str, section: str, date_text: Optional[str], title: Optional[str], url: str) -> str:
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
) -> Tuple[Optional[Path], List[Dict[str, Optional[object]]]]:

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

    rows: List[Dict[str, Optional[object]]] = []
    for row in year_rows:
        year = row["year"]
        idx_url = row["url"]
        idx_html = fetch_html(idx_url)
        speeches = collect_speeches_for_year_index(
            idx_html=idx_html,
            idx_url=idx_url,
            pope_slug=rec["slug"],
            section=section,
            year=str(year),
            fetcher=fetch_html,
        )
        if not speeches:
            continue
        if (max_n_speeches is None):
            max_n_speeches = len(speeches)
        for si, s in enumerate(speeches):
            if (si >= max_n_speeches):
                break

            base_url = s["url"]
            base_url, _ = urldefrag(base_url)  # Strip fragment to normalize URL for DB duplicate detection.
            # If we are scraping EN, base_url is the canonical URL.
            # If we are scraping IT, we *guess* the IT URL and skip only if that exists.
            if want_lang == "EN":
                if speech_url_exists_in_db(_DB_PATH, base_url):
                    print(f"[skip] Already in DB (EN url): {base_url}")
                    continue
            else:
                guessed_it = _rewrite_lang_in_url(base_url, want_lang)
                if guessed_it and speech_url_exists_in_db(_DB_PATH, guessed_it):
                    print(f"[skip] Already in DB ({want_lang} url): {guessed_it}")
                    continue

            base_final_url, base_html = fetch_html_with_final_url(base_url)

            if DEBUG_LANG:
                print(f"[base] requested={want_lang} base_url={base_url}")
                print(
                    f"[base] final_url={base_final_url} base_lang={_lang_from_url(base_final_url) or _lang_from_html(base_html) or '??'}")

            # Determine what language the BASE page actually ended up being (usually EN)
            base_lang = _lang_from_url(base_final_url) or _lang_from_html(base_html) or "EN"

            final_url = base_final_url
            final_html = base_html
            served_lang = base_lang

            # Parse base text once so we can detect "fake translations" that are identical to EN
            base_parsed = extract_location_and_text(base_html, speech_url=base_final_url, debug_loc=False)
            base_text_for_compare = base_parsed.get("text")

            if want_lang != base_lang:
                # 1) Try explicit translation links from the base HTML
                tr_url = find_translation_url(base_html, base_final_url, want_lang)

                candidates: List[str] = []
                if tr_url:
                    candidates.append(tr_url)

                # 2) Fallback: deterministic rewrite (/en/ -> /<want>/) based on the FINAL base URL
                guessed = _rewrite_lang_in_url(base_final_url, want_lang)
                if guessed and guessed != base_final_url:
                    candidates.append(guessed)

                # de-dup while preserving order
                seen_c: Set[str] = set()
                candidates = [u for u in candidates if not (u in seen_c or seen_c.add(u))]

                for cand_url in candidates:
                    try:
                        cand_final_url, cand_html = fetch_html_with_final_url(cand_url)
                    except Exception:
                        continue

                    # Must actually land on the requested lang after redirects
                    if _lang_from_url(cand_final_url) != want_lang:
                        continue

                    # If the page declares a language, it must match
                    detected = _lang_from_html(cand_html)
                    if detected is not None and detected != want_lang:
                        continue

                    # Reject "translations" that are essentially the same as the EN/base content
                    cand_parsed = extract_location_and_text(cand_html, speech_url=cand_final_url, debug_loc=False)
                    cand_text_for_compare = cand_parsed.get("text")
                    if _is_effectively_same_text(base_text_for_compare, cand_text_for_compare):
                        continue

                    # Accept candidate
                    final_url = cand_final_url
                    final_html = cand_html
                    served_lang = want_lang
                    break


            title_clean = _maybe_fix_mojibake(s.get("title"))

            html_for_parse = final_html if served_lang == want_lang else base_html
            url_for_parse = final_url if served_lang == want_lang else base_final_url

            parsed = extract_location_and_text(html_for_parse, speech_url=url_for_parse, debug_loc=debug_loc)

            if DEBUG_LANG:
                print(f"[served] served_lang={served_lang} served_url={final_url}")
                print(f"[served] text_snip={_snippet(parsed.get('text'))}")

            text_value = parsed.get("text") if served_lang == want_lang else "Not available in the requested language."
            embedded_links = parsed.get("embedded_links") if served_lang == want_lang else []

            rows.append({
                "speech_id": make_speech_id(rec["slug"], section, s.get("date"), title_clean, final_url),
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
                "url": final_url if served_lang == want_lang else base_final_url,
                "location": parsed.get("location"),
                "text": text_value,
                "embedded_links": embedded_links,
            })



    if not rows:
        raise SystemExit("No speeches collected for the given filters.")

    out_path = None
    if (save_to_file):
        df = pd.DataFrame.from_records(rows)

        base_dir = _SCRAPER_DIR / "scrape_result"
        print(base_dir)
        base_dir.mkdir(parents=True, exist_ok=True)

        if out:
            out_path = base_dir / Path(out).name
        else:
            years_sorted = sorted(int(y["year"]) for y in year_rows)
            yr_span = f"{years_sorted[0]}-{years_sorted[-1]}" if len(set(years_sorted)) > 1 else f"{years_sorted[0]}"
            out_path = base_dir / f"speeches_{rec['slug']}_{section}_{want_lang}_{yr_span}.feather"

        try:
            df.to_feather(out_path)
        except Exception as e:
            if "pyarrow" in str(e).lower():
                raise SystemExit("Writing Feather requires pyarrow. Install with: pip install pyarrow") from e
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
        max_n_speeches=args.max_n_speeches,
    )

if __name__ == "__main__":
    main()


