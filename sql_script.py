from pathlib import Path
from RUFAS import errors
import sqlite3
import RUFAS.errors as e
import ntpath


def main():
    """
    Main function of weather_script.py. It executes all the necessary commands to edit the csv_file in SQLiteStudio 3
     into the correct format and imports it into the Weather Database.
    """

    print("\nRUFAS: Importing Weather Dataset into Database")
    # Database input
    database = database_input()

    # Selecting a dataset ID for the set to be added
    dataset_ID = id_input(database)

    # Selecting the csv file corresponding to the dataset
    data_in = weather_input()

    # Adding new entry in the Datasets table
    add_dataset(dataset_ID, database, data_in)


def weather_input():
    """
    Prompts the user for an input file. The function will be called twice: once to input the original weather csv file
    as downloaded from DAYMET as data_in, and a second time to select the black csv file that will be used to format
    the data accordingly.
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
    Prompts the user for an input file. The function will be called twice: once to input the original weather csv file
    as downloaded from DAYMET as data_in, and a second time to select the black csv file that will be used to format
    the data accordingly.
    A valid input is:
        Valid path to a csv file in the correct format. The guidelines to format the csv file correctly can be found
        on Basecamp: https://3.basecamp.com/3486446/buckets/5296287/vaults/2784812933

    Returns:
        A string of the weather csv file path.
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
        user_input = input("\nThe following IDs are already in use: " + ", ".join(str(f) for f in used_ID) + \
                           "\nPlease enter a unique positive integer ID: ")
        user_input = int(user_input)
        if user_input in used_ID:
            print("The ID you have entered is already in use. Please try again.")
        else:
            print("The ID has been recorded. Please go ahead and add it to your csv file if you haven't already "
                  "before moving on to the next input.")
    return user_input


def add_dataset(dataset_id, database, csv_file):

    # Extracts csv file name from full path
    csv_name = Path(csv_file)
    csv_name = ntpath.basename(csv_name)

    # Input geographic details
    "Please enter the following details about the location of the dataset:"
    state = input("Enter the corresponding US State (can be null): ")
    county = input("Enter the corresponding county or city (can be null): ")
    lat = float(input("Enter the corresponding latitude (required): "))
    long = float(input("Enter the corresponding longitude (required): "))
    notes = input("Enter any additional notes you might have: ")

    params = (dataset_id, csv_name, state, county, lat, long, notes)

    # Connects to the given database
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Adds new entry in Datasets table
    c.execute("INSERT INTO Datasets VALUES (?, ?, ?, ?, ?, ?, ?)", params)
    conn.commit()


# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
