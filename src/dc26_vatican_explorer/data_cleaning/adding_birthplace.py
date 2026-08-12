"""
This module adds the place of birth for each pope, since missing from data.
"""
# ----------------------
# :: IMPORTS ::
# ----------------------
import sqlite3
from contextlib import closing
from pathlib import Path


# ----------------------
# :: CONSTANTS ::
# ----------------------
# ponytail: keyed on pope_name only. _pope_id is an autoincrement column whose
# value depends on the order popes happen to be scraped in, so hardcoding it
# made every UPDATE silently match zero rows. pope_name is stable and unique.
BIRTH_MAPS = {
    'Benedict XVI': 'Marktl, Germany',
    'John Paul II': 'Wadowice, Poland',
    'Paul VI': 'Concesio, Italy',
    'Francis': 'Buenos Aires, Argentina',
    'Leo XIV': 'Chicago, Illinois, USA',
}

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def add_birthplace_to_db(db_path: str | Path) -> None:
    """Fill in ``popes.place_of_birth`` from the curated map.

    Birthplaces are not published in machine-readable form on vatican.va, so
    they are maintained by hand in :data:`BIRTH_MAPS`. Popes absent from the
    database are skipped quietly; only a pope that is present but unmatched is
    worth warning about.

    Args:
        db_path: Path to the SQLite database.

    """
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            for name, place_of_birth in BIRTH_MAPS.items():
                cursor.execute(
                    '''
                    UPDATE popes
                    SET place_of_birth = ?
                    WHERE pope_name = ?
                    ''',
                    (place_of_birth, name)
                )
                if cursor.rowcount:
                    print(f"Successfully updated {name}.")
    return

# ----------------------
# :: MAIN ENTRYPOINT ::
# ----------------------
def main():
    db_path = "data/vatican_texts.db"
    add_birthplace_to_db(db_path)
    return

if __name__ == "__main__":
    main()