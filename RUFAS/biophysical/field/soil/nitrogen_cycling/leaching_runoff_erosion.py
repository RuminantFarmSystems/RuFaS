from math import exp, log
from typing import Optional

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData

"""
The following are empirical coefficients with the units (kg / L).
"""

NITRATE_RUNOFF_COEFFICIENT = 0.2
AMMONIUM_RUNOFF_COEFFICIENT = 0.2


class LeachingRunoffErosion:
    """
    Manages the movement and loss of nitrogen through erosion and leaching within the soil profile, aligning with SWAT
    sections 4:2.1, 2.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track nitrogen leaching and runoff in the soil profile, creates
        new one if one is not provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha).

    Attributes
    ----------
    data : SoilData
        Stores the SoilData object for tracking nitrogen movement processes.

    References
    ----------
    Vadas, P. A., & Powell, J. M. (2019). Nutrient mass balance and fate in dairy cattle lots with different surface
    materials. Transactions of the ASABE, 62(1), 131–138. https://doi.org/10.13031/trans.12901. This study's findings
    are instrumental in calibrating the coefficients used in this module for accurate simulation of nitrogen loss
    dynamics.

    Notes
    -----
    The empirical coefficients were calibrated using RuFaS with data from a study by Pete Vadas and J. Mark Powell at
    the USDA, focusing on nutrient mass balance and fate in dairy cattle lots with different surface materials.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def leach_runoff_and_erode_nitrogen(self, field_size: float) -> None:
        """This is the main routine for updating nitrogen leaching, runoff, and erosion within the soil profile.

        Parameters
        ----------
        field_size : float
            Size of the field (ha)

        Notes
        -----
        This equation simply calls two helper methods, one executes runoff and erosion operations and the second
        executes leaching operations.

        """
        self._erode_nitrogen(field_size)
        self._leach_nitrogen()

    def _erode_nitrogen(self, field_size: float) -> None:
        """
        This method handles the erosion of nitrogen and updating the soil profile accordingly.

        Parameters
        ----------
        field_size : float
            Size of the field (ha).

        Notes
        -----
        This method only removes nitrogen from the top soil layer. Inorganic nitrogen is removed by runoff, while
        organic nitrogen is removed by sediment erosion.

        """
        surface_layer = self.data.soil_layers[0]

        self.data.nitrate_runoff = 0.0
        self.data.ammonium_runoff = 0.0
        self.data.eroded_fresh_organic_nitrogen = 0.0
        self.data.eroded_stable_organic_nitrogen = 0.0
        self.data.eroded_active_organic_nitrogen = 0.0

        if self.data.accumulated_runoff > 0.0:
            nitrate_conc_in_mobile_h20 = self._calculate_nitrogen_conc_in_mobile_water(
                surface_layer.nitrate_content,
                self.data.accumulated_runoff,
                surface_layer.percolated_water,
                surface_layer.saturation_content,
            )
            nitrates_lost_to_runoff = (
                NITRATE_RUNOFF_COEFFICIENT * nitrate_conc_in_mobile_h20 * self.data.accumulated_runoff
            )

            ammonium_conc_in_mobile_h20 = self._calculate_nitrogen_conc_in_mobile_water(
                surface_layer.ammonium_content,
                self.data.accumulated_runoff,
                surface_layer.percolated_water,
                surface_layer.saturation_content,
            )

            ammonium_lost_to_runoff = (
                AMMONIUM_RUNOFF_COEFFICIENT * ammonium_conc_in_mobile_h20 * self.data.accumulated_runoff
            )

            surface_layer.nitrate_content -= nitrates_lost_to_runoff
            self.data.nitrate_runoff = nitrates_lost_to_runoff
            self.data.annual_runoff_nitrates_total += nitrates_lost_to_runoff * field_size

            surface_layer.ammonium_content -= ammonium_lost_to_runoff
            self.data.ammonium_runoff = ammonium_lost_to_runoff
            self.data.annual_runoff_ammonium_total += ammonium_lost_to_runoff * field_size

        if self.data.eroded_sediment > 0.0:
            fresh_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                surface_layer.fresh_organic_nitrogen_content,
                surface_layer.bulk_density,
                surface_layer.layer_thickness,
                field_size,
                self.data.eroded_sediment,
            )
            stable_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                surface_layer.stable_organic_nitrogen_content,
                surface_layer.bulk_density,
                surface_layer.layer_thickness,
                field_size,
                self.data.eroded_sediment,
            )
            active_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                surface_layer.active_organic_nitrogen_content,
                surface_layer.bulk_density,
                surface_layer.layer_thickness,
                field_size,
                self.data.eroded_sediment,
            )

            surface_layer.fresh_organic_nitrogen_content -= fresh_organic_nitrogen_lost
            self.data.eroded_fresh_organic_nitrogen = fresh_organic_nitrogen_lost
            self.data.annual_eroded_fresh_organic_nitrogen_total += fresh_organic_nitrogen_lost * field_size

            surface_layer.stable_organic_nitrogen_content -= stable_organic_nitrogen_lost
            self.data.eroded_stable_organic_nitrogen = stable_organic_nitrogen_lost
            self.data.annual_eroded_stable_organic_nitrogen_total += stable_organic_nitrogen_lost * field_size

            surface_layer.active_organic_nitrogen_content -= active_organic_nitrogen_lost
            self.data.eroded_active_organic_nitrogen = active_organic_nitrogen_lost
            self.data.annual_eroded_active_organic_nitrogen_total += active_organic_nitrogen_lost * field_size

    def _leach_nitrogen(self) -> None:
        """
        Removes leached nitrogen from each soil layer, then adds the leached nitrogen to the next layer.

        Notes
        -----
        This method determines how much nitrogen will be leached out of each layer without being influenced at all by
        the amount of nitrogen leaching into that layer. It achieves this by calculating the amounts leached out of each
        layer, storing those amounts in a dictionary, appending that dictionary to a list (`percolated_nitrogen`), then
        iterating through the soil profile a second time and adding the leached nitrogen into the appropriate layer. The
        bottom soil layer leaches into the vadose zone.

        """
        percolated_nitrogen = []

        layer_count = len(self.data.soil_layers)
        self.data.set_vectorized_layer_attribute("percolated_nitrates", [0.0] * layer_count)
        self.data.set_vectorized_layer_attribute("percolated_ammonium", [0.0] * layer_count)
        self.data.set_vectorized_layer_attribute("percolated_active_organic_nitrogen", [0.0] * layer_count)

        for layer in self.data.soil_layers:
            if layer.percolated_water == 0.0:
                nitrogen_percolated_to_next_layer = {
                    "nitrates": 0,
                    "ammonium": 0,
                    "active_organic": 0,
                }
                percolated_nitrogen.append(nitrogen_percolated_to_next_layer)
                continue
            if layer.top_depth == 0:
                runoff_water = self.data.accumulated_runoff
            else:
                runoff_water = 0

            nitrate_concentration_in_mobile_water = self._calculate_nitrogen_conc_in_mobile_water(
                nitrogen_content=layer.nitrate_content,
                percolated_water_amount=layer.percolated_water,
                runoff_water_amount=runoff_water,
                soil_saturation_point=layer.saturation_content,
            )
            nitrates_lost = nitrate_concentration_in_mobile_water * layer.percolated_water

            ammonium_concentration_in_mobile_water = self._calculate_nitrogen_conc_in_mobile_water(
                nitrogen_content=layer.ammonium_content,
                percolated_water_amount=layer.percolated_water,
                runoff_water_amount=runoff_water,
                soil_saturation_point=layer.saturation_content,
            )
            ammonium_lost = ammonium_concentration_in_mobile_water * layer.percolated_water

            layer.nitrate_content -= nitrates_lost
            layer.ammonium_content -= ammonium_lost

            layer.percolated_nitrates = nitrates_lost
            layer.percolated_ammonium = ammonium_lost

            nitrogen_percolated_to_next_layer = {"nitrates": nitrates_lost, "ammonium": ammonium_lost}
            percolated_nitrogen.append(nitrogen_percolated_to_next_layer)

        layers_leached_into = self.data.soil_layers[1:] + [self.data.vadose_zone_layer]
        for index in range(len(layers_leached_into)):
            current_layer = layers_leached_into[index]
            amounts_leached_into_layer = percolated_nitrogen[index]

            current_layer.nitrate_content += amounts_leached_into_layer.get("nitrates")
            current_layer.ammonium_content += amounts_leached_into_layer.get("ammonium")

    @staticmethod
    def _determine_erosion_nitrogen_loss_content(
        nitrogen_erosion_concentration: float,
        daily_soil_lost: float,
        enrichment_ratio: float,
    ) -> float:
        """
        This method determines nitrogen mass loss in erosion.

        Parameters
        ----------
        nitrogen_erosion_concentration: float
            The soil nitrogen concentrations for the Fresh, Active, and Stable pools in soil (mg / kg).
        daily_soil_lost: float
            Daily soil loss (Metric Tons / ha).
        enrichment_ratio: float
            Enrichment ratio (unitless).

        Returns
        -------
        float
            nitrogen mass loss in erosion (kg/ha).

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.2.1

        """
        return 0.001 * nitrogen_erosion_concentration * daily_soil_lost * enrichment_ratio

    @staticmethod
    def _determine_enrichment_ratio(daily_soil_lost: float) -> float:
        """
        This method determines the enrichment ratio.

        Parameters
        ----------
        daily_soil_lost: float
            Daily soil loss (Metric Tons/ha).

        Returns
        -------
        float
            Enrichment ratio (unitless).

        References
        ----------
        pseudocode_soil S.4.C.5

        """
        return exp(1.21 - 0.16 * log(daily_soil_lost * 1000))

    @staticmethod
    def _calculate_eroded_organic_nitrogen(
        nitrogen_content: float,
        bulk_density: float,
        layer_thickness: float,
        field_size: float,
        eroded_sediment: float,
    ) -> float:
        """
        This method calculates how much organic nitrogen is lost from the field via eroded sediment.

        Parameters
        ----------
        nitrogen_content : float
            Nitrogen content of the given pool of the top soil layer (kg / ha).
        bulk_density : float
            The density of the top soil layer (Megagrams / cubic meter).
        layer_thickness : float
            The thickness of the top layer of soil (mm).
        field_size : float
            Size of the field (ha).
        eroded_sediment : float
            Amount of sediment that was eroded from the field on the current day (metric tons).

        Returns
        -------
        float
            Amount of nitrogen lost to erosion from the given organic pool in the top soil layer (kg / ha).

        Notes
        -----
        Nitrogen can only be removed from the field by erosion from the top layer of soil, so this method should not be
        used on any other layers of soil.

        """
        nitrogen_concentration = LayerData.determine_soil_nutrient_concentration(
            nitrogen_content, bulk_density, layer_thickness, field_size
        )
        sediment_content_loss = eroded_sediment / field_size
        enrichment_ratio = LeachingRunoffErosion._determine_enrichment_ratio(sediment_content_loss)
        nitrogen_lost = LeachingRunoffErosion._determine_erosion_nitrogen_loss_content(
            nitrogen_concentration, sediment_content_loss, enrichment_ratio
        )
        return min(nitrogen_content, nitrogen_lost)

    @staticmethod
    def _calculate_nitrogen_conc_in_mobile_water(
        nitrogen_content: float,
        runoff_water_amount: float,
        percolated_water_amount: float,
        soil_saturation_point: float,
    ) -> float:
        """
        Calculates how much nitrogen is lost from the given pool on the current day.

        Parameters
        ----------
        nitrogen_content : float
            The content of nitrogen in the given pool in the current layer of soil (kg / ha).
        runoff_water_amount : float
            Amount of surface water runoff on this day (mm). Zero for all layers other than the surface layer
        percolated_water_amount : float
            Amount of water that percolated out of the current soil layer on this day (mm).
        soil_saturation_point : float
            Volume of water in layer when saturated (mm).

        Returns
        -------
        float
            The concentration of nitrogen in the mobile water for a given layer (kg N/ mm H2O).

        Notes
        -----
        This method is described for nitrate in the SWAT+ documentation Equation 4:2.1.2. Here we assume the theta_e,
        the fraction of porosity from which anions are excluded, to be zero

        """

        total_mobile_water = runoff_water_amount + percolated_water_amount
        mobile_water_nitrogen_concentration = (
            nitrogen_content * (1 - exp(-total_mobile_water / (1 * soil_saturation_point))) / total_mobile_water
        )

        return mobile_water_nitrogen_concentration
