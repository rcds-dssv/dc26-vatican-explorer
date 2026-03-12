# src/vatican_scraper/step02_list_pope_year_links.py
from __future__ import annotations

import sys
from urllib.parse import urljoin
import re
import time
import random
import argparse
import json
from typing import List, Dict, Optional, Set, Pattern

import requests
from bs4 import BeautifulSoup

from config import _BASE

from vatican_scraper.step01_list_popes import (
    vatican_fetch_pope_directory_recent,
    papal_find_by_display_name,
)

def _pause(min_s: float = 0.4, max_s: float = 1.2) -> None:
    time.sleep(random.uniform(min_s, max_s))

def parse_years(spec: str) -> List[int]:
    years: Set[int] = set()
    for part in (p.strip() for p in spec.split(",")):
        if not part:
            continue
        if "-" in part:
            a, b = [x.strip() for x in part.split("-", 1)]
            if a.isdigit() and b.isdigit():
                lo, hi = int(a), int(b)
                if lo > hi:
                    lo, hi = hi, lo
                years.update(range(lo, hi + 1))
        elif part.isdigit():
            years.add(int(part))
    return sorted(years)

def fetch_pope_main_html(pope_url: str) -> str:
    _pause()
    r = requests.get(pope_url, timeout=30)
    r.raise_for_status()
    _pause()
    return r.text

def _txt(el) -> Optional[str]:
    return el.get_text(" ", strip=True) if el else None

def _sanitize_section(section: str) -> str:
    s = (section or "").strip().lower()
    if not re.match(r"^[a-z][a-z0-9-]*$", s):
        raise ValueError(f"Bad section '{section}'")
    return s

def _make_year_href_re(section: str) -> Pattern[str]:
    sec = _sanitize_section(section)
    # Accept both:
    #   .../2024.html
    #   .../2024.index.html
    return re.compile(
        rf"/content/([^/]+)/en/{re.escape(sec)}/(\d{{4}})(?:\.index)?\.html?$"
    )

def _norm_label(s: str) -> str:
    s = (s or "").replace("\xa0", " ").strip().lower()
    s = re.sub(r"[:\s]+$", "", s)   # drop trailing ":" etc.
    s = re.sub(r"\s+", " ", s)
    return s

def extract_pope_metadata_from_main(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")

    meta: Dict[str, Optional[str]] = {
        "pope_number": None,
        "pontificate_begin": None,
        "pontificate_end": None,
        "secular_name": None,
        "place_of_birth": None,
    }

    # First pass: pope number from subtitle (works on many pages)
    subtitle_txt = _txt(soup.select_one(".subtitle"))
    if subtitle_txt:
        m = re.search(r"\b(\d+)\b", subtitle_txt)
        meta["pope_number"] = m.group(1) if m else subtitle_txt

    # Robust label-based parsing from the sinottico table
    table = soup.select_one(".sinottico")
    if not table:
        # keep whatever we got from subtitle and return
        meta.setdefault("pontificate_end", None)
        return meta

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if len(cells) < 2:
            # sometimes Vatican uses nested structure; fall back
            cells = tr.find_all(["th", "td"])
        if len(cells) < 2:
            continue

        label = _norm_label(cells[0].get_text(" ", strip=True))
        value = cells[1].get_text(" ", strip=True).replace("\xa0", " ").strip() or None
        if not value:
            continue

        if label in {"beginning pontificate", "inizio pontificato", "début du pontificat"}:
            meta["pontificate_begin"] = value
        elif label in {"end pontificate", "fine pontificato", "fin du pontificat"}:
            meta["pontificate_end"] = value
        elif label in {"secular name", "nome di nascita", "nom de naissance"}:
            meta["secular_name"] = value
        elif label in {"place of birth", "luogo di nascita", "lieu de naissance"}:
            meta["place_of_birth"] = value
        elif label in {"pope number", "numero del papa", "numéro du pape"}:
            # only override if subtitle didn't already give us something
            if not meta["pope_number"]:
                meta["pope_number"] = value

    # active pope often has no end date
    meta.setdefault("pontificate_end", None)
    return meta

def _candidate_anchors(soup: BeautifulSoup):
    return soup.select(
        ".open a[href*='/content/'][href$='.index.html'], "
        ".open a[href*='/content/'][href$='.index.htm']"
    ) or soup.find_all("a", href=True)

def extract_available_years_from_main(html: str, pope_slug: str, section: str) -> List[int]:
    soup = BeautifulSoup(html, "html.parser")
    HREF_YEAR_RE = _make_year_href_re(section)
    years: Set[int] = set()
    for a in _candidate_anchors(soup):
        href = a.get("href", "")
        m = HREF_YEAR_RE.search(href)
        if not m:
            continue
        slug, year_str = m.group(1), m.group(2)
        if slug != pope_slug:
            continue
        years.add(int(year_str))
    return sorted(years)

def extract_year_links_from_main(html: str, pope_slug: str, years: Set[int], section: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    HREF_YEAR_RE = _make_year_href_re(section)
    found: Dict[int, str] = {}
    for a in _candidate_anchors(soup):
        href = a.get("href", "")
        m = HREF_YEAR_RE.search(href)
        if not m:
            continue
        slug, year_str = m.group(1), m.group(2)
        if slug != pope_slug:
            continue
        year = int(year_str)
        if year not in years:
            continue
        abs_url = urljoin(_BASE, href)
        if year not in found:
            found[year] = abs_url
    return [{"year": str(y), "url": found[y]} for y in sorted(found)]

def main() -> None:
    parser = argparse.ArgumentParser(
        description="List year-archive links for a given pope and section, plus metadata."
    )
    parser.add_argument("--pope", required=True)
    parser.add_argument("--years", required=True)
    parser.add_argument("--section", default="angelus", help="e.g., angelus, audiences, speeches")
    args = parser.parse_args()

    section = _sanitize_section(args.section)
    years_list = parse_years(args.years)
    if not years_list:
        print("No valid years parsed from --years.", file=sys.stderr); raise SystemExit(2)
    years_set = set(years_list)

    popes = vatican_fetch_pope_directory_recent()
    rec = papal_find_by_display_name(popes, args.pope)
    if not rec:
        avail = ", ".join(p["display_name"] for p in popes)
        print(f'Pope "{args.pope}" not found. Available: {avail}', file=sys.stderr); raise SystemExit(1)

    html = fetch_pope_main_html(rec["url"])
    meta = extract_pope_metadata_from_main(html)
    print("META\t" + json.dumps(meta, ensure_ascii=False))

    rows = extract_year_links_from_main(html, rec["slug"], years_set, section)
    if not rows:
        available = extract_available_years_from_main(html, rec["slug"], section)
        avail_str = ", ".join(map(str, available)) if available else "none yet"
        req_str = ", ".join(map(str, sorted(years_set)))
        print(
            f"No {section} year index pages found for {args.pope} in requested years [{req_str}]. "
            f"Available on page: {avail_str}.",
            file=sys.stderr,
        )
        raise SystemExit(3)

    missing = sorted(years_set - {int(r["year"]) for r in rows})
    if missing:
        print("Missing years: " + ", ".join(map(str, missing)), file=sys.stderr)

    for r in rows:
        print(f'{r["year"]}\t{r["url"]}')

if __name__ == "__main__":
    main()