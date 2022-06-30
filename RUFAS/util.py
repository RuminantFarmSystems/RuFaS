"""
RUFAS: Ruminant Farm Systems Model
File name: util.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""
import json
import sys
from pathlib import Path

from RUFAS import errors


def get_base_dir():
    """Gets the base directory as reference for all relative paths.

    Unfrozen application - gets the project directory
    Frozen application - gets the executable directory

    Returns:
        Path: The reference directory for all paths in the program.
    """

    # Frozen
    if getattr(sys, 'frozen', False):
        #
        # Get the executable file path
        # Resolve to absolute path
        # Take the parent base_dir/RUFAS_exe
        #                 parent = base_dir/

        return Path(sys.executable).resolve().parent

    # Unfrozen
    else:
        #
        # Get path of current file (util.py)
        # Resolve to absolute path
        # Get the 2nd parent  base_dir/RUFAS/util.py
        #                     parent[0] = base_dir/RUFAS
        #                     parent[1] = base_dir/
        return Path(__file__).resolve().parents[1]


def read_json_file(file_path: Path):
    """
    Description:
        Reads and interprets the JSON file at the given path. Compiles the
        information into dictionaries used to instantiate simulation objects.

    Args:
        file_path (Path): Path to the input json file

    Raises:
        InvalidJSONFileError: If the json file at the given path does not
            conform with the format required

    Returns:
        data: the data read from the json file
    """

    try:
        if file_path.suffix == '.json':
            if not file_path.is_file():
                raise errors.UserInput((str(file_path), 'does not exist'))
        else:
            raise errors.UserInput((str(file_path), 'is not a JSON file'))

        with file_path.open('r') as f:
            data = json.load(f)

        return data

    except errors.UserInput as e:
        print(e.msg)
