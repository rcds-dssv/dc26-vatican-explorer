# A simple example of how to read in the sqlite database file get one entry in a pandas dataframe

import pandas as pd
import sqlite3
from src.config import _DB_PATH


def connect_to_database():
    """Connect to the database"""
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    return conn, cursor


def get_tables_in_database(cursor) -> list:
    """get a list of tables in the database"""

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    return [
        t[0] for t in tables
    ]  # flatten the list, since the default is to return a list of tuples (rows)


def get_column_names_in_table(cursor, table_name: str) -> list:
    """get a list of the columns in a given table of the database"""

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    return [c[1] for c in columns]  # select only the column names


def get_row_count_in_table(cursor, table_name: str) -> int:
    """get the number of rows in a given table"""

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = int(cursor.fetchone()[0])
    return count


def get_first_n_rows_as_df(conn, table_name: str, n: int = 10) -> pd.DataFrame:
    """get the first n rows of the given table and return as a pandas DataFrame"""

    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {n}", conn)

    return df


def get_first_n_entries_in_column(
    cursor, table_name: str, column_name: str, n: int = 10
) -> list:
    """get the first n rows of the given table and return as a pandas DataFrame"""

    cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT {n};")
    values = cursor.fetchall()

    return values


if __name__ == "__main__":
    print("Database path:", _DB_PATH)
    conn, cursor = connect_to_database()

    # print a list of the available tables
    tables = get_tables_in_database(cursor)
    print("Tables in the database:", tables)
    print("")

    # print the number of rows in each table
    for table in tables:
        count = get_row_count_in_table(cursor, table)
        print(f"Table '{table}' has {count} rows.")
    print("")

    # print the available columns in each table
    for table in tables:
        columns = get_column_names_in_table(cursor, table)
        print(f"Columns in the '{table}' table:", columns)
        print("")

    # print the first 10 popes in the database, as a pandas dataframe
    df = get_first_n_rows_as_df(conn, "popes", 10)
    print(df)
    print("")

    # print the first text as a pandas dataframe
    df = get_first_n_rows_as_df(conn, "texts", 10)
    print(df)
    print("")

    # get the first 10 texts in the database, as a list
    sp = get_first_n_entries_in_column(cursor, "texts", "text_content", 10)
    print("First 10 texts:")
    for s in sp:
        print(s)
        print("")
