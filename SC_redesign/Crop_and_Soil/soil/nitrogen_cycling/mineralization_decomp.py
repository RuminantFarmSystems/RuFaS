from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class HumusMineralization:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track nitrogen mineralization and decomposition, creates new one
            if one is not provided.
        field_size : float, optional
            Size of the field (ha)

        Notes
        -----
        The field size is used to initialize a SoilData object for this module to work with, if a pre-configured
        SoilData object is not provided.

        """
        self.data = soil_data or SoilData(field_size=field_size)
