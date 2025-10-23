# src/vatican_scraper/step05_run_pipeline.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

from vatican_scraper.step04_fetch_speech_texts import fetch_speeches_to_feather

def _gather_popes(args) -> List[str]:
    popes: List[str] = []
    if args.pope:   # repeated flags: --pope "Francis" --pope "Benedict XVI"
        popes.extend(args.pope)
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

def main() -> None:
    p = argparse.ArgumentParser(
        description="Run the full Vatican scrape pipeline (multi-pope) and save Feather datasets."
    )
    # You can repeat --pope or use --popes (comma-separated)
    p.add_argument("--pope", action="append", help='Repeatable. e.g., --pope "Francis" --pope "Benedict XVI"')
    p.add_argument("--popes", help='Comma-separated list. e.g., "Francis,Benedict XVI,John Paul II"')

    p.add_argument("--years", required=True, help='e.g., "2020", "2019,2021-2023", "2021-2023"')
    p.add_argument("--section", default="angelus", help="Type of content: e.g., angelus, audiences, speeches")
    p.add_argument("--lang", default="EN", help="Two-letter language code (EN, FR, ES, ...). Default: EN")

    # Note: Step 4 always saves under vatican_scraper/scrape_result/.
    # If you pass --out here with multiple popes, it’s ambiguous, so we ignore it.
    p.add_argument("--out", default=None,
                   help="Optional filename if exactly one pope is provided; ignored for multiple popes.")
    p.add_argument("--debug-loc", action="store_true")

    args = p.parse_args()
    popes = _gather_popes(args)

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
            out_path = fetch_speeches_to_feather(
                pope=pope,
                years_spec=args.years,
                lang=args.lang,
                section=args.section,
                out=(None if multi else args.out),
                debug_loc=args.debug_loc,
            )
            successes.append((pope, out_path))
        except SystemExit as e:
            # fetch_speeches_to_feather raises SystemExit with a string or code.
            msg = e.code if isinstance(e.code, str) else f"exit code {e.code}"
            failures.append((pope, msg))
        except Exception as e:
            failures.append((pope, str(e)))

    # Summary
    if successes:
        print("\n=== Success ===")
        for pope, path in successes:
            print(f"{pope}: {path}")
    if failures:
        print("\n=== Failed ===")
        for pope, msg in failures:
            print(f"{pope}: {msg}")
        # Non-zero exit if any failed
        raise SystemExit(1)

    print("\nPipeline complete.")

if __name__ == "__main__":
    main()


