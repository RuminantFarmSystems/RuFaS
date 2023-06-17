from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from SC_redesign.Crop_and_Soil.manager.events import Event, PlantingEvent, HarvestEvent
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.field.fertilizer_application import FertilizerApplication
from SC_redesign.Crop_and_Soil.field.tillage_application import TillageApplication
from typing import Optional, List, Dict, Tuple
from math import exp
from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation
from SC_redesign.Crop_and_Soil.field.manure_application import ManureApplication
from SC_redesign.Crop_and_Soil.manager.events import TillageEvent
from RUFAS.classes import Time
from RUFAS.output_manager import OutputManager
from copy import copy

# TODO: delete/replace the note block below once satisfied with the design
"""
The current (Feb-2023) state of this module is to guide the development and provide structure for the field and farm
manager classes. The field class, as laid out here, handles the management actions and scenarios that can be performed
in an agricultural field.

Note that some of the field-level attributes will be tracked by the FieldData class
"""

om = OutputManager()


class Field:
    """object representing an agricultural field"""

    def __init__(self, field_data: Optional[FieldData] = None, soil: Optional[Soil] = None,
                 tillage_events: Optional[List[TillageEvent]] = None, plantings: Optional[List[PlantingEvent]] = None,
                 harvestings: Optional[List[HarvestEvent]] = None,
                 custom_crop_specifications: Optional[Dict[str, Dict]] = None):
        # field-wide attributes
        self.field_data = field_data or FieldData()
        """field data component"""

        # soil attributes
        self.soil = soil or Soil(soil_data=None, field_size=self.field_data.field_size)  # default soil if not given.
        """the soil component of the field"""

        # crop attributes
        self.crops: List[Crop] = list()  # empty crop list
        """crops currently in the field"""

        self.planting_events: List[PlantingEvent] = plantings or []
        """List of all planting events that will occur over the run of the simulation in this field."""

        self.harvest_events: List[HarvestEvent] = harvestings or []
        """List of all harvesting events that will occur over the run of the simulation in the field."""

        self.custom_crop_specifications: Dict[str, Dict] = custom_crop_specifications or {}
        """Dictionary where keys are crop references and values are dictionaries containing crop specifications."""

        # Soil amendment attributes
        self.fertilizer_applicator = FertilizerApplication(self.soil)
        """Provides interface for adding fertilizer to the field."""

        self.tiller = TillageApplication(self.field_data, self.soil.data)
        """Provides interface to till the field."""
        self.tillage_events: List[TillageEvent] = tillage_events
        """List of all tillage events that will occur over the run of the simulation in this field."""

        self.is_last_day_of_the_year = False  # TODO: This should be handled elsewhere
        """is today the last day of the simulation year?"""

        self.manure_applicator = ManureApplication(self.soil.data)
        """Manure application interface."""

    def manage_field(self, time: Time, current_weather: CurrentWeather) -> None:
        """main Field function, runs all field routines based on current attribute configuration

        Args:
            time : a Time object, containing the current year and day that the simulation is on.
            current_weather: a CurrentWeather object, containing a collection of today's weather variables needed
                for field processes.


        Details: **All the logic (after setup) will go in this function**
        """
        # --- Soil Management---
        # nutrient amendments
        if self.field_data.is_amendment_day:
            self.amend_soil()

        # tillage
        self.check_tillage_schedule()

        # --- Whole-Field Methods ---
        # Allow non-management field processes (water/nutrient cycling) to occur
        self._execute_daily_processes(current_weather)
        # ... Other ...

        # --- Crop Management ---
        # planting
        self.check_crop_planting_schedule(time)

        # Harvesting.
        self.check_crop_harvest_schedule(time)

        self._remove_dead_crops()
        self._reset_crop_field_coverage_fractions()

        # perform remaining tasks if crops currently in field
        if self.crops is not None:

            self.assess_dormancy(current_weather.daylength)

            self.grow_crops(current_weather.incoming_light, current_weather.min_air_temperature,
                            current_weather.mean_air_temperature, current_weather.max_air_temperature)

            if self.field_data.grazers_present:
                self.graze_field()

            self.check_harvest_schedules(time.day, time.year)
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
    def setup_field(self, soil_config, tillage_config, amendment_config):
        """setup all the attributes that determine how the field will be managed"""
        self.soil = Soil(soil_config)
        self.setup_tillage(tillage_config)
        self.setup_amendments(amendment_config)

    def setup_tillage(self, tillage_config):
        """sets up the tillage details for this field"""
        pass

    def setup_amendments(self, amendment_config):
        """sets up the nutrient amendment details (manure and fertilizer) for this field"""
        pass
        # </editor-fold>

    # <editor-fold desc="--- Soil Management Methods ---">
    def check_tillage_schedule(self, time: Time) -> None:
        """
        Checks the list of Events, and all that are scheduled to happen are passed on to another method to be
        executed.

        Parameters
        ----------
        time : Time
            Time object containing the current day and year of the simulation.
        """
        self.tillage_events, todays_events = self._filter_events(self.tillage_events, time)
        for event in todays_events:
            self.tiller.till_soil(event.tillage_depth, event.incorporation_fraction, event.mixing_fraction,
                                  time.calendar_year,
                                  time.day)

    def amend_soil(self) -> None:
        """amend the soil with nutrients"""
        self.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus(0)
        return

    # </editor-fold>

    # <editor-fold desc="--- Scheduling Methods ---">
    def check_crop_planting_schedule(self, time: Time) -> None:
        """
        Checks the list of PlantingEvents, and all that are scheduled to happen are passed on to another method to be
        executed.

        Parameters
        ----------
        time : Time
            Time object containing the current day and year of the simulation.

        """
        self.planting_events, todays_planting_events = self._filter_events(self.planting_events, time)
        for event in todays_planting_events:
            self._plant_crop(event.crop_reference, event.use_heat_scheduled_harvest, time)

    def check_crop_harvest_schedule(self, time: Time) -> None:
        """
        Checks for all crops for potential harvests that may happen on the current day.

        Parameters
        ----------
        time : Time
            Time object containing the current day and year of the simulation.

        Notes
        -----
        This method checks for scheduled harvests, i.e. checks all the remaining HarvestEvents. It calls the method that
        checks if crops should be harvested based on their heat fraction.

        """
        self.harvest_events, todays_harvest_events = self._filter_events(self.harvest_events, time)
        for event in todays_harvest_events:
            self._harvest_crop(event.crop_reference, event.operation, time)

        self._harvest_heat_scheduled_crops()

    def _harvest_heat_scheduled_crops(self) -> None:
        """
        Checks if any of the active plants in the field are harvested based on their heat schedule, and if so harvests
        them if they meet the heat threshold.

        References
        ----------
        SWAT Theoretical documentation section 5:1.1.1 (Heat Scheduling)

        """
        for crop in self.crops:
            execute_heat_scheduled_harvest = crop.data.use_heat_scheduling and \
                                             crop.data.heat_fraction >= crop.data.harvest_heat_fraction
            if execute_heat_scheduled_harvest:
                crop.crop_management.manage_harvest(HarvestOperation.HARVEST_NOKILL)

    @staticmethod
    def _filter_events(all_events: List[Event], time: Time) -> Tuple[List[Event], List[Event]]:
        """
        Filters out all events from a list that occur on the current day, and creates a new list with all the events
        that were filtered out.

        Parameters
        ----------
        all_events : List[Event]
            List of all Events that will occur over the run of the simulation in this field.
        time : Time
            Object containing the current day and year of the simulation.

        Returns
        -------
        Tuple
            A tuple containing the list of all Events that will occur in this field after the current day, and a list of
            Events that will occur on the current day.

        Notes
        -----
        This method is written to work with generic Events so that it may be used on all the different child classes of
        Event: PlantingEvent, HarvestEvent, ManureEvent, FertilizerEvent, and TillageEvent.

        """
        todays_events = []
        remaining_events = []
        for event in all_events:
            if event.occurs_today(time):
                todays_events.append(event)
            else:
                remaining_events.append(event)
        return remaining_events, todays_events

    # </editor-fold>

    # <editor-fold desc="--- Crop Management Methods ---">
    def _plant_crop(self, crop_reference: str, use_heat_scheduled_harvesting: bool, time: Time) -> None:
        """
        Takes the information necessary to plant a crop, creates a new Crop based on it, then adds it to the field's
        list of current crops.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be planted.
        use_heat_scheduled_harvesting : bool
            Indicates if this crop should be harvested based on the fraction of potential heat units it has accumulated.
        time : Time
            Object containing the current year and day of the simulation.

        Raises
        ------
        KeyError
            If the crop reference is to a custom crop specification, but that specification is not present in the list
            of custom crop specifications.

        Notes
        -----
        The crop reference may contain a reference to a supported crop that already has attributes defined for it, or a
        reference to a custom crop that has user-defined attributes. This method starts by trying to determine if the
        crop is of a supported species, if so it passes it to the supported crop creation method. If not, it passes it
        to the custom crop creation method.

        The harvest method is overwritten for the crop created because that is specified directly by the user, and the
        crop id is set so that the HarvestEvents will be able to identify the correct crop in the field's list of active
        crops.

        """
        supported_species = set(item.value for item in CropSpecies)
        if crop_reference in supported_species:
            crop = self.make_supported_crop(crop_reference)
        else:
            try:
                crop_specifications = copy(self.custom_crop_specifications[crop_reference])
            except KeyError:
                raise KeyError(f"'{self.field_data.name}': expected to have crop specification for '{crop_reference}', "
                               f"received specifications for '{tuple(self.custom_crop_specifications.keys())}' crop "
                               f"types.")
            crop = self.make_crop_from_config_dict(crop_specifications)
        crop.data.use_heat_scheduling = use_heat_scheduled_harvesting
        crop.data.id = crop_reference

        self.crops.append(crop)

        self._record_planting(crop_reference, use_heat_scheduled_harvesting, crop.data.species, time.calendar_year,
                              time.day)

    def _record_planting(self, crop_reference: str, heat_scheduled_harvest: bool, species: str, year: int,
                         day: int) -> None:
        """
        Records a planting event to the OutputManager.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be planted.
        heat_scheduled_harvest : bool
            Indicates if this crop should be harvested based on the fraction of potential heat units it has accumulated.
        species : str
            Name of the species of the crop being planted.
        year : int
            Year in which this crop planting occurs.
        day : int
            Julian day on which this crop planting occurs.

        """
        info_map = {"class": self.__class__.__name__, "function": self._plant_crop.__name__,
                    "prefix": f"field_name:'{self.field_data.name}'", "field_size": self.field_data.field_size,
                    "date": {"year": year, "day": day}, "species": species}
        value = {"crop_reference": crop_reference, "heat_scheduled_harvest": heat_scheduled_harvest}
        om.add_variable("crop_planting", value, info_map)

    def _harvest_crop(self, crop_reference: str, harvest_operation: str, time: Time) -> None:
        """
        Performs the specified crop operation on the specified crop.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be harvested.
        harvest_operation : str
            Name of the harvest operation to be performed on the referenced crop.
        time : Time
            Object containing the current day and year of the simulation.

        Notes
        -----
        This method raises two different warnings, one if multiple active crops share the same id, and one if no active
        crop is found with an id that matches the given crop reference. These are both raised as warnings and not errors
        (which would stop the simulation run) because they could both plausibly happen in a simulation run. The first
        scenario could happen if someone were to specify multiple plantings of the same crop in the same year and
        schedule them to be harvested together, and the second could happen if there was a catastrophic weather event
        that killed off a crop before it could be harvested.

        """
        crops_to_be_harvested = [crop for crop in self.crops if crop.data.id == crop_reference]

        info_map = {"class": self.__class__.__name__, "function": self._harvest_crop.__name__,
                    "prefix": f"field_name:'{self.field_data.name}'",
                    "date": {"day": time.day, "year": time.calendar_year}}
        if len(crops_to_be_harvested) > 1:
            om.add_warning("harvest_warning", "Multiple crops to be harvested by single HarvestEvent.", info_map)
        elif len(crops_to_be_harvested) < 1:
            om.add_warning("harvest_warning", "No crop found to be harvested by a HarvestEvent.", info_map)

        for crop in crops_to_be_harvested:
            harvest_operation_enum = HarvestOperation(harvest_operation)
            crop.crop_management.manage_harvest(harvest_operation_enum)

    def _remove_dead_crops(self) -> None:
        """
        This method removes any crops from the field's list of active crops if they are no longer alive.
        """
        self.crops = [crop for crop in self.crops if crop.data.is_alive]

    def _reset_crop_field_coverage_fractions(self) -> None:
        """
        Resets crops to have equal field coverage while in the field.
        """
        number_of_crops_in_field = len(self.crops)
        if number_of_crops_in_field == 0:
            return

        field_coverage_fraction = 1 / number_of_crops_in_field
        for crop in self.crops:
            crop.data.field_proportion = field_coverage_fraction

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
    def _execute_daily_processes(self, current_weather: CurrentWeather) -> None:
        """Executes all daily updates on this field's soil and crop objects.

        Parameters
        ----------
        current_weather : CurrentWeather
            Object containing the environment conditions on this day.

        Notes
        -----
        This method is designed to make it easier to change the order of process execution, which is desirable because
        it will allow subject-matter experts to more easily experiment with different orders.

        """
        # TODO: implement snow addition, melting, and sublimation - issue #317
        snow_cover = 0
        total_plant_cover = self.field_data.current_residue + self._determine_total_above_ground_biomass()
        self.soil.soil_temp.daily_soil_temperature_update(current_weather.incoming_light,
                                                          current_weather.mean_air_temperature,
                                                          current_weather.min_air_temperature,
                                                          current_weather.max_air_temperature,
                                                          total_plant_cover,
                                                          snow_cover,
                                                          current_weather.annual_mean_air_temperature)

        self._cycle_water(current_weather)

        for crop in self.crops:
            if not crop.data.in_growing_season:
                continue

            crop.heat_units.absorb_heat_units(current_weather.mean_air_temperature, current_weather.min_air_temperature,
                                              current_weather.max_air_temperature)
            crop.root_development.develop_roots()
            crop.nitrogen_incorporation.incorporate_nitrogen(self.soil.data)
            crop.phosphorus_incorporation.incorporate_phosphorus(self.soil.data)
            crop.growth_constraints.constrain_growth(crop.data.max_transpiration, current_weather.mean_air_temperature)
            crop.leaf_area_index.grow_canopy()
            crop.biomass_allocation.allocate_biomass(current_weather.incoming_light)

    def _cycle_water(self, current_weather: CurrentWeather):
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

            It should also be noted that while this method is more messy and complex than it could be, this is a
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
        self.soil.infiltration.infiltrate(precipitation_reaching_soil, 1.0, full_evapotranspirative_demand)
        self.soil.percolation.percolate(self.field_data.seasonal_high_water_table)
        # TODO: find reasonable values/way to set minimum cover management factor - issue #520
        self.soil.soil_erosion.erode(self.field_data.field_size, 0.02, self.field_data.current_residue)
        self.soil.phosphorus_cycling.cycle_phosphorus(precipitation_reaching_soil, self.soil.data.accumulated_runoff,
                                                      self.field_data.field_size, current_weather.mean_air_temperature)
        self.soil.nitrogen_cycling.cycle_nitrogen(self.field_data.field_size)
        self.soil.carbon_cycling.cycle_carbon(precipitation_reaching_soil, current_weather.mean_air_temperature,
                                              self.field_data.field_size)

        weighted_transpiration_total = 0.0
        weights_sum = 0.0
        for crop in self.crops:
            crop.water_dynamics.set_maximum_transpiration(remaining_evapotranspirative_demand)
            weighted_transpiration_total += crop.data.max_transpiration * crop.data.field_proportion
            weights_sum += crop.data.field_proportion
        weighted_average_transpiration = weighted_transpiration_total / weights_sum

        # TODO: Implement snow (melting and sublimation) - issue #317
        snow_water_content = 0.0
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
                crop.data.cumulative_evaporation = 0.0
                crop.data.cumulative_transpiration = 0.0
                crop.data.cumulative_potential_evapotranspiration = 0.0

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
            return 0.0
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
