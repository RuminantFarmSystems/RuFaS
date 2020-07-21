from pathlib import Path
from RUFAS import errors
import sqlite3
import ntpath
import pandas as pd


def main():
    """
    Main function of weather_script.py. It executes all the necessary commands to edit the csv_file in SQLiteStudio 3
     into the correct format and imports it into the Weather Database.
    """

    print("\nRUFAS: Importing Weather Dataset into Database")
    # 1 Database input
    database = database_input()

    # 2 Selecting a dataset ID for the set to be added
    dataset_ID = id_input(database)

    # 3 Selecting the csv file corresponding to the dataset
    data_in = weather_input()
    csv_path = Path(data_in)
    csv_name = ntpath.basename(csv_path)

    # 4 Connecting to the given database
    conn = sqlite3.connect(database)

    # 5 Adding new entry in the Datasets table
    add_dataset(conn, dataset_ID, csv_name)

    # 6 Importing csv file into Skeleton file
    import_data(conn, csv_path)

    # 7 Calculating Taair and left joining to Skeleton:
    calc_taair(conn)
    left_join(conn)

    # 8 Appending new dataset to Observations table:
    add_observations(conn)

    # 9 Cleaning up unnecessary tables and views:
    cleanup(conn)


def weather_input():
    """
    Prompts the user for an input file. The function will be called to input a weather csv file.
    A valid input is:
        Valid path to a csv file in the correct format. The guidelines to format the csv file correctly can be found
        on Basecamp: https://3.basecamp.com/3486446/buckets/5296287/vaults/2784812933

    Returns:
        A string of the weather csv file path.
    """
    user_input = input("\nEnter Weather csv File: ")
    input_path = Path(user_input.strip())

    if input_path.suffix == '.csv':
        if not input_path.is_file():
            raise errors.UserInput("Specified file does not exist")
        else:
            print("Weather csv file Detected...\n")
        return str(input_path)
    else:
        raise errors.UserInput("Invalid Input")


def database_input():
    """
    Prompts the user for an input file. The function will be called to input a weather database file.
    A valid input is:
        Valid path to a database file similar in structure to input/weather/weather.db.

    Returns:
        A string of the weather database file path.
    """
    user_input = input("\nEnter Weather Database File: ")
    print(user_input.lower())

    input_path = Path(user_input.strip())

    if input_path.suffix == '.db':
        if not input_path.is_file():
            raise errors.UserInput("Specified file does not exist")
        else:
            print("Weather Database file Detected...\n")
        return str(input_path)
    else:
        raise errors.UserInput("Invalid Input")


def id_input(database):
    """"
    Each dataset in the weather database has its own dataset_ID, a unique positive integer. This function prints
    out the IDs that are already in use and prompts the user to input an ID for the new dataset being added.
    A valid input is:
        Positive integer that is not already being used by another dataset.

    Returns:
        The ID entered by the user.
    """
    # Connects to the given database
    conn = sqlite3.connect(database)
    c = conn.cursor()

    used_ID = []
    for row in c.execute("SELECT data_ID FROM Datasets ORDER BY data_ID asc"):
        used_ID.append(row)

    for i in range(0, len(used_ID)):
        j = used_ID[i]
        used_ID[i] = j[0]

    user_input = None
    while user_input in used_ID or user_input is None:
        user_input = input("\nThe following IDs are already in use: " + ", ".join(str(f) for f in used_ID) +
                           "\nPlease enter a unique positive integer ID: ")
        user_input = int(user_input)
        if user_input in used_ID:
            print("The ID you have entered is already in use. Please try again.")
        else:
            print("The ID has been recorded. Please go ahead and add it to your csv file if you haven't already "
                  "before moving on to the next input.")
    return user_input


def add_dataset(connection, dataset_id, csv_name):
    """"
    This function will prompt the user to input additional geographic details about the dataset (state, city or county,
    latitude, longitude, and any additional notes if necessary). The function then stores this information and creates
    a new entry in the Datasets table.
    """

    # Input geographic details
    "Please enter the following details about the location of the dataset:"
    state = input("Enter the corresponding US State (can be null): ")
    county = input("Enter the corresponding county or city (can be null): ")
    lat = float(input("Enter the corresponding latitude (required): "))
    long = float(input("Enter the corresponding longitude (required): "))
    notes = input("Enter any additional notes you might have: ")

    params = (dataset_id, csv_name, state, county, lat, long, notes)

    # Creates a cursor in the given database
    c = connection.cursor()

    # Adds new entry in Datasets table
    c.execute("INSERT INTO Datasets VALUES (?, ?, ?, ?, ?, ?, ?)", params)
    connection.commit()


def import_data(connection, csv_path):
    c = connection.cursor()
    # load data
    df = pd.read_csv(csv_path)
    # strip whitespace from from headers
    df.columns = df.columns.str.strip()
    # import data to table
    df.to_sql("Skeleton", connection, if_exists="append", index=False)
    connection.commit()


def calc_taair(connection):
    c = connection.cursor()
    c.execute("CREATE VIEW Taair AS SELECT year,avg(avg) as Taair FROM Skeleton GROUP BY year")
    connection.commit()


def left_join(connection):
    c = connection.cursor()
    c.execute("CREATE TABLE final AS SELECT Skeleton.*,Taair.Taair "
              "FROM Skeleton LEFT JOIN Taair ON Skeleton.year=Taair.year")
    connection.commit()


def add_observations(connection):
    c = connection.cursor()
    c.execute("INSERT INTO Observations SELECT * FROM final")
    connection.commit()


def cleanup(connection):
    c=connection.cursor()
    c.execute("DROP TABLE final")
    c.execute("DROP VIEW Taair")
    c.execute("DELETE FROM Skeleton")
    connection.commit()
    return


# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
