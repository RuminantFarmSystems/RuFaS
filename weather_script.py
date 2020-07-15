from pathlib import Path
from RUFAS import errors
import csv


def main():
    """
    Main function of weather_script.py. It executes all the necessary commands to edit the csv_file (using Excel and
    SQLiteStudio 3) into the correct format and imports it into the Weather Database.
    """

    print("\nRUFAS: Importing Weather Dataset into Database")
    data_in = weather_input()
    data_out = weather_input()

    """"# Deletes unnecessary rows at the top of the file
    delete_extra_rows(data_in, data_out)"""

    # Adds leap days (DAYMET does not report data for leap days)
    add_leap_days(data_out)


def weather_input():
    """
    Prompts the user for an input file. The function will be called twice: once to input the original weather csv file
    as downloaded from DAYMET as data_in, and a second time to select the black csv file that will be used to format
    the data accordingly.
    A valid input is:
        Valid path to a csv file.

    Returns:
        A string of the weather csv file path.
    """
    user_input = input("\nEnter Weather csv File: ")
    print(user_input.lower())

    input_path = Path(user_input.strip())

    if input_path.suffix == '.csv':
        if not input_path.is_file():
            raise errors.UserInput("Specified file does not exist")
        else:
            print("Weather csv file Detected...\n")
        return str(input_path)
    else:
        raise errors.UserInput("Invalid Input")


def delete_extra_rows(data_in, data_out):
    """
    Deletes the first 7 rows of the csv file. In DAYMET, the first 7 rows contain general information about the
    dataset. To be in the correct format, the row containing the parameter names should be the first row of the table.
    """
    with open(data_out, 'r+') as data_out:
        with open(data_in, 'r') as data_in:
            line = 1
            for row in data_in:
                if line <= 7:
                    line += 1
                else:
                    data_out.write(row)


def add_leap_days(data_out):
    return


# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
