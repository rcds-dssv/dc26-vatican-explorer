# src/vatican_scraper/step06_run_pipeline.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

from vatican_scraper.argparser import get_scraper_args
from vatican_scraper.step04_fetch_speech_texts import fetch_speeches_to_feather
from vatican_scraper.step05_add_to_database import add_content_to_db
from config import _DB_PATH



def main() -> None:
    p, args = get_scraper_args()
    popes = args.popes
    

    if not popes:
        p.error("Provide at least one pope via --pope (repeatable) or --popes (comma-separated).")

    # If more than one pope, ignore --out (each run auto-names its own file).
    multi = len(popes) > 1
    if multi and args.out:
        print("[info] Multiple popes provided; ignoring --out and using per-pope auto filenames.")

    successes: List[Tuple[str, Path]] = []
    failures: List[Tuple[str, str]] = []

    for pope in popes:

        try:
            print("======= Fetching content...")
            out_path, rows = fetch_speeches_to_feather(
                pope=pope,
                years_spec=args.years,
                lang=args.lang,
                section=args.section,
                out=(None if multi else args.out),
                debug_loc=args.debug_loc,
                max_n_speeches=args.max_n_speeches
            )

            print("\n======= Adding content to database ...")
            for row in rows:
                print(row["url"])
                _text_id, _pope_id = add_content_to_db(_DB_PATH, row)

                if _text_id:
                    print("Inserted text into database with id:", _text_id)
                else:
                    print("Text record already exists (ignored).")
                if _pope_id:
                    print("Inserted pope into database with id:", _pope_id)
                else:
                    print("Pope record already exists (ignored).")
                print("")


            successes.append((pope, out_path))

        except SystemExit as e:
            # fetch_speeches_to_feather raises SystemExit with a string or code.
            msg = e.code if isinstance(e.code, str) else f"exit code {e.code}"
            failures.append((pope, msg))
        except Exception as e:
            failures.append((pope, str(e)))

    # Summary
    print("\n======= Summary ...")
    if successes:
        print("\n=== Succeeded ===")
        for pope, path in successes:
            print(f"{pope}: {path}")
    if failures:
        print("\n==== Failed ===")
        for pope, msg in failures:
            print(f"{pope}: {msg}")
        # Non-zero exit if any failed
        raise SystemExit(1)

    print("\n======= Pipeline complete.")

if __name__ == "__main__":
    main()


