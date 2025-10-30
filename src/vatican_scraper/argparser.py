# contain the arguments that are expected for the scraping step
import argparse
from typing import List, Tuple

def scraper_parser():

    p = argparse.ArgumentParser(
        description="Run the full Vatican scrape pipeline (multi-pope) and save Feather datasets."
    )

    # You can repeat --pope or use --popes (comma-separated)
    p.add_argument("--pope", default=None, action="append", help='Repeatable. e.g., --pope "Francis" --pope "Benedict XVI". Default: Francis if not specified.')
    p.add_argument("--popes", help='Comma-separated list. e.g., "Francis,Benedict XVI,John Paul II"')

    p.add_argument("--years", default="2025", help='e.g., "2020", "2019,2021-2023", "2021-2023"')
    p.add_argument("--section", default="angelus", help="Type of content: e.g., angelus, audiences, speeches")
    p.add_argument("--lang", default="EN", help="Two-letter language code (EN, FR, ES, ...). Default: EN")

    # Note: Step 4 always saves under vatican_scraper/scrape_result/.
    # If you pass --out here with multiple popes, it’s ambiguous, so we ignore it.
    p.add_argument("--out", default=None,
                   help="Optional filename if exactly one pope is provided; ignored for multiple popes.")
    p.add_argument("--debug-loc", action="store_true")

    p.add_argument("--max_n_speeches",default=None, help='maximum number of speeches to query (int). Default None.', type=int)


    return p


def _gather_popes(args) -> List[str]:

    popes: List[str] = []

    # Ensure args.pope is a non-empty list; assign default if necessary
    # and handle repeated flags: --pope "Francis" --pope "Benedict XVI"
    if args.pope:  
        popes.extend(args.pope)
    if not popes or not isinstance(popes, list) or len(popes) == 0:
        popes = ["Francis"]

    if args.popes:  # comma-separated: --popes "Francis,Benedict XVI,John Paul II"
        popes.extend([p.strip() for p in args.popes.split(",") if p.strip()])

    # de-dup while preserving order
    seen = set()
    uniq = []
    for p in popes:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq

def get_scraper_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    """
    Parse command-line arguments for the Vatican scraper.
    Returns:
        tuple: (ArgumentParser, Namespace) where Namespace contains parsed arguments.
    Purpose:
        - Parses arguments for scraping Vatican speeches, including pope(s), years, section, language, etc.
        - Ensures that the 'pope' argument is always a non-empty list; if not provided, defaults to ['Francis'].
        - Handles both --pope (repeatable) and --popes (comma-separated) arguments.
    """


    p = scraper_parser()
    args = p.parse_args()
    popes = _gather_popes(args)
    args.popes = popes

    # only return the first pope here if a list is given
    args.pope = popes[0]

    return (p, args)