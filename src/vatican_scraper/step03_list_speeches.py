# src/vatican_scraper/step03_list_speeches.py
from __future__ import annotations

import argparse, random, re, sys, time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from vatican_scraper.step01_list_popes import (
    vatican_fetch_pope_directory_recent,
    papal_find_by_display_name,
)
from vatican_scraper.step02_list_pope_year_links import (
    parse_years,
    fetch_pope_main_html,
    extract_year_links_from_main,
    extract_available_years_from_main,
    _sanitize_section,  # reuse validation
)

def _pause(min_s: float = 0.4, max_s: float = 1.2) -> None:
    time.sleep(random.uniform(min_s, max_s))

def fetch_html(url: str) -> str:
    _pause()
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    _pause()
    return r.text

def extract_speeches_from_year_index(
    year_index_html: str,
    year_index_url: str,
    pope_slug: str,
    section: str,
) -> List[Dict[str, Optional[str]]]:
    """
    Pull individual speech links under the .documento ... h2 > a structure.
    Emits: {'title': str, 'url': str, 'date': Optional[str]}
    """
    sec = _sanitize_section(section)
    soup = BeautifulSoup(year_index_html, "html.parser")
    items: List[Dict[str, Optional[str]]] = []
    seen: Set[str] = set()

    for li in soup.select(".documento ul li"):
        a = li.select_one("h2 a[href]")
        if not a:
            continue
        abs_url = urljoin(year_index_url, a["href"])
        # Require pope slug and desired section somewhere in the path
        if f"/content/{pope_slug}/" not in abs_url:
            continue
        if f"/{sec}/" not in abs_url:
            continue

        title = a.get_text(" ", strip=True)
        date_text = None
        ds = li.select_one(".data")
        if ds:
            date_text = ds.get_text(" ", strip=True)
        if not date_text:
            m = re.search(r"\b(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})\b", li.get_text(" ", strip=True))
            if m:
                date_text = m.group(1)

        if abs_url in seen:
            continue
        seen.add(abs_url)
        items.append({"title": title, "url": abs_url, "date": date_text})

    return items

def main() -> None:
    p = argparse.ArgumentParser(description="List individual speech links from Vatican year indexes.")
    p.add_argument("--pope", required=True)
    p.add_argument("--years", required=True)
    p.add_argument("--section", default="angelus", help="e.g., angelus, audiences, speeches")
    args = p.parse_args()

    section = _sanitize_section(args.section)
    years = set(parse_years(args.years))
    if not years:
        print("No valid years parsed from --years.", file=sys.stderr); raise SystemExit(2)

    popes = vatican_fetch_pope_directory_recent()
    rec = papal_find_by_display_name(popes, args.pope)
    if not rec:
        avail = ", ".join(p["display_name"] for p in popes)
        print(f'Pope "{args.pope}" not found. Available: {avail}', file=sys.stderr); raise SystemExit(1)

    pope_main_html = fetch_pope_main_html(rec["url"])

    year_rows = extract_year_links_from_main(pope_main_html, rec["slug"], years, section)
    if not year_rows:
        available = extract_available_years_from_main(pope_main_html, rec["slug"], section)
        req_str = ", ".join(map(str, sorted(years)))
        avail_str = ", ".join(map(str, available)) if available else "none yet"
        print(
            f"No {section} year index pages found for {args.pope} in requested years [{req_str}]. "
            f"Available on page: {avail_str}.",
            file=sys.stderr,
        )
        raise SystemExit(3)

    any_out = False
    for row in year_rows:
        year, idx_url = row["year"], row["url"]
        idx_html = fetch_html(idx_url)
        speeches = extract_speeches_from_year_index(idx_html, idx_url, rec["slug"], section)
        if not speeches:
            print(f"No speeches found on {idx_url}", file=sys.stderr)
            continue
        for s in speeches:
            date = s.get("date") or ""
            title = (s.get("title") or "").replace("\t", " ").strip()
            url = s["url"]
            print(f"{year}\t{date}\t{title}\t{url}")
            any_out = True

    if not any_out:
        raise SystemExit(4)

if __name__ == "__main__":
    main()