from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.field.crop_planting_config import CropPlantingConfig
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from typing import Optional, List, Dict
from SC_redesign.Crop_and_Soil.field.harvest_operations import HarvestOperation

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
        self.crops: Optional[List[Crop]] = None  # empty crop list
        """crops currently in the field"""

    def manage_field(self, day: int, year: int, current_weather: CurrentWeather) -> None:
        """main Field function, runs all field routines based on current attribute configuration

        Args:
            day: the current (sequential) day of the simulation  - TODO: not yet implemented
            year: the current (sequential) year of the simulation - TODO: not yet implemented
            current_weather: a CurrentWeather object, containing a collection of today's weather variables needed
                for field processes.

        Details: **All the logic (after setup) will go in this function**
        """
        # check the schedule to see what needs to be done today
        self.check_schedule(day, year)

        # --- Soil Management---
        # nutrient amendments
        if self.field_data.is_amendment_day:
            self.amend_soil()

        # tillage
        if self.field_data.is_tillage_day:
            self.till_soil()

        # --- Whole-Field Methods ---
        # Allow non-management field processes (water/nutrient cycling) to occur
        self.cycle_water()
        # ... Other ...

        # --- Crop Management ---
        # planting
        if self.field_data.is_planting_day:
            self.plant_crops(self.current_crop_config)

        # perform remaining tasks if crops currently in field
        if self.crops is not None:

            # put crops into dormancy if daylength is as or below dormancy daylength threshold
            if current_weather.daylength <= self.field_data.dormancy_threshold_daylength:
                self.start_dormancy()

            # allow crops to grow
            self.grow_crops(current_weather.incoming_light, current_weather.min_air_temperature,
                            current_weather.mean_air_temperature, current_weather.max_air_temperature)

            # allow grazing
            if self.field_data.grazers_present:
                self.graze_field()

            # conduct harvest routines
            if self.field_data.is_harvest_day:
                self.harvest_crops()

        pass

    @property
    def current_crop_config(self) -> CropPlantingConfig:
        """get/build the current crop species/configuration for this day"""
        return CropPlantingConfig()  # TODO: placeholder to satisfy typing; needs true implementation

    @property
    def _composition_sums_to_one(self) -> bool:
        """ensure that the crop_proportions values sum to 1"""
        return sum([crop.field_proportion for crop in self.crops]) == 1.0

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
        pass
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
    def plant_crops(self, current_crop_config: CropPlantingConfig) -> None:
        """plant the current crop(s) into the filed"""
        for sp in current_crop_config.species:
            self.add_crop(sp)
        pass

    def add_crop(self, species: str, field_cover: float = 1.0,
                 priority: int = 1) -> None:
        """add a crop to the field's current crop list and update relevant attributes

        Args:
            species: the species of crop to plant  - TODO perhaps a Crop or CropData object instead?
            field_cover: the desired proportion of the field for this crop to occupy, must be space available.
            priority: the crop's priority level for resource acquisition
        """
        # check if there's room for the desired cover in the field
        if sum([crop.field_proportion for crop in self.crops]) + field_cover > 1:
            ValueError("Desired proportion of field not available")
        # plant the crop
        self.crops.append(Crop.plant_species(species))
        # ... update field_proportions of all crops
        # ... set the priority of this new crop
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
        soil_layer_attributes = self._get_soil_layer_attributes_for_crop_growth()
        for this_crop in self.crops:
            this_crop.grow_crop(
                layer_nitrates=soil_layer_attributes["nitrates"],
                layer_depths=soil_layer_attributes["depths"],
                layer_phosphates=soil_layer_attributes["phosphates"],
                soil_water_factor=self.soil.data.water_factor,
                max_transpiration=self.field_data.max_transpiration,
                incoming_light=incoming_light,
                evaporation=self.field_data.evaporation,
                transpiration=self.field_data.transpiration,
                adjusted_potential_evapotranspiration=self.field_data.potential_evapotranspiration_adjusted,
                max_evapotranspiration=self.field_data.max_evapotranspiration,
                mean_air_temperature=mean_air_temperature, min_air_temperature=min_air_temperature,
                max_air_temperature=max_air_temperature
            )

    def harvest_crops(self):
        """perform the harvest operation on all crops in the field, depending on the harvest operation"""
        for crop in self.crops:

            if self.field_data.harvest_type == HarvestOperation.HARVEST:
                crop.crop_management.manage_harvest(cut=True, collect=True, kill=True)

            if self.field_data.harvest_type == HarvestOperation.HARVEST_NOKILL:
                crop.crop_management.manage_harvest(cut=True, collect_yield=True, kill=False)

            # TODO: future method to cut crops, leave them in the field to dry prior to harvest?

    def graze_field(self):  # TODO: placeholder; no grazing method currently implemented in RUFAS
        """allow grazers to graze in the field during the current day"""
        pass

    def start_dormancy(self) -> None:
        """Set all crops that can go dormant to being dormant"""
        for crop in self.crops:
            crop.assess_dormancy()
    # </editor-fold>

    # <editor-fold desc="--- Field-level Methods ---">
    def cycle_water(self):
        """allow the water to cycle through the field.

         Details: Water cycling is intimately linked to both soil and crops and, as such, is a property of the
         whole-field. Therefore, it makes most sense for this process to take place within the field class rather
         than in both the crop and soil classes. Water uptake by the crop will likely be an exception that should
         take place during a crop's grow() method. Other exceptions may come up as these modules develop.
         """
        for crop in self.crops:
            crop.water_dynamics.cycle_water()  # TODO: tweak this once water method sare more solidified.
        pass
    # </editor-fold>
