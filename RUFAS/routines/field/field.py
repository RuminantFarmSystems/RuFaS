################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: field.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

This module needs the following inputs in order to operate correctly:

    "latitude": 43.332708

    These are attributes of a field that need to be specified in the json input
    file. The values on the right are just examples from a corn crop type.

        "grow_years": [2009],
        "repeat": 1,
        "planting_date": 121,
        "harvest_date": 319

    From the weather class, the following will be needed:
        T_min
        T_max
        radiation
        T_avg

    From the soil class, the following will be needed:
        soil_layers

        And the following attributes of a soil layer:
            bottom_depth
            Eo_sum = Sum of the Eo values leading up to today
            trans_max
            NO3
            labile_P
            soil_water
            fc_water
            wilting_water
"""
################################################################################
import json
from RUFAS import util, errors
from pathlib import Path
from .crop.crop import Crop
from .soil.soil import Soil


class Field:
    def __init__(self, field_name, field_data, time):
        self.field_name = field_name

        input_dir = util.get_base_dir() / 'Inputs'

        self.soil_data = read_json_file(input_dir / 'soil_profiles' / field_data['soil'])
        self.crop_data = read_json_file(input_dir / 'crop_rotations' / field_data['crop'])
        self.application_data = read_json_file(input_dir / 'applications' / field_data['applications'])

        self.soil = Soil(self.soil_data, self.application_data, time)

        self.crop = Crop(self.crop_data, time)


def read_json_file(file_path:Path):
    try:
        if file_path.suffix == '.json':
            if not file_path.is_file():
                raise errors.UserInput((str(file_path), 'does not exist'))
        else:
            raise errors.UserInput((str(file_path), 'is not a JSON file'))

        with file_path.open('r') as f:
            data = json.load(f)

        return data

    except errors.UserInput as e:\
        print(e.msg)

