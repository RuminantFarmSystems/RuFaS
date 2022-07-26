from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.crop.crop_types import crop_config

# TODO: add overall description of Corn class, along with 
#   description of attributes - GitHub Issue #170


class Corn(BaseCrop):
    def __init__(self, crop_name, data):
        """create an instance of Corn"""
        super().__init__()

        # get alfalfa variables from input data:
        self.plant_years = data['plant_years']
        self.repeat = data['repeat']
        self.planting_day = data['planting_day']
        self.harvest_day = data['harvest_day']
        self.harvest_type = data['harvest_type']
        self.planting_order = data['planting_order'].lower()
        self.extracted = data['extracted']
        self.crop_name = crop_name

        # assign attributes from corn dictionary in crop config file
        for key, val in crop_config.CORN.items():
            setattr(self, key, val)
