from typing import Optional
from math import exp
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class LeachingRunoffErosion:

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track carbon in the soil profile, creates new one if one is not
            provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    @staticmethod
    def _determine_nitrogen_concentration(soluble_nitrogen_amount: float,
                                          soil_water_runoff_sum: float,
                                          saturation_content: float) -> float:
        """This method determines the concentration (kg N/mm H20) of the inorganic pools NO3/NH4 in the top soil layer

        Parameters
        ----------
        soluble_nitrogen_amount: float
            amount of soluble nitrogen (kg /mm H20)
        soil_water_runoff_sum: float
            Sum of runoff and soil water for layer (mm H2O)
        saturation_content: float
            volume of water in layer when saturated (mm)

        Returns
        -------
        float
            the concentration of the inorganic pools NO3/NH4 in the top soil layer (kg /mm H20)

        References
        -------
        pseudocode_soil S.6.C.1
        """
        return soluble_nitrogen_amount * (1 - (exp(-soil_water_runoff_sum/saturation_content))/soil_water_runoff_sum)

    @staticmethod
    def _determine_NO3_runoff_amount(nitrogen_concentration: float,
                                     runoff: float,
                                     runoff_extraction_coef=0.1) -> float:
        """This method determines the amount of NO3 runoff for the first layer

        Parameters
        ----------
        nitrogen_concentration: float
            the concentration of the inorganic pools NO3/NH4 in the top soil layer (kg N/mm H20)
        runoff_extraction_coef: float default for NO3 = 0.1
            coefficient of extraction for runoff (unitless)
        runoff: float
            daily runoff of H2O (mm)

        Returns
        -------
        float:
            the amount of NO3 runoff from the first layer (kg/ha)

        References
        -------
        pseudocode_soil S.6.C.2
        """
        return nitrogen_concentration*runoff*runoff_extraction_coef

    @staticmethod
    def _determine_NH4_runoff_amount(nitrogen_concentration: float,
                                     runoff: float,
                                     runoff_extraction_coef=1) -> float:
        """This method determines the amount of NH4 runoff for the first layer

        Parameters
        ----------
        nitrogen_concentration: float
            the concentration of the inorganic pools NO3/NH4 in the top soil layer (kg N/mm H20)
        runoff_extraction_coef: float default for NH4 = 1
            coefficient of extraction for runoff (unitless)
        runoff: float
            daily runoff of H2O (mm)

        Returns
        -------
        float:
            the amount of NH4 runoff from the first layer (kg/ha)

        References
        -------
        pseudocode_soil S.6.C.2
        """
        return nitrogen_concentration*runoff*runoff_extraction_coef
