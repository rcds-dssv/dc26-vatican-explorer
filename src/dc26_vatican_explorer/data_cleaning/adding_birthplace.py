"""
This module adds the place of birth for each pope, since missing from data.
"""
# ----------------------
# :: IMPORTS ::
# ----------------------
import sqlite3
from contextlib import closing


# ----------------------
# :: CONSTANTS ::
# ----------------------
BIRTH_MAPS = {
    'Benedict XVI': {
        '_pope_id': 1,
        'place_of_birth': 'Marktl, Germany'
    },
    'John Paul II': {
        '_pope_id': 2,
        'place_of_birth': 'Wadowice, Poland'
    },
    'Paul VI': {
        '_pope_id': 3,
        'place_of_birth': 'Concesio, Italy'
    },
    'Francis': {
        '_pope_id': 4,
        'place_of_birth': 'Buenos Aires, Argentina'
    },
    'Leo XIV': {
        '_pope_id': 5,
        'place_of_birth': 'Chicago, Illinois',
    },
}

# ----------------------
# :: FUNCTIONS ::
# ----------------------
def add_birthplace_to_db(db_path):
    
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            for name, pope_info in BIRTH_MAPS.items():
                cursor.execute(
                    '''
                    UPDATE popes
                    SET place_of_birth = ?
                    WHERE _pope_id = ? AND pope_name = ?
                    ''',
                    (pope_info['place_of_birth'], pope_info['_pope_id'], name)
                )
                if cursor.rowcount == 0:
                    print(f"Warning: No match found for {name} with ID {pope_info['_pope_id']}. No update made.")
                else:
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