from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.crop.crop_types import crop_config


# TODO: add overall description of Alfalfa class, along with 
#  description of attributes - GitHub Issue #170
class Alfalfa(BaseCrop):

    """``Alfalfa`` is a child of the ``BaseCrop`` class, and one of the main crop types.
       Attributes of ``Alfalfa`` are derived from data collected for the crop.
       The crop-specific attributes for alfala, are located in the crop config variable ``ALFALFA`` in crop_config.py.
       See the inherited class ``BaseCrop`` for all other attributes and member functions.
       
       Args: 
        crop_name (str): the name of the crop
        data (dict): data used to construct the class
    """
    def __init__(self, crop_name, data):
        """create an instance of Alfalfa"""
        super().__init__()

        # get alfalfa variables from input data:
        self.plant_years = data['plant_years']
        self.repeat = data['repeat']
        self.planting_day = data['planting_day']
        self.harvest_day = data['harvest_day']
        self.planting_order = data['planting_order'].lower()
        self.extracted = data['extracted']
        self.crop_name = crop_name

        # assign attributes from alfalfa dictionary in crop config file
        for key, val in crop_config.ALFALFA.items():
            setattr(self, key, val)
