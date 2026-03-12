# src/vatican_scraper/step03_list_speeches.py
from __future__ import annotations

import argparse, random, re, sys, time
from typing import Callable, Dict, List, Optional, Set
from urllib.parse import urljoin

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


def extract_month_links_for_speeches(
    year_html: str,
    year_url: str,
    pope_slug: str,
    year: str,
) -> List[str]:
    """
    Find month pages like:
      /content/<slug>/en/speeches/<year>/<month>.html
      /content/<slug>/en/speeches/<year>/<month>.index.html
    Returns absolute URLs in (page) order, de-duplicated.
    """
    soup = BeautifulSoup(year_html, "html.parser")
    pat = re.compile(
        rf"/content/{re.escape(pope_slug)}/en/speeches/{re.escape(year)}/[a-z]+(\.index)?\.html?$",
        re.IGNORECASE,
    )

    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not pat.search(href):
            continue
        abs_url = urljoin(year_url, href)
        if abs_url not in seen:
            seen.add(abs_url)
            out.append(abs_url)
    return out


def collect_speeches_for_year_index(
    idx_html: str,
    idx_url: str,
    pope_slug: str,
    section: str,
    year: str,
    fetcher: Callable[[str], str] = fetch_html,
) -> List[Dict[str, Optional[str]]]:
    """
    Returns list of {'title': str, 'url': str, 'date': Optional[str]}.
    Handles the speeches-specific year->month traversal.
    """
    speeches = extract_speeches_from_year_index(idx_html, idx_url, pope_slug, section)

    if not speeches and _sanitize_section(section) == "speeches":
        month_urls = extract_month_links_for_speeches(idx_html, idx_url, pope_slug, year)

        # Fallback: sometimes you’re given .../2024.index.html but month links are on .../2024.html
        if not month_urls and idx_url.endswith(".index.html"):
            alt_url = idx_url.replace(".index.html", ".html")
            alt_html = fetcher(alt_url)
            month_urls = extract_month_links_for_speeches(alt_html, alt_url, pope_slug, year)

        for murl in month_urls:
            mhtml = fetcher(murl)
            speeches.extend(extract_speeches_from_year_index(mhtml, murl, pope_slug, section))

    return speeches



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
        speeches = collect_speeches_for_year_index(
            idx_html=idx_html,
            idx_url=idx_url,
            pope_slug=rec["slug"],
            section=section,
            year=year,
            fetcher=fetch_html,
        )
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