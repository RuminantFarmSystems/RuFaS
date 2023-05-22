from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from typing import Optional, List, Dict
from math import exp
from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation

# TODO: delete/replace the note block below once satisfied with the design
"""
The current (Feb-2023) state of this module is to guide the development and provide structure for the field and farm
manager classes. The field class, as laid out here, handles the management actions and scenarios that can be performed
in an agricultural field.

Note that some of the field-level attributes will be tracked by the FieldData class
"""


class Field:
    """object representing an agricultural field"""

    def __init__(self, field_data: Optional[FieldData] = None, soil: Optional[Soil] = None):
        # field-wide attributes
        self.field_data = field_data or FieldData()
        """field data component"""

        # soil attributes
        self.soil = soil or Soil(soil_data=None, field_size=self.field_data.field_size)  # default soil if not given.
        """the soil component of the field"""

        # crop attributes
        self.crops: List[Crop] = list()  # empty crop list
        """crops currently in the field"""

        self.is_last_day_of_the_year = False  # TODO: This should be handled elsewhere
        """is today the last day of the simulation year?"""

    def manage_field(self, day: int, year: int, current_weather: CurrentWeather) -> None:
        """main Field function, runs all field routines based on current attribute configuration

        Args:
            day: the current (sequential) day of the simulation  - TODO: not yet implemented
            year: the current (sequential) year of the simulation - TODO: not yet implemented
            current_weather: a CurrentWeather object, containing a collection of today's weather variables needed
                for field processes.

        Details: **All the logic (after setup) will go in this function**
        """
        # What needs to be done today?
        self.check_schedule(day, year)

        # --- Soil Management---
        # nutrient amendments
        if self.field_data.is_amendment_day:
            self.amend_soil()

        # tillage
        if self.field_data.is_tillage_day:
            self.till_soil()

        # daily soil routine

        # determine total amount of residue and above-ground biomass present on the given day
        total_plant_cover = self.field_data.current_residue + self._determine_total_above_ground_biomass()

        # TODO: track snow cover on soil surface somewhere - Issue #317
        self.soil.daily_soil_routine(current_weather.incoming_light, current_weather.mean_air_temperature,
                                     current_weather.min_air_temperature, current_weather.max_air_temperature,
                                     total_plant_cover, current_weather.snow_fall,
                                     current_weather.annual_mean_air_temperature)

        # TODO: track snow cover on soil surface somewhere - Issue #317

        # --- Whole-Field Methods ---
        # Allow non-management field processes (water/nutrient cycling) to occur
        self.cycle_water(current_weather)
        # ... Other ...

        # --- Crop Management ---
        # planting
        if self.field_data.is_planting_day:
            self.plant_crops(self.field_data.current_crop_config)

        # perform remaining tasks if crops currently in field
        if self.crops is not None:

            self.assess_dormancy(current_weather.daylength)

            self.grow_crops(current_weather.incoming_light, current_weather.min_air_temperature,
                            current_weather.mean_air_temperature, current_weather.max_air_temperature)

            if self.field_data.grazers_present:
                self.graze_field()

            self.check_harvest_schedules(day, year)
            self.harvest_scheduled_crops()

        # annual resets
        if self.is_last_day_of_the_year:
            self.perform_annual_reset()

        pass

    @property
    def _composition_sums_to_one(self) -> bool:
        """ensure that the crop_proportions values sum to 1"""
        return sum([crop.data.field_proportion for crop in self.crops]) == 1.0

    # <editor-fold desc="--- Setup Methods ---">
    def setup_field(self, soil_config, tillage_config, amendment_config, crop_config):
        """setup all the attributes that determine how the field will be managed"""
        self.soil = Soil(soil_config)
        self.setup_tillage(tillage_config)
        self.setup_amendments(amendment_config)
        self.setup_crop_schedule(crop_config)

    def setup_tillage(self, tillage_config):
        """sets up the tillage details for this field"""
        pass

    def setup_amendments(self, amendment_config):
        """sets up the nutrient amendment details (manure and fertilizer) for this field"""
        pass

    def setup_crop_schedule(self, crop_config):
        """sets up the cropping schedule (species, planting/harvest dates, etc)"""
        pass
        # </editor-fold>

    # <editor-fold desc="--- Soil Management Methods ---">
    def till_soil(self) -> None:
        """till the soil"""
        pass

    def amend_soil(self) -> None:
        """amend the soil with nutrients"""
        self.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus(0)
        return

    # </editor-fold>

    # <editor-fold desc="--- Scheduling Methods ---">
    def check_schedule(self, year: int, day: int) -> None:
        """check if any scheduled activities need to be completed today.

        Args:
            year: the current year
            day: the current day of the year

        Details:
            This method should check the dates on which certain actions should be performed against the year and day.
            Then, the boolean attributes that trigger the relevant operations should be updated.
            For example, if we need to plant a crop today, this method will set `self.field_data.is_planting_day=True`.
         """
        pass
    # </editor-fold>

    # <editor-fold desc="--- Crop Management Methods ---">
    def plant_crops(self, crops_config: List[Dict], coverage: Optional[List[float]] = None) -> None:
        """adds all crop(s) into the field from the current configuration specs

        Args:
            crops_config: a list of crop config dictionaries (see make_crop_from_config_dict), one for each crop to be
                planted
            coverage: a list of field coverages for each crop (% of the field); must sum to less than 1
        """
        if coverage is not None:
            if sum(coverage) > 1.0:
                raise ValueError("the sum of coverage is greater than 1.0")

        for i in range(len(crops_config)):
            conf = crops_config[i]
            cov = coverage[i] if coverage is not None else None
            crop = self.make_crop_from_config_dict(conf)
            self.add_crop(crop, cov)

    @staticmethod
    def make_crop_from_config_dict(config: Dict) -> Crop:
        """Initializes a new crop from a configuration dictionary

        Args:
            config: a dictionary containing specifications for the crop to be initialized.

        Details: if the "species" key is present in the dictionary, that value is checked against the supported
            crop species. If it is supported, that supported crop is initialized. Otherwise, a custom crop is
            created (with 'custom' prepended to species name, if given).

        Returns: a Crop object, initialized with the desired attribute values.
        """
        if "species" in config.keys():
            accepted_species = set(item.value for item in CropSpecies)
            species = config.pop("species")

            if species in accepted_species:
                return Field.make_supported_crop(species=species, **config)
            else:
                config["species"] = "custom " + str(species)

        return Field.make_custom_crop(**config)

    @staticmethod
    def make_supported_crop(species: str, **specs) -> Crop:
        """creates a crop instance with attributes determined by the species of the crop.

        Args:
            species: one of the supported species
            **specs: an optional set of arguments, passed to CropSpeciesDataFactory that customize the
              crop species

        Details: species attributes are read from species configuration files/classes. This method of creating
            a crop does not allow for customizing crop values. It is limited to creating the default crops
            supported by the CropSpecies Enum.

        Returns: a Crop object, initialized with the desired attribute values.
        """
        crop_species = CropSpecies(species)
        crop_data = CropSpeciesDataFactory.create_species_data(crop_species, **specs)
        return Crop(crop_data)

    @staticmethod
    def make_custom_crop(**specs) -> Crop:
        """creates a crop instance with customized attributes.

        Args:
            **specs: an optional set of arguments, passed to CropSpeciesDataFactory that customize the
              crop species

        Details, this can be used to create a new ('unsupported') crop species/type
        """
        crop_data = CropData(**specs)
        return Crop(crop_data)

    def add_crop(self, crop: Crop, field_cover: Optional[float] = None) -> None:
        """add a crop to the field's current crop list and update relevant attributes

        Args:
            crop: the crop object to add to the field
            field_cover: the desired proportion of the field for this crop to occupy, must be space available. If not
                provided, each crop will occupy an equal proportion of the field.

        Raises: ValueError if there is no room in the field for the desired field_cover of this crop
        """

        if field_cover is None:
            self.crops.append(crop)
            for this_crop in self.crops:
                this_crop.data.field_proportion = 1 / len(self.crops)
        else:
            crop.data.field_proportion = field_cover
            self.crops.append(crop)

        total_cover = sum([crp.data.field_proportion for crp in self.crops])
        if total_cover > 1.0:
            raise ValueError("more than 100% of the field is occupied")

    def reset_perennial(self):
        """resets some attributes for perennial crops at the start of the new growing season"""
        pass

    def _get_soil_layer_attributes_for_crop_growth(self) -> Dict[str, List[float]]:
        """restructure soil layer data to be used for crop growth methods"""
        layer_attr_dict = {"depths": [],
                           "nitrates": [],
                           "phosphates": []}
        for layer in self.soil.data.soil_layers:
            layer_attr_dict["depths"].append(layer.bottom_depth)
            layer_attr_dict["nitrates"].append(layer.nitrate)
            layer_attr_dict["phosphates"].append(layer.phosphate)

        return layer_attr_dict

        # NOTE: I had originally opted to have separate properties in the Soil class that made these lists,
        # but, unless other classes need these variables in this format, this seems to be most efficient.
        # i.e.,
        #
        # @property
        # def layer_depths(self):
        #     """Get a list of the lowest depth for each soil layer"""
        #     return [layer.bottom_depth for layer in self.data.soil_layers]
        #
        # @property
        # def layer_nitrates(self):
        #     """Place the nitrate values from each soil layer into a list"""
        #     return [layer.nitrate for layer in self.data.soil_layers]
        #
        # @property
        # def layer_phosphates(self):
        #     """Place the nitrate values from each soil layer into a list"""
        #     return [layer.phosphate for layer in self.data.soil_layers]

    def grow_crops(self, incoming_light, min_air_temperature, mean_air_temperature, max_air_temperature) -> None:
        """allow the current crops to execute their daily growth routines"""
        for this_crop in self.crops:
            this_crop.grow_crop(soil_data=self.soil.data, incoming_light=incoming_light,
                                mean_air_temperature=mean_air_temperature, min_air_temperature=min_air_temperature,
                                max_air_temperature=max_air_temperature)

    def check_harvest_schedules(self, day, year) -> None:
        """executes the check_harvest_schedule method for each crop, passing the current day and year"""
        for crop in self.crops:
            crop.crop_management.check_harvest_schedule(current_day=day, current_year=year)

    def harvest_scheduled_crops(self) -> None:
        """perform the harvest operation on all crops in the field, depending on the harvest operation, if today is
        the crop's harvest day.

        After the harvest, this method adds any residue to the soil. Root residue is only added if the
        harvest operation killed the crop.
        """
        for crop in self.crops:
            if not crop.data.is_harvest_day:
                continue  # move on to checking next crop

            if crop.data.next_harvest_operation == HarvestOperation.HARVEST:
                crop.crop_management.manage_harvest(cut=True, collect=True, kill=True)

            if crop.data.next_harvest_operation == HarvestOperation.HARVEST_NOKILL:
                crop.crop_management.manage_harvest(cut=True, collect_yield=True, kill=False)

            self.soil.data.plant_surface_residue += (crop.data.yield_residue or 0)
            if not crop.data.is_alive:
                self.soil.data.plant_root_residue += (crop.data.root_biomass or 0)

    def graze_field(self):  # TODO: placeholder; no grazing method currently implemented in RUFAS
        """allow grazers to graze in the field during the current day"""
        pass

    def assess_dormancy(self, daylength: float) -> None:
        """Transitions all crops to dormancy, that are capable of going dormant

        Args:
            daylength: length of time from sunup to sundown on the current day (hours)

        Details:
            If the length of the current day is at or below the dormancy threshold length, all crops that can go dormant
            should be put into dormancy. If the length is greater than the threshold length, all crops
            should be brought out of dormancy.

        """
        if daylength <= self.field_data.dormancy_threshold_daylength:

            for crop in self.crops:
                crop.dormancy.enter_dormancy()
        else:
            for crop in self.crops:
                crop.data.is_dormant = False
    # </editor-fold>

    # <editor-fold desc="--- Field-level Methods ---">
    def cycle_water(self, current_weather: CurrentWeather):
        """allow the water to cycle through the field.

        Args:
            current_weather: a CurrentWeather object, containing a collection of today's weather variables needed
                for field processes.

        Details: This method executes all water-related processes that occur within Crop and Soil objects. Having a
            separate method to handle water processes altogether is necessary because processes that effect water in the
            soil are dependent on processes that effect water in crops and vice versa. The most complex process that is
            executed in this method is evapotranspiration, which is executed in the following order
                - Evaporation of water in canopies of crops.
                - Sublimation of water in snow pack (not implemented in V1)
                - Evaporation from the soil profile.
                - Transpiration from crops (amount of water taken up by plants is equal to the amount they transpirate,
                    and this amount depends on the evapotranspirative demand after water has been removed from canopies)

            It should also be noted that while this method is more messy and complex than it should be, this is a
            conscious design choice that will allow for SME's to more easily and freely experiment with different orders
            of processes. This is necessary because there is not necessarily one correct order for processes to run in.

        """
        watering_amount = self._determine_watering_amount(current_weather.rainfall)
        total_precipitation = current_weather.rainfall + watering_amount
        precipitation_reaching_soil = self._handle_water_in_crop_canopies(total_precipitation)

        full_evapotranspirative_demand = self._determine_potential_evapotranspiration(
            current_weather.incoming_light, current_weather.max_air_temperature, current_weather.min_air_temperature,
            current_weather.mean_air_temperature)

        remaining_evapotranspirative_demand = self._evaporate_from_crop_canopies(full_evapotranspirative_demand)

        # TODO: figure out how to determine weighting coefficient when there are multiple crops in the field - issue
        #  #519
        self.soil.infiltration.infiltrate(precipitation_reaching_soil, 1, full_evapotranspirative_demand)
        self.soil.percolation.percolate(self.field_data.seasonal_high_water_table)
        # TODO: find reasonable values/way to set minimum cover management factor - issue #520
        self.soil.soil_erosion.erode(self.field_data.field_size, 0.02, self.field_data.current_residue)
        self.soil.phosphorus_cycling.cycle_phosphorus(precipitation_reaching_soil, self.soil.data.accumulated_runoff,
                                                      self.field_data.field_size, current_weather.mean_air_temperature)
        self.soil.nitrogen_cycling.cycle_nitrogen(self.field_data.field_size)

        weighted_transpiration_total = 0.0
        weights_sum = 0.0
        for crop in self.crops:
            crop.water_dynamics.set_maximum_transpiration(remaining_evapotranspirative_demand)
            weighted_transpiration_total += crop.data.max_transpiration * crop.data.field_proportion
            weights_sum += crop.data.field_proportion
        weighted_average_transpiration = weighted_transpiration_total / weights_sum

        # TODO: Implement snow (melting and sublimation) - issue #317
        snow_water_content = 0
        above_ground_biomass = self._determine_total_above_ground_biomass()

        soil_evaporation_and_sublimation_amount = self._determine_soil_evaporation_and_sublimation_adjusted(
            above_ground_biomass, self.soil.data.plant_surface_residue, snow_water_content,
            remaining_evapotranspirative_demand, weighted_average_transpiration)

        # TODO: sublimate and adjust soil_evaporation_and_sublimation_amount here - issue #317

        self.soil.evaporation.evaporate(soil_evaporation_and_sublimation_amount)
        remaining_evapotranspirative_demand -= self.soil.data.water_evaporated

        actual_evaporation = full_evapotranspirative_demand - remaining_evapotranspirative_demand

        for crop in self.crops:
            if crop.data.in_growing_season:
                crop.water_uptake.uptake_water(self.soil)
                crop.water_dynamics.cycle_water(actual_evaporation, crop.data.total_water_uptake,
                                                full_evapotranspirative_demand)
            else:
                crop.data.cumulative_evaporation = 0
                crop.data.cumulative_transpiration = 0
                crop.data.cumulative_potential_evapotranspiration = 0

    def _determine_watering_amount(self, rainfall: float) -> float:
        """Manages watering of the field.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall that occurs on this day (mm)

        Returns
        -------
        float
            Amount of water used to irrigate the field on this day (mm)

        Notes
        -----
        This method drives the engine of irrigation for RuFaS. It tracks how much water has been added to the field by
        rainfall over a user-defined interval, and when at the end of the interval it determines how much water still
        needs to be added to the field based on how much watering has to occur over said interval (also defined by the
        user). The counter that tracks how where in the interval the simulation is and the amount of water that still
        needs to be applied are reset at the end of every interval. The water that is added to the field from the farm's
        resources is tracked on an annual basis, so that water budgeting may be accurately predicted.

        """
        if not self.field_data.watering_occurs:
            return 0.0

        self.field_data.current_water_deficit -= rainfall
        self.field_data.current_water_deficit = max(0.0, self.field_data.current_water_deficit)

        if self.field_data.days_into_watering_interval == self.field_data.watering_interval:
            self.field_data.days_into_watering_interval = 0
            water_applied_this_interval = self.field_data.current_water_deficit
            self.field_data.current_water_deficit = self.field_data.watering_amount_in_mm
            self.field_data.annual_irrigation_water_use_total += water_applied_this_interval
            return water_applied_this_interval

        self.field_data.days_into_watering_interval += 1
        return 0.0

    def _handle_water_in_crop_canopies(self, precipitation_total: float) -> float:
        """Adds water to canopies of all the crops in the field and removes any excess water from them.

        Parameters
        ----------
        precipitation_total : float
            Total amount of precipitation that fell on the field today (mm)

        Returns
        -------
        float
            Amount of water that reaches the soil surface (mm)

        Notes
        -----
        This method accounts for the edge case that no water was lost from the crop canopy yesterday and the capacity in
        the canopy went down overnight, so water is lost from the canopy to the ground before any evapotranspiration can
        happen. A caveat is that if there is excess water in the canopy of one crop, it cannot be transferred to the
        canopy of another.
        TODO: distribute water evenly/proportionally/fairly between crop canopies - issue #513
        """
        precipitation_reaching_soil = precipitation_total
        excess_canopy_water = 0
        for crop in self.crops:
            canopy_water_excess_capacity = crop.data.water_canopy_storage_capacity - crop.data.canopy_water

            excess_water_in_canopy = min(0.0, canopy_water_excess_capacity)
            excess_canopy_water += -1 * excess_water_in_canopy
            if excess_water_in_canopy != 0.0:
                crop.data.canopy_water = crop.data.water_canopy_storage_capacity

            water_taken_to_be_stored = max(0.0, canopy_water_excess_capacity)
            water_taken_to_be_stored = min(precipitation_reaching_soil, water_taken_to_be_stored)
            crop.data.canopy_water += water_taken_to_be_stored
            precipitation_reaching_soil -= water_taken_to_be_stored

        return precipitation_reaching_soil + excess_canopy_water

    def _evaporate_from_crop_canopies(self, evapotranspirative_demand: float) -> float:
        """Evaporates water from crops' canopies and reduces evapotranspirative demand accordingly.

        Parameters
        ----------
        evapotranspirative_demand : float
            Evapotranspirative demand on the field on the current day (mm)

        Returns
        -------
        float
            Evapotranspirative demand after evaporating water from crops' canopies (mm)

        References
        ----------
        SWAT Theoretical documentation section 2:2.3.1

        Notes
        -----
        This method iterates through the crops in the field, for each determines how much water was evaporated from its
        canopy, then reduces the evapotranspirative demand by that amount. If the remaining evapotranspirative demand
        reaches 0, then no more water should be evaporated so the method stops running.
        TODO: evaporate water evenly/proportionally/fairly from crop canopies - issue #513
        """
        remaining_evapotranspirative_demand = evapotranspirative_demand
        for crop in self.crops:
            amount_evaporated = crop.water_dynamics.evaporate_from_canopy(remaining_evapotranspirative_demand)
            remaining_evapotranspirative_demand -= amount_evaporated
            if remaining_evapotranspirative_demand == 0.0:
                break
        return remaining_evapotranspirative_demand

    def _determine_total_above_ground_biomass(self) -> float:
        """Calculate the total amount of above-ground biomass still on the plant(s) in the field (kg / ha)"""
        total_above_ground_biomass = 0
        for crop in self.crops:
            total_above_ground_biomass += crop.data.above_ground_biomass
        return total_above_ground_biomass

    @staticmethod
    def _determine_potential_evapotranspiration(extra_terrestrial_radiation: float, max_air_temp: float,
                                                min_air_temp: float,
                                                avg_air_temp: float) -> float:
        """Calculates the potential evapotranspiration for a given day.

        Parameters
        ----------
        extra_terrestrial_radiation : float
            Radiation from the aliens (MJ per square meter per day)
        max_air_temp : float
            Maximum air temperature (degrees C)
        min_air_temp : float
            Minimum air temperature (degrees C)
        avg_air_temp : float
            Average air temperature (degrees C)

        Returns
        -------
        float
            potential evapotranspiration (mm)

        References
        ----------
        SWAT Reference: 2:2.2.24

        Notes
        -----
        This method calculates the evapotranspirative demand for the entire field on any given day using the Hargreaves
        method.

        """
        if avg_air_temp is None:
            calculated_avg_air_temp = (max_air_temp + min_air_temp) / 2
            latent_heat_vaporization = Field._determine_latent_heat_vaporization(calculated_avg_air_temp)
            return (0.0023 * extra_terrestrial_radiation * ((max_air_temp - min_air_temp) ** (-0.5))
                    * (calculated_avg_air_temp + 17.8)) / latent_heat_vaporization
        else:
            latent_heat_vaporization = Field._determine_latent_heat_vaporization(avg_air_temp)
            return (0.0023 * extra_terrestrial_radiation * ((max_air_temp - min_air_temp) ** (-0.5))
                    * (avg_air_temp + 17.8)) / latent_heat_vaporization

    @staticmethod
    def _determine_latent_heat_vaporization(avg_air_temp: float) -> float:
        """Determine latent heat of vaporization for a given day.

        Parameters
        ----------
        avg_air_temp : float
            Average air temperature (degrees C)

        Returns
        -------
        float
            latent heat of vaporization (MJ per kg)

        References
        ----------
        SWAT Reference: 1:2.3.6

        """
        return 2.501 - ((2.361 * (10 ** (-3))) * avg_air_temp)

    @staticmethod
    def _determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass: float, residue: float,
                                                             snow_water_content: float,
                                                             potential_evapotranspiration_adjusted: float,
                                                             transpiration: float) -> float:
        """Calculate the amount of sublimation and soil evaporation for this day, adjusted for plant use.
        Parameters
        ----------
        above_ground_biomass : float
            Mass of plant above ground (kg per hectare)
        residue : float
            Biomass separated from plant on the ground (kg per hectare)
        snow_water_content : float
            Amount of water in the snow pack (mm)
        potential_evapotranspiration_adjusted : float
            Potential evapotranspiration adjusted for evaporation of free water in canopy (mm)
        transpiration : float
            Maximum transpiration for a given day (mm)
        Returns
        -------
        float
            Soil evaporation and sublimation, adjusted for plant water use (mm)
        References
        ----------
        SWAT Theoretical documentation eqn. 2:2.3.7, 9
        """
        soil_cover_index = Field._determine_soil_cover_index(above_ground_biomass, residue, snow_water_content)
        max_soil_evaporation_sublimation = potential_evapotranspiration_adjusted * soil_cover_index
        adjusted_soil_evaporation_sublimation = \
            (max_soil_evaporation_sublimation * potential_evapotranspiration_adjusted) / \
            (max_soil_evaporation_sublimation + transpiration)
        actual_soil_evaporation_sublimation = min(max_soil_evaporation_sublimation,
                                                  adjusted_soil_evaporation_sublimation)
        return actual_soil_evaporation_sublimation

    @staticmethod
    def _determine_soil_cover_index(above_ground_biomass: float, residue: float, snow_water_content: float) -> float:
        """Calculate the soil cover index.
        Parameters
        ----------
        above_ground_biomass : float
            Mass of plant above ground (kg per hectare)
        residue : float
            Biomass separated from plant on the ground (kg per hectare)
        snow_water_content : float
            Amount of water from snow (mm)
        Returns
        -------
        Float
            Soil cover index (unitless)
        References
        ----------
        SWAT Theoretical documentation eqn. 2:2.3.8
        """
        if snow_water_content > 0.5:
            return 0.5
        else:
            return exp((-5.0 * (10 ** (-5))) * (above_ground_biomass + residue))

    # TODO: this method will not be used until sublimation is implemented - issue #317
    @staticmethod
    def _determine_maximum_soil_evaporation(soil_evaporation_adj: float, snow_water_content: float) -> float:
        """Calculates the maximum amount of evaporation from soil in a given day
        Parameters
        ----------
        soil_evaporation_adj : float
            Maximum soil evaporation adjusted for plant water use on a given day (mm)
        snow_water_content : float
            Amount of water in the snow pack on a given day prior to accounting for sublimation (mm)
        TODO: verify that "amount of water in the snow pack on a given day" (2:2.3.3.1) and "snow water content"
            (2:2.3.3) mean the same thing - address this with #317
        Returns
        -------
        float
            Maximum soil water evaporation on a given day (mm)
        References
        ----------
        SWAT Theoretical documentation section 2:2.3.3.1
        """
        if soil_evaporation_adj < snow_water_content:
            return 0
        else:
            return soil_evaporation_adj - snow_water_content

    # </editor-fold>

    # <editor-fold desc="--- Annual Reset Methods ---">
    def perform_annual_reset(self) -> None:
        """Collect all annual accumulated totals from Field, Crop, and Soil modules, write them to some sort of output
            file, and then reset all annual totals"""
        self.soil.data.do_annual_reset()
        self.field_data.perform_annual_field_reset()
        return
