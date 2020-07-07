from RUFAS import util
from pathlib import Path
from RUFAS import errors
import os


def main():

    print("\nRUFAS: Importing Weather Dataset into Database")
    file = weather_input()


def weather_input():
    user_input = input("\nEnter Weather csv File: ")
    print(user_input.lower())

    input_path = Path(user_input.strip())

    if input_path.suffix == '.csv':
        if not input_path.is_file():
            raise errors.UserInput("Specified file does not exist")
        else:
            print("Weather csv file Detected...\n")
        return [input_path]
    else:
        raise errors.UserInput("Invalid Input")


# -------------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()