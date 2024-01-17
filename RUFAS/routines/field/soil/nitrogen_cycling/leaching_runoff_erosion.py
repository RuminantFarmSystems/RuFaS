from typing import Optional
from math import exp, log

from RUFAS.routines.field.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS, CUBIC_MILLIMETERS_TO_LITERS
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData


"""
This module handles the movement and loss of nitrogen due to erosion and leaching within the soil profile, and is based
on SWAT sections 4:2.1, 2
"""

"""
These coefficients were determined empirically by calibrating RuFaS with data from an experiment conducted by Pete Vadas
and J. Mark Powell at the USDA.

Reference:
Vadas, P. A., & Powell, J. M. (2019). Nutrient mass balance and fate in dairy cattle lots with different surface
materials. Transactions of the ASABE, 62(1), 131–138. https://doi.org/10.13031/trans.12901

"""
NITRATE_RUNOFF_COEFFICIENT = 1e-8
AMMONIUM_RUNOFF_COEFFICIENT = 8e-6
NITRATE_PERCOLATION_COEFFICIENT = 6e-8
AMMONIUM_PERCOLATION_COEFFICIENT = 4e-6
ACTIVE_ORGANIC_NITROGEN_PERCOLATION_COEFFICIENT = 5e-8


class LeachingRunoffErosion:

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track nitrogen leaching and runoff in the soil profile, creates
            new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
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
        self._leach_nitrogen(field_size)

    def _erode_nitrogen(self, field_size: float) -> None:
        """This method handles the erosion of nitrogen and updating the soil profile accordingly.

        Parameters
        ----------
        field_size : float
            Size of the field (ha)

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
            nitrates_lost_to_runoff = self._calculate_nitrogen_removed_by_water(
                surface_layer.nitrate_content, self.data.accumulated_runoff, NITRATE_RUNOFF_COEFFICIENT,
                surface_layer.bulk_density, surface_layer.layer_thickness, field_size
            )

            ammonium_lost_to_runoff = self._calculate_nitrogen_removed_by_water(
                surface_layer.ammonium_content, self.data.accumulated_runoff, AMMONIUM_RUNOFF_COEFFICIENT,
                surface_layer.bulk_density, surface_layer.layer_thickness, field_size
            )

            surface_layer.nitrate_content -= nitrates_lost_to_runoff
            self.data.nitrate_runoff = nitrates_lost_to_runoff
            self.data.annual_runoff_nitrates_total += nitrates_lost_to_runoff * field_size

            surface_layer.ammonium_content -= ammonium_lost_to_runoff
            self.data.ammonium_runoff = ammonium_lost_to_runoff
            self.data.annual_runoff_ammonium_total += ammonium_lost_to_runoff * field_size

        if self.data.eroded_sediment > 0.0:
            fresh_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                surface_layer.fresh_organic_nitrogen_content, surface_layer.bulk_density,
                surface_layer.layer_thickness, field_size, self.data.eroded_sediment)
            stable_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                surface_layer.stable_organic_nitrogen_content, surface_layer.bulk_density,
                surface_layer.layer_thickness, field_size, self.data.eroded_sediment)
            active_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                surface_layer.active_organic_nitrogen_content, surface_layer.bulk_density,
                surface_layer.layer_thickness, field_size, self.data.eroded_sediment)

            surface_layer.fresh_organic_nitrogen_content -= fresh_organic_nitrogen_lost
            self.data.eroded_fresh_organic_nitrogen = fresh_organic_nitrogen_lost
            self.data.annual_eroded_fresh_organic_nitrogen_total += fresh_organic_nitrogen_lost * field_size

            surface_layer.stable_organic_nitrogen_content -= stable_organic_nitrogen_lost
            self.data.eroded_stable_organic_nitrogen = stable_organic_nitrogen_lost
            self.data.annual_eroded_stable_organic_nitrogen_total += stable_organic_nitrogen_lost * field_size

            surface_layer.active_organic_nitrogen_content -= active_organic_nitrogen_lost
            self.data.eroded_active_organic_nitrogen = active_organic_nitrogen_lost
            self.data.annual_eroded_active_organic_nitrogen_total += active_organic_nitrogen_lost * field_size

    def _leach_nitrogen(self, field_size: float) -> None:
        """
        Removes leached nitrogen from each soil layer, then adds the leached nitrogen to the next layer.

        Parameters
        ----------
        field_size : float
            Size of the field in which nitrogen is being leached (ha).

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
                    "active_organic": 0
                }
                percolated_nitrogen.append(nitrogen_percolated_to_next_layer)
                continue

            nitrates_lost = self._calculate_nitrogen_removed_by_water(
                layer.nitrate_content, layer.percolated_water, NITRATE_PERCOLATION_COEFFICIENT, layer.bulk_density,
                layer.layer_thickness, field_size
            )
            ammonium_lost = self._calculate_nitrogen_removed_by_water(
                layer.ammonium_content, layer.percolated_water, AMMONIUM_PERCOLATION_COEFFICIENT, layer.bulk_density,
                layer.layer_thickness, field_size
            )
            active_organic_nitrogen_lost = self._calculate_nitrogen_removed_by_water(
                layer.active_organic_nitrogen_content, layer.percolated_water,
                ACTIVE_ORGANIC_NITROGEN_PERCOLATION_COEFFICIENT, layer.bulk_density, layer.layer_thickness, field_size
            )

            layer.nitrate_content -= nitrates_lost
            layer.ammonium_content -= ammonium_lost
            layer.active_organic_nitrogen_content -= active_organic_nitrogen_lost

            layer.percolated_nitrates = nitrates_lost
            layer.percolated_ammonium = ammonium_lost
            layer.percolated_active_organic_nitrogen = active_organic_nitrogen_lost

            nitrogen_percolated_to_next_layer = {
                "nitrates": nitrates_lost,
                "ammonium": ammonium_lost,
                "active_organic": active_organic_nitrogen_lost
            }
            percolated_nitrogen.append(nitrogen_percolated_to_next_layer)

        layers_leached_into = self.data.soil_layers[1:] + [self.data.vadose_zone_layer]
        for index in range(len(layers_leached_into)):
            current_layer = layers_leached_into[index]
            amounts_leached_into_layer = percolated_nitrogen[index]

            current_layer.nitrate_content += amounts_leached_into_layer.get("nitrates")
            current_layer.ammonium_content += amounts_leached_into_layer.get("ammonium")
            current_layer.active_organic_nitrogen_content += amounts_leached_into_layer.get("active_organic")

    @staticmethod
    def _determine_erosion_nitrogen_loss_content(nitrogen_erosion_concentration: float,
                                                 daily_soil_lost: float,
                                                 enrichment_ratio: float) -> float:
        """This method determines nitrogen mass loss in erosion

        Parameters
        ----------
        nitrogen_erosion_concentration: float
            the soil nitrogen concentrations for the Fresh, Active, and Stable pools in soil (mg / kg)
        daily_soil_lost: float
            daily soil loss (Metric Tons / ha)
        enrichment_ratio: float
            Enrichment ratio (unitless)

        Returns
        -------
        float
            nitrogen mass loss in erosion (kg/ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.2.1

        """
        return 0.001 * nitrogen_erosion_concentration * daily_soil_lost * enrichment_ratio

    @staticmethod
    def _determine_enrichment_ratio(daily_soil_lost: float) -> float:
        """This method determines the enrichment ratio

        Parameters
        ----------
        daily_soil_lost: float
            daily soil loss (Metric Tons/ha)

        Returns
        -------
        float
            enrichment ratio (unitless)

        References
        ----------
        pseudocode_soil S.4.C.5

        Notes
        -----
        TODO These numbers are modified ans suspected of retrieved from other references instead of SWAT, kept here
        issue #486

        """
        return exp(1.21 - 0.16 * log(daily_soil_lost * 1000))

    @staticmethod
    def _calculate_eroded_organic_nitrogen(nitrogen_content: float, bulk_density: float, layer_thickness: float,
                                           field_size: float, eroded_sediment: float) -> float:
        """This method calculates how much organic nitrogen is lost from the field via eroded sediment.

        Parameters
        ----------
        nitrogen_content : float
            Nitrogen content of the given pool of the top soil layer (kg / ha)
        bulk_density : float
            The density of the top soil layer (Megagrams / cubic meter)
        layer_thickness : float
            The thickness of the top layer of soil (mm)
        field_size : float
            Size of the field (ha)
        eroded_sediment : float
            Amount of sediment that was eroded from the field on the current day (metric tons)

        Returns
        -------
        float
            Amount of nitrogen lost to erosion from the given organic pool in the top soil layer (kg / ha)

        Notes
        -----
        Nitrogen can only be removed from the field by erosion from the top layer of soil, so this method should not be
        used on any other layers of soil.

        """
        nitrogen_concentration = LayerData.determine_soil_nutrient_concentration(nitrogen_content, bulk_density,
                                                                                 layer_thickness, field_size)
        sediment_content_loss = eroded_sediment / field_size
        enrichment_ratio = LeachingRunoffErosion._determine_enrichment_ratio(sediment_content_loss)
        nitrogen_lost = LeachingRunoffErosion._determine_erosion_nitrogen_loss_content(nitrogen_concentration,
                                                                                       sediment_content_loss,
                                                                                       enrichment_ratio)
        return min(nitrogen_content, nitrogen_lost)

    @staticmethod
    def _calculate_nitrogen_removed_by_water(
            nitrogen_content: float,
            water_amount: float,
            extraction_coefficient: float,
            bulk_density: float,
            layer_thickness: float,
            field_size: float,
    ) -> float:
        """
        Calculates how much nitrogen is lost from the given pool on the current day.

        Parameters
        ----------
        nitrogen_content : float
            The content of nitrogen in the given pool in the current layer of soil (kg / ha).
        water_amount : float
            Amount of water that percolated out of the current soil layer on this day (mm).
        extraction_coefficient : float
            Coefficient for adjusting the amount leached based on the pool leached from (L ^ -1).
        bulk_density : float
            Density of the soil layer containing the nitrogen (Megagram / cubic meter).
        layer_thickness : float
            Thickness of the soil layer containing the nitrogen (mm).
        field_size : float
            Size of the field containing the nitrogen (ha).

        Returns
        -------
        float
            The amount of nitrogen that leaches out of the current pool and into the next lowest layer on the current
            day (kg / ha).

        Notes
        -----
        This method for calculating nitrogen loss due to water movement is very simplistic and is applied to loss
        through different pathways, including leaching (nitrogen removed by water percolating through a soil layer) and
        runoff (nitrogen removed by water running off a soil profile). This approach multiplies the amount of nitrogen
        in the pool that is experiencing loss by the amount of water that is removing the nitrogen, and then multiplies
        that product by an empirical factor to compute the actual amount of nitrogen loss. This approach has been
        successfully applied in modelling nutrient loss for other nutrients, principally phosphorus in Pete Vadas'
        SurPhos model.

        """
        water_amount_in_liters = \
            water_amount * field_size * HECTARES_TO_SQUARE_MILLIMETERS * CUBIC_MILLIMETERS_TO_LITERS

        nitrogen_content_in_mg_per_kg = LayerData.determine_soil_nutrient_concentration(
            nitrogen_content,
            bulk_density,
            layer_thickness,
            field_size
        )

        nitrogen_leached_in_mg_per_kg = nitrogen_content_in_mg_per_kg * extraction_coefficient * water_amount_in_liters

        nitrogen_leached_in_kg_per_ha = LayerData.determine_soil_nutrient_area_density(
            nitrogen_leached_in_mg_per_kg,
            bulk_density,
            layer_thickness,
            field_size
        )

        return min(nitrogen_content, nitrogen_leached_in_kg_per_ha)
