from typing import Optional
from math import exp, log

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


"""
This module handles the movement and loss of nitrogen due to erosion and leaching within the soil profile, and is based
on SWAT sections 4:2.1, 2
"""


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
        self._leach_nitrogen()

    def _erode_nitrogen(self, field_size: float) -> None:
        """This method handles the erosion of nitrogen and updating the soil profile accordingly.

        Parameters
        ----------
        field_size : float
            Size of the field (ha)

        References
        ----------
        pseudocode_soil [S.4.C.2] (determines what the runoff extraction coefficient will be for nitrates and ammonium)
        TODO: find literature source for these values, issue #495

        Notes
        -----
        This method only removes nitrogen from the top soil layer. Inorganic nitrogen is removed by runoff, while
        organic nitrogen is removed by sediment erosion. When determining the amounts of nitrates and ammonium lost to
        runoff, 0.1 is used as the runoff extraction coefficient for nitrates and 1.0 for ammonium.

        """
        if self.data.accumulated_runoff > 0.0:
            nitrates_lost_to_runoff = self._calculate_inorganic_nitrogen_loss(
                self.data.soil_layers[0].nitrate_content, self.data.soil_layers[0].water_content,
                self.data.soil_layers[0].saturation_content, self.data.accumulated_runoff, 0.1)
            ammonium_lost_to_runoff = self._calculate_inorganic_nitrogen_loss(
                self.data.soil_layers[0].ammonium_content, self.data.soil_layers[0].water_content,
                self.data.soil_layers[0].saturation_content, self.data.accumulated_runoff, 1.0)

            self.data.soil_layers[0].nitrate_content -= nitrates_lost_to_runoff
            self.data.annual_runoff_nitrates_total += nitrates_lost_to_runoff * field_size

            self.data.soil_layers[0].ammonium_content -= ammonium_lost_to_runoff
            self.data.annual_runoff_ammonium_total += ammonium_lost_to_runoff * field_size

        if self.data.eroded_sediment > 0.0:
            fresh_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                self.data.soil_layers[0].fresh_organic_nitrogen_content, self.data.soil_layers[0].bulk_density,
                self.data.soil_layers[0].layer_thickness, field_size, self.data.eroded_sediment)
            stable_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                self.data.soil_layers[0].stable_organic_nitrogen_content, self.data.soil_layers[0].bulk_density,
                self.data.soil_layers[0].layer_thickness, field_size, self.data.eroded_sediment)
            active_organic_nitrogen_lost = self._calculate_eroded_organic_nitrogen(
                self.data.soil_layers[0].active_organic_nitrogen_content, self.data.soil_layers[0].bulk_density,
                self.data.soil_layers[0].layer_thickness, field_size, self.data.eroded_sediment)

            self.data.soil_layers[0].fresh_organic_nitrogen_content -= fresh_organic_nitrogen_lost
            self.data.annual_eroded_fresh_organic_nitrogen_total += fresh_organic_nitrogen_lost * field_size

            self.data.soil_layers[0].stable_organic_nitrogen_content -= stable_organic_nitrogen_lost
            self.data.annual_eroded_stable_organic_nitrogen_total += stable_organic_nitrogen_lost * field_size

            self.data.soil_layers[0].active_organic_nitrogen_content -= active_organic_nitrogen_lost
            self.data.annual_eroded_active_organic_nitrogen_total += active_organic_nitrogen_lost * field_size

    def _leach_nitrogen(self) -> None:
        """Removes leached nitrogen from each soil layer, then adds the leached nitrogen to the next layer.

        References
        ----------
        pseudocode_soil [S.4.C.8] (determines what the leaching extraction coefficient will be for each pool/layer)
        TODO: find literature source for these values, issue #495

        Notes
        -----
        This method determines how much nitrogen will be leached out of each layer without being influenced at all by
        the amount of nitrogen leaching into that layer. It achieves this by calculating the amounts leached out of each
        layer, storing those amounts in a dictionary, appending that dictionary to a list (`percolated_nitrogen`), then
        iterating through the soil profile a second time and adding the leached nitrogen into the appropriate layer. The
        bottom soil layer leaches into the vadose zone.

        The leaching extraction coefficient is 1.0 except when leaching from the nitrate pool in all non-top soil
        layers, in which case it is 2.5.

        """
        percolated_nitrogen = []
        for layer in self.data.soil_layers:
            if layer.percolated_water == 0.0:
                nitrogen_percolated_to_next_layer = {
                    "nitrates": 0,
                    "ammonium": 0,
                    "active_organic": 0
                }
                percolated_nitrogen.append(nitrogen_percolated_to_next_layer)
                continue

            nitrate_extraction_coefficient = 1.0 if layer.top_depth == 0 else 2.5

            nitrates_lost = self._calculate_nitrogen_lost_to_leaching(
                layer.nitrate_content, layer.field_capacity_content, layer.percolated_water,
                nitrate_extraction_coefficient, False)
            ammonium_lost = self._calculate_nitrogen_lost_to_leaching(
                layer.ammonium_content, layer.field_capacity_content, layer.percolated_water, 1.0, False)
            active_organic_nitrogen_lost = self._calculate_nitrogen_lost_to_leaching(
                layer.active_organic_nitrogen_content, layer.field_capacity_content, layer.percolated_water, 1.0, True)

            layer.nitrate_content -= nitrates_lost
            layer.ammonium_content -= ammonium_lost
            layer.active_organic_nitrogen_content -= active_organic_nitrogen_lost

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
    def _determine_nitrogen_concentration(soluble_nitrogen_amount: float,
                                          soil_water_runoff_sum: float,
                                          saturation_content: float) -> float:
        """This method determines the concentration of the inorganic pools NO3/NH4 in the top soil layer.

        Parameters
        ----------
        soluble_nitrogen_amount: float
            Amount of soluble nitrogen (kg / ha)
        soil_water_runoff_sum: float
            Sum of runoff and soil water for layer (mm H2O)
        saturation_content: float
            Volume of water in layer when saturated (mm)

        Returns
        -------
        float
            The concentration of the inorganic pools NO3/NH4 in the top soil layer (kg / mm H20)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.1.2

        Notes
        -----
        This equation has been modified for use in RuFaS, it no longer accounts for the fraction of porosity from which
        anions are excluded.

        """
        return soluble_nitrogen_amount * (1 - (exp(-soil_water_runoff_sum/saturation_content))/soil_water_runoff_sum)

    @staticmethod
    def _determine_nitrogen_runoff_amount(nitrogen_concentration: float,
                                          runoff: float,
                                          runoff_extraction_coef: float) -> float:
        """This method determines the amount of nitrate runoff for the first layer.

        Parameters
        ----------
        nitrogen_concentration: float
            The content of inorganic (nitrate or ammonium) nitrogen in the top soil layer (kg N/mm H20)
        runoff_extraction_coef: float
            Coefficient of extraction for runoff (unitless)
        runoff: float
            Daily runoff of H2O (mm)

        Returns
        -------
        float:
            The amount of nitrate runoff from the first layer (kg/ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 4:2.1.5

        Notes
        -----
        The SWAT equation uses beta_NO3 as the runoff extraction coefficient (see SWAT Input file .BSN "NPERCO", page
        104). RuFaS instead simplifies the runoff extraction coefficient to be 0.1 for determining nitrate runoff and
        1.0 for ammonium runoff.
        """
        return nitrogen_concentration * runoff * runoff_extraction_coef

    @staticmethod
    def _calculate_inorganic_nitrogen_loss(nitrogen_content: float, water_content: float, saturation_content: float,
                                           runoff: float, runoff_extraction_coefficient: float) -> float:
        """Calculates the amount of nitrogen lost from the given pool due to runoff.

        Parameters
        ----------
        nitrogen_content : float
            Amount of inorganic nitrogen in the top soil layer (kg / ha)
        water_content : float
            Water content of the top soil layer (mm)
        saturation_content : float
            Amount of water in the top soil layer when saturated (mm)
        runoff : float
            Amount of precipitation than left the field through runoff on the current day (mm)
        runoff_extraction_coefficient : float
            Coefficient of extraction for runoff (unitless)

        Returns
        -------
        float
            The amount of inorganic nitrogen lost from the top layer of soil on the current day (kg / ha)

        Notes
        -----
        Precipitation that runs off the field only effects the top soil layer, so this method should only ever be used
        to calculate nitrogen lost from the top soil layer.

        """
        water_sum = water_content + runoff
        nitrogen_concentration = LeachingRunoffErosion._determine_nitrogen_concentration(nitrogen_content, water_sum,
                                                                                         saturation_content)
        nitrogen_lost_to_runoff = LeachingRunoffErosion._determine_nitrogen_runoff_amount(nitrogen_concentration,
                                                                                          runoff,
                                                                                          runoff_extraction_coefficient)
        return min(nitrogen_content, nitrogen_lost_to_runoff)

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
    def _determine_nitrogen_percolation_water_concentration(nitrogen_content: float,
                                                            field_capacity_content: float,
                                                            percolation_amount: float) -> float:
        """Calculates concentration of nitrogen in the soil water for determining the amount of nitrogen leached between
            soil layers.

        Parameters
        ----------
        nitrogen_content : float
            Amount of nitrogen in a specific pool in this layer of soil (kg / ha)
        field_capacity_content : float
            Amount of water in this soil layer when at field capacity (mm)
        percolation_amount : float
            The amount of water that percolated out of this layer of soil on the current day (mm)

        Returns
        -------
        float
            The concentration of nitrogen in the soil layer for use in calculating the amount of nitrogen leached by
            percolation (kg / ha / mm water)

        References
        ----------
        pseudocode_soil eqn. [S.4.C.6]

        Notes
        -----
        The origin of this equation is currently unknown, but reflects experimentally observed results. It is meant to
        be used to calculate the concentrations of nitrates, ammonium, and active organic nitrogen in the soil.
        TODO: find literature source for this equation, issue #495

        """
        return nitrogen_content / (field_capacity_content + percolation_amount)

    @staticmethod
    def _adjust_active_organic_nitrogen_concentration(active_organic_nitrogen_concentration: float) -> float:
        """Adjusts the concentration of active organic nitrogen in the soil water before it is leached from.

        Parameters
        ----------
        active_organic_nitrogen_concentration : float
            Concentration of active organic nitrogen in the water of this soil layer (kg / ha / mm water)

        Returns
        -------
        float
            The adjusted active organic nitrogen concentration in this soil layer (kg / ha / mm water)

        References
        ----------
        pseudocode_soil eqn. [S.4.C.7]

        Notes
        -----
        This equation adjusts the active organic nitrogen concentration so that its behaviour is closer to observed
        results.
        TODO: find literature source for this equation, issue #495

        """
        return active_organic_nitrogen_concentration / 50

    @staticmethod
    def _determine_leached_nitrogen(nitrogen_concentration: float, percolation_amount: float,
                                    leaching_extraction_coefficient: float) -> float:
        """Calculates the amount of nitrogen leached from the given pool into the next soil layer.

        Parameters
        ----------
        nitrogen_concentration : float
            Concentration of nitrogen in the soil water of the given pool (kg / ha / mm water)
        percolation_amount : float
            Amount of water that percolated out of the current soil layer on this day (mm)
        leaching_extraction_coefficient : float
            Coefficient for adjusting the amount leached based on depth (unitless)

        Returns
        -------
        float
            The amount of nitrogen percolated from the current soil layer on the current day (kg / ha)

        References
        ----------
        pseudocode_soil eqn. [S.4.C.8]

        Notes
        -----
        This method is used to determine how much nitrate, ammonium, and organic active nitrogen is percolated out of
        the current soil layer. For ammonium and organic active nitrogen, the leaching extraction coefficient is always
        1.0. The leaching extraction coefficient for nitrate is 1.0 for the top layer, and 2.5 for all other layers.
        This equation has been calibrated so that it best models experimental results.
        TODO: find literature source for this equation, issue #495

        """
        adjusted_concentration = nitrogen_concentration / leaching_extraction_coefficient
        return adjusted_concentration * percolation_amount

    @staticmethod
    def _calculate_nitrogen_lost_to_leaching(nitrogen_content: float, field_capacity_content: float,
                                             percolation_amount: float, leaching_extraction_coefficient: float,
                                             is_active_organic_nitrogen: bool) -> float:
        """Calculates how much nitrogen is lost from the given pool on the current day.

        Parameters
        ----------
        nitrogen_content : float
            The content of nitrogen in the given pool in the current layer of soil (kg / ha)
        field_capacity_content : float
            Amount of water in this soil layer when at field capacity (mm)
        percolation_amount : float
            Amount of water that percolated out of the current soil layer on this day (mm)
        leaching_extraction_coefficient : float
            Coefficient for adjusting the amount leached based on depth (unitless)
        is_active_organic_nitrogen  : bool
            Status indicating whether the pool being leached from is the active organic nitrogen pool or not

        Returns
        -------
        float
            The amount of nitrogen that leaches out of the current pool and into the next lowest layer on the current
            day (kg / ha)

        Notes
        -----
        Only the concentration of active organic nitrogen gets adjusted, which necessitates the need for the parameter
        indicating whether the pool being leached from is the active organic pool.

        """
        nitrogen_concentration = LeachingRunoffErosion._determine_nitrogen_percolation_water_concentration(
            nitrogen_content, field_capacity_content, percolation_amount)

        if is_active_organic_nitrogen:
            nitrogen_concentration = LeachingRunoffErosion._adjust_active_organic_nitrogen_concentration(
                nitrogen_concentration)

        nitrogen_lost = LeachingRunoffErosion._determine_leached_nitrogen(nitrogen_concentration, percolation_amount,
                                                                          leaching_extraction_coefficient)
        return min(nitrogen_content, nitrogen_lost)
