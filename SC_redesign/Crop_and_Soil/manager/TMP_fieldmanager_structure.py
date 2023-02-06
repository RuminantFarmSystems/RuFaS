from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from typing import Optional, List
from dataclasses import dataclass

@dataclass(kw_only=True)
class FieldData:
    """data object to track the field-specific variables"""

class Field:  # TODO: move to field/ directory
    """object representing an agricultural field"""
    def __init__(self, field_data: Optional[FieldData] = None, soil: Optional[Soil] = None):
        # field-wide attributes
        field_data = field_data or FieldData()
        """field data component"""

        # soil attributes
        self.soil = soil or Soil()  # default soil if not given.
        """the soil component of the field"""
        self.is_amendment_day: bool = False
        """should nutrients be added to the soil today?"""
        self.is_tillage_day: bool = False
        """should the soil be tilled today?"""

        # crop attributes
        self.crops: Optional[List[Crop]] = None  # empty crop list
        """crops currently in the field"""
        self.crop_proportions: Optional[List[float]] = None  # empty comp list
        """proportion of the field's area that each crop occupies"""
        self.priorities: Optional[List[float]] = None
        """the priorities of each crop for obtaining nutrients from a given soil layer"""
        self.is_planting_day: bool = False
        """is today the day to plant new crops?"""
        self.is_cutting_day: bool = False
        """is today the day to cut crops in the field?"""
        self.harvest_proportion: float = 1
        """the proportion of cut crop biomass that will be removed from the field"""

    def manage_field(self, day, year, current_weather) -> None:
        """main Field function, runs all field routines based on current attribute configuration

        Details: **All the logic (after setup) will go in this function**
        """
        # --- Soil Management---
        # nutrient amendments
        if self.is_amendment_day:
            self.amend_soil()

        # tillage
        if self.is_tillage_day:
            self.till_soil()

        # Allow non-management soil processes (water/nutrient cycling) to occur
        # ...
        # ...

        # --- Crop Management ---
        # planting
        if self.is_planting_day:
            self.plant_crops(self.current_crop_config)

        # skip remaining tasks if no crops currently in field
        if self.crops is None:  # empty crop list, early return (or similar)
            return

        # allow crops to grow
        self.grow_crops()

        if self.field_data.grazers_present:
            self.graze_field()

        # conduct harvest routines
        if self.is_cutting_day:
            self.cut_crops()

        pass

    @property
    def current_crop_config(self):
        """get the current crop species/configuration for this day"""
        pass

    # --- Setup Methods ---
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

    # --- Soil Managmenet Methods ---

    def till_soil(self) -> None:
        """till the soil"""
        pass

    def amend_soil(self) -> None:
        """amend the soil with nutrients"""
        pass

    # ---- Crop Management ----
    def plant_crops(self, current_crop_config) -> None:
        """plant the current crop(s) into the filed"""
        for sp in current_crop_config.species:
            self.add_crop(sp)
        pass

    def add_crop(self, species: str, field_cover: float = 1.0,
                 priority: int = 1) -> None:
        """add a crop to the field's current crop list and update relevant attributes"""
        if sum(self.crop_proportions) + field_cover > 1:
            ValueError("Desired proportion of field not available")
        self.crops.append(Crop.plant_species(species))
        self.crop_proportions.append(field_cover)
        self.priorities.append(priority)

    def grow_crops(self, incoming_light, mean_air_temperature, max_air_temperature) -> None:
        """allow the current crops to execute their daily growth routines"""
        for this_crop in self.crops:
            this_crop.grow_crop(layer_nitrates=self.soil.layer_nitrates,
                                layer_phosphates=self.soil.layer_phosphates,
                                layer_depths=self.soil.layer_depths,
                                soil_water_factor=self.soil.water_factor,
                                evaporation=self.field_data.evaporation,
                                max_transpiration=self.field_data.max_transpiration,
                                max_evapotranspiration=self.field_data.max_evapotranspiration,
                                incoming_light=incoming_light,
                                mean_air_temperature=mean_air_temperature,
                                max_air_temperature=max_air_temperature)

    def cut_crops(self):
        """cut all crops in the field, either removing the cut biomass as harvest or leaving it in the field as
        residue to be incorporated into the soil depending upon 'harvest_percent'
        """
        cuttings = [this_crop.cut(fraction=self.cut_fraction) for this_crop in self.crops]
        if self.harvest_proportion > 0:
            # ... remove cut biomass from field
            pass
        else:
            # ... leave cut biomass in field as residue
            pass

        # ... kill crops if not perennial
        pass

    def graze_field(self):
        """allow grazers to graze in the field during on the current day"""
        pass

    @property
    def _composition_sums_to_one(self) -> bool:
        """ensure that the crop_proportions values sum to 1"""
        return sum(self.crop_proportions) == 1.0
