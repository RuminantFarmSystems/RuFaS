"""
RUFAS: Ruminant Farm Systems Model
File name: field.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""

import json
from RUFAS import util, errors
from pathlib import Path
from .crop.crop import Crop
from .soil.soil import Soil
from .application_management.application_management import ApplicationManagement


class Field:
    def __init__(self, field_name, field_data, space, time):
        """
        Description:
            The Field class is an organizational object for aggregating Soil,
            Crop, and Application objects. This structure simplifies the model,
            especially for input and output. The primary function of this class
            is reading the JSON files specified as containing crop, soil, and
            field management information associated with this field and assigning
            that data to relevant simulation objects associated with this Field
            object.
        Args:
            field_name: the name of the field specified in the input JSON
            field_data: data describing the field specified in the input JSON
            space: an instance of the Space class specified in classes.py
            time: an instance of the Time class specified in classes.py
        """
        self.field_name = field_name

        input_dir = util.get_base_dir() / 'Inputs'

        self.soil_data = read_json_file(input_dir / 'soil_profiles' / field_data['soil'])
        self.crop_data = read_json_file(input_dir / 'crop_rotations' / field_data['crop'])
        self.application_data = read_json_file(input_dir / 'applications' / field_data['applications'])

        self.soil = Soil(self.soil_data)
        self.application_management = ApplicationManagement(self.application_data, time)
        self.crop = Crop(self.crop_data, space, time)


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
