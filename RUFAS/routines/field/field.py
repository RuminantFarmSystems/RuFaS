"""
RUFAS: Ruminant Farm Systems Model
File name: field.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
import pandas as pd
from RUFAS import util
from .crop.crop import *
from .soil.soil import *
from .field_management.field_management import *
from ...util import read_json_file


def daily_fields_routine(fields, manure_storage, weather, time):
    for field in fields.fields.values():
        soil = field.soil
        crop = field.crop
        crop_type = crop.current_crop
        field_management = field.field_management

        # If the crop is not planted yet, determine whether it is planted today
        # Necessary here so that field management can be scheduled prior to planting
        if not crop_type.planted and not crop_type.killed:
            calculate_start(soil, crop, field_management, weather, time)

        daily_field_management_routine(soil, manure_storage, field_management, weather, time)
        daily_soil_routine(soil, crop, field_management, weather, time)
        daily_crop_routine(soil, crop, field_management, weather, time)

    fields.summarize_fields()
    fields.summarize_annual_variables()


def annual_fields_routine(fields, time):
    for field in fields.fields.values():
        annual_crop_routine(field.crop, time)


class Fields:
    def __init__(self, fields_data, time):
        self.fields = {}
        for field_name, field_data in fields_data.items():
            self.fields[field_name] = Field(field_name, field_data, time)

        self.profile_SW = 0.0
        self.runoff = 0.0
        self.drainage = 0.0
        self.erosion = 0.0
        self.ET = 0.0

        self.runoff_annual = 0.0
        self.drainage_annual = 0.0
        self.erosion_annual = 0.0
        self.ET_annual = 0.0

        self.manure_applied = 0.0
        self.manure_N_applied = 0.0
        self.manure_P_applied = 0.0

        self.manure_applied_annual = 0.0
        self.manure_N_applied_annual = 0.0
        self.manure_P_applied_annual = 0.0

        self.profile_N = 0.0
        self.profile_P = 0.0

        self.N_runoff = 0.0
        self.P_runoff = 0.0

        self.N_drainage = 0.0
        self.P_drainage = 0.0

        self.N_erosion = 0.0
        self.P_erosion = 0.0

        self.N_runoff_annual = 0.0
        self.P_runoff_annual = 0.0
        self.N_drainage_annual = 0.0
        self.P_drainage_annual = 0.0
        self.N_erosion_annual = 0.0
        self.P_erosion_annual = 0.0

        self.yield_actual = 0.0
        self.N_yield = 0.0
        self.P_yield = 0.0

        self.yield_annual = 0.0
        self.N_yield_annual = 0.0
        self.P_yield_annual = 0.0

    def summarize_fields(self):
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

            self.yield_actual += crop.yield_actual
            self.N_yield += crop.N_yield
            self.P_yield += crop.P_yield

    def summarize_annual_variables(self):
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

class cropTime:
    def __init__(self,time, data):
        """
        Description:
            This object is responsible for creating and tracking time in the simulation.
        Args:
            config: instance of the Config class containing information necessary
                to initialize time
        """
        # number of years
        years = time.years
        crop_list= data['crops']
        times={
        "year" : [2009]*365+[2010]*365,
        "day" : sum(years,[])}
        df=pd.DataFrame(times)
        df['crops_growing'] = [[] for _ in range(len(df))]
        for index, row in df.iterrows():
            for crop in crop_list.keys():
                for i in range(0,len(crop_list[crop]['plant_years'])):
                    if (crop_list[crop]['plant_years'][i] == row['year'] and crop_list[crop]['planting_day'] < row['day']) and (crop_list[crop]['harvest_day'] > row['day']):
                        df.loc[index,'d'].append(crop)
        print(df)

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

        soil_data = read_json_file(input_dir / 'soil' / field_data['soil'])
        crop_data = read_json_file(input_dir / 'crop' / field_data['crop'])
        field_management_data = read_json_file(input_dir / 'field_management' / field_data['field_management'])

        self.soil = Soil(soil_data)
        self.field_management = FieldManagement(field_management_data, time)
        self.crop = Crop(crop_data, time)
        self.croptime= cropTime(time,crop_data)

