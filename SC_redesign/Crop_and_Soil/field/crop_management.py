from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData

"""
This module is based on the crop-related aspects of SWAT 6.1 'General Management'.

The CropManagement class is a component class of the Crop composite and serves as the foundation for
planting (6:1.1), Cutting/Harvesting (6:1.2, 6:1.5), Grazing (6:1.3), Crop death (6:1.4, 6:1.5), and
end of growing season (6:1.5)

The basic cut() and kill() methods are implemented in crop.py, which will be called by the logic
of this class.
"""

# TODO: This class will likely need to be reconciled with yields.py

class CropManagement:
    def __int__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()

        # Logic of crop management

        # Note: planting is done directly within Field.manage_field()

        # Harvest (without killing) Operation SWAT 6:1.2
    def harvest_without_killing(self, harvest_index_override: Optional[float] = None,
                                harvest_efficiency: Optional[float] = None) -> None:
        """harvest the crop, without killing it

        Args:
            harvest_index_override: an optional harvest index value, if given, the alternate method for calculating yield
                is used

        SWAT Reference: 6:1.2 'Harvest Operation'

        Details:
        """
        pass


