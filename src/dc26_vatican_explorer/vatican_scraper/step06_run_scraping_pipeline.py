# src/dc26_vatican_explorer/vatican_scraper/step06_run_scraping_pipeline.py
from __future__ import annotations

import itertools
from pathlib import Path
from dc26_vatican_explorer.config import _DB_PATH
from dc26_vatican_explorer.vatican_scraper.argparser import get_scraper_args
from dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts import fetch_speeches_to_feather
from dc26_vatican_explorer.vatican_scraper.step05_add_to_database import add_content_to_db



def main() -> None:
    p, args = get_scraper_args()

    popes: list[str] = args.popes
    sections: list[str] = args.sections
    langs: list[str] = args.langs

    if not popes:
        p.error("Provide at least one pope via --pope (repeatable) or --popes (comma-separated).")

    multi = len(popes) * len(sections) * len(langs) > 1
    if multi and args.out:
        print("[info] Multiple popes/sections/langs provided; ignoring --out and using auto filenames.")

    successes: list[tuple[str, str, str, Path]] = []
    failures: list[tuple[str, str, str, str]] = []

    for pope, section, lang in itertools.product(popes, sections, langs):
        label = f"{pope} / {section} / {lang}"
        print(f"\n{'='*60}")
        print(f"=== {label}")
        print(f"{'='*60}")

        try:
            print("======= Fetching content...")
            out_path, rows = fetch_speeches_to_feather(
                pope=pope,
                years_spec=args.years,
                lang=lang,
                section=section,
                out=(None if multi else args.out),
                debug_loc=args.debug_loc,
                max_n_speeches=args.max_n_speeches
            )

            print("\n======= Adding content to database ...")
            for row in rows:
                print(row["url"])

                if not (row.get("text") or "").strip():
                    print("[WARNING] Scraper returned empty text for this record.")

                _text_id, _pope_id = add_content_to_db(_DB_PATH, row)

                if _text_id:
                    print("Inserted/updated text in database with id:", _text_id)
                elif (row.get("text") or "").strip():
                    print("Text record already has content (skipped).")
                else:
                    print("Text record exists but content is still empty (scraper returned nothing).")
                if _pope_id:
                    print("Inserted pope into database with id:", _pope_id)
                else:
                    print("Pope record already exists (ignored).")
                print("")

            successes.append((pope, section, lang, out_path))

        except SystemExit as e:
            msg = e.code if isinstance(e.code, str) else f"exit code {e.code}"
            failures.append((pope, section, lang, msg))
        except Exception as e:
            failures.append((pope, section, lang, str(e)))

    # Summary
    print("\n======= Summary ...")
    if successes:
        print("\n=== Succeeded ===")
        for pope, section, lang, path in successes:
            print(f"  {pope} / {section} / {lang}: {path}")
    if failures:
        print("\n==== Failed ===")
        for pope, section, lang, msg in failures:
            print(f"  {pope} / {section} / {lang}: {msg}")
        raise SystemExit(1)

    print("\n======= Pipeline complete.")

if __name__ == "__main__":
    main()


