from pathlib import Path
import sqlite3
import ntpath
import sql_script
import pandas as pd
from RUFAS.classes import is_leap_year
from RUFAS import errors
import atexit


def main():
    """
    Main function of csv_script.py. It executes all the necessary commands to edit the DAYMET csv_file (using Excel and
    SQLiteStudio 3) into the correct format to be processed and integrate into the weather database.
    This script only transforms the raw DAYMET dataset into another csv dataset in the correct format. To integrate the
    formatted csv file into the database, sql_script.py has to be run separately.
    """

    print("\nRUFAS: Importing Weather Dataset into Database")
    # 1 DAYMET dataset input
    data_in = sql_script.weather_input()
    csv_path = Path(data_in)
    csv_name = ntpath.basename(csv_path)

    # 2 Database input
    database = sql_script.database_input()

    # 3 Connecting to the weather database
    conn = sqlite3.connect(database)

    # 4 Importing csv file into Skeleton file
    import_data(conn, csv_path)

    # 5 Adds leap days (DAYMET does not report data for leap days)
    add_leap_days(conn)


def import_data(connection, csv_path):
    c = connection.cursor()
    # load data (skip first 7 rows, specific to DAYMET format)
    df = pd.read_csv(csv_path,skiprows=7)
    # strip whitespace from headers
    df.columns = df.columns.str.strip()
    df.columns = ["year", "jday", "dayl", "precip", "srad", "swe", "high", "low", "vp"]

    # import data to table
    df.to_sql("Skeleton2", connection, if_exists="append", index=False)
    connection.commit()


def add_leap_days(connection):
    c = connection.cursor()
    # find first and last year, last day
    c.execute("SELECT min(year) from Skeleton2")
    start_year = c.fetchone()[0]
    c.execute("SELECT max(year) from Skeleton2")
    end_year = c.fetchone()[0]
    c.execute("SELECT max(jday) from Skeleton2 WHERE year=(SELECT max(year) from Skeleton2)")
    end_day = c.fetchone()[0]

    y = start_year
    while not is_leap_year(y):
        y += 1

    if is_leap_year(y):
        if y == end_year:
            """if end_day == 365:
            c.execute()"""
            return
        else:
            while y <= end_year:
                c.execute("INSERT INTO Skeleton2\
                SELECT ?, 366, dayl, precip, srad, swe, high, low, vp FROM Skeleton2 WHERE year = ? AND jday = 365", (y,y))
                y += 4
    connection.commit()


# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
