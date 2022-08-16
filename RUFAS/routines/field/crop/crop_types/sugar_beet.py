from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop


class SugarBeet(BaseCrop):
    """SugarBeet class"""
    def __init__(self, crop_name, data):
        """create an instance of SugarBeet

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="sugar_beet")

    # species-specific methods ...
