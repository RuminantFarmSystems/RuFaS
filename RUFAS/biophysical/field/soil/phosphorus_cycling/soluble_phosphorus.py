from math import exp, inf
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


class SolublePhosphorus:
    """
    Tracks the movement of phosphorus in the soil profile using equations from the APLE (Agricultural Phosphorus Loss
    Estimator) model.

    Parameters
    ----------
    soil_data : SoilData, optional
        An instance of SoilData for tracking the movement of phosphorus through the soil profile. If not provided, a new
        instance will be created with the specified field size.
    field_size : float, optional
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object that stores and manages the phosphorus data within the soil profile.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """
        This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track phosphorus as it moves through the soil profile, creates
            new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha).

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def daily_update_routine(self, runoff: float, field_size: float) -> None:
        """
        Removes phosphorus from the top layer of soil due to runoff, and moves phosphorus downward through the soil
        profile as water percolates through it.

        Parameters
        ----------
        runoff : float
            Amount of rainfall that runs off the field on the current day (mm).
        field_size : float
            Size of the field (ha).

        Notes
        -----
        This method is responsible for adjusting phosphorus levels in the soil profile as dictated by the two processes
        it simulates. First, if there is any runoff on the current day, it calculates how much phosphorus is lost from
        the top soil layer as a result and removes it. Then it iterates through the soil profile, calculating how much
        phosphorus is carried downward by percolating water and moving that phosphorus between the layers.

        """
        self.data.soil_phosphorus_runoff = 0.0
        if runoff > 0:
            phosphorus_runoff = self._determine_phosphorus_runoff_from_top_soil(
                runoff,
                field_size,
                self.data.soil_layers[0].labile_inorganic_phosphorus_content,
                self.data.soil_layers[0].bulk_density,
                self.data.soil_layers[0].layer_thickness,
            )
            self.data.soil_layers[0].labile_inorganic_phosphorus_content -= phosphorus_runoff
            self.data.soil_phosphorus_runoff = phosphorus_runoff
            self.data.annual_soil_phosphorus_runoff += phosphorus_runoff

        for layer_index in range(len(self.data.soil_layers)):
            current_layer = self.data.soil_layers[layer_index]
            current_layer.percolated_phosphorus = 0.0

            if layer_index != len(self.data.soil_layers) - 1:
                next_layer = self.data.soil_layers[layer_index + 1]
            else:
                next_layer = self.data.vadose_zone_layer

            phosphorus_percolated = self._determine_phosphorus_percolated_from_layer(
                current_layer.labile_inorganic_phosphorus_content,
                current_layer.bulk_density,
                current_layer.layer_thickness,
                current_layer.clay_fraction,
                current_layer.percolated_water,
                field_size,
            )

            current_layer.percolated_phosphorus = phosphorus_percolated
            current_layer.labile_inorganic_phosphorus_content -= phosphorus_percolated
            next_layer.labile_inorganic_phosphorus_content += phosphorus_percolated

    # --- Static methods ---
    @staticmethod
    def _determine_phosphorus_runoff_from_top_soil(
        runoff: float,
        field_size: float,
        labile_phosphorus: float,
        bulk_density: float,
        layer_thickness: float,
    ) -> float:
        """
        This method calculates how much phosphorus is lost from the top soil layer to runoff.

        Parameters
        ----------
        runoff : float
            Amount of rainfall that runs off the field on the current day (mm).
        field_size : float
            Size of the field (ha).
        labile_phosphorus : float
            Concentration of labile phosphorus in the soil layer (kg / ha).
        bulk_density : float
            Density of the soil layer (megagrams / cubic meter).
        layer_thickness : float
            Thickness of the soil layer (mm).

        Returns
        -------
        float
            Amount of phosphorus removed from the soil layer by runoff water (kg / ha).

        References
        ----------
        APLE Theoretical eqn. [9] (used to calculate `top_layer_dissolved_reactive_phosphorus_runoff`)

        """
        runoff_in_liters = (
            runoff
            * field_size
            * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
            * GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS
        )
        runoff_in_liters_per_hectare = runoff_in_liters / field_size

        top_layer_soil_phosphorus_concentration = LayerData.determine_soil_nutrient_concentration(
            labile_phosphorus, bulk_density, layer_thickness, field_size
        )
        extraction_coefficient = 0.005
        top_layer_dissolved_reactive_phosphorus_runoff = (
            top_layer_soil_phosphorus_concentration
            * extraction_coefficient
            * runoff_in_liters_per_hectare
            * (10 ** (-6))
        )

        adjusted_phosphorus_runoff = min(labile_phosphorus, top_layer_dissolved_reactive_phosphorus_runoff)
        return adjusted_phosphorus_runoff

    @staticmethod
    def _determine_isotherm_slope(clay_fraction: float) -> float:
        """
        Calculates the slope of the linear phosphorus sorption isotherm.

        Parameters
        ----------
        clay_fraction : float
            Fraction clay content of a soil layer, expressed in the range [0, 1.0] (unitless).

        Returns
        -------
        float
            The slope of the phosphorus sorption isotherm (unitless).

        References
        ----------
        APLE Theoretical Documentation eqn. [15]

        """
        return 173.51 * clay_fraction + 8.48

    @staticmethod
    def _determine_isotherm_intercept(isotherm_slope: float) -> float:
        """
        Calculates the intercept of the linear phosphorus sorption isotherm.

        Parameters
        ----------
        isotherm_slope : float
            The slope of the phosphorus sorption isotherm (unitless).

        Returns
        -------
        float
            The intercept of the phosphorus sorption isotherm (unitless).

        References
        ----------
        APLE Theoretical Documentation eqn. [16]

        """
        return 4.726 * isotherm_slope - 8.97

    @staticmethod
    def _determine_dissolved_reactive_phosphorus_leachate(
        soil_phosphorus: float, isotherm_slope: float, isotherm_intercept: float
    ) -> float:
        """
        Calculates how much phosphorus can be leached out of a soil layer by percolation from layer.

        Parameters
        ----------
        soil_phosphorus : float
            Concentration of phosphorus in the soil layer (mg phosphorous per kg soil).
        isotherm_slope : float
            Slope of the phosphorus sorption isotherm (unitless).
        isotherm_intercept
             Intercept of the phosphorus sorption isotherm (unitless).

        Returns
        -------
        float
            Concentration of dissolved phosphorus in the soil water that can be leached into the next layer (mg / L).

        References
        ----------
        APLE Theoretical Documentation eqn. [14]

        Notes
        -----
        The maximum bound on the Phosphorus concentration of 20 milligrams per liter comes from page 8 of the APLE
        Theoretical documentation, in the paragraph below equations [16].

        """
        try:
            dissolved_reactive_phosphorus_leachate = exp((soil_phosphorus * 1.5 - isotherm_intercept) / isotherm_slope)
        except OverflowError:
            dissolved_reactive_phosphorus_leachate = inf
        return min(20.0, dissolved_reactive_phosphorus_leachate)

    @staticmethod
    def _determine_percolated_water_volume(percolated_water: float, field_size: float) -> float:
        """
        Calculates the volume of water that is percolated out of a soil layer.

        Parameters
        ----------
        percolated_water : float
            Amount of water that percolated out of the soil layer on a given day (mm).
        field_size : float
            Size of the field (ha).

        Returns
        -------
        float
            Volume of water that percolated out of the soil on the current day (L).

        """
        percolated_water_in_cubic_millimeters = (
            percolated_water * field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
        )
        percolated_water_in_liters = (
            percolated_water_in_cubic_millimeters * GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS
        )
        return percolated_water_in_liters

    @staticmethod
    def _determine_phosphorus_percolated_from_layer(
        labile_phosphorus: float,
        bulk_density: float,
        layer_thickness: float,
        clay_fraction: float,
        percolated_water: float,
        field_size: float,
    ) -> float:
        """
        Calculates the actual amount of phosphorus that leaves a soil layer and enters the one below it.

        Parameters
        ----------
        labile_phosphorus : float
            The labile phosphorus content of this layer of soil (kg / ha).
        bulk_density : float
            The density of this soil layer (megagrams / cubic meter).
        layer_thickness : float
            The thickness of this layer of soil (mm).
        clay_fraction : float
            The fraction of clay content expressed of soil in this layer,
            expressed as a number in the range [0, 1.0] (unitless).
        percolated_water : float
            The amount of water that percolated from this soil layer on the current day (mm).
        field_size : float
            The size of the field (ha).

        Returns
        -------
        float
            The amount of phosphorus that leaves this layer of soil on the current day (kg / ha).

        """
        soil_phosphorus_concentration = LayerData.determine_soil_nutrient_concentration(
            labile_phosphorus, bulk_density, layer_thickness, field_size
        )

        isotherm_slope = SolublePhosphorus._determine_isotherm_slope(clay_fraction)
        isotherm_intercept = SolublePhosphorus._determine_isotherm_intercept(isotherm_slope)

        dissolved_reactive_phosphorus_leachate = SolublePhosphorus._determine_dissolved_reactive_phosphorus_leachate(
            soil_phosphorus_concentration, isotherm_slope, isotherm_intercept
        )

        percolated_water_in_liters = SolublePhosphorus._determine_percolated_water_volume(percolated_water, field_size)

        dissolved_reactive_phosphorus_leachate_in_mg = (
            dissolved_reactive_phosphorus_leachate * percolated_water_in_liters
        )

        dissolved_reactive_phosphorus_leachate_in_kg_per_ha = (
            dissolved_reactive_phosphorus_leachate_in_mg * GeneralConstants.MILLIGRAMS_TO_KG
        ) / field_size

        actual_dissolved_reactive_phosphorus_leachate = min(
            labile_phosphorus, dissolved_reactive_phosphorus_leachate_in_kg_per_ha
        )
        return actual_dissolved_reactive_phosphorus_leachate
