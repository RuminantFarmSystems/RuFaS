from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop


class Corn(BaseCrop):
    """Corn class"""
    def __init__(self, crop_name, data):
        """create an instance of Corn
                    
           Args: 
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="corn")

    # species-specific methods ...
