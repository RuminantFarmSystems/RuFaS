"""
RUFAS: Ruminant Farm Systems Model (field module)
File name: field.py
Description: This module contains functions and classes relevant to agricultural fields
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
           Clay Morrow, morrowcj@outlook.com
"""
import pandas as pd
from RUFAS import util
from .crop.crop import *
from .soil.soil import *
from .field_management.field_management import *
from ...util import read_json_file


def daily_fields_routine(fields, manure_storage, weather, time):
    """execute field management, crop, and soil routines for each field and generate summaries.
    
    Args: 
      fields: instance of Fields class
      manure_storage: instance of ManureStorage class
      weather: instance of Weather class
      time: instance of Time class
    """
    for field in fields.fields.values():
        soil = field.soil
        crop = field.crop
        croptime = field.croptime
        field_management = field.field_management

        # If the crop is not planted yet, determine whether it is planted today
        # Necessary here so that field management can be scheduled prior to planting
        
        # if not crop_type.planted and not crop_type.killed:
        #     calculate_start(soil, crop, field_management, weather, time)

        daily_field_management_routine(soil, manure_storage, field_management, weather, time)
        daily_soil_routine(soil, crop, field_management, weather, time)
        daily_crop_routine(soil, crop, field_management, weather, time, croptime)

    fields.summarize_fields()
    fields.summarize_annual_variables()


def annual_fields_routine(fields, time):
    """perform annual crop routines for each field

    Args:
      fields: instance of Fields class
      time: instance of Time class

    Description: execute ``annual_crop_routine()`` for each field
    """
    for field in fields.fields.values():
        annual_crop_routine(field.crop, time)


class Fields:
    """a class defining attributes and methods for a set of agricultural fields"""
    def __init__(self, fields_data, time):
        """create an instance of the ``Fields`` class

        Args:
          fields_data: a dictionary with keys corresponding to field names and values containing dictionaries of data
             for each field
          time: an instance of the Time class
        """
        self.fields = {}
        """:obj:`dict`: a dictionary whose keys are field names and whose values are instances of the 
            ```Field``` class"""
        for field_name, field_data in fields_data.items():
            self.fields[field_name] = Field(field_name, field_data, time)

        self.profile_SW = 0.0
        """water in the soil profile (mm)"""  # Psuedocode S.1.A.5
        self.runoff = 0.0
        """:obj:`float`: soil surface runoff"""  # Psuedocode S.2.8.1?? TODO - GitHub Issue #174
        self.drainage = 0.0  # TODO: no clear reference in psuedocode - GitHub Issue #168
        self.erosion = 0.0  # equivalent to sed (S.3.A.1)?? TODO: no clear reference in psuedocode - GitHub Issue #168
        self.ET = 0.0  # TODO: no reference in psuedocode - GitHub Issue #168

        self.runoff_annual = 0.0
        """:obj:`float`: annual summation of ``runoff``"""
        self.drainage_annual = 0.0
        """:obj:`float`: annual summation of ``drainage``"""
        self.erosion_annual = 0.0
        """:obj:`float`: annual summation of ``erosion``"""
        self.ET_annual = 0.0
        """:obj:`float`: annual summation of ``ET``"""
        
        self.manure_applied = 0.0  # is this manure mass (S.5.D.III.1)? TODO: No clear reference in pseudocode - Github Issue #168
                                                                      # TODO: what are the units? - GitHub Issue #174
        self.manure_N_applied = 0.0  # TODO: No clear reference in pseudocode - Github Issue #168
                                     # TODO: what are the units? - GitHub Issue #174
        self.manure_P_applied = 0.0  # TODO: No clear reference in pseudocode - Github Issue #168
                                     # TODO: what are the units? - GitHub Issue #174

        self.manure_applied_annual = 0.0
        """:obj:`float`: annual summation of ``manure_applied``"""
        self.manure_N_applied_annual = 0.0
        """:obj:`float`: annual summation of ``manure_N_applied``"""
        self.manure_P_applied_annual = 0.0
        """:obj:`float`: annual summation of ``manure_P_applied``"""

        self.profile_N = 0.0  # TODO: what are the units? - GitHub Issue #174
        self.profile_P = 0.0  # TODO: what are the units? - GitHub Issue #174

        self.N_runoff = 0.0  # TODO: what are the units? - GitHub Issue #174
        self.P_runoff = 0.0  # TODO: what are the units? - GitHub Issue #174

        self.N_drainage = 0.0  # TODO: what are the units? - GitHub Issue #174
        self.P_drainage = 0.0  # TODO: what are the units? - GitHub Issue #174

        self.N_erosion = 0.0  # TODO: what are the units? - GitHub Issue #174
        self.P_erosion = 0.0  # TODO: what are the units? - GitHub Issue #174

        self.N_runoff_annual = 0.0
        """:obj:`float`: annual summation of ``N_runoff``"""
        self.P_runoff_annual = 0.0
        """:obj:`float`: annual summation of ``P_runoff``"""
        self.N_drainage_annual = 0.0
        """:obj:`float`: annual summation of ``N_drainage``"""
        self.P_drainage_annual = 0.0
        """:obj:`float`: annual summation of ``P_drainage``"""
        self.N_erosion_annual = 0.0
        """:obj:`float`: annual summation of ``N_erosion``"""
        self.P_erosion_annual = 0.0
        """:obj:`float`: annual summation of ``P_erosion``"""

        self.yield_actual = 0.0  # TODO: what are the units? - GitHub Issue #174
        self.N_yield = 0.0  # TODO: what are the units? - GitHub Issue #174
        self.P_yield = 0.0  # TODO: what are the units? - GitHub Issue #174

        self.yield_annual = 0.0
        """:obj:`float`: annual summation of ``yield_actual``"""
        self.N_yield_annual = 0.0
        """:obj:`float`: annual summation of ``N_yield``"""
        self.P_yield_annual = 0.0
        """:obj:`float`: annual summation of ``P_yield``"""

    def summarize_fields(self):
        """Description:
            reset the attributes of a Fields instance to 0 and then add up crop, soil, 
            and field management attributes for each field - 
            giving the overall sum of these properties across fields.
        """
        # Why are these set to their initialization values again? This seems redundant (prior to the loop)
        self.profile_SW = 0.0
        self.runoff = 0.0
        self.drainage = 0.0
        self.erosion = 0.0
        self.ET = 0.0

        self.manure_applied = 0.0
        self.manure_N_applied = 0.0
        self.manure_P_applied = 0.0

        self.profile_N = 0.0
        self.profile_P = 0.0

        self.N_runoff = 0.0
        self.P_runoff = 0.0

        self.N_drainage = 0.0
        self.P_drainage = 0.0

        self.N_erosion = 0.0
        self.P_erosion = 0.0

        self.yield_actual = 0.0
        self.N_yield = 0.0
        self.P_yield = 0.0

        for field in self.fields.values():
            soil = field.soil
            crop = field.crop.current_crop
            field_management = field.field_management

            self.profile_SW += soil.profile_SW
            self.runoff += soil.runoff
            self.drainage += soil.drainage
            self.erosion += soil.sed
            self.ET += soil.ET_act

            self.manure_applied += field_management.manure_applied
            self.manure_N_applied += field_management.manure_N_applied
            self.manure_P_applied += field_management.manure_P_applied

            self.profile_N += soil.profile_N
            self.profile_P += soil.profile_P

            self.N_runoff += soil.N_runoff
            self.P_runoff += soil.P_runoff

            self.N_drainage += soil.N_drainage
            self.P_drainage += soil.P_drainage

            self.N_erosion += soil.N_erosion
            self.P_erosion += soil.P_erosion


            for crop_type in crop.values():
                self.yield_actual += crop_type.yield_actual
                self.N_yield += crop_type.N_yield
                self.P_yield += crop_type.P_yield

    def summarize_annual_variables(self):
        """
        Description:
            update attributes annually by accumulation, 
            resulting in across-year sums of their values
        """
        self.runoff_annual += self.runoff
        self.drainage_annual += self.drainage
        self.erosion_annual += self.erosion
        self.ET_annual += self.ET

        self.manure_applied_annual += self.manure_applied
        self.manure_N_applied_annual += self.manure_N_applied
        self.manure_P_applied_annual += self.manure_P_applied

        self.N_runoff_annual += self.N_runoff
        self.P_runoff_annual += self.P_runoff
        self.N_drainage_annual += self.N_drainage
        self.P_drainage_annual += self.P_drainage
        self.N_erosion_annual += self.N_erosion
        self.P_erosion_annual += self.P_erosion

        self.yield_annual += self.yield_actual
        self.N_yield_annual += self.N_yield
        self.P_yield_annual += self.P_yield

    def annual_reset(self):
        """
        Description:
            reset some attributes to 0 for each field
        """
        for field in self.fields.values():
            field.crop.annual_reset()
            field.soil.annual_reset()
            field.field_management.annual_reset()

        self.runoff_annual = 0.0
        self.drainage_annual = 0.0
        self.erosion_annual = 0.0
        self.ET_annual = 0.0

        self.manure_applied_annual = 0.0
        self.manure_N_applied_annual = 0.0
        self.manure_P_applied_annual = 0.0

        self.N_runoff_annual = 0.0
        self.P_runoff_annual = 0.0
        self.N_drainage_annual = 0.0
        self.P_drainage_annual = 0.0
        self.N_erosion_annual = 0.0
        self.P_erosion_annual = 0.0

        self.yield_annual = 0.0
        self.N_yield_annual = 0.0
        self.P_yield_annual = 0.0

class Field:
    """
    The Field class is an organizational object for aggregating Soil,
    Crop, and Application objects. This structure simplifies the model,
    especially for input and output. The primary function of this class
    is reading the JSON files specified as containing crop, soil, and
    field management information associated with this field and assigning
    that data to relevant simulation objects associated with this Field
    object.
    """
    def __init__(self, field_name, field_data, time):
        """create an instance of the ``Field`` class.

        Args:
            field_name: the name of the field specified in the input JSON
            field_data: data describing the field specified in the input JSON
            time: an instance of the Time class
        """
        self.field_name = field_name
        """str: name of the field"""

        input_dir = util.get_base_dir() / 'input'

        soil_data = read_json_file(input_dir / 'soil' / field_data['soil'])
        crop_data = read_json_file(input_dir / 'crop' / field_data['crop'])
        field_management_data = read_json_file(input_dir / 'field_management' / field_data['field_management'])

        self.soil = Soil(soil_data)
        """an instance of the ``Soil`` class"""
        self.field_management = FieldManagement(field_management_data, time)
        """an instance of the ``FieldManagement`` class"""

        self.crop = Crop(crop_data)
        """an instance of the ``Crop`` class"""
        self.croptime= cropTime(time,crop_data, self.crop)
        """an instance of the ``CropTime`` class"""

