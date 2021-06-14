from pathlib import Path
import sqlite3
import ntpath
import pandas as pd
import atexit


def main():
    """
    Main function of weather_script.py. It executes all the necessary commands to edit the csv_file in SQLiteStudio 3
     into the correct format and imports it into the Weather Database.
    """

    try:
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
        import_data(conn, csv_path, dataset_ID)

        # 7 Calculating Taair and left joining to Skeleton:
        calc_taair(conn)
        left_join(conn)

        # 8 Appending new dataset to Observations table:
        add_observations(conn)

        # 9 Cleaning up unnecessary tables and views:
        atexit.register(cleanup, conn)

    except:
        cleanup(conn)
        c = conn.cursor()
        try:
            c.execute("DELETE FROM Datasets WHERE data_ID = ?", (dataset_ID,))
            conn.commit()
        except:
            pass

        try:
            c.execute("DELETE FROM Observations WHERE ID = ?", (dataset_ID,))
            conn.commit()
        except:
            pass

        raise Exception("Error during addition to database")


def weather_input():
    """
    Prompts the user for an input file. The function will be called to input a weather csv file.
    A valid input is:
        Valid path to a csv file in the correct format. The guidelines to format the csv file correctly can be found
        on Basecamp: https://3.basecamp.com/3486446/buckets/5296287/vaults/2784812933

    Returns:
        A string of the weather csv file path.
    """
    user_input = None
    while user_input is None or not Path(user_input).is_file():
        user_input = input("\nEnter Weather csv File: ")
        input_path = Path(user_input.strip())

        if input_path.suffix == '.csv':
            if not input_path.is_file():
                print("Specified file does not exist. Enter a valid csv file")
                user_input = None
                continue
            else:
                print("Weather csv file Detected...\n")
            return str(input_path)
        else:
            print("Invalid Input. Enter a valid csv file")
            user_input = None
            continue


def database_input():
    """
    Prompts the user for an input file. The function will be called to input a weather database file.
    A valid input is:
        Valid path to a database file similar in structure to input/weather/weather.db.

    Returns:
        A string of the weather database file path.
    """
    user_input = None
    while user_input is None or not Path(user_input).is_file():

        user_input = input("\nEnter Weather Database File: ")
        input_path = Path(user_input.strip())

        if input_path.suffix == '.db':
            if not input_path.is_file():
                print("Specified file does not exist. Enter a valid .db file")
                user_input = None
                continue
            else:
                print("Weather Database file Detected...\n")
            return str(input_path)
        else:
            print("Invalid Input. Enter a valid .db file")
            user_input = None
            continue


def id_input(database):
    """
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
    while user_input in used_ID or user_input is None or user_input <= 0:
        user_input = input("\nThe following IDs are already in use: " + ", ".join(str(f) for f in used_ID) +
                           "\nPlease enter a unique positive integer ID: ")
        try:
            user_input = int(user_input)
        except ValueError:
            print("Invalid input. ID must be a positive integer")
            user_input = None
            continue

        if user_input in used_ID:
            print("The ID you have entered is already in use. Please try again.")
        elif user_input <= 0:
            print("Invalid input. ID must be a positive integer")
        else:
            print("The ID has been recorded.")
    return user_input


def add_dataset(connection, dataset_id, csv_name):
    """"
    This function will prompt the user to input additional geographic details about the dataset (state, city or county,
    latitude, longitude, and any additional notes if necessary). The function then stores this information and creates
    a new entry in the Datasets table.
    """

    # Input geographic details
    "Please enter the following details about the location of the dataset:"
    state = input("Enter the corresponding US State: (if null, press Enter) ")

    county = input("Enter the corresponding county or city: (if null, press Enter) ")

    lat = None
    while lat is None or lat < -90 or lat > 90:
        lat = input("Enter the corresponding latitude: (if null, press Enter) ")
        if lat == "":
            break
        try:
            lat = float(lat)
        except ValueError:
            print("Invalid Input: Latitude has to be a numeric")
            lat = None
            continue
        if lat < -90 or lat > 90:
            print("Invalid Input: Latitude has to be between -90 and 90")

    long = None
    while long is None or long < -180 or long > 80:
        long = input("Enter the corresponding longitude: (if null, press Enter) ")
        if long == "":
            break
        try:
            long = float(long)
        except ValueError:
            print("Invalid Input: Longitude has to be a numeric")
            long = None
            continue
        if long < -180 or long > 80:
            print("Invalid Input: Longitude has to be between -180 and 80")

    notes = input("Enter any additional notes you might have: (if null, press Enter) ")

    params = (dataset_id, csv_name, state, county, lat, long, notes)

    # Creates a cursor in the given database
    c = connection.cursor()

    # Adds new entry in Datasets table
    c.execute("INSERT INTO Datasets VALUES (?, ?, ?, ?, ?, ?, ?)", params)
    c.execute("UPDATE Datasets SET state = NULL WHERE state = '' ")
    c.execute("UPDATE Datasets SET county = NULL WHERE county = '' ")
    c.execute("UPDATE Datasets SET latitude = NULL WHERE latitude = '' ")
    c.execute("UPDATE Datasets SET longitude = NULL WHERE longitude = '' ")
    c.execute("UPDATE Datasets SET Notes = NULL WHERE Notes = '' ")

    connection.commit()


def import_data(connection, csv_path, dataset_ID):
    c = connection.cursor()
    # load data
    df = pd.read_csv(csv_path)
    # strip whitespace from headers
    df.columns = df.columns.str.strip()
    # import data to table
    df.to_sql("Skeleton", connection, if_exists="append", index=False)
    c.execute("UPDATE Skeleton SET ID = ?", (dataset_ID,))
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
    c = connection.cursor()
    try:
        c.execute("DROP TABLE final")
    except:
        pass

    try:
        c.execute("DROP VIEW Taair")
    except:
        pass

    try:
        c.execute("DELETE FROM Skeleton")
    except:
        pass

    connection.commit()
    return


# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()