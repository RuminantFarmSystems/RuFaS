from pathlib import Path
import sqlite3
import ntpath
import sql_script
import pandas as pd
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
    """# Deletes unnecessary rows at the top of the file
    delete_extra_rows(data_in)

    # Adds leap days (DAYMET does not report data for leap days)
    add_leap_days(data_out)"""


def import_data(connection, csv_path):
    c = connection.cursor()
    # load data (skip first 7 rows, specific to DAYMET format)
    df = pd.read_csv(csv_path,skiprows=7)
    # strip whitespace from headers
    df.columns = df.columns.str.strip()

    # import data to table
    # df.to_sql("Skeleton", connection, if_exists="append", index=False)
    # c.execute("UPDATE Skeleton SET ID = ?", (dataset_ID,))
    # connection.commit()

# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
