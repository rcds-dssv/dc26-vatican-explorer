import sqlite3
from contextlib import closing
from pathlib import Path


def debug_francis_entry(db_path, target_title):
    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row

        # We use a parameterized query (?) to safely handle the single quote in the title
        query = """
            SELECT p.pope_name, t.title, t.date, t.section, p.pontificate_begin
            FROM popes p
            JOIN texts t ON p._pope_id = t.pope_id
            WHERE t.title = ?
        """

        row = connection.execute(query, (target_title,)).fetchone()

        if row:
            print("--- RAW DATABASE ENTRY FOUND ---")
            for key in row:
                print(f"{key.upper()}: {row[key]!r}")
            print("--------------------------------")
        else:
            print(
                "No entry found with that exact title. Double-check for trailing spaces or hidden characters."
            )
    return


def main():
    db_path = Path("data/vatican_texts.db")
    problem_title = 'To the National Confederation of the "Misericordie d\' Italia" on the occasion of the anniversary of its meeting with Pope John Paul II on 14 June 1986 (14 June 2014)'

    debug_francis_entry(db_path, problem_title)
    return


if __name__ == "__main__":
    main()
