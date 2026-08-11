import argparse

from dc26_vatican_explorer.database_utils.database_helpers import query_texts

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Query speech texts from the Vatican database.")
    p.add_argument("--pope", default=None, help='Pope display name, e.g. "John Paul II"')
    p.add_argument("--section", default=None, help='Section, e.g. "homilies"')
    p.add_argument("--years", default=None, help='Year or range, e.g. "1977-1978"')
    p.add_argument("--lang", default=None, help='Two-letter language code, e.g. "EN"')
    p.add_argument("--field", default="text_content", help='Row field to print (default: text_content)')
    p.add_argument("--first", action="store_true", help="Print only the first result")
    args = p.parse_args()

    rows = query_texts(pope_name=args.pope, section=args.section, years=args.years, language=args.lang)
    if not rows:
        print("No results found.")
    target = rows[:1] if args.first else rows
    for row in target:
        print(row.get(args.field, f"(field '{args.field}' not found)"))