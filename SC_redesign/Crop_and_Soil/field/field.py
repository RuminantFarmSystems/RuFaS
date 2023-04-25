from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from typing import Optional, List, Dict
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
        self.soil = soil or Soil()  # default soil if not given.
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
        self.soil.fertilizer_phosphorus.add_fertilizer_phosphorus(0)
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
        the crop's harvest day
        """
        for crop in self.crops:
            if not crop.data.is_harvest_day:
                continue  # move on to checking next crop

            if crop.data.next_harvest_operation == HarvestOperation.HARVEST:
                crop.crop_management.manage_harvest(cut=True, collect=True, kill=True)

            if crop.data.next_harvest_operation == HarvestOperation.HARVEST_NOKILL:
                crop.crop_management.manage_harvest(cut=True, collect_yield=True, kill=False)

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

         Details: Water cycling is intimately linked to both soil and crops and, as such, is a property of the
         whole-field. Therefore, it makes most sense for this process to take place within the field class rather
         than in both the crop and soil classes. Water uptake by the crop will likely be an exception that should
         take place during a crop's grow() method. Other exceptions may come up as these modules develop.
         """
        total_initial_canopy_free_water = 0
        for crop in self.crops:
            crop.water_dynamics.cycle_water()  # TODO: tweak this once water method sare more solidified.
            total_initial_canopy_free_water += crop.data.initial_canopy_free_water
            crop.water_uptake.uptake_water()

        # TODO: track snow cover on soil surface somewhere - Issue #317
        # TODO: figure out how to determine weighting coefficient when there are multiple crops in the field
        # TODO: figure out how to determine minimum cover management factor when there are multiple crops in the field
        self.soil.daily_soil_water_routine(rainfall=current_weather.rainfall, weighting_coefficient=1,
                                           has_seasonal_high_water_table=self.field_data.seasonal_high_water_table,
                                           solar_radiation=current_weather.incoming_light,
                                           max_air_temp=current_weather.max_air_temperature,
                                           min_air_temp=current_weather.min_air_temperature,
                                           avg_air_temp=current_weather.mean_air_temperature,
                                           above_ground_biomass=self._determine_total_above_ground_biomass(),
                                           residue=self.field_data.current_residue,
                                           snow_water_content=current_weather.snow_fall,
                                           initial_canopy_free_water=total_initial_canopy_free_water,
                                           minimum_cover_management_factor=0.2, field_size=self.field_data.field_size)
        pass

    def _determine_total_above_ground_biomass(self) -> float:
        """Calculate the total amount of above-ground biomass still on the plant(s) in the field (kg / ha)"""
        total_above_ground_biomass = 0
        for crop in self.crops:
            total_above_ground_biomass += crop.data.above_ground_biomass
        return total_above_ground_biomass

    # </editor-fold>

    # <editor-fold desc="--- Annual Reset Methods ---">
    def perform_annual_reset(self) -> None:
        """Collect all annual accumulated totals from Field, Crop, and Soil modules, write them to some sort of output
            file, and then reset all annual totals"""
        self.soil.data.do_annual_reset()
        return
