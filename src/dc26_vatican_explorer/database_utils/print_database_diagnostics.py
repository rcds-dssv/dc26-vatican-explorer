import argparse

from dc26_vatican_explorer.database_utils.database_helpers import print_content_diagnostic

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Print database content diagnostics.")
    p.add_argument(
        "--show-missing-urls",
        action="store_true",
        help="Also print URLs of records with missing text_content.",
    )
    args = p.parse_args()
    print_content_diagnostic(show_missing_urls=args.show_missing_urls)
