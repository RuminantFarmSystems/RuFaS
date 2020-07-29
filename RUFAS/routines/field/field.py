"""
RUFAS: Ruminant Farm Systems Model
File name: field.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""

from RUFAS import util
from .crop.crop import Crop
from .soil.soil import Soil
from .field_management.field_management import FieldManagement
from ...util import read_json_file


class Field:
    def __init__(self, field_name, field_data, time):
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
            time: an instance of the Time class specified in classes.py
        """
        self.field_name = field_name

        input_dir = util.get_base_dir() / 'input'

        self.soil_data = read_json_file(input_dir / 'soil' / field_data['soil'])
        self.crop_data = read_json_file(input_dir / 'crop' / field_data['crop'])
        self.field_management_data = read_json_file(input_dir / 'field_management' / field_data['field_management'])

        self.soil = Soil(self.soil_data)
        self.field_management = FieldManagement(self.field_management_data, time)
        self.crop = Crop(self.crop_data, time)
