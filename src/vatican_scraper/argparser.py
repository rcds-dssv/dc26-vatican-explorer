# contain the arguments that are expected for the scraping step
import argparse

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

def get_scraper_args():

    p = scraper_parser()
    args = p.parse_args()

    # Ensure args.pope is a non-empty list; assign default if necessary
    pope_list = getattr(args, "pope", None)
    if not pope_list or not isinstance(pope_list, list) or len(pope_list) == 0:
        pope_list = ["Francis"]

    args.pope = pope_list

    return (p, args)