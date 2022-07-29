from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop


class Potato(BaseCrop):
    """Potato class"""
    def __init__(self, crop_name, data):
        """create an instance of Potato

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="potato")

    # species-specific methods ...
