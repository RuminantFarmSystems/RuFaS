from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import MEGAGRAMS_TO_KILOGRAMS, HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_LITERS

"""
This module tracks the movement of phosphorus in the soil profile based on equations from APLE.
"""


class SolublePhosphorus:

    def __init__(self, soil_data: Optional[SoilData] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.

        """
        self.data = soil_data or SoilData()

    def daily_update_routine(self, runoff: float) -> None:
        """Removes phosphorus from the top layer of soil due to runoff, and moves phosphorus downward through the soil
            profile as water percolates through it.

        Parameters
        ----------
        runoff : float
            Amount of rainfall that runs off the field on the current day (mm)

        """
        if runoff:
            self._remove_runoff_phosphorus_from_top_soil(runoff)

    def _remove_runoff_phosphorus_from_top_soil(self, runoff: float, field_size) -> None:
        """This method calculates how much phosphorus is lost from the top soil layer to runoff, then removes that
            amount.

        Parameters
        ----------
        runoff : float
            Amount of rainfall that runs off the field on the current day (mm)
        field_size : float
            Size of the field (ha)

        References
        ----------
        APLE Theoretical eqn. [9] (used to calculate `top_layer_dissolved_reactive_phosphorus_runoff`)

        """
        runoff_in_liters = (runoff * field_size * HECTARES_TO_SQUARE_MILLIMETERS) * CUBIC_MILLIMETERS_TO_LITERS
        runoff_in_liters_per_hectare = runoff_in_liters / field_size

        top_layer_soil_phosphorus_concentration = self._determine_soil_phosphorus_concentration(
            self.data.soil_layers[0].labile_phosphorus_content, self.data.soil_layers[0].bulk_density,
            self.data.soil_layers[0].layer_thickness)
        extraction_coefficient = 0.005
        top_layer_dissolved_reactive_phosphorus_runoff = top_layer_soil_phosphorus_concentration * \
            extraction_coefficient * runoff_in_liters_per_hectare * (10 ** (-6))

        adjusted_phosphorus_runoff = min(self.data.soil_layers[0].labile_phosphorus_content,
                                         top_layer_dissolved_reactive_phosphorus_runoff)
        self.data.soil_layers[0].labile_phosphorus_content -= adjusted_phosphorus_runoff
        self.data.annual_soil_phosphorus_runoff += adjusted_phosphorus_runoff * field_size

    # --- Static methods ---
    @staticmethod
    def _determine_isotherm_slope(percent_clay_content: float) -> float:
        """Calculates the slope of the linear phosphorus sorption isotherm.

        Parameters
        ----------
        percent_clay_content : float
            Percent clay content of a soil layer, expressed in the range [0, 100] (unitless)

        Returns
        -------
        float
            The slope of the phosphorus sorption isotherm (unitless)

        References
        ----------
        APLE Theoretical Documentation eqn. [15]

        """
        return 173.51 * (percent_clay_content / 100) + 8.48

    @staticmethod
    def _determine_isotherm_intercept(isotherm_slope: float) -> float:
        """Calculates the intercept of the linear phosphorus sorption isotherm.

        Parameters
        ----------
        isotherm_slope : float
            The slope of the phosphorus sorption isotherm (unitless)

        Returns
        -------
        float
            The intercept of the phosphorus sorption isotherm (unitless)

        References
        ----------
        APLE Theoretical Documentation eqn. [15]

        """
        return 4.726 * isotherm_slope - 8.97

    @staticmethod
    def _determine_soil_phosphorus_concentration(labile_phosphorus: float, bulk_density: float,
                                                 layer_thickness: float) -> float:
        """Calculates the concentration of phosphorus in a soil layer.

        Parameters
        ----------
        labile_phosphorus : float
            Labile phosphorus content of this soil layer (kg phosphorus per ha)
        bulk_density : float
            Bulk density of the soil layer (Megagram per cubic meter)
        layer_thickness : float
            Thickness of the soil layer (mm)

        Returns
        -------
        float
            The concentration of phosphorus in the soil layer (mg phosphorous per kg soil)

        """
        density_in_kg = bulk_density * MEGAGRAMS_TO_KILOGRAMS
        pass
