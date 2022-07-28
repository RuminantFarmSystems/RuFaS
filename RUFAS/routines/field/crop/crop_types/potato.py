from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.crop.crop_types import crop_config

# TODO: add overall description of Potato class, along with
#   description of attributes - GitHub Issue #170


class Potato(BaseCrop):
    """``Potato`` is a child of the ``BaseCrop`` class, and one of the main crop types.
       Attributes of ``Potato`` are derived from data collected for the crop.
       The crop-specific attributes for potato, are located in the crop config variable ``POTATO`` in crop_config.py.
       See the inherited class ``BaseCrop`` for all other attributes and member functions.
    """
    def __init__(self, crop_name, data):
        """create an instance of Potato

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__()

        # get potato variables from input data:
        self.plant_years = data['plant_years']
        self.repeat = data['repeat']
        self.planting_day = data['planting_day']
        self.harvest_day = data['harvest_day']
        self.harvest_type = data['harvest_type']
        self.planting_order = data['planting_order'].lower()
        self.extracted = data['extracted']
        self.crop_name = crop_name

        # assign attributes from potato dictionary in crop config file
        for key, val in crop_config.POTATO.items():
            setattr(self, key, val)
