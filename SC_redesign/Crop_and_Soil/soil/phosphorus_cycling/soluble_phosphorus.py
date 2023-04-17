from typing import Optional
from math import exp

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import MEGAGRAMS_TO_KILOGRAMS, HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_LITERS, CUBIC_MILLIMETERS_TO_CUBIC_METERS, KILOGRAMS_TO_MILLIGRAMS, MILLIGRAMS_TO_KILOGRAMS

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

    def daily_update_routine(self, runoff: float, field_size: float) -> None:
        """Removes phosphorus from the top layer of soil due to runoff, and moves phosphorus downward through the soil
            profile as water percolates through it.

        Parameters
        ----------
        runoff : float
            Amount of rainfall that runs off the field on the current day (mm)
        field_size : float
            Size of the field (ha)

        """
        if runoff:
            self._remove_runoff_phosphorus_from_top_soil(runoff, field_size)

        for layer_index in range(len(self.data.soil_layers)):
            current_layer = self.data.soil_layers[layer_index]
            soil_phosphorus_concentration = self._determine_soil_phosphorus_concentration(
                current_layer.labile_phosphorus_content, current_layer.bulk_density, current_layer.layer_thickness,
                field_size)

            isotherm_slope = self._determine_isotherm_slope(current_layer.percent_clay_content)
            isotherm_intercept = self._determine_isotherm_intercept(isotherm_slope)

            dissolved_reactive_phosphorus_leachate = self._determine_dissolved_reactive_phosphorus_leachate(
                soil_phosphorus_concentration, isotherm_slope, isotherm_intercept)

            percolated_water_in_liters = self._determine_percolated_water_volume(current_layer.percolated_water,
                                                                                 field_size)

            dissolved_reactive_phosphorus_leachate_in_mg = dissolved_reactive_phosphorus_leachate * \
                percolated_water_in_liters

            dissolved_reactive_phosphorus_leachate_in_kg_per_ha = (dissolved_reactive_phosphorus_leachate_in_mg *
                                                                   MILLIGRAMS_TO_KILOGRAMS) / field_size

            actual_dissolved_reactive_phosphorus_leachate = min(current_layer.labile_phosphorus_content,
                                                                dissolved_reactive_phosphorus_leachate_in_kg_per_ha)

            if layer_index != len(self.data.soil_layers) - 1:
                next_layer = self.data.soil_layers[layer_index + 1]
            else:
                next_layer = self.data.vadose_zone_layer

            current_layer.labile_phosphorus_content -= actual_dissolved_reactive_phosphorus_leachate
            next_layer.labile_phosphorus_content += actual_dissolved_reactive_phosphorus_leachate

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
            self.data.soil_layers[0].layer_thickness, field_size)
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
        APLE Theoretical Documentation eqn. [16]

        """
        return 4.726 * isotherm_slope - 8.97

    @staticmethod
    def _determine_soil_phosphorus_concentration(labile_phosphorus: float, bulk_density: float,
                                                 layer_thickness: float, field_size: float) -> float:
        """Calculates the concentration of phosphorus in a soil layer.

        Parameters
        ----------
        labile_phosphorus : float
            Labile phosphorus content of this soil layer (kg phosphorus per ha)
        bulk_density : float
            Bulk density of the soil layer (Megagram per cubic meter)
        layer_thickness : float
            Thickness of the soil layer (mm)
        field_size : float
            Area of the field (ha)

        Returns
        -------
        float
            The concentration of phosphorus in the soil layer (mg phosphorous per kg soil)

        """
        soil_volume_in_cubic_meters = layer_thickness * (field_size * HECTARES_TO_SQUARE_MILLIMETERS) * \
            CUBIC_MILLIMETERS_TO_CUBIC_METERS
        soil_mass_in_kg = bulk_density * MEGAGRAMS_TO_KILOGRAMS * soil_volume_in_cubic_meters
        soil_phosphorus_mass_in_mg = labile_phosphorus * field_size * KILOGRAMS_TO_MILLIGRAMS
        return soil_phosphorus_mass_in_mg / soil_mass_in_kg

    @staticmethod
    def _determine_dissolved_reactive_phosphorus_leachate(soil_phosphorus: float, isotherm_slope: float,
                                                          isotherm_intercept: float) -> float:
        """Calculates how much phosphorus can be leached out of a soil layer by percolation from layer.

        Parameters
        ----------
        soil_phosphorus : float
            Concentration of phosphorus in the soil layer (mg phosphorous per kg soil)
        isotherm_slope : float
            Slope of the phosphorus sorption isotherm (unitless)
        isotherm_intercept
             Intercept of the phosphorus sorption isotherm (unitless)

        Returns
        -------
        float
            Concentration of dissolved phosphorus in the soil water that can be leached into the next layer (mg per L)

        References
        ----------
        APLE Theoretical Documentation eqn. [14]

        Notes
        -----
        TODO: this equation is in the code, both old RuFaS and SurPhos, but is not in the documentation. Also not clear
            what the units are, amend this notes section after talking with Pete.

        """
        dissolved_reactive_phosphorus_leachate = exp((soil_phosphorus * 1.5 - isotherm_intercept) / isotherm_slope)
        return min(20.0, dissolved_reactive_phosphorus_leachate)

    @staticmethod
    def _determine_percolated_water_volume(percolated_water: float, field_size: float) -> float:
        """Calculates the volume of water that is percolated out of a soil layer.

        Parameters
        ----------
        percolated_water : float
            Amount of water that percolated out of the soil layer on a given day (mm)
        field_size : float
            Size of the field (ha)

        Returns
        -------
        float
            Volume of water that percolated out of the soil on the current day (L)

        """
        percolated_water_in_cubic_millimeters = percolated_water * field_size * HECTARES_TO_SQUARE_MILLIMETERS
        percolated_water_in_liters = percolated_water_in_cubic_millimeters * CUBIC_MILLIMETERS_TO_LITERS
        return percolated_water_in_liters
